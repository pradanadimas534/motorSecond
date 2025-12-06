import streamlit as st
import pandas as pd
from cbr_motor import CBRMotor

st.set_page_config(page_title="Rekomendasi Motor Bekas - CBR", layout="wide")

st.title("🔍 Sistem Rekomendasi Motor Bekas (CBR)")
st.write("Temukan motor bekas terbaik sesuai kebutuhanmu!")

# Load dataset
cbr = CBRMotor("dataset/motor_second.csv")


# =========================
#   INPUT KRITERIA USER
# =========================
st.subheader("Masukkan Kriteria Motor yang Dicari")

col1, col2 = st.columns(2)

with col1:
    budget = st.slider("Budget Maksimal (Juta)", 5, 50, 15)
    tahun_min = st.slider("Tahun Minimal", 2000, 2024, 2015)
    odometer_max = st.slider("Odometer Maksimal (km)", 0, 100000, 30000)

with col2:
    jenis = st.selectbox("Jenis Motor", ["matic", "bebek", "sport", "trail"])
    transmisi = st.selectbox("Transmisi", ["automatic", "manual"])
    pajak_status = st.selectbox("Status Pajak", ["Hidup", "Mati", "Bebas (apa saja)"])

model = st.text_input("Model (opsional, boleh kosong)", "")

# Pajak mapping
if pajak_status == "Hidup":
    pajak_query = 100
elif pajak_status == "Mati":
    pajak_query = 250
else:
    pajak_query = 150

# Jenis mapping (user input → dataset)
jenis_map = {
    "matic": "skuter",
    "bebek": "bebek",
    "sport": "sport",
    "trail": "trail",
}
jenis_dataset = jenis_map[jenis.lower()]

# Query
query = {
    "model": model if model else "unknown",
    "tahun": tahun_min,
    "harga": budget * 1000,
    "transmisi": transmisi.lower(),
    "odometer": odometer_max,
    "jenis": jenis_dataset,
    "pajak": pajak_query,
    "konsumsiBBM": 50,
    "mesin": 125,
}


# =========================
#   TOMBOL HASIL CBR
# =========================
if st.button("🔎 Cari Rekomendasi"):
    result = cbr.run_cbr(query)

    st.subheader("✨ Top 3 Rekomendasi Motor")
    st.dataframe(result)

    st.write("### 📊 Detail Similarity")
    st.dataframe(result[['model', 'tahun', 'harga', 'similarity']])

    if st.button("💾 Simpan Sebagai Case Baru (Retain)"):
        cbr.retain(query)
        st.success("Case baru berhasil disimpan!")


st.markdown("---")
st.write("📌 Sistem ini menggunakan *Case-Based Reasoning* dengan perhitungan *cosine similarity* untuk mencari motor bekas terbaik sesuai kebutuhanmu.")
