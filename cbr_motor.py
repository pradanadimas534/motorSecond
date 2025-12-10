import os
import pandas as pd
import math

class CBRMotor:

    def __init__(self, csv_path="dataset/motor_second.csv"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(base_dir, csv_path)

        self.df = pd.read_csv(self.csv_path)

        # Normalisasi text
        self.df["transmisi"] = self.df["transmisi"].str.lower().str.strip()
        self.df["jenis"] = self.df["jenis"].str.lower().str.strip()

        # kategori
        self.transmisi_categories = sorted(self.df["transmisi"].unique())
        self.jenis_categories = sorted(self.df["jenis"].unique())

        # encoding manual
        self.df["transmisi_enc"] = self.df["transmisi"].apply(lambda x: self.transmisi_categories.index(x))
        self.df["jenis_enc"] = self.df["jenis"].apply(lambda x: self.jenis_categories.index(x))

        self.features = [
            "tahun", "harga", "odometer", "pajak",
            "konsumsiBBM", "mesin",
            "transmisi_enc", "jenis_enc"
        ]

        # normalisasi
        self.min_vals = self.df[self.features].min()
        self.max_vals = self.df[self.features].max()

    # ===========================
    # Helper
    # ===========================
    def _encode(self, value, categories, name):
        value = str(value).lower().strip()
        if value not in categories:
            raise ValueError(f"Nilai '{value}' tidak dikenal untuk '{name}'. Valid: {categories}")
        return categories.index(value)

    def _normalize(self, value, min_v, max_v):
        if max_v - min_v == 0:
            return 0
        return (value - min_v) / (max_v - min_v)

    def _cosine_similarity(self, v1, v2):
        dot = sum(a*b for a,b in zip(v1,v2))
        mag1 = math.sqrt(sum(a*a for a in v1))
        mag2 = math.sqrt(sum(b*b for b in v2))
        if mag1 == 0 or mag2 == 0:
            return 0
        return dot / (mag1*mag2)

    # ===========================
    # 1. RETRIEVE
    # ===========================
    def retrieve(self, query):

        q_vec = [
            float(query["tahun"]),
            float(query["harga"]),
            float(query["odometer"]),
            float(query["pajak"]),
            float(query["konsumsiBBM"]),
            float(query["mesin"]),
            self._encode(query["transmisi"], self.transmisi_categories, "transmisi"),
            self._encode(query["jenis"], self.jenis_categories, "jenis"),
        ]

        q_norm = [
            self._normalize(q_vec[i], self.min_vals[self.features[i]], self.max_vals[self.features[i]])
            for i in range(len(self.features))
        ]

        sims = []

        for idx, row in self.df.iterrows():
            case_vec = [row[f] for f in self.features]
            case_norm = [
                self._normalize(case_vec[i], self.min_vals[self.features[i]], self.max_vals[self.features[i]])
                for i in range(len(self.features))
            ]
            sim = self._cosine_similarity(q_norm, case_norm)
            sims.append((idx, sim))

        sims.sort(key=lambda x: x[1], reverse=True)
        top_idx = [s[0] for s in sims[:3]]

        df_top = self.df.loc[top_idx].copy()
        df_top["similarity"] = [s[1] for s in sims[:3]]

        return df_top

    # ===========================
    # 2. REUSE
    # ===========================
    def reuse(self, retrieved_cases):
        """Ambil case terbaik dari retrieve."""
        return retrieved_cases.iloc[0]  # best case

    # ===========================
    # 3. REVISE
    # ===========================
    def revise(self, recommended_case, feedback, corrected_case=None):
        """
        Streamlit version:
        - feedback True  → user setuju
        - feedback False → gunakan corrected_case yang diberikan UI
        """
        if feedback:
            return recommended_case
        
        # User memberikan revisi melalui UI
        return corrected_case

    # ===========================
    # 4. RETAIN
    # ===========================
    def retain(self, case):
        """Simpan case baru ke CSV"""
        case["transmisi_enc"] = self._encode(case["transmisi"], self.transmisi_categories, "transmisi")
        case["jenis_enc"] = self._encode(case["jenis"], self.jenis_categories, "jenis")

        self.df = pd.concat([self.df, pd.DataFrame([case])], ignore_index=True)
        self.df.to_csv(self.csv_path, index=False)

    # ===========================
    # CBR MAIN (Streamlit Friendly)
    # ===========================
    def run_cbr(self, query):
        retrieved = self.retrieve(query)
        reused = self.reuse(retrieved)
        return retrieved  # Streamlit akan lihat top 3
