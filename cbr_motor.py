import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from numpy.linalg import norm

from cbr_preparation import CBRMotorPreparation


class CBRMotor:
    def __init__(self, csv_path="dataset/motor_second.csv"):
        # --- Autopath supaya file CSV selalu ketemu ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, csv_path)

        print("Loading CSV from:", full_path)

        self.csv_path = full_path

        # ======================================================
        # 1. LOAD RAW CSV
        # ======================================================
        raw_df = pd.read_csv(full_path)

        # ======================================================
        # 2. PREPARATION & VALIDATION
        # ======================================================
        prep = CBRMotorPreparation()
        self.df = prep.process(raw_df)  # dataset bersih + encode aman

        # Simpan category asli untuk encoder query
        self.transmisi_categories = self.df["transmisi"].astype("category").cat.categories
        self.jenis_categories = self.df["jenis"].astype("category").cat.categories

        # ======================================================
        # 3. FITUR NUMERIK
        # ======================================================
        self.features = [
            "tahun", "harga", "odometer", "pajak",
            "konsumsiBBM", "mesin",
            "transmisi_enc", "jenis_enc"
        ]

        # ======================================================
        # 4. NORMALISASI
        # ======================================================
        self.scaler = MinMaxScaler()
        self.df_scaled = self.scaler.fit_transform(self.df[self.features])

    # ============================================================
    # SAFE ENCODER (ANTI ERROR & ANTI VALUE BARU)
    # ============================================================
    def _encode_value(self, value, categories, name):
        value = str(value).lower().strip()
        if value not in categories:
            raise ValueError(
                f"Nilai '{value}' tidak dikenal pada kategori '{name}'. "
                f"Kategori valid: {list(categories)}"
            )
        return list(categories).index(value)

    def _encode_transmisi(self, value):
        return self._encode_value(value, self.transmisi_categories, "transmisi")

    def _encode_jenis(self, value):
        return self._encode_value(value, self.jenis_categories, "jenis")

    # ============================================================
    # CBR SEARCH
    # ============================================================
    def run_cbr(self, query, k=3):
        """
        Menghitung cosine similarity antara query dan dataset.
        """
        # Safety check
        required = ["tahun", "harga", "odometer", "pajak",
                    "konsumsiBBM", "mesin", "transmisi", "jenis"]

        for r in required:
            if r not in query:
                raise ValueError(f"Query '{r}' tidak ditemukan!")

        # Query → vector numerik
        query_vector = np.array([
            float(query["tahun"]),
            float(query["harga"]),
            float(query["odometer"]),
            float(query["pajak"]),
            float(query["konsumsiBBM"]),
            float(query["mesin"]),
            self._encode_transmisi(query["transmisi"]),
            self._encode_jenis(query["jenis"]),
        ], dtype=float)

        # Normalisasi query
        query_scaled = self.scaler.transform([query_vector])[0]

        # Cosine similarity
        sims = []
        for i in range(len(self.df_scaled)):
            a = query_scaled
            b = self.df_scaled[i]
            cosine_sim = np.dot(a, b) / (norm(a) * norm(b) + 1e-9)
            sims.append(cosine_sim)

        # Urutan terbaik
        idx_top = np.argsort(sims)[-k:][::-1]

        result = self.df.iloc[idx_top].copy()
        result["similarity"] = np.array(sims)[idx_top]

        return result

    # ============================================================
    # RETAIN — simpan case baru ke CSV
    # ============================================================
    def retain(self, query):
        """
        Menyimpan case baru ke dataset CSV dan re-training scaler.
        """

        # Convert dict ke DataFrame
        new_case = pd.DataFrame([query])

        # Encode kategori
        new_case["transmisi"] = str(query["transmisi"]).lower().strip()
        new_case["jenis"] = str(query["jenis"]).lower().strip()

        new_case["transmisi_enc"] = self._encode_transmisi(new_case["transmisi"].iloc[0])
        new_case["jenis_enc"] = self._encode_jenis(new_case["jenis"].iloc[0])

        # Tambah ke dataset
        self.df = pd.concat([self.df, new_case], ignore_index=True)

        # Save ke CSV
        self.df.to_csv(self.csv_path, index=False)

        # Update kategori encoder
        self.transmisi_categories = self.df["transmisi"].astype("category").cat.categories
        self.jenis_categories = self.df["jenis"].astype("category").cat.categories

        # Rebuild scaler
        self.df_scaled = self.scaler.fit_transform(self.df[self.features])

        print("Case baru berhasil disimpan:", self.csv_path)

