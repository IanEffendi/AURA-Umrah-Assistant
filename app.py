import os

final_code = r'''
import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="AURA Assistant", page_icon="\u1332B")

# Ambil secrets secara aman
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.error("GEMINI_API_KEY tidak ditemukan di Secrets.")
except Exception as e:
    st.error(f"Gagal konfigurasi Gemini: {e}")

system_instruction = "Anda adalah AURA, Asisten Umrah Ramah & Amanah. Bantu jamaah dengan sopan."
model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)

def connect_to_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Mendukung struktur secrets Streamlit Cloud
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # GANTI ID BERIKUT DENGAN ID GOOGLE SHEET ANDA
        return client.open_by_key("ID_SPREADSHEET_ANDA_DISINI").sheet1
    except Exception as e:
        st.sidebar.error(f"Sheets Error: {e}")
        return None

st.title("\u1332B AURA Assistant")
menu = st.sidebar.selectbox("Navigasi", ["Chat AI", "Daftar Umrah"])

if menu == "Chat AI":
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Tanya AURA di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        try:
            response = model.generate_content(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"): st.markdown(response.text)
        except Exception as e:
            st.error(f"Error AI: {e}")

else:
    st.subheader("Form Pendaftaran")
    with st.form("reg_form"):
        nama = st.text_input("Nama Lengkap")
        wa = st.text_input("Nomor WhatsApp")
        submitted = st.form_submit_button("Kirim Pendaftaran")
        
        if submitted:
            if nama and wa:
                sheet = connect_to_sheets()
                if sheet:
                    sheet.append_row([nama, wa, str(datetime.now())])
                    st.success("Alhamdulillah, data pendaftaran telah kami terima!")
                else:
                    st.error("Gagal menyambung ke database. Periksa ID Spreadsheet.")
            else:
                st.warning("Mohon lengkapi Nama dan WA.")
'''

with open('app.py', 'w') as f: f.write(final_code)
print("FILE app.py DIPERBARUI. Silakan salin ke GitHub dan REBOOT app!")
