import pytest
import atlasopenmagic as atom
from servicex import dataset


@pytest.mark.parametrize(
    "input_ds, expected_type",
    [
        ("123", dataset.CERNOpenData),  # Record ID
        ("root://eospublic.cern.ch//eos/", dataset.FileList),  # EOS prefix
        ("root://eospublic.cern.ch//eos/*", dataset.XRootD),  # XRootD with wildcard
        ("/eos/opendata/atlas/rucio/somefile.root", dataset.FileList),  # eos path
        ("301204", dataset.FileList),  # DSID using get_urls
    ],
)
def test_sample_finder(input_ds, expected_type):
    """
    Test the _sample_finder function from servicex_wrap
    """
    result = atom.servicex_wrap._sample_finder(input_ds)
    assert isinstance(result, expected_type)
