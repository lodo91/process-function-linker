import streamlit as st
import pandas as pd

# =======================
# CONFIGURAZIONE APP
# =======================
st.set_page_config(page_title="Process Function Linker", layout="wide")

# =======================
# CARICAMENTO FILES
# =======================
st.title("🔗 Process Function Linker")

uploaded_file_func = st.file_uploader("Carica il file delle Funzioni", type=["xlsx"])
uploaded_file_proc = st.file_uploader("Carica il file dei Processi", type=["xlsx"])

if uploaded_file_func and uploaded_file_proc:
    df_func = pd.read_excel(uploaded_file_func)
    df_proc = pd.read_excel(uploaded_file_proc)

    st.success("File caricati correttamente ✅")

    # =======================
    # INIZIALIZZAZIONE SESSION STATE
    # =======================
    if "selected_domain" not in st.session_state:
        st.session_state.selected_domain = None
    if "selected_subdomain" not in st.session_state:
        st.session_state.selected_subdomain = None
    if "selected_process" not in st.session_state:
        st.session_state.selected_process = None
    if "selected_functions" not in st.session_state:
        st.session_state.selected_functions = []

    # =======================
    # FILTRI A DISCESA
    # =======================
    st.markdown("---")
    st.subheader("📂 Selezione Dominio, Sottodominio e Processo")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.session_state.selected_domain = st.selectbox(
            "Dominio",
            options=[""] + sorted(df_proc["Domain"].dropna().unique().tolist()),
            index=0 if st.session_state.selected_domain is None else
            ([""] + sorted(df_proc["Domain"].dropna().unique().tolist())).index(st.session_state.selected_domain)
            if st.session_state.selected_domain in df_proc["Domain"].values else 0,
            key="domain_selector"
        )

    with col2:
        filtered_subdomains = df_proc[df_proc["Domain"] == st.session_state.selected_domain]["Subdomain"].dropna().unique() \
            if st.session_state.selected_domain else []
        st.session_state.selected_subdomain = st.selectbox(
            "Sottodominio",
            options=[""] + sorted(filtered_subdomains),
            index=0 if st.session_state.selected_subdomain is None else
            ([""] + sorted(filtered_subdomains)).index(st.session_state.selected_subdomain)
            if st.session_state.selected_subdomain in filtered_subdomains else 0,
            key="subdomain_selector"
        )

    with col3:
        filtered_processes = df_proc[
            (df_proc["Domain"] == st.session_state.selected_domain) &
            (df_proc["Subdomain"] == st.session_state.selected_subdomain)
        ]["Process"].dropna().unique() if st.session_state.selected_subdomain else []
        st.session_state.selected_process = st.selectbox(
            "Processo",
            options=[""] + sorted(filtered_processes),
            index=0 if st.session_state.selected_process is None else
            ([""] + sorted(filtered_processes)).index(st.session_state.selected_process)
            if st.session_state.selected_process in filtered_processes else 0,
            key="process_selector"
        )

    # =======================
    # SELEZIONE FUNZIONI
    # =======================
    st.markdown("---")
    st.subheader("🏷️ Seleziona Funzioni collegate")

    all_functions = sorted(df_func["Function_Name"].dropna().unique().tolist())

    st.session_state.selected_functions = st.multiselect(
        "Funzioni da collegare al processo selezionato:",
        options=all_functions,
        default=st.session_state.selected_functions,
        key="func_selector"
    )

    # =======================
    # PULSANTI
    # =======================
    st.markdown("---")
    colA, colB = st.columns(2)

    with colA:
        if st.button("💾 Salva collegamento"):
            if st.session_state.selected_process and st.session_state.selected_functions:
                st.success(f"Collegamento salvato per il processo: **{st.session_state.selected_process}**")
            else:
                st.warning("⚠️ Seleziona un processo e almeno una funzione prima di salvare.")

    with colB:
        if st.button("🔄 Reset selezioni"):
            for key in [
                "selected_domain", "selected_subdomain", "selected_process", "selected_functions",
                "domain_selector", "subdomain_selector", "process_selector", "func_selector"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()

else:
    st.info("⬆️ Carica entrambi i file per iniziare.")
