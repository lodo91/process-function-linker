import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Process-Function Linker", layout="wide")

st.title("🔗 Process–Function Linker")

# --- Upload dei file Excel ---
st.sidebar.header("📂 Upload data")
uploaded_processes = st.sidebar.file_uploader("Upload Process List (.xlsx)", type=["xlsx"])
uploaded_functions = st.sidebar.file_uploader("Upload Function List (.xlsx)", type=["xlsx"])

# Session state per i link salvati
if "links" not in st.session_state:
    st.session_state.links = []

# --- Caricamento dati ---
if uploaded_processes and uploaded_functions:
    processes_df = pd.read_excel(uploaded_processes)
    functions_df = pd.read_excel(uploaded_functions)

    process_col = st.sidebar.selectbox("Select Process column", processes_df.columns)
    function_col = st.sidebar.selectbox("Select Function column", functions_df.columns)

    st.subheader("1️⃣ Select a Process")
    selected_process = st.selectbox("Process:", processes_df[process_col])

    st.subheader("2️⃣ Select one or more Functions")
    selected_functions = st.multiselect("Functions:", functions_df[function_col])

    # Bottone per salvare il collegamento
    if st.button("💾 Save link"):
        for f in selected_functions:
            st.session_state.links.append({"Process": selected_process, "Function": f})
        st.success(f"Linked {selected_process} to {len(selected_functions)} function(s).")
        st.rerun()  # <— sostituito e funzionante su Streamlit Cloud

    # Mostra i link salvati
    if st.session_state.links:
        st.subheader("3️⃣ Saved links")
        links_df = pd.DataFrame(st.session_state.links)
        st.dataframe(links_df, use_container_width=True)

        # Esporta in Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            links_df.to_excel(writer, index=False, sheet_name="Links")
        excel_data = output.getvalue()

        st.download_button(
            label="⬇️ Download Excel",
            data=excel_data,
            file_name="process_function_links.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

else:
    st.info("Please upload both the Process and Function Excel files to start.")
