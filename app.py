import streamlit as st
import pandas as pd

st.title("🔗 Process Function Mapper v3")
st.write("Mappa i processi alle funzioni usando dropdown multilivello (Dominio → Sottodominio → Processo → Sottoprocesso).")

# Caricamento file Excel
uploaded_proc = st.file_uploader("Carica file Processi (Excel)", type=["xlsx"])
uploaded_func = st.file_uploader("Carica file Funzioni (Excel)", type=["xlsx"])

if uploaded_proc and uploaded_func:
    df_proc = pd.read_excel(uploaded_proc)
    df_func = pd.read_excel(uploaded_func)

    st.markdown("### Anteprima Processi (prime righe)")
    st.dataframe(df_proc.head())

    st.markdown("### Anteprima Funzioni (prime righe)")
    st.dataframe(df_func.head())

    # Inizializzazione stato
    if "links" not in st.session_state:
        st.session_state.links = []

    # --- Dropdown multilivello ---
    st.markdown("---")
    st.subheader("Seleziona Dominio")
    domains = sorted(df_proc["Dominio"].dropna().unique().tolist())
    selected_domain = st.selectbox("Seleziona Dominio", [""] + domains, index=0, key="selected_domain")

    if selected_domain:
        subdomains = sorted(df_proc[df_proc["Dominio"] == selected_domain]["Sottodominio"].dropna().unique().tolist())
    else:
        subdomains = []

    st.subheader("Seleziona Sottodominio")
    selected_subdomain = st.selectbox("Seleziona Sottodominio", [""] + subdomains, index=0, key="selected_subdomain")

    if selected_subdomain:
        processes = sorted(df_proc[
            (df_proc["Dominio"] == selected_domain) &
            (df_proc["Sottodominio"] == selected_subdomain)
        ]["Processo"].dropna().unique().tolist())
    else:
        processes = []

    st.subheader("Seleziona Processo")
    selected_process = st.selectbox("Seleziona Processo", [""] + processes, index=0, key="selected_process")

    if selected_process:
        subprocesses = sorted(df_proc[
            (df_proc["Dominio"] == selected_domain) &
            (df_proc["Sottodominio"] == selected_subdomain) &
            (df_proc["Processo"] == selected_process)
        ]["Sottoprocesso"].dropna().unique().tolist())
    else:
        subprocesses = []

    st.subheader("Seleziona Sottoprocesso (opzionale)")
    selected_subprocess = st.selectbox("Seleziona Sottoprocesso", [""] + subprocesses, index=0, key="selected_subprocess")

    # --- Selezione Funzioni ---
    st.markdown("---")
    st.subheader("Seleziona Funzioni collegate")
    available_functions = sorted(df_func["Function_Name"].dropna().unique().tolist())
    selected_functions = st.multiselect(
        "Seleziona le funzioni da collegare",
        options=available_functions,
        default=st.session_state.get("selected_functions", []),
        key="selected_functions"
    )

    # --- Bottone conferma ---
    if st.button("Confermo collegamento"):
        if selected_process and selected_functions:
            new_link = {
                "Dominio": selected_domain,
                "Sottodominio": selected_subdomain,
                "Processo": selected_process,
                "Sottoprocesso": selected_subprocess,
                "Funzioni collegate": ", ".join(selected_functions)
            }
            st.session_state.links.append(new_link)
            st.success("✅ Collegamento salvato con successo!")

            # 🔁 Reset completo: 4 livelli + funzioni
            for key in ["selected_domain", "selected_subdomain", "selected_process", "selected_subprocess", "selected_functions"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        else:
            st.warning("⚠️ Seleziona almeno un processo e una funzione prima di confermare.")

    # --- Tabella riepilogativa ---
    if st.session_state.links:
        st.markdown("### Collegamenti salvati")
        st.dataframe(pd.DataFrame(st.session_state.links))

else:
    st.info("⬆️ Carica entrambi i file per iniziare.")
