# AI-1 Model Architect — Achmad Rifan

Bagian ini berisi seluruh pekerjaan **AI-1 (Model Architect)**: perancangan arsitektur, pipeline pelatihan, dan evaluasi model Deep Learning NLP yang menjadi inti dari aplikasi ChatKasir.

---

## Tools & Environment

### Bahasa & Runtime

| Tool   | Versi    | Keterangan                                         |
| ------ | -------- | -------------------------------------------------- |
| Python | `>=3.12` | Versi runtime yang digunakan                       |
| uv     | Latest   | Package & environment manager pengganti pip + venv |

### Dependencies

| Library      | Versi      | Kegunaan                                                            |
| ------------ | ---------- | ------------------------------------------------------------------- |
| TensorFlow   | `>=2.21.0` | Framework utama untuk membangun dan melatih model Deep Learning NLP |
| NumPy        | `>=2.4.4`  | Operasi numerik dalam pipeline data dan preprocessing               |
| Pandas       | `>=3.0.2`  | Manipulasi dan loading dataset dari DS-1                            |
| scikit-learn | `>=1.8.0`  | Evaluasi model: precision, recall, dan F1-score per entitas         |
| Jupyter      | `>=1.1.1`  | Lingkungan eksplorasi dan dokumentasi proses eksperimen             |
| ipykernel    | `>=7.2.0`  | Menghubungkan environment uv ke kernel Jupyter di VS Code           |

### Cara Setup Environment

```bash
# Clone repo dan masuk ke folder ini
cd ai-model

# uv otomatis membaca pyproject.toml dan menginstall semua dependencies
uv sync

# Daftarkan kernel ke Jupyter / VS Code
uv run python -m ipykernel install --user --name chatkasir-ai --display-name "ChatKasir AI (uv)"
```

Setelah itu, buka file `.ipynb` di VS Code dan pilih kernel **"ChatKasir AI (uv)"** di pojok kanan atas.

---

## Struktur Folder & File

```
ai-model/
├── notebooks/
│   ├── 01_model_architecture.ipynb
│   ├── 02_training.ipynb
│   └── 03_evaluation.ipynb
├── src/
│   └── model.py
├── logs/
├── pyproject.toml
├── uv.lock
├── .python-version
└── README.md
```

### `notebooks/`

Berisi seluruh proses eksperimen dalam format Jupyter Notebook. Diberi nomor urut agar alur kerja mudah diikuti.

| File                          | Keterangan                                                                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `01_model_architecture.ipynb` | Perancangan dan verifikasi arsitektur model. Mencakup eksplorasi awal dataset dari DS-1, definisi hyperparameter, dan `model.summary()`     |
| `02_training.ipynb`           | Pipeline pelatihan end-to-end: data loading, tokenisasi, padding, konfigurasi optimizer, dan iterasi eksperimen hingga akurasi ≥85%         |
| `03_evaluation.ipynb`         | Evaluasi model final pada test set: tabel metrik precision, recall, F1-score per entitas (product, quantity, price), dan analisis kesalahan |

### `src/`

Berisi kode Python bersih yang diekspor dari notebook setelah model final. Digunakan oleh **AI-2 API & Inference** untuk diintegrasikan ke dalam FastAPI.

| File       | Keterangan                                                                                                     |
| ---------- | -------------------------------------------------------------------------------------------------------------- |
| `model.py` | Definisi fungsi `build_model()` yang dapat diimport sebagai modul. Dibuat di Minggu 4 setelah arsitektur final |

### `logs/`

Berisi log TensorBoard yang dihasilkan selama proses pelatihan. Diisi mulai Minggu 4 saat training final dijalankan.

```bash
# Cara menjalankan TensorBoard
uv run tensorboard --logdir logs/
```

### File Konfigurasi

| File              | Keterangan                                                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `pyproject.toml`  | Daftar dependencies dan konfigurasi project yang dikelola oleh `uv`                                                         |
| `uv.lock`         | Lockfile otomatis dari `uv` — memastikan semua anggota tim menginstall versi library yang identik. **Jangan diedit manual** |
| `.python-version` | Menentukan versi Python yang digunakan `uv` di folder ini secara otomatis                                                   |
| `README.md`       | Dokumentasi ini                                                                                                             |

---

## Catatan untuk Anggota Tim Lain

- **DS-1 Data Engineer:** Dataset final yang sudah dibersihkan diletakkan di folder `data/` pada root repo. Format yang diharapkan dan spesifikasi kolom dikonfirmasi bersama di Weekly Sync Minggu 1.
- **AI-2 API & Inference:** File model final (`.keras` atau `SavedModel`) diupload ke Google Drive. Link download publik dicantumkan di README root repo. Script load model tersedia di `src/model.py`.
