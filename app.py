
import streamlit as st
import pandas as pd

st.title("Process - Function Linker")

st.write("Upload your Excel or CSV files to create relationships between Processes and Functions.")

process_file = st.file_uploader("Upload Process file", type=["xlsx", "csv"])
function_file = st.file_uploader("Upload Function file", type=["xlsx", "csv"])

if process_file and function_file:
    df_proc = pd.read_excel(process_file) if process_file.name.endswith('xlsx') else pd.read_csv(process_file)
    df_func = pd.read_excel(function_file) if function_file.name.endswith('xlsx') else pd.read_csv(function_file)

    st.write("### Process Data")
    st.dataframe(df_proc.head())
    st.write("### Function Data")
    st.dataframe(df_func.head())

    st.write("Now link processes to one or more functions.")
    process_col = st.selectbox("Select Process column", df_proc.columns)
    function_col = st.selectbox("Select Function column", df_func.columns)

    if st.button("Generate Output"):
        merged = []
        for _, proc in df_proc.iterrows():
            for _, func in df_func.iterrows():
                merged.append({
                    "Process": proc[process_col],
                    "Function": func[function_col]
                })
        df_out = pd.DataFrame(merged)
        st.success("Output created!")
        st.dataframe(df_out.head())
        df_out.to_excel("output.xlsx", index=False)
        st.download_button("Download Excel", df_out.to_csv(index=False).encode("utf-8"), "output.csv", "text/csv")

