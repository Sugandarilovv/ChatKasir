# Menggunakan image dasar Python 3.10 yang ringan
FROM python:3.10-slim

# Menentukan direktori kerja di dalam container
WORKDIR /code

# Menyalin file requirements.txt ke dalam container
COPY requirements.txt .

# Menginstal semua library yang dibutuhkan
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh file project kita ke dalam container
COPY . .

# Menyesuaikan path agar folder data berada di dalam direktori kerja (/code)
# Ini penting karena aplikasi kita akan mendownload file dari Google Drive
ENV SLANG_DICT_PATH="data/final/slang_utama.csv"

# Membuat folder untuk tempat menyimpan model, kamus slang, dan CACHE untuk gdown
RUN mkdir -p models data/final /.cache

# Hugging Face Spaces secara default menggunakan user dengan ID 1000.
# Kita perlu memberikan hak akses agar aplikasi bisa menyimpan file download & cache.
RUN chown -R 1000:1000 /code /.cache

# Beralih menggunakan user ID 1000 untuk alasan keamanan
USER 1000

# Menjalankan server FastAPI menggunakan Uvicorn di port 7860 (standar Hugging Face)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]