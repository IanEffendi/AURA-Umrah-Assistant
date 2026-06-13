import os

# Kode versi ultra-stabil: Tanpa Tabs, Tanpa Layout Kompleks untuk reset UI
final_code = r'''
import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Hindari layout='wide' jika masih error, gunakan default
st.set_page_config(page_title="AURA Assistant", page_icon="\u1332B")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.warning("API Key belum siap.")

system_instruction = "Anda adalah AURA, Asisten Umrah Ramah & Amanah."
model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)

def connect_to_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open_by_key("ID_SPREADSHEET_ANDA_DISINI").sheet1
    except Exception as e:
        return None

# Navigasi Sederhana
st.title("\u1332B AURA Assistant")
menu = st.sidebar.selectbox("Menu Utama", ["Chat", "Daftar"])

if menu == "Chat":
    st.subheader("Tanya Jawab")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ketik di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        chat = model.start_chat()
        response = chat.send_message(prompt)
        
        with st.chat_message("assistant"): st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

else:
    st.subheader("Form Pendaftaran")
    with st.form("f1"):
        nama = st.text_input("Nama")
        wa = st.text_input("WA")
        if st.form_submit_button("Kirim"):
            if nama and wa:
                sheet = connect_to_sheets()
                if sheet:
                    sheet.append_row([nama, wa, str(datetime.now())])
                    st.success("Berhasil!")
            else:
                st.error("Isi data!")
'''

with open('app.py', 'w') as f:
    f.write(final_code)

with open('aura_assistant.py', 'w') as f:
    f.write(final_code)

print("KODE DIPERBARUI. Silakan salin ke GitHub dan klik REBOOT di Streamlit Cloud!")
