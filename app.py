import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import urllib.parse

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(page_title="AURA Umrah Assistant", page_icon="🕋", layout="centered")

# ==========================================
# INISIALISASI GEMINI API
# ==========================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Parameter Kreatif: Persona AURA
system_instruction = """
Anda adalah AURA (Asisten Umrah Ramah & Amanah), representasi virtual dari biro perjalanan Umrah & Haji terpercaya.
Gaya bahasa Anda: Sangat ramah, Islami (gunakan salam, masyaAllah, alhamdulillah), antusias, sopan, dan profesional.
Tujuan utama Anda: Memberikan informasi paket umrah, melayani pertanyaan jamaah, dan mengarahkan (closing) mereka untuk mendaftar.
Jika jamaah menunjukkan ketertarikan, arahkan mereka untuk mengisi form pendaftaran di tab 'Form Pendaftaran' di aplikasi ini.
Jangan berhalusinasi tentang harga jika tidak yakin, katakan bahwa admin akan memberikan detail brosur via WhatsApp.
"""

model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)

# ==========================================
# KONEKSI KE GOOGLE SHEETS
# ==========================================
def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    # GANTI URL DI BAWAH DENGAN URL SPREADSHEET ANDA
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/ID_SPREADSHEET_ANDA_DISINI/edit").sheet1
    return sheet

# ==========================================
# UI APLIKASI
# ==========================================
st.title("🕋 AURA: Asisten Umrah & Haji Anda")
st.write("Assalamu'alaikum! Selamat datang di layanan asisten virtual kami. Ada yang bisa AURA bantu hari ini?")

# Membuat Tab untuk Chat dan Form
tab1, tab2 = st.tabs(["💬 Chat dengan AURA", "📝 Form Pendaftaran"])

# --- TAB 1: CHATBOT ---
with tab1:
    # Memory Chat (menyimpan histori percakapan)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Tampilkan histori
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input User
    if prompt := st.chat_input("Ketik pertanyaan Anda di sini... (Contoh: Apa saja paket umrah bulan depan?)"):
        # Tampilkan chat user
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate respon Gemini
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        
        # Tampilkan chat bot
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# --- TAB 2: FORM PENDAFTARAN & WHATSAPP CLOSING ---
with tab2:
    st.header("Formulir Minat Jamaah")
    st.write("Silakan isi data diri Anda. AURA akan segera menghubungkan Anda dengan tim layanan pelanggan kami untuk proses selanjutnya.")
    
    with st.form("form_pendaftaran"):
        nama = st.text_input("Nama Lengkap")
        email = st.text_input("Email")
        no_hp = st.text_input("Nomor WhatsApp (Contoh: 08123456789)")
        alamat = st.text_area("Alamat Domisili")
        paket = st.selectbox("Paket yang Diminati", ["Umrah Reguler (9 Hari)", "Umrah Plus Turki (12 Hari)", "Umrah Ramadhan", "Haji Furoda", "Belum Menentukan"])
        
        submit_button = st.form_submit_button("Kirim Data & Chat Admin")
        
        if submit_button:
            if nama and no_hp:
                try:
                    # 1. Simpan ke Google Sheets
                    sheet = connect_to_sheets()
                    waktu_daftar = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sheet.append_row([nama, email, no_hp, alamat, paket, waktu_daftar])
                    st.success("Alhamdulillah! Data Anda berhasil disimpan.")
                    
                    # 2. Buat Link WhatsApp otomatis untuk "Closing"
                    admin_phone = "6281234567890" # GANTI DENGAN NOMOR WA ADMIN
                    pesan_wa = f"Assalamu'alaikum Admin. Saya {nama}. Saya sudah mengisi form minat jamaah. Saya tertarik dengan {paket}. Mohon informasi lebih lanjut."
                    pesan_encoded = urllib.parse.quote(pesan_wa)
                    link_wa = f"https://wa.me/{admin_phone}?text={pesan_encoded}"
                    
                    st.info("Silakan klik tombol di bawah ini untuk langsung terhubung dengan Admin via WhatsApp dan mendapatkan brosur lengkap!")
                    st.markdown(f'<a href="{link_wa}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px 24px; border:none; border-radius:5px; cursor:pointer;">Hubungi Admin via WhatsApp</button></a>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Terjadi kesalahan sistem: {e}")
            else:
                st.warning("Mohon lengkapi Nama dan Nomor WhatsApp Anda.")