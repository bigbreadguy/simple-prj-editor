import os

from mitosheet.streamlit.v1 import spreadsheet
import streamlit as st

from src.functions import parse_prj, join_data

st.title("Simple ContamW project file editor")

data_dir = os.path.join("data")
if not os.path.isdir(data_dir):
    os.mkdir(data_dir)

prj_file = st.file_uploader("Choose a .prj file", type=["prj"])
if prj_file is not None:
    # Parse data from the uploaded .prj file
    (
        flow_paths,
        zones,
        zones_col_name_string,
        flow_paths_col_name_string,
        header_string,
        flow_elements_string,
        other_elements_string,
        initial_zone_concentrations_string,
        footer_string
    ) = parse_prj(prj_file)

    # Merge and display dataframes

    edited_dfs, code = spreadsheet(
        flow_paths,
        import_folder=data_dir
    )
    flow_paths = edited_dfs.popitem(last=False)[1]

    # Join data into a string
    full_data = join_data(
        flow_paths,
        zones,
        zones_col_name_string,
        flow_paths_col_name_string,
        header_string,
        flow_elements_string,
        other_elements_string,
        initial_zone_concentrations_string,
        footer_string
    )

    st.download_button(
        label="Download edited data as prj file",
        data=full_data,
        file_name=prj_file.name,
        mime="text/plain",
    )
    st.write(
        ":red[※ Only the data in the first sheet "
        "will be converted to prj file]"
    )
