import streamlit as st
import utils

def show_archive():
    st.header("Archivierte Ergebnisse")
    if st.session_state['guest']:
        st.warning("Archivierte Daten im Gästelogin können verlorengehen.")
        utils.display_results(st.session_state.get('guest_results', []))
    else:
        utils.display_results(st.session_state.get('results', []))