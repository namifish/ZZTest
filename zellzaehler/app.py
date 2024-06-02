import streamlit as st
import zellzaehler.login as login
import zellzaehler.main_page as main_page
import zellzaehler.archive as archive
import zellzaehler.account as account
import zellzaehler.utils as utils

st.set_page_config(page_title="ZellZähler", page_icon="🔬")

# Initialisiere Datenbank und Benutzerdaten
utils.init_db()
utils.init_user_data()

st.title("ZellZähler")
utils.set_background('images/hintergrundtransparent.png')

# Initialisiere Session-States, falls sie nicht existieren
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'register' not in st.session_state:
    st.session_state['register'] = False

if 'guest' not in st.session_state:
    st.session_state['guest'] = False

# Benutzer-Authentifizierung
if not st.session_state['authenticated'] and not st.session_state['guest']:
    if st.session_state['register']:
        login.show_register()
    else:
        login.show_login()
else:
    # Hauptnavigation
    view = st.sidebar.radio("Ansicht wählen", ["Einführung", "Zählen", "Archiv", "Account"])
    # Seiteninhalt je nach Auswahl anzeigen
    if view == "Einführung":
        main_page.introduction()
    elif view == "Zählen":
        main_page.counting()
    elif view == "Archiv":
        archive.show_archive()
    elif view == "Account":
        account.manage_account()
