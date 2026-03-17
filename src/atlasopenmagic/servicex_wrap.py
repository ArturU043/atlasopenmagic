"""This module provides a wrapper to fetch data with ServiceX for the atlasopenmagic package."""

from servicex import query, deliver
from servicex_analysis_utils import ds_type_resolver, to_awk
import logging


def get_data(
    datasets: str | int | list[str | int],
    tree: str,
    branch_filter: str | list[str],
    selection: str | None = None,
    nfiles: int = -1,
    return_paths: bool = False,
    **kwargs,
):
    """Fetch data using ServiceX based on the given selection and dataset.

    Args:
        selection (str): The selection criteria for the data.
        dataset (str): The dataset identifier. Can be DSID key, /eos path, XRootD url, or CernOpenData record ID
        tree (str): The name of the tree to query.
        branch_filter (str | list[str]): The branches to retrieve.
        nfiles (int): Number of files to process. Default is 500.
        return_paths (bool): If True, returns file paths instead of loaded data. Default is False.
        **kwargs: Additional keyword arguments for data delivery and conversion.

    Returns:
        filtered_files: Loaded in awkward arrays or a list of paths if specified
    """

    datasets = datasets if isinstance(datasets, list) else [datasets]

    query_up = query.UprootRaw(
        [
            {"treename": tree, "filter_name": branch_filter, "cut": selection},
        ]
    )

    queries = []

    for sample in datasets:
        logging.info("Preparing query for sample: %s", sample)

        queries.append(
            {
                "NFiles": nfiles,
                "Name": sample,
                "Dataset": ds_type_resolver(sample),
                "Query": query_up,
            }
        )

    spec = {"General": {"Delivery": "LocalCache"}, "Sample": queries}

    filtered_files = deliver(spec, **kwargs)  # Query sent to ServiceX server

    if return_paths is False:
        # Convert to Awkward arrays
        return to_awk(filtered_files, **kwargs)  # dictionary of arrays
    else:
        return filtered_files  # dictionary of paths
