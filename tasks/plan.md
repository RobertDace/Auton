# Plan: DocuReport Auto (Windows Application)

## 1. Arsitektur Komponen
1. **`core.models`**:
   - `ActivityItem`: id, description, photo_paths (list of str), date_str, custom_notes
   - `DateGroup`: date_str (ISO YYYY-MM-DD), display_date (Senin, 12 Oktober 2026), activities (list of ActivityItem)
   - `ReportProject`: project_name, base_folder, date_groups (list of DateGroup), output_path, created_at, updated_at
2. **`core.image_processor`**:
   - `fix_orientation(image)`: Koreksi rotasi EXIF smartphone
   - `create_thumbnail(image_path, size=(160, 120))`: Generator thumbnail cepat dengan cache memori/temp
   - `get_scaled_dimensions(image_path, target_width_cm=7.5)`: Hitung proporsi lebar x tinggi
3. **`core.docx_generator`**:
   - `generate_report(project: ReportProject, output_path: str, progress_callback=None)`:
     - Buat dokumen Word berorientasi Landscape Letter
     - Setup tabel 4 kolom dengan lebar presisi (0.95cm, 4.80cm, 6.23cm, 11.34cm)
     - Sisipkan header tabel: No., Tanggal, Keterangan, Dokumentasi (Arial 11pt Bold, center)
     - Iterasi setiap tanggal & kegiatan:
       - No. diincrement per tanggal
       - Tanggal dicetak pada baris pertama tanggal bersangkutan
       - Keterangan dicetak dengan teks rapi
       - Dokumentasi disisipkan foto proporsional (~7.5 cm) dengan spasi rapi
     - Simpan file `.docx` dan kembalikan status sukses
4. **`gui.theme`**:
   - Palet warna modern (Slate dark/light, Emerald accents, border halus)
   - Font family dan sizing
5. **`gui.components`**:
   - `Sidebar`: Folder browser, Date list, Proyek status, Save/Load project
   - `ActivityForm`: Preset selector, custom text, add/update/delete activity
   - `PhotoGrid`: Visual multi-select photo thumbnails dengan badge pilihan & click preview
   - `ProgressModal`: Dialog proses pembuatan dokumen Word
6. **`run.py` & `build_exe.py`**:
   - Entrypoint & skrip pembuatan bundle `.exe`

## 2. Urutan Pengerjaan (Build Order)
1. **Fase 1**: Data Model & Core Engines (`models.py`, `image_processor.py`, `docx_generator.py`)
2. **Fase 2**: Unit Testing & Validasi Dokumen Word terhadap contoh asli
3. **Fase 3**: GUI Architecture (CustomTkinter Main Window, Theme, Sidebar, Activity Form, Photo Grid)
4. **Fase 4**: Integrasi End-to-End & Background Threading (Export Word + Progress Bar)
5. **Fase 5**: Build Executable (`build_exe.py`) & Pengujian Langsung di Windows
