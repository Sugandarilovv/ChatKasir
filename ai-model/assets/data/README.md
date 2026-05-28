# Data Assets

Folder ini digunakan untuk menyimpan dataset biner (.npz) dan model_config.json

Karena batasan ukuran file GitHub (maksimal 100MB), file dataset utama **tidak diikutsertakan** dalam repositori ini.

## Cara Mengunduh Dataset dan Config JSON
Bagi anggota tim yang baru melakukan *clone* repositori ini, silakan ikuti langkah berikut agar notebook training dan evaluation bisa berjalan:

1. Unduh file `dataset_chatkasir.npz` melalui link Google Drive berikut:
   **https://drive.google.com/file/d/1sqU62MGvUpYnkj6nJpsvj6wwNrLc-1dD/view?usp=sharing**
2. Unduh file `model_config.json` melalui link Google Drive berikut:
   **https://drive.google.com/file/d/1szcbYKU0TE6DtG6jvxWAXiU3svjjPIfY/view?usp=sharing**
3. Pindahkan file yang sudah diunduh tersebut ke dalam folder berikut (`ai-model/assets/data/`).
4. Pastikan nama file tidak berubah (`dataset_chatkasir.npz`) dan (`model_config.json`)

---
*Catatan: File ini sudah dimasukkan ke dalam `.gitignore`, sehingga perubahan atau penambahan dataset lokal di komputer Anda tidak akan ter-push ke GitHub.*