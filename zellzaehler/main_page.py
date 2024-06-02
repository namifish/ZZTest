import streamlit as st
import pandas as pd
import utils
from datetime import datetime

def introduction():
    if st.session_state['guest']:
        st.header("Einführung")
        st.write("""
        Willkommen bei der ZellZähler-App!

        **Funktionen:**
        - **Probenummer eingeben**: Gib eine eindeutige Probenummer ein, um eine neue Zählung zu starten.
        - **Zählen**: Führe die Zählungen durch, indem du die entsprechenden Knöpfe drückst.
        - **Neuen Zellentyp definieren**: Klicke auf diesen Knopf, um die unteren drei Knöpfe umzubenennen.
        - **Korrigieren**: Ermöglicht das manuelle Korrigieren der Zählerstände.
        - **Rückgängig**: Macht den letzten Schritt rückgängig.
        - **Zählung zurücksetzen**: Setzt alle Zählerstände auf Null zurück.
        - **Ergebnisse speichern**: Nach jeder Session die aktuellen Zählungsergebnisse speichern und archivieren.
        - **Archiv**: Zeigt alle gespeicherten Zählungsergebnisse an, die nach Probenummern durchsucht werden können.

        Diese App wurde für das Hämatologie Praktikum an der ZHAW erschaffen. Sie hilft beim Differenzieren des weissen Blutbildes. Entwickelt von Sarah 'Viki' Ramos Zähnler und Lucia Schweizer. Die Illustration ist von Sarah 'Viki' Ramos Zähnler.
        """)
    else:
        st.header("Einführung")
        st.write(f"""
        Willkommen bei der ZellZähler-App, {st.session_state['username']}!

        **Funktionen:**
        - **Probenummer eingeben**: Gib eine eindeutige Probenummer ein, um eine neue Zählung zu starten.
        - **Zählen**: Führe die Zählungen durch, indem du die entsprechenden Knöpfe drückst.
        - **Neuen Zellentyp definieren**: Klicke auf diesen Knopf, um die unteren drei Knöpfe umzubenennen.
        - **Korrigieren**: Ermöglicht das manuelle Korrigieren der Zählerstände.
        - **Rückgängig**: Macht den letzten Schritt rückgängig.
        - **Zählung zurücksetzen**: Setzt alle Zählerstände auf Null zurück.
        - **Ergebnisse speichern**: Nach jeder Session die aktuellen Zählungsergebnisse speichern und archivieren.
        - **Archiv**: Zeigt alle gespeicherten Zählungsergebnisse an, die nach Probenummern durchsucht werden können.

        Diese App wurde für das Hämatologie Praktikum an der ZHAW erschaffen. Sie hilft beim Differenzieren des weissen Blutbildes. Entwickelt von Sarah 'Viki' Ramos Zähnler und Lucia Schweizer. Die Illustration ist von Sarah 'Viki' Ramos Zähnler.
        """)

button_names = [
    "Pro   ", "Mye   ", "Meta   ", "Stab   ", "Seg   ", "Eos   ",
    "Baso   ", "Mono   ", "Ly   ", "Div1   ", "Div2   ", "Div3   "
]

def counting():

    # Initialisieren der Session-States
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'sample_number' not in st.session_state:
        st.session_state['sample_number'] = ""

    if 'count_session' not in st.session_state:
        st.session_state['count_session'] = 1

    if 'custom_names' not in st.session_state:
        st.session_state['custom_names'] = ["Div1   ", "Div2   ", "Div3   "]

    for name in button_names:
        if f'count_{name}' not in st.session_state:
            st.session_state[f'count_{name}'] = 0

    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = False

    if 'name_edit_mode' not in st.session_state:
        st.session_state['name_edit_mode'] = False

    st.session_state['sample_number'] = st.text_input("Probenummer eingeben", value=st.session_state['sample_number'])

    if not st.session_state['sample_number']:
        st.warning("Bitte gib eine Probenummer ein, um zu beginnen.")
        if st.session_state['guest']:
            st.warning("Archivierte Daten im Gästelogin können verlorengehen.")
            
    else:
        st.subheader(f"Aktuelle Zählungssession: {st.session_state['count_session']}")

        top_columns = st.columns((2, 2, 3))

        with top_columns[0]:
            if st.button('Rückgängig', key='undo_button', help="Macht den letzen Schritt rückgängig.", use_container_width=True):
                utils.undo_last_step(button_names)
                st.rerun()

        with top_columns[1]:
            if st.button('Korrigieren', help="Manuelle Korrektur der Zählerstände. Mit zweitem Klick den Korrekturmodus beenden.", use_container_width=True):
                st.session_state['edit_mode'] = not st.session_state['edit_mode']
                st.rerun()

        with top_columns[2]:
            if st.button('Neuen Zellentyp definieren', help="Individuelle Umbenennung der unteren drei Zählerknöpfe. Die neue Benennung erscheint nicht auf der Tabelle.", use_container_width=True):
                st.session_state['name_edit_mode'] = not st.session_state['name_edit_mode']
                st.rerun()

        total_count = sum(st.session_state[f'count_{name}'] for name in button_names)
        st.header(f"{total_count}/100")

        if total_count <= 100:
            st.progress(total_count / 100)
            
        if total_count == 100:
            st.success("100 Zellen gezählt!")
            st.write("Ergebnisse:")

            result_df = pd.DataFrame({'Zellentyp': button_names, 'Anzahl': [st.session_state[f'count_{name}'] for name in button_names]})
            st.dataframe(result_df, hide_index=True)

            if st.session_state['count_session'] == 1:
                st.session_state['result_df_1'] = result_df
            else:
                st.session_state['result_df_2'] = result_df

        if total_count > 100:
            st.error("Die Gesamtzahl darf 100 nicht überschreiten. Bitte mache den letzten Schritt rückgängig oder korrigiere den Zählerstand.")

        rows = [st.columns((1.5, 1.5, 1.5)) for _ in range(4)]
        button_pressed = None

        for name in button_names:
            index = button_names.index(name)
            row_index, col_index = divmod(index, 3)
            col = rows[row_index][col_index]
            with col:
                display_name = name
                if name.strip() in ["Div1", "Div2", "Div3"]:
                    display_name = st.session_state['custom_names'][int(name.strip()[-1]) - 1]
                button_label = f"{display_name}\n({st.session_state[f'count_{name}']})"
                if st.button(button_label, key=f'button_{name}', use_container_width=True):
                    if not st.session_state['edit_mode'] and not st.session_state['name_edit_mode']:
                        utils.save_state(button_names)
                        button_pressed = name
                if st.session_state['edit_mode']:
                    new_count = st.number_input("Zähler korrigieren", value=st.session_state[f'count_{name}'], key=f'edit_{name}')
                    if new_count + sum(st.session_state[f'count_{n}'] for n in button_names if n != name) <= 100:
                        st.session_state[f'count_{name}'] = new_count
                    else:
                        st.error("Die Gesamtzahl darf 100 nicht überschreiten.")

        if st.session_state['name_edit_mode']:
            for i in range(3):
                new_name = st.text_input(f"Neuer Name für {button_names[9+i]}", value=st.session_state['custom_names'][i].strip(), key=f'custom_name_{i}')
                st.session_state['custom_names'][i] = new_name + '   '

        if button_pressed is not None:
            utils.increment_button_count(button_pressed, button_names)
            if total_count + 1 == 100:
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        bottom_columns = st.columns((2, 2, 2))

        with bottom_columns[0]:
            if st.button('Zählung zurücksetzen', help="Setzt alle Zählerstände wieder auf null.", use_container_width=True):
                utils.reset_counts(button_names)
                st.rerun()

        with bottom_columns[2]:
            if st.session_state['count_session'] == 1:
                if st.button("Speichern & weiter zur 2. Zählung", use_container_width=True):
                    if total_count == 100:
                        utils.save_results(button_names)
                        utils.reset_counts(button_names)
                        st.session_state['count_session'] = 2
                    else:
                        st.error("Die Gesamtzahl der Zellen muss 100 betragen.")

            if st.session_state['count_session'] == 2:
                if st.button("Zählung beenden & archivieren", help="Die gespeicherten Ergebnisse sind im Archiv sichtbar.", use_container_width=True):
                    if total_count == 100:
                        utils.save_results(button_names)
                        utils.upload_to_github(utils.DB_FILE, utils.repo, 'zellzaehler.db')
                        utils.upload_to_github(utils.LOGIN_FILE, utils.repo, 'login_hashed_password_list.csv')
                        utils.reset_counts(button_names)
                        st.session_state['count_session'] = 1
                    else:
                        st.error("Die Gesamtzahl der Zellen muss 100 betragen.")
