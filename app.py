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
        # Menggunakan gemini-1.5-flash (Gemini 3 Flash belum dirilis secara publik, versi terbaru adalah 1.5)
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("ERROR: GEMINI_API_KEY tidak ditemukan di Secrets.")
except Exception as e:
    st.error(f"ERROR AI CONFIG: {e}")

def connect_to_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = dict(st.secrets["gcp_service_account"])
        
        # Perbaikan Private Key: Menangani karakter escape dan spasi berlebih
        if "private_key" in creds_info:
            key = creds_info["private_key"]
            if "\\n" in key:
                key = key.replace("\\n", "\n")
            creds_info["private_key"] = key
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1VvwjYo0ghGU7Glw1hHxYkKeO-TAmMY_ql7Ty9qUWC4M").sheet1
    except Exception as e:
        st.error(f"Detail Error Koneksi Sheets: {e}")
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
            full_prompt = f"Persona: Anda adalah AURA (Asisten Umrah Ramah & Amanah) yang Islami. Pertanyaan: {prompt}"
            response = model.generate_content(full_prompt)
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
                with st.spinner("Sedang memproses ke database..."):
                    sheet = connect_to_sheets()
                    if sheet:
                        sheet.append_row([nama, wa, paket, str(datetime.now())])
                        st.success(f"Alhamdulillah, data Saudara/i {nama} berhasil terdaftar!")
                    else: st.error("Koneksi gagal. Cek kembali format Private Key di Secrets Streamlit.")
            else: st.warning("Harap lengkapi Nama dan No. WhatsApp.")
