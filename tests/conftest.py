import pytest


@pytest.fixture(scope="session")
def build_dir(tmp_path_factory):
    """Temporary build directory for compiled binaries"""
    return tmp_path_factory.mktemp("build")
