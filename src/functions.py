import io
from typing import Tuple, List

import pandas as pd
from pandas import DataFrame
from streamlit.runtime.uploaded_file_manager import UploadedFile


def parse_prj(
        prj_file: UploadedFile
) -> tuple[DataFrame, str | None, list[str], str, str]:
    passed_start = False
    passed_end = False
    pre_strings = []
    column_names = None
    columns = []
    target_strings = []
    post_strings = []

    for row in prj_file.readlines():
        line = row.decode("CP949")
        if passed_start and line.startswith("-999"):
            passed_end = True

        if not passed_start:
            pre_strings.append(line)
        elif passed_start and not passed_end:
            if line.startswith("!"):
                column_names = line
                columns = column_names.split()
                columns.remove("!")
                columns.extend(["Unnamed 0", "Unnamed 1"])
            else:
                target_strings.append(line)
        elif passed_start and passed_end:
            post_strings.append(line)

        if line.endswith("flow paths:\n"):
            passed_start = True

    raw_data = "\n".join(target_strings)
    data = pd.read_csv(io.StringIO(raw_data), names=columns, sep=r"\s+")

    return (
        data,
        column_names,
        target_strings,
        "\n".join(pre_strings),
        "\n".join(post_strings)
    )
