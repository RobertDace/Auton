# DocuReport Auto — Generator Laporan Dokumentasi Kegiatan ke Word (.docx)

Aplikasi desktop Windows modern berbasis Python (CustomTkinter) untuk mengotomatisasi penyusunan laporan dokumentasi kegiatan berfoto ke dalam format Microsoft Word (`.docx`).

Tampilan dan struktur dokumen yang dihasilkan **100% identik dan presisi** sesuai format standar instansi/proyek lapangan:
- **Orientasi**: Landscape (Letter / A4)
- **Tabel 4 Kolom**:
  1. `No.` (0.95 cm) — Nomor urut kegiatan per tanggal (1, 2, 3...)
  2. `Tanggal` (4.80 cm) — Format tanggal Indonesia (`Senin, 12 Oktober 2026`)
  3. `Keterangan` (6.23 cm) — Uraian kegiatan, sudut foto bangunan, atau rincian material/peralatan
  4. `Dokumentasi` (11.34 cm) — Foto diskalakan proporsional (~7.5 cm) dan terpusat rapi tanpa merusak tabel.

---

## Fitur Utama

1. **Pemindaian Folder Otomatis**:
   - Mendeteksi subfolder tanggal (seperti `2026-10-12`, `2026-10-13`, dst.).
   - Menghitung jumlah foto per tanggal secara otomatis.

2. **Galeri Thumbnail Interaktif**:
   - Thumbnail foto dimuat di *background thread* sehingga antarmuka tetap ringan dan responsif (60fps).
   - Klik kartu foto untuk memilih/melampirkan foto ke kegiatan yang aktif.
   - Klik dua kali (*Double click*) pada foto untuk membuka pratinjau zoom resolusi penuh.
   - Tombol *Pilih Semua* dan *Reset Pilihan* untuk kemudahan seleksi foto dalam jumlah banyak.

3. **Manajemen Baris Kegiatan Cepat**:
   - Dropdown **Preset Keterangan Cepat**:
     - *Foto Bangunan Tampak Depan*
     - *Foto Bangunan Tampak Samping Kanan / Kiri*
     - *Foto Bangunan Tampak Belakang*
     - *Foto Material yang Dibeli :* (Otomatis menyisipkan daftar semen, bata, besi, dll.)
     - *Foto Peralatan yang Dibeli :* (Otomatis menyisipkan daftar gerobak, cangkul, dll.)
   - Dukungan teks kustom multibaris (*multiline*).
   - Tambah, edit, dan hapus baris kegiatan per tanggal.
   - Fleksibel melampirkan 1, 2, 4, hingga >10 foto per kegiatan.

4. **Simpan & Buka Draft Proyek (`.json`)**:
   - Pekerjaan laporan yang belum selesai dapat disimpan sebagai file draft (`.json`) dan dibuka kembali sewaktu-waktu tanpa kehilangan progres pemilihan foto.

5. **Ekspor Word Asinkron (Multithreaded)**:
   - Dilengkapi *Progress Modal* dengan persentase dan nama file foto yang sedang diproses.
   - Tombol langsung untuk *"Buka File Word"* dan *"Buka Folder"* begitu ekspor selesai.

---

## Cara Menjalankan

### 1. Menjalankan Langsung via Python
Pastikan dependensi terpasang:
```bash
pip install -r requirements.txt
```
Jalankan aplikasi:
```bash
python run.py
```

### 2. Menjalankan Pengujian Otomatis (Unit & E2E Test)
```bash
python -m unittest tests/test_docx_generator.py
python -m unittest tests/test_e2e_workflow.py
```

### 3. Kompilasi Menjadi File `.exe` Mandiri Windows
Untuk membuat file eksekusi `.exe` yang bisa dibuka di komputer mana pun tanpa perlu install Python:
```bash
python build_exe.py
```
File `.exe` akan dihasilkan di dalam folder `dist/DocuReport_Auto/DocuReport_Auto.exe`.
