import streamlit as st
import pandas as pd
from cbr_motor import CBRMotor

st.set_page_config(page_title="Rekomendasi Motor Bekas - CBR", layout="wide")

st.title("🔍 Sistem Rekomendasi Motor Bekas (CBR)")
st.write("Temukan motor bekas terbaik sesuai kebutuhanmu!")

# ==========================================
# INIT SESSION STATE
# ==========================================
if "step" not in st.session_state:
    st.session_state.step = "input"

if "df_top" not in st.session_state:
    st.session_state.df_top = None

if "best_case" not in st.session_state:
    st.session_state.best_case = None

if "reused" not in st.session_state:
    st.session_state.reused = None


# ==========================================
# LOAD CBR
# ==========================================
cbr = CBRMotor("dataset/motor_second.csv")


# ==========================================
# INPUT USER
# ==========================================
if st.session_state.step == "input":

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

    pajak_query = 100 if pajak_status == "Hidup" else 250 if pajak_status == "Mati" else 150
    jenis_map = {"matic": "skuter", "bebek": "bebek", "sport": "sport", "trail": "trail"}
    jenis_dataset = jenis_map[jenis.lower()]

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

    if st.button("🔎 Cari Rekomendasi"):
        # RETRIEVE
        df_top = cbr.retrieve(query)
        st.session_state.df_top = df_top

        best = df_top.iloc[0]
        st.session_state.best_case = best

        reused = cbr.reuse(best)
        st.session_state.reused = reused

        st.session_state.step = "review"


# ==========================================
# STEP 2 – TAMPILKAN REKOMENDASI
# ==========================================
if st.session_state.step == "review":

    st.subheader("✨ Rekomendasi Terdekat")
    st.dataframe(st.session_state.df_top)

    st.subheader("📌 Rekomendasi Utama")
    st.dataframe(pd.DataFrame([st.session_state.reused]))

    st.markdown("### Apakah rekomendasi ini sesuai?")
    feedback = st.radio("Feedback:", ["Ya", "Tidak"])

    if feedback == "Ya":
        final = cbr.revise(st.session_state.reused, True)
        cbr.retain(final)
        st.session_state.step = "selesai"

    else:
        st.session_state.step = "revise"
        st.rerun()


# ==========================================
# STEP 3 – FORM REVISI
# ==========================================
if st.session_state.step == "revise":

    st.subheader("✏️ Perbaiki Data Motor")

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
        final = cbr.revise(st.session_state.reused, False, corrected_case)
        cbr.retain(final)
        st.session_state.step = "selesai"


# ==========================================
# STEP 4 – DONE
# ==========================================
if st.session_state.step == "selesai":
    st.success("🎉 Case berhasil diproses dan disimpan!")
    if st.button("🔄 Cari Lagi"):
        st.session_state.step = "input"
        st.rerun()


st.markdown("---")
st.write("📌 Sistem ini menggunakan *Case-Based Reasoning* (CBR) dengan manual cosine similarity.")
