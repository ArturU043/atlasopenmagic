import pytest
from unittest.mock import patch
import json
import atlasopenmagic as atom
from servicex import dataset, query


@pytest.mark.parametrize(
    "input_ds, expected_type",
    [
        ("123", dataset.CERNOpenData),  # Record ID
        ("root://eospublic.cern.ch//eos/", dataset.FileList),
        ("root://eospublic.cern.ch//eos/*", dataset.XRootD),
        (
            "/eos/opendata/atlas/rucio/somefile.root",
            dataset.FileList,
        ),  # eos path
        ("301204", dataset.FileList),  # DSID using get_urls
    ],
)
def test_sample_finder(input_ds, expected_type):
    """
    Test the _sample_finder function from servicex_wrap
    """
    # Do mocking of get_urls to return a known file list
    with patch.object(
        atom.metadata, "get_urls", return_value=["root://eospublic.cern.ch//eos/path/to/file.root"]
    ):
        result = atom.servicex_wrap._sample_finder(input_ds)
    assert isinstance(result, expected_type)


def test_get_data():
    """
    Test that get_data builds the correct spec and calls deliver as expected.
    """

    dataset = "301204"
    fake_files = ["root://eospublic.cern.ch//eos/path/to/file.root"]
    fake_deliver_result = {dataset: ["/local/cache/file.root"]}

    # --- Mocking ---
    with patch.object(
        atom.servicex_wrap, "_sample_finder", return_value=fake_files
    ) as mock_finder, patch.object(
        atom.servicex_wrap, "deliver", return_value=fake_deliver_result
    ) as mock_deliver:

        result = atom.servicex_wrap.get_data(
            dataset=dataset,
            tree="nominal",
            branch_filter=["pt", "eta"],
            selection="pt > 20",
            nfiles=5,
            return_paths=True,
            some_kwarg="test_kwarg",
        )

    # --- Verify behavior ---
    assert result == ["/local/cache/file.root"]

    # _sample_finder should be called once
    mock_finder.assert_called_once_with(dataset)

    # deliver should be called once
    mock_deliver.assert_called_once()
    spec_arg = mock_deliver.call_args.args[0]  # first arg
    kwargs = mock_deliver.call_args.kwargs

    # Ensure the kwargs were passed through
    assert kwargs["some_kwarg"] == "test_kwarg"

    # --- Inspect spec structure ---
    assert spec_arg["General"]["Delivery"] == "LocalCache"
    assert len(spec_arg["Sample"]) == 1

    sample = spec_arg["Sample"][0]
    assert sample["Name"] == dataset
    assert sample["Dataset"] == fake_files
    assert sample["NFiles"] == 5

    # Inspect the query object
    assert isinstance(sample["Query"], query.UprootRaw)
    # retrieve the selection string and load to [dict]
    sent_query = json.loads(sample["Query"].generate_selection_string())[0]

    # assert user-input parameters
    assert sent_query["cut"] == "pt > 20"
    assert sent_query["treename"] == "nominal"
    assert sent_query["filter_name"] == ["pt", "eta"]
