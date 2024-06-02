import streamlit as st
import utils
import sqlite3
import time

def manage_account():
    st.header("Account-Verwaltung")
    if st.session_state['guest']:
        st.warning("Nicht angemeldet. Achtung: Archivierte Daten im Gästelogin können verlorengehen.")
        if st.button("Zurück zum Login", key="guest_back_to_login"):
            st.session_state['authenticated'] = False
            st.session_state['guest'] = False
            st.session_state['register'] = False
            st.rerun()
    else:
        st.write(f"**Eingeloggter User:** {st.session_state['username']}")
        grid_columns = st.columns((2, 2, 1))

        with grid_columns[0]:
            if st.button("Passwort ändern", key="change_password_button", use_container_width=True):
                st.session_state['change_password'] = True
            if st.button("Benutzernamen ändern", key="change_username_button", use_container_width=True):
                st.session_state['change_username'] = True

        with grid_columns[1]:
            if st.button("Account löschen", key="delete_account_button", use_container_width=True):
                st.session_state['delete_account'] = True
            if st.button("Abmelden", key="logout_button", use_container_width=True):
                st.success(f"Auf Wiedersehen, {st.session_state['username']}!")
                st.session_state['authenticated'] = False
                st.session_state['guest'] = False
                st.session_state['register'] = False
                time.sleep(2)
                st.rerun()

        # Passwort ändern
        if 'change_password' in st.session_state and st.session_state['change_password']:
            new_password = st.text_input("Neues Passwort", type="password", key="new_password")
            confirm_password = st.text_input("Passwort bestätigen", type="password", key="confirm_password")
            if st.button("Passwort ändern", key="confirm_change_password"):
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        users = utils.load_user_data()
                        users.loc[users['username'] == st.session_state['username'], 'password'] = utils.encrypt_password(new_password)
                        utils.save_user_data(users)
                        st.success("Passwort erfolgreich geändert.")
                        st.session_state['change_password'] = False
                        time.sleep(4)
                        st.rerun()
                    else:
                        st.error("Passwörter stimmen nicht überein.")
                else:
                    st.error("Bitte fülle alle Felder aus.")
            if st.button("Abbrechen", key="cancel_change_password"):
                st.session_state['change_password'] = False
                st.rerun()

        # Benutzername ändern
        if 'change_username' in st.session_state and st.session_state['change_username']:
            new_username = st.text_input("Neuer Benutzername", key="new_username")
            if st.button("Benutzernamen ändern", key="confirm_change_username"):
                if new_username:
                    users = utils.load_user_data()
                    if new_username not in users['username'].values:
                        # Username aktualisieren
                        users.loc[users['username'] == st.session_state['username'], 'username'] = new_username
                        utils.save_user_data(users)

                        conn = sqlite3.connect(utils.DB_FILE)
                        c = conn.cursor()
                        c.execute('UPDATE results SET username=? WHERE username=?', (new_username, st.session_state['username']))
                        conn.commit()
                        conn.close()

                        st.session_state['username'] = new_username
                        st.success("Benutzername erfolgreich geändert.")
                        st.session_state['change_username'] = False
                        time.sleep(4)
                        st.rerun()
                    else:
                        st.error("Benutzername existiert bereits.")
                else:
                    st.error("Bitte gib einen neuen Benutzernamen ein.")
            if st.button("Abbrechen", key="cancel_change_username"):
                st.session_state['change_username'] = False
                st.rerun()

        # Account löschen
        if 'delete_account' in st.session_state and st.session_state['delete_account']:
            st.warning("Achtung: Alle archivierten Daten gehen verloren.")
            if st.button("Account löschen: bestätigen", key="confirm_delete_account"):
                utils.delete_user(st.session_state['username'])
                st.success("Account erfolgreich gelöscht. Du wirst automatisch zum Login weitergeleitet.")
                st.session_state['authenticated'] = False
                st.session_state['delete_account'] = False
                time.sleep(4)
                st.rerun()
            if st.button("Abbrechen", key="cancel_delete_account"):
                st.session_state['delete_account'] = False

if st.button("Daten auf Datenbank absichern", key="upload_to_github_button"):
    utils.upload_to_github(utils.DB_FILE, utils.repo, 'zellzaehler/data/zellzaehler.db')
    utils.upload_to_github(utils.LOGIN_FILE, utils.repo, 'zellzaehler/data/login_hashed_password_list.csv')
    st.success("Daten erfolgreich auf GitHub abgesichert.")
