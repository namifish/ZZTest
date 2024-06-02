import streamlit as st
import utils
import time

def show_login():
    st.subheader("Login")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    login_columns = st.columns((0.5, 3, 3, 3, 0.5))

    with login_columns[1]:
        if st.button("Login", use_container_width=True):
            if username and password:
                if utils.verify_user(username, password):
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.session_state['results'] = utils.get_user_results(username)
                    st.rerun()
                else:
                    st.error("Ungültiger Benutzername oder Passwort.")
            else:
                st.error("Bitte gib sowohl Benutzernamen als auch Passwort ein.")

    with login_columns[2]:
        if st.button("Registrieren", use_container_width=True):
            st.session_state['register'] = True
            st.rerun()

    with login_columns[3]:
        if st.button("Weiter als Gast", use_container_width=True):
            st.session_state['guest'] = True
            if 'guest_results' not in st.session_state:
                st.session_state['guest_results'] = []
            st.rerun()

def show_register():
    st.subheader("Registrieren")
    reg_username = st.text_input("Wähle einen Benutzernamen")
    reg_password = st.text_input("Wähle ein Passwort", type="password")
    reg_confirm_password = st.text_input("Passwort bestätigen", type="password")
    register_columns = st.columns((0.5, 3, 3, 0.5))

    with register_columns[1]:
        if st.button("Registrieren", use_container_width=True):
            if reg_username and reg_password and reg_confirm_password:
                if reg_password == reg_confirm_password:
                    if utils.register_user(reg_username, reg_password):
                        utils.upload_to_github(utils.LOGIN_FILE, utils.repo, 'login_hashed_password_list.csv')
                        st.success("Registrierung erfolgreich. Du kannst dich jetzt einloggen.")
                        st.session_state['register'] = False
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Benutzername existiert bereits. Bitte wähle einen anderen Benutzernamen.")
                else:
                    st.error("Passwörter stimmen nicht überein.")
            else:
                st.error("Bitte fülle alle erforderlichen Felder aus.")

    with register_columns[2]:
        if st.button("Zurück zum Login", use_container_width=True):
            st.session_state['register'] = False
            st.rerun()