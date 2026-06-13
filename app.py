import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="AURA Assistant", page_icon="\u1332B")

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash', 
                                    system_instruction="Anda adalah AURA, Asisten Umrah Ramah & Amanah. Bantu jamaah dengan sopan.")
    else:
        st.error("API KEY belum diisi di Secrets Streamlit Cloud.")
except Exception as e:
    st.error(f"Gagal AI: {e}")

def connect_to_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # ID SPREADSHEET ANDA SUDAH DIPASANG DI BAWAH INI
        return client.open_by_key("1VvwjYo0ghGU7Glw1hHxYkKeO-TAmMY_ql7Ty9qUWC4M").sheet1
    except Exception as e:
        return None

st.title("\u1332B AURA Assistant")
menu = st.sidebar.selectbox("Menu", ["Chat AI", "Pendaftaran"])

if menu == "Chat AI":
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Tanya AURA..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        try:
            response = model.generate_content(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"): st.markdown(response.text)
        except Exception as e:
            st.error("Koneksi AI Gagal. Pastikan GEMINI_API_KEY di Secrets sudah benar.")
else:
    st.subheader("Pendaftaran Umrah")
    with st.form("form_daftar"):
        nama = st.text_input("Nama Lengkap")
        wa = st.text_input("No. WhatsApp")
        if st.form_submit_button("Kirim"):
            if nama and wa:
                sheet = connect_to_sheets()
                if sheet:
                    sheet.append_row([nama, wa, str(datetime.now())])
                    st.success("Pendaftaran Berhasil Disimpan!")
                else:
                    st.error("Gagal menyimpan. Pastikan Service Account sudah di-Invite ke Google Sheet sebagai Editor.")
            else:
                st.warning("Mohon isi Nama dan WA.")

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from google.colab import userdata

# Cell ini untuk mengetes akses Google Sheet Anda dari Colab
# Masukkan JSON Service Account Anda di bawah ini untuk tes
def test_connection():
    try:
        # Ambil kredensial dari secrets yang sudah Anda buat di cell pertama
        # (Asumsi Anda sudah mengisi secrets_content di cell 2e5f1585)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Jika Anda menjalankan di Colab, kita bisa coba simulasi koneksi
        # GANTI ID DI BAWAH INI DENGAN ID SHEET ANDA
        SHEET_ID = '1VvwjYo0ghGU7Glw1hHxYkKeO-TAmMY_ql7Ty9qUWC4M'
        
        print(f"Mencoba menghubungkan ke sheet: {SHEET_ID}...")
        # Catatan: Ini hanya tes jika Anda sudah memasukkan JSON ke variabel
        # Jika belum, pastikan langkah manual 'Share' di browser sudah dilakukan.
        print("Tips: Pastikan email 'client_email' sudah di-invite di Google Sheet.")
    except Exception as e:
        print(f"Error: {e}")

test_connection()
