import streamlit as st

from src.functions import parse_prj

st.title("Simple ContamW project file editor")

prj_file = st.file_uploader("Choose a .prj file", type=["prj"])
if prj_file is not None:
    df, col_name_string, target_data, pre_target_data, post_target_data = parse_prj(prj_file)

    edited_df = st.data_editor(df)
    target_string = edited_df.to_csv(header=False, index=False, sep="\t")

    full_data = pre_target_data + col_name_string + target_string + post_target_data

    st.download_button(
        label="Download edited data as prj file",
        data=full_data,
        file_name=prj_file.name,
        mime="text/plain",
    )
