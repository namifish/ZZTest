import pandas as pd
import bcrypt
import sqlite3
import os
import base64
import io
from datetime import datetime
from github import Github
import streamlit as st

LOGIN_FILE = "zellzaehler/data/login_hashed_password_list.csv"
DB_FILE = "zellzaehler/data/zellzaehler.db"

# GitHub repository details
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = st.secrets["github"]["repo"]
GITHUB_OWNER = st.secrets["github"]["owner"]

# Initialize GitHub connection
github = Github(GITHUB_TOKEN)
repo = github.get_repo(f"{GITHUB_OWNER}/{GITHUB_REPO}")

def set_background(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
                username TEXT,
                sample_number TEXT,
                count_session INTEGER,
                date TEXT,
                counts TEXT,
                FOREIGN KEY(username) REFERENCES users(username)
              )''')
    conn.commit()
    conn.close()

def init_user_data():
    if not os.path.exists(LOGIN_FILE):
        df = pd.DataFrame(columns=['username', 'password'])
        df.to_csv(LOGIN_FILE, index=False)

def load_user_data():
    if not os.path.exists(LOGIN_FILE):
        init_user_data()
    return pd.read_csv(LOGIN_FILE)

def save_user_data(data):
    data.to_csv(LOGIN_FILE, index=False)

def encrypt_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode())

def verify_user(username, password):
    users = load_user_data()
    if username in users['username'].values:
        hashed_password = users[users['username'] == username]['password'].values[0]
        if verify_password(password, hashed_password):
            return True
    return False

def register_user(username, password):
    users = load_user_data()
    if username in users['username'].values:
        return False
    new_user = pd.DataFrame([[username, encrypt_password(password)]], columns=['username', 'password'])
    users = pd.concat([users, new_user], ignore_index=True)
    save_user_data(users)
    upload_to_github(LOGIN_FILE, repo, 'zellzaehler/data/login_hashed_password_list.csv')
    return True

def delete_user(username):
    users = load_user_data()
    users = users[users['username'] != username]
    save_user_data(users)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM results WHERE username=?', (username,))
    conn.commit()
    conn.close()

    delete_user_from_github(username)

def save_user_results(username, sample_number, count_session, date_time, current_counts):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    counts_str = ','.join(f'{key}:{value}' for key, value in current_counts.items())
    c.execute('''INSERT INTO results (username, sample_number, count_session, date, counts)
                 VALUES (?, ?, ?, ?, ?)''', (username, sample_number, count_session, date_time, counts_str))
    conn.commit()
    conn.close()

def get_user_results(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT sample_number, count_session, date, counts FROM results WHERE username=?', (username,))
    results = c.fetchall()
    conn.close()
    return results

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def upload_to_github(file_path, repo, github_path):
    with open(file_path, "r", encoding="latin1") as file:
        content = file.read()
    try:
        contents = repo.get_contents(github_path)
        repo.update_file(github_path, "Updated data", content, contents.sha)
    except Exception as e:
        repo.create_file(github_path, "Initial commit", content)

def delete_from_github(repo, github_path):
    try:
        contents = repo.get_contents(github_path)
        repo.delete_file(contents.path, "Deleted data", contents.sha)
    except Exception as e:
        print(f"Error deleting {github_path} from GitHub: {e}")

def delete_user_from_github(username):
    # Delete user data from login file
    login_path = 'zellzaehler/data/login_hashed_password_list.csv'
    try:
        login_file = repo.get_contents(login_path)
        login_data = login_file.decoded_content.decode()
        lines = login_data.split('\n')
        updated_lines = [line for line in lines if not line.startswith(username + ',')]
        new_login_data = '\n'.join(updated_lines)
        repo.update_file(login_path, "Deleted user", new_login_data, login_file.sha)
    except Exception as e:
        print(f"Error updating {login_path} on GitHub: {e}")

    # Delete user data from database file
    db_path = 'zellzaehler/data/zellzaehler.db'
    try:
        db_file = repo.get_contents(db_path)
        local_db_path = "zellzaehler_temp.db"
        with open(local_db_path, "wb") as file:
            file.write(db_file.decoded_content)
        conn = sqlite3.connect(local_db_path)
        c = conn.cursor()
        c.execute('DELETE FROM results WHERE username=?', (username,))
        conn.commit()
        conn.close()
        with open(local_db_path, "rb") as file:
            new_db_data = file.read()
        repo.update_file(db_path, "Deleted user data", new_db_data.decode('latin1'), db_file.sha)
        os.remove(local_db_path)
    except Exception as e:
        print(f"Error updating {db_path} on GitHub: {e}")

def display_results(results):
    if not results:
        st.write("Keine gespeicherten Ergebnisse.")
        return

    button_names = [
        "Pro   ", "Mye   ", "Meta   ", "Stab   ", "Seg   ", "Eos   ",
        "Baso   ", "Mono   ", "Ly   ", "Div1   ", "Div2   ", "Div3   "
    ]

    if isinstance(results[0], dict):
        sample_numbers = list(set(result['sample_number'] for result in results))
        selected_sample = st.selectbox("Probenummer auswählen", sample_numbers)
    else:
        sample_numbers = list(set(result[0] for result in results))
        selected_sample = st.selectbox("Probenummer auswählen", sample_numbers)

    if selected_sample:
        data = {name: [0, 0, 0] for name in button_names}

        if isinstance(results[0], dict):
            for result in results:
                if result['sample_number'] == selected_sample:
                    sample_number = result['sample_number']
                    count_session = result['count_session']
                    date = result['date']
                    counts = result['counts']

                    if count_session == 1:
                        for name in button_names:
                            data[name][0] = counts.get(name, 0)
                    else:
                        for name in button_names:
                            data[name][1] = counts.get(name, 0)
        else:
            for result in results:
                if result[0] == selected_sample:
                    sample_number = result[0]
                    count_session = result[1]
                    date = result[2]
                    counts_str = result[3]
                    counts = dict(item.split(":") for item in counts_str.split(","))
                    counts = {key: int(value) for key, value in counts.items()}

                    if count_session == 1:
                        for name in button_names:
                            data[name][0] = counts.get(name, 0)
                    else:
                        for name in button_names:
                            data[name][1] = counts.get(name, 0)

        for name in button_names:
            data[name][2] = (data[name][0] + data[name][1]) / 2

        counts_df = pd.DataFrame(data, index=['1. Zählung', '2. Zählung', 'Durchschnitt']).T.reset_index()
        counts_df.columns = ['Zellentyp', '1. Zählung', '2. Zählung', 'Durchschnitt']
        st.dataframe(counts_df, hide_index=True)

        excel_data = to_excel(counts_df)
        st.download_button(label='Excel runterladen', data=excel_data, file_name=f'{selected_sample}.xlsx', key=f'download_{selected_sample}')

def increment_button_count(name, button_names):
    total_count = sum(st.session_state[f'count_{name}'] for name in button_names)
    if total_count >= 100:
        st.error("Das Zählziel von 100 wurde bereits erreicht.")
    else:
        st.session_state[f'count_{name}'] += 1
        st.rerun()

def save_state(button_names):
    current_counts = {name: st.session_state[f'count_{name}'] for name in button_names}
    st.session_state['history'].append(current_counts)

def undo_last_step(button_names):
    if st.session_state['history']:
        last_state = st.session_state['history'].pop()
        for name in button_names:
            st.session_state[f'count_{name}'] = last_state[name]
        st.rerun()

def reset_counts(button_names):
    for name in button_names:
        st.session_state[f'count_{name}'] = 0
    st.rerun()

def save_results(button_names):
    sample_number = st.session_state['sample_number']
    count_session = st.session_state['count_session']
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_counts = {name: st.session_state[f'count_{name}'] for name in button_names}
    if 'username' in st.session_state:
        save_user_results(st.session_state['username'], sample_number, count_session, date_time, current_counts)
        st.session_state['results'] = get_user_results(st.session_state['username'])
    else:
        guest_result = {
            'sample_number': sample_number,
            'count_session': count_session,
            'date': date_time,
            'counts': current_counts
        }
        st.session_state['guest_results'].append(guest_result)
    if count_session == 2:
        st.session_state['count_session'] = 1
        st.session_state['sample_number'] = ""
    else:
        st.session_state['count_session'] += 1
    reset_counts(button_names)
