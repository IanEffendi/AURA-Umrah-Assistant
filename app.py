import os

# Kode aplikasi yang sudah bersih dan benar
final_code = r'''
import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import urllib.parse
import requests

st.set_page_config(page_title="AURA Umrah Assistant", page_icon="\u1332B", layout="centered")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Gagal memuat API Key.")

system_instruction = """
Anda adalah AURA (Asisten Umrah Ramah & Amanah), representasi virtual dari biro perjalanan Umrah & Haji terpercaya.
Gaya bahasa Anda: Sangat ramah, Islami (salam, masyaAllah, alhamdulillah), sopan, dan profesional.
"""

model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)

def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    spreadsheet_id = "ID_SPREADSHEET_ANDA_DISINI" 
    if spreadsheet_id == "ID_SPREADSHEET_ANDA_DISINI":
        st.error("Silakan isi ID Spreadsheet Anda di kode ini.")
        return None
    return client.open_by_key(spreadsheet_id).sheet1

st.title("AURA Assistant")
tab1, tab2 = st.tabs(["Chat", "Pendaftaran"])

with tab1:
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).markdown(m["content"])
    if prompt := st.chat_input("Tanya AURA..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = model.start_chat().send_message(prompt)
        st.chat_message("assistant").markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

with tab2:
    with st.form("reg_form"):
        nama = st.text_input("Nama")
        no_hp = st.text_input("WhatsApp (628...)")
        paket = st.selectbox("Pilihan Paket", ["Umrah Reguler", "Umrah Plus", "Haji Furoda"])
        if st.form_submit_button("Kirim Pendaftaran"):
            if nama and no_hp:
                try:
                    sheet = connect_to_sheets()
                    if sheet:
                        sheet.append_row([nama, no_hp, paket, str(datetime.now())])
                        st.success("Pendaftaran Berhasil Dikirim!")
                except Exception as e: st.error(f"Gagal: {e}")
'''

# Simpan ke kedua nama file agar tidak bingung
with open('aura_assistant.py', 'w') as f:
    f.write(final_code)

with open('app.py', 'w') as f:
    f.write(final_code)

print('BERHASIL: File aura_assistant.py dan app.py sekarang identik dan sudah diperbaiki!')