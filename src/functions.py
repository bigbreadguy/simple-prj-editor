import io
from typing import Tuple, List

import pandas as pd
from pandas import DataFrame
from streamlit.runtime.uploaded_file_manager import UploadedFile


def parse_prj(
        prj_file: UploadedFile
) -> tuple[DataFrame, str | None, str, str]:
    """
    :param prj_file: UploadedFile
    :return: parsed data
    """
    passed_start_flow_elements = False
    passed_end_flow_elements = False
    passed_start_zones = False
    passed_end_zones = False
    passed_start_flow_paths = False
    passed_end_flow_paths = False
    header_data = []
    flow_elements_strings = []
    zones_column_names = None
    zones_columns = []
    zones_strings = []
    flow_paths_column_names = None
    flow_paths_columns = []
    flow_paths_strings = []
    footer_data = []

    for row in prj_file.readlines():
        line = row.decode("CP949")

        # Check end condition of each section
        if (
            passed_start_flow_elements
            and line.startswith("-999")
            and not passed_end_flow_elements
        ):
            passed_end_flow_elements = True
        if (
            passed_start_zones
            and line.startswith("-999")
            and not passed_end_zones
            and passed_end_flow_elements
        ):
            passed_end_zones = True
        if (
            passed_start_flow_paths
            and line.startswith("-999")
            and not passed_end_flow_paths
            and passed_end_flow_elements
            and passed_end_zones
        ):
            passed_end_flow_paths = True

        # Parse data by section
        if not passed_start_flow_paths:
            header_data.append(line)
        elif passed_start_flow_paths and not passed_end_flow_paths:
            if line.startswith("!"):
                flow_paths_column_names = line
                flow_paths_columns = flow_paths_column_names.split()
                flow_paths_columns.remove("!")
                flow_paths_columns.extend(["Unnamed 0", "Unnamed 1"])
            else:
                flow_paths_strings.append(line)
        elif passed_start_flow_paths and passed_end_flow_paths:
            footer_data.append(line)

        # Check start condition of each section
        if "flow elements" in line and not passed_start_flow_elements:
            passed_start_flow_elements = True
        if (
            "zones" in line
            and passed_end_flow_elements
            and not passed_start_zones
        ):
            passed_start_zones = True
        if (
            "flow paths:" in line
            and passed_end_flow_elements
            and passed_end_zones
            and not passed_start_flow_paths
        ):
            passed_start_flow_paths = True

    raw_data_flow_paths = "".join(flow_paths_strings)
    data_flow_paths = pd.read_csv(
        io.StringIO(raw_data_flow_paths), names=flow_paths_columns, sep=r"\s+")

    return (
        data_flow_paths,
        flow_paths_column_names,
        "".join(header_data),
        "".join(footer_data)
    )
