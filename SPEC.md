# Spesifikasi Teknis: Generator Laporan Dokumentasi Word (DocuReport Windows)

## 1. Objective (Tujuan)
Membangun aplikasi desktop Windows modern (berbasis Python CustomTkinter) yang mengotomatisasi penyusunan laporan dokumentasi kegiatan berfoto ke dalam format Microsoft Word (`.docx`). Format laporan secara presisi mereplikasi dokumen standar instansi/lapangan (`Dokumentasi Laporan Revitalisasi TK Cahaya Hati Oktober.docx`):
- Format Halaman: Landscape (Letter / A4)
- Tabel 4 Kolom:
  1. `No.` (0.95 cm) — Nomor urut per kelompok tanggal
  2. `Tanggal` (4.80 cm) — Format Indonesia (misal: *Senin, 05 Oktober 2026*)
  3. `Keterangan` (6.23 cm) — Uraian kegiatan, sudut foto bangunan, atau daftar peralatan/material
  4. `Dokumentasi` (11.34 cm) — Penempatan foto proporsional (~7.5 cm lebar) yang tersusun rapi tanpa merusak margin tabel.
- Jumlah foto per item kegiatan bersifat fleksibel (1, 2, 4, hingga >10 foto).
- Mendukung fitur Simpan/Buka Draft Proyek (`.json`) sehingga proses entri laporan dapat dicicil dan dilanjutkan kapan saja.

---

## 2. Tech Stack & Dependencies
- **Bahasa**: Python 3.10+ (Terverifikasi di sistem: Python 3.14)
- **GUI Framework**: `customtkinter` (Modern dark/light desktop UI dengan DPI-awareness di Windows)
- **Word Processing**: `python-docx` (Manipulasi dokumen Word, tabel, border, spasi, dan penyisipan gambar `wp:inline`)
- **Image Processing**: `Pillow (PIL)` (Thumbnail generation, pembacaan resolusi, koreksi orientasi EXIF, scaling proporsional)
- **Packaging**: `pyinstaller` (Untuk kompilasi menjadi file eksekusi Windows `.exe` mandiri)

---

## 3. Project Structure
```text
f:\Projectan\AUTON/
├── SPEC.md                      # Dokumen spesifikasi teknis (living document)
├── requirements.txt             # Dependensi Python
├── run.py                       # File eksekusi utama aplikasi
├── build_exe.py                 # Skrip build otomatis PyInstaller ke .exe
├── tasks/
│   ├── plan.md                  # Rencana implementasi modular
│   └── todo.md                  # Checklist progress pengerjaan tugas
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py            # Model data: ActivityItem, DateGroup, ProjectReport
│   │   ├── image_processor.py   # Resize proporsional, EXIF orientation fix, thumbnail cache
│   │   └── docx_generator.py    # Mesin penyusun tabel Word & penyisipan foto presisi
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app.py               # Main Window CustomTkinter
│   │   ├── theme.py             # Definisi warna, font, dan style komponen
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── sidebar.py       # Pemilih folder, daftar tanggal, dan manajemen draft
│   │       ├── photo_grid.py    # Galeri visual thumbnail foto dengan multiselect
│   │       ├── activity_form.py # Input keterangan dengan preset dropdown cepat
│   │       └── progress_modal.py# Modal progres ekspor Word dengan indikator visual
└── tests/
    ├── __init__.py
    ├── test_image_processor.py  # Unit test pemrosesan gambar
    └── test_docx_generator.py   # Unit test pembuatan tabel Word dan skala foto
```

---

## 4. Commands
- **Menjalankan Aplikasi**:
  `python run.py`
- **Menjalankan Unit Test**:
  `python -m unittest discover tests`
- **Kompilasi Standalone .exe Windows**:
  `python build_exe.py`

---

## 5. Aturan Tata Letak & Skala Dokumen Word (Spesifikasi Presisi)
1. **Orientasi**: Landscape (`w:orient="landscape"`), Margin Kiri/Kanan: 2.0 cm, Atas/Bawah: 2.0 cm.
2. **Lebar Kolom**:
   - Kolom 1 (`No.`): 540 dxa (~0.95 cm)
   - Kolom 2 (`Tanggal`): 2720 dxa (~4.80 cm)
   - Kolom 3 (`Keterangan`): 3530 dxa (~6.23 cm)
   - Kolom 4 (`Dokumentasi`): 6430 dxa (~11.34 cm)
3. **Penyisipan Foto**:
   - Setiap foto diskalakan ke lebar maksimum 7.5 cm (menjaga rasio aspek asli, tinggi menyesuaikan otomatis).
   - Foto diletakkan di dalam paragraf sel kolom Dokumentasi dengan perataan tengah (*center alignment*).
   - Jarak antar foto dalam satu kegiatan diatur dengan spasi paragraf rapi (spacing after: 6pt - 10pt).
4. **Tipografi Dokumen**:
   - Font Family: `Arial`
   - Ukuran Font: `11 pt`
   - Header Tabel: Huruf Tebal (*Bold*), rata tengah (*center*).
   - Isi Kolom Tanggal: Hari, DD Bulan YYYY (Bahasa Indonesia).

---

## 6. Fitur Unggulan Antarmuka (UI/UX Ergonomics)
1. **Deteksi Tanggal Otomatis**: Mendeteksi subfolder tanggal (seperti `2026-10-12`) atau tanggal dari metadata timestamp foto.
2. **Katalog Keterangan Cepat (Preset)**:
   - *Foto Bangunan Tampak Depan*
   - *Foto Bangunan Tampak Samping Kiri Depan*
   - *Foto Bangunan Tampak Samping Kanan Depan*
   - *Foto Bangunan Tampak Samping Kanan*
   - *Foto Bangunan Tampak Samping Kiri*
   - *Foto Bangunan Tampak Belakang*
   - *Foto Bangunan Tampak Pojok Belakang Kiri*
   - *Foto Bangunan Tampak Pojok Belakang Kanan*
   - *Foto Peralatan yang Dibeli:* (dengan template daftar)
   - *Foto Material yang Dibeli:* (dengan template daftar)
   - *Kustom Bebas*
3. **Galeri Thumbnail Interaktif**: Thumbnail berukuran responsif, ada badge tanda centang jika foto terpilih, dan klik ganda untuk pratinjau zoom.
4. **Multithreaded Export**: Proses rendering Word berjalan di *background worker thread* dengan progress bar animasi sehingga aplikasi tidak pernah freeze / Not Responding.

---

## 7. Boundaries (Batasan)
- **Selalu lakukan**:
  - Validasi keberadaan file gambar sebelum dimasukkan ke Word.
  - Periksa orientasi EXIF kamera ponsel (agar foto tidak terbalik/miring).
  - Berikan notifikasi sukses beserta tombol langsung untuk *"Buka File Word"* dan *"Buka Folder"*.
- **Tanya dulu**:
  - Jika pengguna ingin menimpa file Word yang sedang terbuka di aplikasi Microsoft Word lain.
- **Jangan pernah**:
  - Mengubah, memindahkan, atau menghapus file foto asli milik pengguna.
  - Mengunci antarmuka (freeze) saat memproses file gambar berukuran besar.

---

## 8. Success Criteria (Kriteria Keberhasilan)
1. [x] Aplikasi dapat dibuka langsung di Windows via `python run.py`.
2. [x] Mampu membaca folder foto (misal: `F:\TK Cahaya Hati\Foto Timestamp Reevitalisasi TK Cahaya Hati 10-12-26`).
3. [x] Menampilkan thumbnail visual foto dengan cepat dan mulus.
4. [x] Memungkinkan pengguna membuat baris kegiatan, memilih preset/custom keterangan, dan memilih foto (1 hingga puluhan foto).
5. [x] Menghasilkan file `.docx` dengan tabel 4 kolom, skala foto proporsional ~7.5 cm, orientasi Landscape, dan font Arial 11pt yang identik dengan dokumen contoh.
6. [x] Fitur Simpan & Buka Draft Proyek (`.json`) bekerja 100% tanpa ada data yang hilang.
7. [x] Tersedia skrip build PyInstaller untuk membuat file `.exe` mandiri.
