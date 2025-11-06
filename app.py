import streamlit as st
import pandas as pd

st.set_page_config(page_title="Process–Function Linker v2", layout="wide")

st.title("🔗 Process ⇄ Function Linker")
st.markdown("Upload your process and function lists, then map each process to one or more functions.")

# --- File upload ---
uploaded_processes = st.sidebar.file_uploader("Upload Process List (.xlsx)", type=["xlsx"])
uploaded_functions = st.sidebar.file_uploader("Upload Function List (.xlsx)", type=["xlsx"])

if uploaded_processes and uploaded_functions:
    processes_df = pd.read_excel(uploaded_processes)
    functions_df = pd.read_excel(uploaded_functions)

    st.subheader("📋 Process Data")
    st.dataframe(processes_df)

    st.subheader("🏢 Function Data")
    st.dataframe(functions_df)

    # --- Initialize session state ---
    if "links" not in st.session_state:
        st.session_state.links = []
        st.session_state.current_index = 0

    processes = processes_df.iloc[:, 0].tolist()
    functions = functions_df.iloc[:, 0].tolist()

    if st.session_state.current_index < len(processes):
        current_process = processes[st.session_state.current_index]
        st.subheader(f"➡️ Process {st.session_state.current_index + 1}/{len(processes)}: **{current_process}**")

        selected_functions = st.multiselect("Select one or more functions for this process:", functions)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Confirm and go to next"):
                for func in selected_functions:
                    st.session_state.links.append({"Process": current_process, "Function": func})
                st.session_state.current_index += 1
                st.rerun()  # 🔧 updated: replaces st.experimental_rerun()

        with col2:
            if st.button("🔄 Reset mapping"):
                st.session_state.links = []
                st.session_state.current_index = 0
                st.rerun()

    else:
        st.success("🎉 All processes have been linked!")
        result_df = pd.DataFrame(st.session_state.links)
        st.dataframe(result_df)

        output_name = "process_function_links.xlsx"
        result_df.to_excel(output_name, index=False)
        with open(output_name, "rb") as f:
            st.download_button("⬇️ Download Output File", data=f, file_name=output_name)
else:
    st.info("Please upload both Excel files to start.")
