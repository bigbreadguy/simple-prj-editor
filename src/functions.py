import io
from typing import Tuple, List, Dict

import pandas as pd
from pandas import DataFrame
from streamlit.runtime.uploaded_file_manager import UploadedFile


def parse_prj(
        prj_file: UploadedFile
) -> tuple[DataFrame, DataFrame, dict[int, str], str | None, str | None, str, str, str, str, str]:
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
    flow_elements_dict = dict()
    flow_elements_strings = []
    other_elements_strings = []
    zones_column_names = None
    zones_columns = []
    zones_strings = []
    initial_zone_concentrations_strings = []
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
        if not passed_start_flow_elements:
            header_data.append(line)
        if passed_start_flow_elements and not passed_end_flow_elements:
            flow_elements_strings.append(line)
            if line[0].isdigit():
                elements = line.split()
                key = int(elements[0])
                value = elements[-1]
                flow_elements_dict[key] = value
        if passed_end_flow_elements and not passed_start_zones:
            other_elements_strings.append(line)
        if passed_start_zones and not passed_end_zones:
            if line.startswith("!"):
                zones_column_names = line
                zones_columns = zones_column_names.split()
                zones_columns.remove("!")
                zones_columns = list(
                    filter(
                        lambda s: '<' not in s and '>' not in s, zones_columns
                    )
                )
            else:
                zones_strings.append(line)
        if passed_end_zones and not passed_start_flow_paths:
            initial_zone_concentrations_strings.append(line)
        if passed_start_flow_paths and not passed_end_flow_paths:
            if line.startswith("!"):
                flow_paths_column_names = line
                flow_paths_columns = flow_paths_column_names.split()
                flow_paths_columns.remove("!")
                flow_paths_columns.extend(["Unnamed 0", "Unnamed 1"])
            else:
                flow_paths_strings.append(line)
        if passed_end_flow_paths:
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

    raw_data_zones = "".join(zones_strings)
    data_zones = pd.read_csv(
        io.StringIO(raw_data_zones), names=zones_columns, sep=r"\s+"
    )

    return (
        data_flow_paths,
        data_zones,
        flow_elements_dict,
        zones_column_names,
        flow_paths_column_names,
        "".join(header_data),
        "".join(flow_elements_strings),
        "".join(other_elements_strings),
        "".join(initial_zone_concentrations_strings),
        "".join(footer_data)
    )


def join_data(
        flow_paths: DataFrame,
        zones: DataFrame,
        zones_col_name_string: str,
        flow_paths_col_name_string: str,
        header_string: str,
        flow_elements_string: str,
        other_elements_string: str,
        initial_zone_concentrations_string: str,
        footer_string: str
):
    flow_paths_string = flow_paths.to_csv(header=False, index=False, sep="\t")
    zones_string = zones.to_csv(header=False, index=False, sep="\t")
    full_string = (
            header_string
            + flow_elements_string
            + other_elements_string
            + zones_col_name_string
            + zones_string
            + initial_zone_concentrations_string
            + flow_paths_col_name_string
            + flow_paths_string
            + footer_string
    )

    return full_string.encode("CP949")
