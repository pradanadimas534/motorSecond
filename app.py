import streamlit as st
import pandas as pd
from cbr_motor import CBRMotor

st.set_page_config(page_title="Rekomendasi Motor Bekas - CBR", layout="wide")

st.title("🔍 Sistem Rekomendasi Motor Bekas (CBR)")
st.write("Temukan motor bekas terbaik sesuai kebutuhanmu!")

# =====================================
# LOAD CBR CLASS
# =====================================
cbr = CBRMotor("dataset/motor_second.csv")

# =====================================
# INPUT USER
# =====================================
st.subheader("Masukkan Kriteria Motor")

col1, col2 = st.columns(2)

with col1:
    budget = st.slider("Budget Maksimal (Juta)", 5, 50, 15)
    tahun_min = st.slider("Tahun Minimal", 2000, 2024, 2015)
    odometer_max = st.slider("Odometer Maksimal (km)", 0, 100000, 30000)

with col2:
    jenis = st.selectbox("Jenis Motor", ["matic", "bebek", "sport", "trail"])
    transmisi = st.selectbox("Transmisi", ["automatic", "manual"])
    pajak_status = st.selectbox("Status Pajak", ["Hidup", "Mati", "Bebas (apa saja)"])

model = st.text_input("Model (opsional)", "")

# Mapping pajak
if pajak_status == "Hidup":
    pajak_query = 100
elif pajak_status == "Mati":
    pajak_query = 250
else:
    pajak_query = 150

# Mapping jenis dataset
jenis_map = {
    "matic": "skuter",
    "bebek": "bebek",
    "sport": "sport",
    "trail": "trail",
}

jenis_dataset = jenis_map[jenis.lower()]

# Buat query final
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

# =====================================
# BUTTON PREDIKSI
# =====================================
if st.button("🔎 Cari Rekomendasi"):

    retrieved_cases = cbr.retrieve(query)

    st.subheader("✨ Top 3 Rekomendasi Motor")
    st.dataframe(retrieved_cases)

    best_case = cbr.reuse(retrieved_cases)

    st.subheader("📌 Rekomendasi Utama")
    st.write(best_case)

    # Feedback User (REVISION)
    st.markdown("### Apakah rekomendasi ini sesuai?")
    feedback = st.radio("Feedback:", ["Ya", "Tidak"])

    if feedback == "Tidak":
        st.markdown("### Masukkan Data Motor yang Benar")

        colA, colB = st.columns(2)
        with colA:
            rev_tahun = st.number_input("Tahun", 1990, 2024, 2020)
            rev_harga = st.number_input("Harga", 1000, 100000, 15000)
            rev_odometer = st.number_input("Odometer", 0, 200000, 30000)
            rev_pajak = st.number_input("Pajak", 50, 300, 150)

        with colB:
            rev_konsumsi = st.number_input("Konsumsi BBM", 10, 100, 50)
            rev_mesin = st.number_input("Mesin (CC)", 50, 250, 125)
            rev_transmisi = st.selectbox("Transmisi Revisi", ["automatic", "manual"])
            rev_jenis = st.selectbox("Jenis Revisi", ["skuter", "bebek", "sport", "trail"])

        corrected_case = {
            "tahun": rev_tahun,
            "harga": rev_harga,
            "odometer": rev_odometer,
            "pajak": rev_pajak,
            "konsumsiBBM": rev_konsumsi,
            "mesin": rev_mesin,
            "transmisi": rev_transmisi,
            "jenis": rev_jenis,
        }

        if st.button("💾 Simpan Revisi (RETAIN)"):
            final_case = cbr.revise(best_case, False, corrected_case)
            cbr.retain(final_case)
            st.success("Revisi disimpan sebagai case baru!")

    else:
        st.success("Rekomendasi disetujui! Tidak perlu revisi.")
        final_case = cbr.revise(best_case, True)

st.markdown("---")
st.write("📌 Sistem ini menggunakan *Case-Based Reasoning* (CBR) dengan manual cosine similarity.")
