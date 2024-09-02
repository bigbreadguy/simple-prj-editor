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
    zones_target = zones[["Z#", "name"]]

    merged_data = flow_paths.merge(
        zones_target, how="left", left_on="n#", right_on="Z#")
    merged_data.rename(columns={"name": "존 이름(from)"}, inplace=True)
    merged_data.drop(columns=["Z#"], inplace=True)

    merged_data = merged_data.merge(
        zones_target, how="left", left_on="m#", right_on="Z#")
    merged_data.rename(columns={"name": "존 이름(to)"}, inplace=True)
    merged_data.drop(columns=["Z#"], inplace=True)

    merged_data["존 이름(from)"] = merged_data.apply(
        lambda row: "외기" if row["n#"] == -1 else row["존 이름(from)"], axis=1)
    merged_data["존 이름(to)"] = merged_data.apply(
        lambda row: "외기" if row["m#"] == -1 else row["존 이름(to)"], axis=1)

    edited_dfs, code = spreadsheet(
        merged_data,
        import_folder=data_dir
    )
    merged_data = edited_dfs.popitem(last=False)[1]
    flow_paths_edited = merged_data.drop(
        columns=["존 이름(from)", "존 이름(to)"], inplace=False)

    # Join data into a string
    full_data = join_data(
        flow_paths_edited,
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
