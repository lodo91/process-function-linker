import streamlit as st 
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Process Function Mapper v3", layout="wide")
st.title("🔗 Process Function Mapper v3")
st.markdown("Mappa i processi alle funzioni usando dropdown multilivello (Dominio → Sottodominio → Processo → Sottoprocesso).")

st.sidebar.header("Carica i file di input")
proc_file = st.sidebar.file_uploader("File Processi (.xlsx)", type=["xlsx"])
func_file = st.sidebar.file_uploader("File Funzioni (.xlsx)", type=["xlsx"])


# -------------------- LETTURA FILE PROCESSI --------------------
def read_proc_file(f):
    df = pd.read_excel(f)
    expected = ['Dominio','Sottodominio','Processo','Sottoprocesso']
    if list(df.columns[:4]) != expected:
        mapping = {}
        for i, name in enumerate(expected):
            if i < len(df.columns):
                mapping[df.columns[i]] = name
        df = df.rename(columns=mapping)
    for col in expected:
        if col not in df.columns:
            df[col] = ""
    return df[expected].fillna("")


# -------------------- LETTURA FILE FUNZIONI --------------------
def read_func_file(f):
    df = pd.read_excel(f)
    if "Function_Name" in df.columns:
        col = "Function_Name"
    elif "Funzione" in df.columns:
        col = "Funzione"
    else:
        col = df.columns[0]
    df = df.rename(columns={col: "Function_Name"})
    return df[["Function_Name"]]


# -------------------- SE CARICATI I FILE --------------------
if proc_file and func_file:
    df_proc = read_proc_file(proc_file)
    df_func = read_func_file(func_file)

    st.sidebar.success("File caricati correttamente ✅")

    # Inizializzazione session state
    if "links" not in st.session_state:
        st.session_state.links = []

    if "reset_flag" not in st.session_state:
        st.session_state.reset_flag = False

    if "func_selector" not in st.session_state:
        st.session_state.func_selector = []


    # -------------------- RESET SICURO --------------------
    if st.session_state.reset_flag:
        # Reset solo al primo ciclo utile, prima che venga creato il widget
        st.session_state.func_selector = []
        st.session_state.reset_flag = False


    # -------------------- SELEZIONE PROCESSI --------------------
    st.subheader("Anteprima Processi (prime righe)")
    st.dataframe(df_proc.head())

    st.subheader("Anteprima Funzioni (prime righe)")
    st.dataframe(df_func.head())

    st.markdown("---")
    st.subheader("Seleziona Processo")

    domini = sorted([d for d in df_proc["Dominio"].unique() if d])
    dominio_sel = st.selectbox("Seleziona Dominio", ["-- scegli --"] + domini)

    sottodominio_sel = processo_sel = sottoprocesso_sel = None

    if dominio_sel != "-- scegli --":
        sottodomini = sorted(df_proc[df_proc["Dominio"] == dominio_sel]["Sottodominio"].unique())
        sottodomini = [s for s in sottodomini if s]
        sottodominio_sel = st.selectbox("Seleziona Sottodominio", ["-- scegli --"] + sottodomini)

    if sottodominio_sel and sottodominio_sel != "-- scegli --":
        processi = sorted(df_proc[(df_proc["Dominio"] == dominio_sel) &
                                  (df_proc["Sottodominio"] == sottodominio_sel)]["Processo"].unique())
        processi = [p for p in processi if p]
        processo_sel = st.selectbox("Seleziona Processo", ["-- scegli --"] + processi)
    else:
        processo_sel = st.selectbox("Seleziona Processo", ["-- scegli --"] + sorted(df_proc[df_proc["Dominio"] == dominio_sel]["Processo"].unique()))

    if processo_sel and processo_sel != "-- scegli --":
        sottoprocessi = sorted(df_proc[(df_proc["Dominio"] == dominio_sel) &
                                       (df_proc["Processo"] == processo_sel)]["Sottoprocesso"].unique())
        sottoprocessi = [sp for sp in sottoprocessi if sp]
        if sottoprocessi:
            sottoprocesso_sel = st.selectbox("Seleziona Sottoprocesso (opzionale)", ["-- nessuno --"] + sottoprocessi)
        else:
            sottoprocesso_sel = "-- nessuno --"


    # -------------------- SELEZIONE FUNZIONI --------------------
    st.markdown("---")
    st.subheader("Seleziona Funzioni collegate")

    available_functions = df_func["Function_Name"].tolist()

    selected = st.multiselect(
        "Seleziona le funzioni da collegare",
        options=available_functions,
        default=st.session_state.func_selector,
        key="func_selector"
    )


    # -------------------- BOTTONI --------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Conferma collegamento"):
            dominio_val = dominio_sel if dominio_sel != "-- scegli --" else ""
            sottodominio_val = sottodominio_sel if sottodominio_sel not in ["-- scegli --", None] else ""
            processo_val = processo_sel if processo_sel != "-- scegli --" else ""
            sottoprocesso_val = sottoprocesso_sel if sottoprocesso_sel not in ["-- nessuno --", None] else ""

            for fn in selected:
                st.session_state.links.append({
                    "Dominio": dominio_val,
                    "Sottodominio": sottodominio_val,
                    "Processo": processo_val,
                    "Sottoprocesso": sottoprocesso_val,
                    "Function": fn
                })

            st.success("✅ Collegamento salvato")

            # Attiva il reset nel ciclo successivo
            st.session_state.reset_flag = True
            st.rerun()


    with col2:
        if st.button("🗑️ Rimuovi ultima associazione"):
            if st.session_state.links:
                st.session_state.links.pop()
                st.rerun()
            else:
                st.info("Nessuna associazione da rimuovere.")

    with col3:
        if st.button("🔄 Reset tutto"):
            st.session_state.links = []
            st.session_state.func_selector = []
            st.session_state.reset_flag = False
            st.rerun()


    # -------------------- TABELLA RISULTATI --------------------
    st.markdown("---")
    st.subheader("Collegamenti salvati")

    if st.session_state.links:
        df_links = pd.DataFrame(st.session_state.links)
        st.dataframe(df_links)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_links.to_excel(writer, index=False, sheet_name="Links")

        st.download_button(
            "⬇️ Esporta Excel",
            data=output.getvalue(),
            file_name="mappatura_funzioni.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Nessun collegamento salvato finora.")

else:
    st.info("Carica entrambi i file Excel per iniziare.")
