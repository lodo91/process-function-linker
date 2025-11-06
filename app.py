import streamlit as st
import pandas as pd

st.set_page_config(page_title="Process Function Mapper v2", layout="centered")
st.title("🔗 Process Function Mapper v2")
st.write("Mappa i processi alle funzioni — analizza un processo alla volta e salva le relazioni.")

# Upload
st.sidebar.header("Carica file di input")
proc_file = st.sidebar.file_uploader("File Processi (.csv o .xlsx)", type=["csv","xlsx"])
func_file = st.sidebar.file_uploader("File Funzioni (.csv o .xlsx)", type=["csv","xlsx"])

def read_file(f):
    if f is None:
        return None
    name = f.name.lower()
    if name.endswith(".xlsx"):
        return pd.read_excel(f)
    else:
        return pd.read_csv(f)

if proc_file and func_file:
    df_proc = read_file(proc_file)
    df_func = read_file(func_file)

    if "Process_Name" not in df_proc.columns:
        st.error("Il file processi deve avere la colonna 'Process_Name' (es. nome del processo).")
    elif "Function_Name" not in df_func.columns:
        st.error("Il file funzioni deve avere la colonna 'Function_Name'.")
    else:
        # Session state
        if "idx" not in st.session_state:
            st.session_state.idx = 0
        if "links" not in st.session_state:
            st.session_state.links = []
        if "selected_funcs" not in st.session_state:
            st.session_state.selected_funcs = []

        total = len(df_proc)
        idx = st.session_state.idx

        st.sidebar.markdown(f"Processo corrente: **{idx+1} / {total}**")
        # Show current process
        processo = df_proc.iloc[idx]["Process_Name"]
        st.subheader(f"Processo {idx+1} / {total}")
        st.markdown(f"**{processo}**")

        # Function selection
        selected_funcs = st.multiselect(
            "Seleziona una o più funzioni collegate",
            df_func["Function_Name"].tolist()
        )
)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Indietro") and idx>0:
                st.session_state.idx = max(0, idx-1)
                st.rerun()
        with col2:
            if st.button("💾 Conferma e passa al prossimo"):
                # 💾 salva i link scelti
                for f in selected_funcs:
                    st.session_state.links.append({"Process": processo, "Function": f})

        # 🧹 reset della selezione (pulisce il multiselect)
        st.session_state.selected_funcs = []

        # ⏭️ passa al prossimo processo
        if st.session_state.idx < total - 1:
            st.session_state.idx += 1
            st.rerun()
        else:
            st.success("Hai completato l'analisi di tutti i processi.")
        with col3:
            if st.button("Salta e passa al prossimo"):
                if st.session_state.idx < total-1:
                    st.session_state.idx += 1
                    st.rerun()
                else:
                    st.success("Hai completato l'analisi di tutti i processi.")

        st.markdown("---")
        st.subheader("Collegamenti salvati (in tempo reale)")
        if st.session_state.links:
            df_links = pd.DataFrame(st.session_state.links)
            st.dataframe(df_links)
            # possibilità di rimuovere l'ultima riga
            if st.button("🗑️ Rimuovi ultima associazione"):
                st.session_state.links.pop()
                st.rerun()
            # export
            st.download_button(
                "⬇️ Esporta in Excel (una riga per Process-Funzione)",
                df_links.to_csv(index=False).encode("utf-8"),
                "mappatura_process_function.csv",
                "text/csv"
            )
        else:
            st.info("Non ci sono ancora collegamenti salvati. Usa 'Conferma e passa al prossimo' per salvare.")
else:
    st.info("Carica i file di Processi e Funzioni (colonne richieste: 'Process_Name' e 'Function_Name').")
    st.markdown("""
    ### Esempio file CSV
    - processi: colonne -> Process_Name
    - funzioni: colonne -> Function_Name
    """)
