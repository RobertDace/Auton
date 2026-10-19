import os
import threading
from typing import Optional, List
import customtkinter as ctk
from tkinter import filedialog, messagebox

from .theme import Theme
from .components.sidebar import Sidebar
from .components.activity_form import ActivityForm
from .components.photo_grid import PhotoGrid
from .components.progress_modal import ProgressModal

from ..core.models import ReportProject, DateGroup, ActivityItem
from ..core.image_processor import ImageProcessor
from ..core.docx_generator import DocxGenerator

class DocuReportApp(ctk.CTk):
    """Jendela utama aplikasi desktop DocuReport Windows."""
    def __init__(self):
        super().__init__()

        # Inisialisasi Konfigurasi Tampilan
        ctk.set_appearance_mode(Theme.APPEARANCE_MODE)
        ctk.set_default_color_theme(Theme.COLOR_THEME)

        self.title("DocuReport Auto — Generator Laporan Dokumentasi Word (.docx)")
        self.geometry("1280x820")
        self.minsize(1050, 680)
        self.configure(fg_color=Theme.BG_DARK)

        # Inisialisasi Data & Engine
        self.project = ReportProject()
        self.image_processor = ImageProcessor()
        self.active_date_group: Optional[DateGroup] = None

        self._init_layout()

        # Deteksi default jika folder F:\TK Cahaya Hati ada di sistem
        default_sample_dir = r"F:\TK Cahaya Hati\Foto Timestamp Reevitalisasi TK Cahaya Hati 10-12-26"
        if os.path.exists(default_sample_dir):
            self.project.base_folder = default_sample_dir
            self.sidebar.lbl_folder_path.configure(text=default_sample_dir)
            self.sidebar.scan_and_populate_dates(default_sample_dir)

    def _init_layout(self):
        # 1. Sidebar Navigasi di Sebelah Kiri
        self.sidebar = Sidebar(
            self,
            project=self.project,
            on_date_selected=self._on_date_selected,
            on_generate_requested=self._on_generate_requested,
            on_project_changed=self._on_project_changed
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        # 2. Area Konten Utama di Sebelah Kanan
        self.main_container = ctk.CTkFrame(self, fg_color=Theme.BG_DARK, corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        # Top Bar Judul Proyek & Info
        self.top_bar = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, height=52, corner_radius=0)
        self.top_bar.pack(fill="x", padx=0, pady=0)

        self.lbl_project_title = ctk.CTkLabel(
            self.top_bar,
            text="Proyek: Laporan Revitalisasi",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.lbl_project_title.pack(side="left", padx=16, pady=12)

        self.lbl_active_date_badge = ctk.CTkLabel(
            self.top_bar,
            text="Silakan pilih tanggal di sidebar kiri",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_active_date_badge.pack(side="left", padx=10, pady=12)

        # Tombol ganti tema (Dark / Light)
        self.btn_theme_toggle = ctk.CTkButton(
            self.top_bar,
            text="🌓 Mode Tema",
            font=ctk.CTkFont(size=11),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            width=100,
            height=28,
            command=self._toggle_appearance_mode
        )
        self.btn_theme_toggle.pack(side="right", padx=16, pady=12)

        # Kontainer Dua Kolom (Kiri: ActivityForm, Kanan: PhotoGrid)
        self.split_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.split_container.pack(fill="both", expand=True, padx=8, pady=8)

        # Kolom Kiri: Form Manajemen Kegiatan & Preset (~380px)
        self.activity_form = ActivityForm(
            self.split_container,
            on_activity_selected=self._on_activity_selected,
            on_activity_updated=self._on_activity_updated,
            width=390
        )
        self.activity_form.pack(side="left", fill="both", padx=(0, 6), pady=0)
        self.activity_form.pack_propagate(False)

        # Kolom Kanan: Galeri Foto Interaktif (Expand)
        self.photo_grid = PhotoGrid(
            self.split_container,
            image_processor=self.image_processor,
            on_selection_changed=self._on_photo_selection_changed
        )
        self.photo_grid.pack(side="right", fill="both", expand=True, padx=(6, 0), pady=0)

    def _on_date_selected(self, date_group: DateGroup):
        """Dipanggil saat pengguna memilih salah satu tanggal dari sidebar."""
        self.active_date_group = date_group
        self.lbl_active_date_badge.configure(
            text=f"Aktif: {date_group.display_date}",
            text_color=Theme.ACCENT_PRIMARY
        )

        # Muat daftar kegiatan pada tanggal ini ke form
        self.activity_form.load_date_group(date_group)

        # Muat foto-foto yang ada di folder tanggal ini
        photos = self._get_photos_for_date(date_group.date_str)

        # Sinkronkan pilihan foto dengan kegiatan aktif
        active_act = self.activity_form.active_activity
        selected_photos = active_act.photo_paths if active_act else []
        self.photo_grid.load_photos(photos, pre_selected=selected_photos)

    def _get_photos_for_date(self, date_str: str) -> List[str]:
        """Mencari file foto yang sesuai dengan tanggal di dalam folder proyek."""
        if not self.project.base_folder or not os.path.exists(self.project.base_folder):
            return []

        # 1. Cek apakah ada subfolder persis dengan nama date_str (misal: 2026-10-12)
        sub_path = os.path.join(self.project.base_folder, date_str)
        if os.path.isdir(sub_path):
            files = [
                os.path.join(sub_path, f) for f in os.listdir(sub_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]
            files.sort()
            return files

        # 2. Cek apakah foto-foto ada di root folder dengan awalan nama tanggal (misal 20261012_)
        compact_date = date_str.replace("-", "")
        root_files = []
        for f in os.listdir(self.project.base_folder):
            full_p = os.path.join(self.project.base_folder, f)
            if os.path.isfile(full_p) and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                if compact_date in f or date_str in f:
                    root_files.append(full_p)

        if root_files:
            root_files.sort()
            return root_files

        # 3. Fallback: jika hanya ada 1 grup tanggal, muat semua foto di root
        if len(self.project.date_groups) == 1:
            all_root = [
                os.path.join(self.project.base_folder, f) for f in os.listdir(self.project.base_folder)
                if os.path.isfile(os.path.join(self.project.base_folder, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]
            all_root.sort()
            return all_root

        return []

    def _on_activity_selected(self, activity: Optional[ActivityItem]):
        """Dipanggil saat pengguna memilih salah satu kegiatan di list."""
        if not activity:
            self.photo_grid.set_selected_photos([])
            return

        self.photo_grid.set_selected_photos(activity.photo_paths)

    def _on_photo_selection_changed(self, selected_photos: List[str]):
        """Dipanggil saat pengguna mencentang/menghapus pilihan foto di galeri."""
        self.activity_form.update_selected_photos_for_active(selected_photos)
        self.sidebar.refresh_date_list()

    def _on_activity_updated(self):
        """Dipanggil saat kegiatan diperbarui/ditambahkan/dihapus."""
        self.sidebar.refresh_date_list()

    def _on_project_changed(self):
        """Dipanggil saat proyek dimuat dari draft atau folder baru dibuka."""
        self.sidebar.refresh_date_list()

    def _on_generate_requested(self):
        """Alur kerja ekspor dokumen Word laporan dokumentasi."""
        # Validasi
        if not self.project.date_groups:
            messagebox.showwarning("Peringatan", "Belum ada tanggal kegiatan yang dibuat.")
            return

        total_activities = sum(len(dg.activities) for dg in self.project.date_groups)
        if total_activities == 0:
            messagebox.showwarning("Peringatan", "Belum ada baris kegiatan yang ditambahkan pada tanggal mana pun.")
            return

        # Dialog pemilihan lokasi simpan file Word
        default_name = f"Dokumentasi Laporan Revitalisasi {os.path.basename(self.project.base_folder or 'Kegiatan')}.docx"
        output_filepath = filedialog.asksaveasfilename(
            title="Simpan Laporan Word",
            initialfile=default_name,
            defaultextension=".docx",
            filetypes=[("Microsoft Word Document", "*.docx")]
        )
        if not output_filepath:
            return

        # Buka Modal Progress
        modal = ProgressModal(self, title="Menyusun Laporan Word...")

        def export_worker():
            try:
                def progress_cb(cur, total, msg):
                    self.after(0, modal.update_progress, cur, total, msg)

                DocxGenerator.generate_report(
                    project=self.project,
                    output_filepath=output_filepath,
                    progress_callback=progress_cb
                )
                self.after(0, modal.finish_success, output_filepath)
            except Exception as e:
                self.after(0, modal.finish_error, str(e))

        threading.Thread(target=export_worker, daemon=True).start()

    def _toggle_appearance_mode(self):
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
