import os

from mitosheet.streamlit.v1 import spreadsheet
import streamlit as st

from src.functions import parse_prj

st.title("Simple ContamW project file editor")

data_dir = os.path.join("data")
if not os.path.isdir(data_dir):
    os.mkdir(data_dir)

prj_file = st.file_uploader("Choose a .prj file", type=["prj"])
if prj_file is not None:
    df, col_name_string, target_data, pre_target_data, post_target_data = parse_prj(prj_file)

    edited_dfs, code = spreadsheet( 
        df,
        import_folder=data_dir
    )

    target_string = edited_dfs.popitem(last=False)[1].to_csv(header=False, index=False, sep="\t")
    full_string = pre_target_data + col_name_string + target_string + post_target_data
    full_data = full_string.encode("CP949")

    st.download_button(
        label="Download edited data as prj file",
        data=full_data,
        file_name=prj_file.name,
        mime="text/plain",
    )
    st.write(":red[※ Only the data in the first sheet will be converted to prj file]")
