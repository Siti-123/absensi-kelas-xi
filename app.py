import streamlit as st
import pandas as pd
from datetime import datetime
import os
from google import genai

# Setup API Key (Masukkan API Key dari Google AI Studio jika ingin fitur AI aktif)
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# 1. Database Data Siswa (NISN: {"nama": ..., "pin": ...})
DATA_SISWA = {
    "1001": {"nama": "Budi Santoso", "pin": "1234"},
    "1002": {"nama": "Siti Rahma", "pin": "5678"},
    "1003": {"nama": "Ani Wijaya", "pin": "4321"},
    "1004": {"nama": "Doni Pratama", "pin": "8888"},
    "1005": {"nama": "Eko Prasetyo", "pin": "9999"}
}

FILE_ABSENSI = "absensi_nisn.csv"

st.set_page_config(page_title="Portal Absensi Mandiri Kelas XI", layout="centered")
st.title("🏫 Portal Absensi Mandiri - Kelas XI")
st.write("Masukkan NISN dan PIN Rahasia Anda untuk melakukan presensi.")

tab1, tab2 = st.tabs(["📌 Input Presensi", "📊 Rekap & Analisis AI (Guru)"])

# ---------------- TAB 1: PRESENSI SISWA ----------------
with tab1:
    with st.form("form_absensi", clear_on_submit=True):
        nisn_input = st.text_input("Nomor Induk Siswa (NISN):")
        pin_input = st.text_input("PIN Rahasia (4 Digit):", type="password")
        status_opsi = st.selectbox("Status Kehadiran:", ["Hadir", "Izin", "Sakit"])
        keterangan_input = st.text_input("Keterangan Tambahan (Opsional):", placeholder="Misal: Surat dokter / Acara keluarga")

        btn_submit = st.form_submit_button("Kirim Presensi")

    if btn_submit:
        if nisn_input in DATA_SISWA:
            if DATA_SISWA[nisn_input]["pin"] == pin_input:
                nama_siswa = DATA_SISWA[nisn_input]["nama"]
                waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                data_baru = {
                    "NISN": nisn_input,
                    "Nama": nama_siswa,
                    "Status": status_opsi,
                    "Keterangan": keterangan_input if keterangan_input else "-",
                    "Waktu": waktu_sekarang
                }
                
                df_baru = pd.DataFrame([data_baru])
                df_baru.to_csv(FILE_ABSENSI, mode='a', header=not os.path.exists(FILE_ABSENSI), index=False)
                st.success(f"✅ Presensi Berhasil! Selamat pagi, **{nama_siswa}** ({status_opsi} pada {waktu_sekarang}).")
            else:
                st.error("❌ PIN Rahasia salah!")
        else:
            st.error("❌ NISN tidak terdaftar.")

# ---------------- TAB 2: REKAPITULASI (GURU) ----------------
with tab2:
    st.subheader("Rekap Kehadiran Harian")
    if os.path.exists(FILE_ABSENSI):
        df_log = pd.read_csv(FILE_ABSENSI)
        st.dataframe(df_log, use_container_width=True)

        if st.button("🤖 Jalankan Analisis Kehadiran AI") and API_KEY:
            with st.spinner("Menganalisis tren kehadiran..."):
                try:
                    client = genai.Client(api_key=API_KEY)
                    prompt = f"Berikut adalah data log absensi kelas hari ini:\n{df_log.to_string()}\nTolong berikan ringkasan singkat jumlah Hadir, Sakit, Izin, dan saran untuk guru."
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    st.info("### Hasil Analisis AI:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Gagal memproses AI: {e}")
    else:
        st.warning("Belum ada data presensi yang masuk hari ini.")