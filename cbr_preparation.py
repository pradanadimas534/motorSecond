import pandas as pd
import numpy as np

class CBRMotorPreparation:
    REQUIRED_COLUMNS = [
        "model", "tahun", "harga", "transmisi",
        "odometer", "jenis", "pajak",
        "konsumsiBBM", "mesin"
    ]

    CATEGORICAL = ["transmisi", "jenis"]
    NUMERIC = ["tahun", "harga", "odometer", "pajak", "konsumsiBBM", "mesin"]

    # ============================================================
    # CHECK STRUCTURE — memastikan kolom lengkap
    # ============================================================
    def validate_structure(self, df):
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"❌ Kolom hilang dalam dataset: {missing}")
        return True

    # ============================================================
    # CLEANING — mempersiapkan data agar aman
    # ============================================================
    def clean_dataframe(self, df):
        df = df.copy()

        # --- 1. Drop duplikat ---
        df.drop_duplicates(inplace=True)

        # --- 2. Bersihkan spasi/kapital kategori ---
        for col in self.CATEGORICAL:
            df[col] = df[col].astype(str).str.lower().str.strip()

        # --- 3. Replace nilai kategori yang kosong ---
        for col in self.CATEGORICAL:
            df[col].replace(["", "nan", None], df[col].mode()[0], inplace=True)

        # --- 4. Converter numerik + hapus nilai aneh ---
        for col in self.NUMERIC:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Hapus nilai NaN akibat error conversion
        df.dropna(subset=self.NUMERIC, inplace=True)

        # --- 5. Hapus outlier kasar (anti harga 0, km 10 juta) ---
        for col in self.NUMERIC:
            q1 = df[col].quantile(0.01)
            q3 = df[col].quantile(0.99)
            df = df[(df[col] >= q1) & (df[col] <= q3)]

        return df

    # ============================================================
    # ENCODE — ubah kategori jadi angka
    # ============================================================
    def encode_dataframe(self, df):
        df = df.copy()

        df["transmisi_enc"] = df["transmisi"].astype("category").cat.codes
        df["jenis_enc"] = df["jenis"].astype("category").cat.codes

        return df

    # ============================================================
    # MAIN PIPELINE — digunakan oleh CBRMotor
    # ============================================================
    def process(self, df):
        self.validate_structure(df)
        df = self.clean_dataframe(df)
        df = self.encode_dataframe(df)
        return df
