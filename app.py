import os

from mitosheet.streamlit.v1 import spreadsheet
import streamlit as st

from src.functions import parse_prj, join_data

st.title("ContamW 프로젝트 파일 에디터")

data_dir = os.path.join("data")
if not os.path.isdir(data_dir):
    os.mkdir(data_dir)

prj_file = st.file_uploader(".prj 파일을 선택해 주세요.", type=["prj"])
if prj_file is not None:
    # Parse data from the uploaded .prj file
    (
        flow_paths,
        zones,
        flow_elements,
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

    flow_paths.rename(columns={
        "e#": "경로 종류",
        "relHt": "상대 높이",
        "mult": "전체 면적"
    }, inplace=True)

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

    columns = list(merged_data.columns)
    n_index = columns.index("n#")
    m_index = columns.index("m#")
    new_columns = [col for col in columns if col not in ["존 이름(from)", "존 이름(to)"]]
    new_columns.insert(n_index + 1, "존 이름(from)")
    new_columns.insert(m_index + 2, "존 이름(to)")

    merged_data = merged_data[new_columns]

    st.write("**경로 종류 보기**")
    st.json(flow_elements)

    edited_dfs, code = spreadsheet(
        merged_data,
        import_folder=data_dir
    )

    file_to_import = st.file_uploader(".prj 파일로 변환 할 파일(.csv 또는 .xlsx)을 선택해 주세요.", type=["csv", "xlsx"])
    if file_to_import is not None:
        file_to_import_dir = os.path.join(data_dir, file_to_import.name)
        with open(file_to_import_dir, "wb") as f:
            f.write(file_to_import.read())

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
        label="수정한 내용(.prj로 변환) 다운로드",
        data=full_data,
        file_name=prj_file.name,
        mime="text/plain",
    )
    st.write(
        ":red[※ 첫 번째 시트의 데이터 만 .prj 파일로 변환 됩니다.]"
    )
