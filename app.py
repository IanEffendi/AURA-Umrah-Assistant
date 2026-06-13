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
        # Menggunakan gemini-1.5-flash-latest untuk kompatibilitas lebih baik
        model = genai.GenerativeModel('gemini-1.5-flash-latest',
                                    system_instruction="Anda adalah AURA, Asisten Umrah Ramah & Amanah. Bantu jamaah dengan sopan, Islami, dan informatif.")
    else:
        st.error("ERROR: GEMINI_API_KEY tidak ditemukan di Secrets.")
except Exception as e:
    st.error(f"ERROR AI CONFIG: {e}")

def connect_to_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1VvwjYo0ghGU7Glw1hHxYkKeO-TAmMY_ql7Ty9qUWC4M").sheet1
    except Exception as e:
        st.error(f"ERROR KONEKSI SHEETS: {e}")
        return None

st.title("\u1332B AURA Assistant")
st.markdown("--- ")
menu = st.sidebar.selectbox("Pilih Menu", ["Chat AI (Tanya Jawab)", "Pendaftaran Jamaah"])

if menu == "Chat AI (Tanya Jawab)":
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("Tanya AURA tentang Umrah..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        try:
            response = model.generate_content(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"): st.markdown(response.text)
        except Exception as e: st.error(f"AI Error: {e}")
else:
    st.subheader("Formulir Pendaftaran")
    with st.form("form_daftar"):
        nama = st.text_input("Nama Lengkap")
        wa = st.text_input("Nomor WhatsApp (Aktif)")
        paket = st.selectbox("Pilih Paket", ["Paket Reguler", "Paket Plus", "Paket VIP"])
        if st.form_submit_button("Kirim Pendaftaran"):
            if nama and wa:
                with st.spinner("Menyimpan data..."):
                    sheet = connect_to_sheets()
                    if sheet:
                        sheet.append_row([nama, wa, paket, str(datetime.now())])
                        st.success(f"Alhamdulillah, data Saudara/i {nama} berhasil terdaftar!")
                        st.info("Admin kami akan segera menghubungi Anda.")
                    else: st.error("Gagal menyimpan. Pastikan Service Account sudah di-invite sebagai Editor di Google Sheet.")
            else: st.warning("Harap lengkapi Nama dan No. WhatsApp.")
