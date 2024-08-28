import streamlit as st

from src.functions import parse_prj

st.title("Simple ContamW project file editor")

prj_file = st.file_uploader("Choose a .prj file", type=["prj"])
if prj_file is not None:
    df, col_name_string, target_data, pre_target_data, post_target_data = parse_prj(prj_file)

    edited_df = st.dataframe(df)