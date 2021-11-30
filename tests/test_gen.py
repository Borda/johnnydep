# coding: utf-8
from __future__ import unicode_literals

import os

import pytest

from johnnydep.lib import JohnnyDist


here = os.path.dirname(__file__)


def test_generated_metadata_from_dist_name(make_dist):
    make_dist()
    jdist = JohnnyDist("jdtest")
    expected_metadata = {
        "author": "default author",
        "author_email": "default@example.org",
        "description": "default long text for PyPI landing page \U0001f4a9",
        "home_page": "https://www.example.org/default",
        "license": "MIT",
        "metadata_version": "2.1",
        "name": "jdtest",
        "platforms": ["default platform"],
        "summary": "default text for metadata summary",
        "version": "0.1.2",
    }
    # different versions of setuptools can put a different number of newlines at the
    # end of the long description metadata
    assert jdist.metadata.pop("description").rstrip() == expected_metadata.pop("description")
    assert jdist.metadata == expected_metadata


def test_generated_metadata_from_dist_path(make_dist):
    _dist, dist_path, _checksum = make_dist()
    jdist = JohnnyDist(dist_path)
    expected_metadata = {
        "author": "default author",
        "author_email": "default@example.org",
        "description": "default long text for PyPI landing page \U0001f4a9",
        "home_page": "https://www.example.org/default",
        "license": "MIT",
        "metadata_version": "2.1",
        "name": "jdtest",
        "platforms": ["default platform"],
        "summary": "default text for metadata summary",
        "version": "0.1.2",
    }
    assert jdist.metadata.pop("description").rstrip() == expected_metadata.pop("description")
    assert jdist.metadata == expected_metadata


def test_build_from_sdist(add_to_index):
    sdist_fname = os.path.join(here, "copyingmock-0.2.tar.gz")
    fragment = "#md5=9aa6ba13542d25e527fe358d53cdaf3b"
    add_to_index(name="copyingmock", path=sdist_fname, urlfragment=fragment)
    dist = JohnnyDist("copyingmock")
    assert dist.name == "copyingmock"
    assert dist.summary == "A subclass of MagicMock that copies the arguments"
    assert dist.required_by == []
    assert dist.import_names == ["copyingmock"]
    assert dist.homepage == "https://github.com/wimglenn/copyingmock"
    assert dist.extras_available == []
    assert dist.extras_requested == []
    assert dist.project_name == "copyingmock"
    assert dist.download_link.startswith("file://")
    assert dist.download_link.endswith("copyingmock-0.2.tar.gz")
    assert dist.checksum == "md5=9aa6ba13542d25e527fe358d53cdaf3b"


def test_plaintext_whl_metadata(add_to_index):
    # this dist uses an old-skool metadata version 1.2
    sdist_fname = os.path.join(here, "testpath-0.3.1-py2.py3-none-any.whl")
    fragment = "#md5=12728181294cf6f815421081d620c494"
    add_to_index(name="testpath", path=sdist_fname, urlfragment=fragment)
    dist = JohnnyDist("testpath==0.3.1")
    assert dist.serialise(fields=["name", "summary", "import_names", "homepage"]) == [
        {
            "name": "testpath",
            "summary": "Test utilities for code working with files and commands",
            "import_names": ["testpath"],
            "homepage": "https://github.com/jupyter/testpath",
        }
    ]


def test_old_metadata_20(add_to_index):
    # the never-officially-supported-but-out-in-the-wild metadata 2.0 spec (generated by wheel v0.30.0)
    whl_fname = os.path.join(here, "m20dist-0.1.2-py2.py3-none-any.whl")
    fragment = "#md5=488652bac3e1705e5646ea6a51f4d441"
    add_to_index(name="m20dist", path=whl_fname, urlfragment=fragment)
    jdist = JohnnyDist("m20dist")
    expected_metadata = {
        "author": "default author",
        "author_email": "default@example.org",
        "description": "default long text for PyPI landing page \U0001f4a9\n\n\n",
        "home_page": "https://www.example.org/default",
        "license": "MIT",
        "metadata_version": "2.0",
        "name": "m20dist",
        "platforms": ["default platform"],
        "summary": "default text for metadata summary",
        "version": "0.1.2",
    }
    assert jdist.metadata == expected_metadata
    assert jdist.checksum == "md5=488652bac3e1705e5646ea6a51f4d441"


def test_index_file_without_checksum_in_urlfragment(add_to_index, mocker):
    whl_fname = os.path.join(here, "vanilla-0.1.2-py2.py3-none-any.whl")
    add_to_index(name="vanilla", path=whl_fname)
    jdist = JohnnyDist("vanilla")
    assert jdist.versions_available == ["0.1.2"]
    mocker.patch("johnnydep.pipper.urlretrieve", return_value=(whl_fname, {}))
    assert jdist.checksum == "md5=8a20520dcb1b7a729b827a2c4d75a0b6"


def test_cant_pin():
    whl_fname = os.path.join(here, "vanilla-0.1.2-py2.py3-none-any.whl")
    jdist = JohnnyDist(whl_fname)
    with pytest.raises(Exception) as cm:
        jdist.pinned
    assert str(cm.value) == "Can not pin because no version available is in spec"
