import streamlit as st 
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Process Function Mapper v3", layout="wide")
st.title("🔗 Process Function Mapper v3")
st.markdown("Mappa i processi alle funzioni usando dropdown multilivello (Dominio → Sottodominio → Processo → Sottoprocesso).")

st.sidebar.header("Carica i file di input")
proc_file = st.sidebar.file_uploader("File Processi (.xlsx)", type=["xlsx"])
func_file = st.sidebar.file_uploader("File Funzioni (.xlsx)", type=["xlsx"])


# ----------------------------- LETTURA FILE ------------------------------

def read_proc_file(f):
    df = pd.read_excel(f)
    expected = ['Dominio','Sottodominio','Processo','Sottoprocesso']
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
        return df[['Function_Name']]
    elif 'Funzione' in df.columns:
        return df[['Funzione']].rename(columns={'Funzione':'Function_Name'})
    else:
        return df[[df.columns[0]]].rename(columns={df.columns[0]:'Function_Name'})


# ----------------------------- LOGICA APP ------------------------------

if proc_file and func_file:
    df_proc = read_proc_file(proc_file)
    df_func = read_func_file(func_file)

    st.sidebar.success("File caricati correttamente ✅")

    st.subheader("Anteprima Processi")
    st.dataframe(df_proc.head())

    st.subheader("Anteprima Funzioni")
    st.dataframe(df_func.head())

    # Init session storage
    if "links" not in st.session_state:
        st.session_state.links = []
    if "func_selector" not in st.session_state:
        st.session_state.func_selector = []
    if "_reset_flag" not in st.session_state:
        st.session_state._reset_flag = False

    # ----------------------------- DROPDOWN ------------------------------

    domini = sorted([d for d in df_proc["Dominio"].unique() if d])
    dominio_sel = st.selectbox("Seleziona Dominio", ["-- scegli --"] + domini)

    if dominio_sel != "-- scegli --":
        df1 = df_proc[df_proc["Dominio"] == dominio_sel]
        sottodomini = sorted([s for s in df1["Sottodominio"].unique() if s])
        sottodominio_sel = st.selectbox("Seleziona Sottodominio", ["-- scegli --"] + sottodomini)
    else:
        sottodominio_sel = None

    if sottodominio_sel and sottodominio_sel != "-- scegli --":
        df2 = df1[df1["Sottodominio"] == sottodominio_sel]
        processi = sorted([p for p in df2["Processo"].unique() if p])
        processo_sel = st.selectbox("Seleziona Processo", ["-- scegli --"] + processi)
    else:
        processo_sel = None

    if processo_sel and processo_sel != "-- scegli --":
        df3 = df2[df2["Processo"] == processo_sel]
        sottoprocessi = sorted([sp for sp in df3["Sottoprocesso"].unique() if sp])
        if sottoprocessi:
            sottoprocesso_sel = st.selectbox("Seleziona Sottoprocesso", ["-- nessuno --"] + sottoprocessi)
        else:
            sottoprocesso_sel = "-- nessuno --"
    else:
        sottoprocesso_sel = None

    # ----------------------------- MULTISELECT FUNZIONI ------------------------------

    st.markdown("---")
    st.subheader("Seleziona Funzioni collegate")

    functions = df_func["Function_Name"].tolist()

    selected = st.multiselect(
        "Seleziona le funzioni da collegare",
        options=functions,
        key="func_selector"   # ✅ usa chiave nuova, NON in conflitto
    )

    # Reset applicato dopo il rerun
    if st.session_state._reset_flag:
        st.session_state.func_selector = []
        st.session_state._reset_flag = False


    # ----------------------------- CONFERMA COLLEGAMENTO ------------------------------

    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        if st.button("💾 Conferma collegamento"):

            dominio_val = dominio_sel if dominio_sel not in ["-- scegli --"] else ""
            sottodominio_val = sottodominio_sel if sottodominio_sel not in ["-- scegli --"] else ""
            processo_val = processo_sel if processo_sel not in ["-- scegli --"] else ""
            sottoprocesso_val = sottoprocesso_sel if sottoprocesso_sel not in ["-- nessuno --"] else ""

            for fn in selected:
                st.session_state.links.append({
                    "Dominio": dominio_val,
                    "Sottodominio": sottodominio_val,
                    "Processo": processo_val,
                    "Sottoprocesso": sottoprocesso_val,
                    "Function": fn
                })

            st.success("Collegamento salvato ✅")

            # ✅ reset sicuro (rinviato al prossimo ciclo)
            st.session_state._reset_flag = True
            st.rerun()


    # ----------------------------- RIMOZIONE / RESET ------------------------------

    with col2:
        if st.button("🗑️ Rimuovi ultima associazione"):
            if st.session_state.links:
                st.session_state.links.pop()
                st.rerun()
            else:
                st.info("Non ci sono associazioni da rimuovere.")

    with col3:
        if st.button("🔄 Reset tutto"):
            st.session_state.links = []
            st.session_state.func_selector = []
            st.rerun()


    # ----------------------------- ESPORTAZIONE ------------------------------

    st.markdown("---")
    st.subheader("Collegamenti salvati")

    if st.session_state.links:
        df_links = pd.DataFrame(st.session_state.links)
        st.dataframe(df_links)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_links.to_excel(writer, index=False, sheet_name="Links")

        st.download_button(
            "⬇️ Esporta in Excel",
            data=output.getvalue(),
            file_name="mappatura_v3.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Carica i file 'processi.xlsx' e 'funzioni.xlsx' nella sidebar per iniziare.")

