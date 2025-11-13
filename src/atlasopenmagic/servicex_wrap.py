"""This module provides a wrapper to fetch data with ServiceX for the atlasopenmagic package."""

from servicex import query, deliver
from servicex_analysis_utils import ds_type_resolver, to_awk, get_structure as sx_get_structure
from .metadata import get_urls
import logging


def _sample_finder(dataset: str | int):
    """Helper function to resolve dataset type and get files."""
    try:
        files = ds_type_resolver(get_urls(dataset))
    except Exception as e1:
        logging.debug("get_urls failed: %s", e1)
        try:
            files = ds_type_resolver(str(dataset))
        except Exception as e2:
            logging.debug("ds_type_resolver failed: %s", e2)
            raise ValueError(f"Could not resolve dataset: {dataset}, errors: {e1}, {e2}")
    return files


def fetch_data(
    dataset: str | int,
    tree: str,
    branch_filter: str | list[str],
    selection: str | None = None,
    nfiles: int = 500,
    arrays: bool = True,
    **kwargs,
):
    """Fetch data using ServiceX based on the given selection and dataset.

    Args:
        selection (str): The selection criteria for the data.
        dataset (str): The dataset identifier. Can be DSID key or eos path or RECORDID

    Returns:
        dict: A dictionary containing the fetched data.
    """
    # Resolve dataset type
    files = _sample_finder(dataset)
    # Create a ServiceX query
    query_up = query.UprootRaw(
        [
            {"treename": tree, "filter_name": branch_filter, "cut": selection},
        ]
    )

    spec = {
        "General": {"Delivery": "LocalCache"},
        "Sample": [
            {
                "Name": str(dataset),
                "Dataset": files,
                "Query": query_up,
                "NFiles": nfiles,
            }
        ],
    }

    filtered_files = deliver(spec, **kwargs)

    if arrays:
        # Convert to Awkward arrays
        return to_awk(filtered_files, **kwargs)
    else:
        return filtered_files


def get_structure(dataset: str | int, **kwargs):
    """Get the file structure of the sample."""
    files = _sample_finder(dataset)
    return sx_get_structure(files, **kwargs)
