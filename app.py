import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Process Function Mapper v3", layout="wide")
st.title("🔗 Process Function Mapper v3")
st.markdown("Mappa i processi alle funzioni usando dropdown multilivello (Dominio → Sottodominio → Processo → Sottoprocesso).")

# Sidebar per caricamento file
st.sidebar.header("Carica i file di input")
proc_file = st.sidebar.file_uploader("File Processi (.xlsx)", type=["xlsx"])
func_file = st.sidebar.file_uploader("File Funzioni (.xlsx)", type=["xlsx"])

# --- Funzioni di lettura file ---

def read_proc_file(f):
    df = pd.read_excel(f)
    expected = ['Dominio', 'Sottodominio', 'Processo', 'Sottoprocesso']
    # Mappa colonne simili
    if list(df.columns[:4]) != expected:
        cols = list(df.columns)
        mapping = {}
        for i, name in enumerate(expected):
            if i < len(cols):
                mapping[cols[i]] = name
        df = df.rename(columns=mapping)
    for c in expected:
        if c not in df.columns:
            df[c] = ""
    df = df.fillna("")
    return df[expected]

def read_func_file(f):
    df = pd.read_excel(f)
    if 'Function_Name' in df.columns:
        return df[['Function_Name']].rename(columns={'Function_Name':'Function_Name'})
    elif 'Funzione' in df.columns:
        return df[['Funzione']].rename(columns={'Funzione':'Function_Name'})
    else:
        return df[[df.columns[0]]].rename(columns={df.columns[0]:'Function_Name'})

# --- Main logic ---
if proc_file and func_file:
    df_proc = read_proc_file(proc_file)
    df_func = read_func_file(func_file)

    # Mostra anteprime
    st.sidebar.success("File caricati correttamente")
    st.subheader("Anteprima Processi (prime righe)")
    st.dataframe(df_proc.head())

    st.subheader("Anteprima Funzioni (prime righe)")
    st.dataframe(df_func.head())

    # Inizializza session_state
    if "links" not in st.session_state:
        st.session_state.links = []
    if "selected_functions" not in st.session_state:
        st.session_state.selected_functions = []
    if "dominio_sel" not in st.session_state:
        st.session_state.dominio_sel = ""
    if "sottodominio_sel" not in st.session_state:
        st.session_state.sottodominio_sel = ""
    if "processo_sel" not in st.session_state:
        st.session_state.processo_sel = ""
    if "sottoprocesso_sel" not in st.session_state:
        st.session_state.sottoprocesso_sel = ""

    # Dropdown multilivello
    domini = sorted(df_proc["Dominio"].dropna().unique().tolist())
    dominio_sel = st.selectbox(
        "Seleziona Dominio",
        options=[""] + domini,
        key="dominio_sel"
    )

    if dominio_sel:
        sottodomini = sorted(df_proc[df_proc["Dominio"] == dominio_sel]["Sottodominio"].dropna().unique().tolist())
    else:
        sottodomini = []
    sottodominio_sel = st.selectbox(
        "Seleziona Sottodominio",
        options=[""] + sottodomini,
        key="sottodominio_sel"
    )

    if sottodominio_sel:
        processi = sorted(df_proc[
            (df_proc["Dominio"] == dominio_sel) &
            (df_proc["Sottodominio"] == sottodominio_sel)
        ]["Processo"].dropna().unique().tolist())
    elif dominio_sel:
        processi = sorted(df_proc[df_proc["Dominio"] == dominio_sel]["Processo"].dropna().unique().tolist())
    else:
        processi = []
    processo_sel = st.selectbox(
        "Seleziona Processo",
        options=[""] + processi,
        key="processo_sel"
    )

    if processo_sel:
        sottoprocessi = sorted(df_proc[
            (df_proc["Dominio"] == dominio_sel) &
            (df_proc["Processo"] == processo_sel)
        ]["Sottoprocesso"].dropna().unique().tolist())
    else:
        sottoprocessi = []
    sottoprocesso_sel = st.selectbox(
        "Seleziona Sottoprocesso (opzionale)",
        options=[""] + sottoprocessi,
        key="sottoprocesso_sel"
    )

    st.markdown("---")
    st.subheader("Seleziona Funzioni collegate")
    functions = df_func['Function_Name'].tolist()
    selected = st.multiselect(
        "Seleziona le funzioni da collegare",
        options=functions,
        default=st.session_state.get("selected_functions", []),
        key="selected_functions"
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    # --- Bottone "Conferma collegamento"
    with col1:
        if st.button("💾 Conferma collegamento"):
            dominio_val = dominio_sel or ""
            sottodominio_val = sottodominio_sel or ""
            processo_val = processo_sel or ""
            sottoprocesso_val = sottoprocesso_sel or ""

            for fn in selected:
                st.session_state.links.append({
                    "Dominio": dominio_val,
                    "Sottodominio": sottodominio_val,
                    "Processo": processo_val,
                    "Sottoprocesso": sottoprocesso_val,
                    "Function": fn
                })

            st.session_state.selected_functions = []
            st.success("Collegamento salvato.")
            st.rerun()

    # --- Bottone "Rimuovi ultima"
    with col2:
        if st.button("🗑️ Rimuovi ultima associazione"):
            if st.session_state.links:
                st.session_state.links.pop()
                st.success("Ultima associazione rimossa.")
                st.rerun()
            else:
                st.info("Non ci sono associazioni da rimuovere.")

    # --- Bottone "Reset tutto"
    with col3:
        if st.button("🔄 Reset tutto"):
            st.session_state.links = []
            st.session_state.selected_functions = []
            st.session_state.dominio_sel = ""
            st.session_state.sottodominio_sel = ""
            st.session_state.processo_sel = ""
            st.session_state.sottoprocesso_sel = ""
            st.success("Tutto resettato.")
            st.rerun()

    st.markdown("---")
    st.subheader("Collegamenti salvati")
    if st.session_state.links:
        df_links = pd.DataFrame(st.session_state.links)
        st.dataframe(df_links)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_links.to_excel(writer, index=False, sheet_name="Links")
        data = output.getvalue()
        st.download_button(
            "⬇️ Esporta in Excel",
            data=data,
            file_name="mappatura_v3.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Ancora nessun collegamento salvato. Usa 'Conferma collegamento' per iniziare.")

else:
    st.info("Carica i file 'processi.xlsx' e 'funzioni.xlsx' nella sidebar per iniziare.")
