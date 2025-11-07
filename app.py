import streamlit as st
import pandas as pd

# === Caricamento file ===
st.title("Process Function Linker")

uploaded_proc = st.file_uploader("Carica file Processi (Excel)", type=["xlsx"])
uploaded_func = st.file_uploader("Carica file Funzioni (Excel)", type=["xlsx"])

if uploaded_proc and uploaded_func:
    df_proc = pd.read_excel(uploaded_proc)
    df_func = pd.read_excel(uploaded_func)

    st.success("File caricati con successo!")

    # === Selezione Dominio ===
    st.markdown("---")
    st.subheader("Seleziona Processo")

    selected_domain = st.selectbox(
        "Dominio",
        options=[""] + sorted(df_proc["Dominio"].dropna().unique().tolist()),
        index=0,
        key="selected_domain"
    )

    filtered_subdomains = (
        df_proc[df_proc["Dominio"] == selected_domain]["Sottodominio"].dropna().unique().tolist()
        if selected_domain else []
    )

    selected_subdomain = st.selectbox(
        "Sottodominio",
        options=[""] + sorted(filtered_subdomains),
        index=0,
        key="selected_subdomain"
    )

    filtered_processes = (
        df_proc[
            (df_proc["Dominio"] == selected_domain) &
            (df_proc["Sottodominio"] == selected_subdomain)
        ]["Processo"].dropna().unique().tolist()
        if selected_subdomain else []
    )

    selected_process = st.selectbox(
        "Processo",
        options=[""] + sorted(filtered_processes),
        index=0,
        key="selected_process"
    )

    # === Selezione Funzioni ===
    st.markdown("---")
    st.subheader("Seleziona Funzioni collegate")

    functions = df_func["Function_Name"].dropna().unique().tolist()

    selected_functions = st.multiselect(
        "Seleziona le funzioni da collegare",
        options=functions,
        default=st.session_state.get("selected_functions", []),
        key="selected_functions"
    )

    # === Bottone di conferma ===
    if "collegamenti" not in st.session_state:
        st.session_state.collegamenti = []

    if st.button("Confermo collegamento"):
        if selected_functions and selected_process:
            # Salvataggio del collegamento
            st.session_state.collegamenti.append({
                "Dominio": selected_domain,
                "Sottodominio": selected_subdomain,
                "Processo": selected_process,
                "Funzioni collegate": selected_functions
            })
            st.success("Collegamento confermato e salvato con successo!")

            # Reset delle selezioni
            for key in ["selected_functions", "selected_domain", "selected_subdomain", "selected_process"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        else:
            st.warning("Seleziona almeno un processo e una funzione prima di confermare.")

    # === Visualizzazione collegamenti ===
    if st.session_state.collegamenti:
        st.markdown("---")
        st.subheader("Collegamenti confermati")
        st.dataframe(pd.DataFrame(st.session_state.collegamenti))

else:
    st.info("Carica entrambi i file per iniziare.")
