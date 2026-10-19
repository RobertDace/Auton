# Tasks: DocuReport Auto

- [x] Task 1: Setup data models (`src/core/models.py`)
  - Acceptance: Model `ActivityItem`, `DateGroup`, `ReportProject` mendukung serialisasi/deserialisasi JSON draft project
  - Verify: Test unit serialization
  - Files: `src/core/models.py`

- [x] Task 2: Setup Image Processor (`src/core/image_processor.py`)
  - Acceptance: Mampu memuat gambar, menangani EXIF auto-rotate, membuat thumbnail memori cepat, dan menghitung aspect ratio proporsional
  - Verify: Test dengan sampel foto GPS Map Camera asli dari folder `F:\TK Cahaya Hati`
  - Files: `src/core/image_processor.py`

- [x] Task 3: Setup Word Document Generator Engine (`src/core/docx_generator.py`)
  - Acceptance: Menghasilkan file `.docx` Landscape Letter dengan tabel 4 kolom persis (No: 0.95cm, Tanggal: 4.80cm, Keterangan: 6.23cm, Dokumentasi: 11.34cm), skala foto ~7.5cm, dan font Arial 11pt
  - Verify: Jalankan unit test dan inspeksi file `.docx` hasil render
  - Files: `src/core/docx_generator.py`

- [x] Task 4: Setup UI Theme & Styling (`src/gui/theme.py`)
  - Acceptance: Palet warna modern (Slate & Emerald), tipografi, styling konsisten untuk Dark & Light mode
  - Files: `src/gui/theme.py`

- [x] Task 5: Setup GUI Components (`src/gui/components/`)
  - Acceptance:
    - `sidebar.py`: Pemilih direktori, daftar tanggal terdeteksi, ringkasan jumlah foto, tombol Simpan/Buka Draft
    - `photo_grid.py`: Tampilan galeri thumbnail interaktif dengan multi-selection, indikator terpilih, dan quick preview
    - `activity_form.py`: Form entri keterangan dengan preset dropdown cepat, input kustom, dan daftar aktivitas yang tersimpan per tanggal
    - `progress_modal.py`: Modal progress dialog saat Word sedang digenerate
  - Files: `src/gui/components/*.py`

- [x] Task 6: Main GUI Window & Integration (`src/gui/app.py` & `run.py`)
  - Acceptance: Semua komponen terhubung, alur kerja dari pemilihan folder -> penyusunan aktivitas -> ekspor Word berjalan mulus tanpa freeze (multithreading)
  - Verify: Jalankan `python run.py` dan uji seluruh alur kerja
  - Files: `src/gui/app.py`, `run.py`

- [x] Task 7: Setup Build Executable Script (`build_exe.py`)
  - Acceptance: Skrip PyInstaller terkonfigurasi untuk memaketkan aplikasi menjadi `.exe` mandiri
  - Files: `build_exe.py`, `requirements.txt`
