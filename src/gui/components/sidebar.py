import os
import re
from typing import List, Optional, Callable
import customtkinter as ctk
from tkinter import filedialog, messagebox

from ..theme import Theme
from ...core.models import ReportProject, DateGroup, format_indonesian_date

class Sidebar(ctk.CTkFrame):
    """Sidebar navigasi utama:

    - Pemilihan folder foto proyek
    - Deteksi subfolder tanggal otomatis (misal: 2026-10-12)
    - Navigasi daftar tanggal kegiatan
    - Simpan / Buka Draft Proyek (.json)
    - Tombol utama 'Generate Laporan Word (.docx)'
    """
    def __init__(
        self,
        master,
        project: ReportProject,
        on_date_selected: Optional[Callable[[DateGroup], None]] = None,
        on_generate_requested: Optional[Callable[[], None]] = None,
        on_project_changed: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            width=280,
            corner_radius=0,
            fg_color=Theme.BG_SIDEBAR,
            **kwargs
        )
        self.project = project
        self.on_date_selected = on_date_selected
        self.on_generate_requested = on_generate_requested
        self.on_project_changed = on_project_changed

        self.date_buttons = {}
        self.active_date_str: Optional[str] = None

        self._init_ui()

    def _init_ui(self):
        # 1. App Brand Header
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(18, 12))

        lbl_logo = ctk.CTkLabel(
            brand_frame,
            text="📑 DOCUREPORT",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        lbl_logo.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            brand_frame,
            text="Generator Laporan Dokumentasi Word",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=Theme.TEXT_MUTED
        )
        lbl_sub.pack(anchor="w")

        # 2. Folder Picker
        folder_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=8)
        folder_frame.pack(fill="x", padx=14, pady=6)

        lbl_fld = ctk.CTkLabel(
            folder_frame,
            text="Folder Foto Proyek:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        lbl_fld.pack(anchor="w", padx=12, pady=(10, 4))

        self.lbl_folder_path = ctk.CTkLabel(
            folder_frame,
            text="Belum memilih folder",
            font=ctk.CTkFont(size=10),
            text_color=Theme.TEXT_MUTED,
            wraplength=230,
            justify="left"
        )
        self.lbl_folder_path.pack(anchor="w", padx=12, pady=(0, 8))

        self.btn_browse = ctk.CTkButton(
            folder_frame,
            text="📂 Pilih Folder Foto",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            height=30,
            command=self.browse_folder
        )
        self.btn_browse.pack(fill="x", padx=12, pady=(0, 10))

        # 3. Daftar Tanggal Kegiatan (Scrollable)
        date_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_header_frame.pack(fill="x", padx=16, pady=(12, 4))

        lbl_dates = ctk.CTkLabel(
            date_header_frame,
            text="Daftar Tanggal:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        lbl_dates.pack(side="left")

        self.btn_add_date = ctk.CTkButton(
            date_header_frame,
            text="+ Tanggal",
            font=ctk.CTkFont(size=10),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            width=65,
            height=22,
            command=self.add_manual_date_dialog
        )
        self.btn_add_date.pack(side="right")

        self.dates_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=6
        )
        self.dates_scroll.pack(fill="both", expand=True, padx=10, pady=4)

        # 4. Panel Bawah (Simpan/Buka Draft & Generate Word)
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", side="bottom", padx=14, pady=16)

        draft_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        draft_frame.pack(fill="x", pady=(0, 8))

        self.btn_save_draft = ctk.CTkButton(
            draft_frame,
            text="💾 Simpan Draft",
            font=ctk.CTkFont(size=11),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            height=28,
            command=self.save_draft_dialog
        )
        self.btn_save_draft.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_load_draft = ctk.CTkButton(
            draft_frame,
            text="📂 Buka Draft",
            font=ctk.CTkFont(size=11),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            height=28,
            command=self.load_draft_dialog
        )
        self.btn_load_draft.pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Tombol Utama Ekspor Word
        self.btn_generate = ctk.CTkButton(
            bottom_frame,
            text="📄 GENERATE LAPORAN WORD",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Theme.ACCENT_SUCCESS,
            hover_color=Theme.ACCENT_SUCCESS_HOVER,
            height=42,
            corner_radius=8,
            command=self._on_generate_clicked
        )
        self.btn_generate.pack(fill="x", pady=(4, 0))

    def browse_folder(self):
        """Membuka dialog pemilih folder dan memindai subfolder tanggal."""
        initial_dir = self.project.base_folder if os.path.exists(self.project.base_folder) else "F:\\"
        folder = filedialog.askdirectory(title="Pilih Folder Berisi Foto Tanggal", initialdir=initial_dir)
        if not folder:
            return

        self.project.base_folder = folder
        self.lbl_folder_path.configure(text=folder)

        # Pindai subfolder berformat tanggal YYYY-MM-DD
        self.scan_and_populate_dates(folder)

        if self.on_project_changed:
            self.on_project_changed()

    def scan_and_populate_dates(self, base_folder: str):
        """Memindai subfolder di dalam base_folder yang cocok dengan pola tanggal."""
        try:
            subdirs = [
                d for d in os.listdir(base_folder)
                if os.path.isdir(os.path.join(base_folder, d))
            ]
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca direktori: {e}")
            return

        # Pola tanggal YYYY-MM-DD
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        detected_dates = [d for d in subdirs if date_pattern.match(d)]
        detected_dates.sort()

        if detected_dates:
            # Masukkan ke project jika belum ada
            for d in detected_dates:
                self.project.get_or_create_date_group(d)
        else:
            # Jika tidak ada subfolder tanggal, periksa apakah di root ada foto
            root_photos = [
                f for f in os.listdir(base_folder)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]
            if root_photos and not self.project.date_groups:
                # Buat grup tanggal default hari ini
                from datetime import date
                today_str = date.today().strftime("%Y-%m-%d")
                self.project.get_or_create_date_group(today_str)

        self.refresh_date_list()

        # Pilih tanggal pertama secara default
        if self.project.date_groups:
            self.select_date(self.project.date_groups[0].date_str)

    def refresh_date_list(self):
        """Merender ulang daftar tombol tanggal di sidebar."""
        for w in self.dates_scroll.winfo_children():
            w.destroy()
        self.date_buttons.clear()

        if not self.project.date_groups:
            empty_lbl = ctk.CTkLabel(
                self.dates_scroll,
                text="Belum ada tanggal terdeteksi.",
                font=ctk.CTkFont(size=11),
                text_color=Theme.TEXT_MUTED
            )
            empty_lbl.pack(pady=10)
            return

        for dg in self.project.date_groups:
            is_active = (self.active_date_str == dg.date_str)
            item_frame = ctk.CTkFrame(
                self.dates_scroll,
                fg_color="#1e3a5f" if is_active else Theme.BG_CARD,
                border_width=1,
                border_color=Theme.ACCENT_PRIMARY if is_active else Theme.BORDER_COLOR,
                corner_radius=6,
                height=38
            )
            item_frame.pack(fill="x", padx=2, pady=3)

            # Hitung total foto yang dilampirkan di grup tanggal ini
            total_attached = sum(len(a.photo_paths) for a in dg.activities)

            btn = ctk.CTkButton(
                item_frame,
                text=dg.display_date,
                anchor="w",
                font=ctk.CTkFont(size=11, weight="bold" if is_active else "normal"),
                fg_color="transparent",
                hover_color=Theme.BORDER_LIGHT,
                text_color=Theme.TEXT_PRIMARY,
                height=32,
                command=lambda d=dg.date_str: self.select_date(d)
            )
            btn.pack(side="left", fill="x", expand=True, padx=6)

            badge = ctk.CTkLabel(
                item_frame,
                text=f"{total_attached} Foto",
                font=ctk.CTkFont(size=10),
                text_color=Theme.ACCENT_SUCCESS if total_attached > 0 else Theme.TEXT_MUTED,
                width=50
            )
            badge.pack(side="right", padx=6)

            self.date_buttons[dg.date_str] = item_frame

    def select_date(self, date_str: str):
        """Mengaktifkan tanggal tertentu."""
        self.active_date_str = date_str
        self.refresh_date_list()

        group = next((dg for dg in self.project.date_groups if dg.date_str == date_str), None)
        if group and self.on_date_selected:
            self.on_date_selected(group)

    def add_manual_date_dialog(self):
        """Dialog untuk menambahkan tanggal secara manual (format YYYY-MM-DD)."""
        dialog = ctk.CTkInputDialog(
            text="Masukkan Tanggal Kegiatan (Format: YYYY-MM-DD, contoh: 2026-10-17):",
            title="Tambah Tanggal Kegiatan"
        )
        val = dialog.get_input()
        if not val:
            return

        val = val.strip()
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not date_pattern.match(val):
            messagebox.showwarning("Format Salah", "Gunakan format tanggal YYYY-MM-DD (contoh: 2026-10-17)")
            return

        self.project.get_or_create_date_group(val)
        self.refresh_date_list()
        self.select_date(val)
        if self.on_project_changed:
            self.on_project_changed()

    def save_draft_dialog(self):
        """Menyimpan draft proyek ke file JSON."""
        filepath = filedialog.asksaveasfilename(
            title="Simpan Draft Proyek Laporan",
            defaultextension=".json",
            filetypes=[("JSON Draft Proyek", "*.json")]
        )
        if not filepath:
            return

        try:
            self.project.save_to_json(filepath)
            messagebox.showinfo("Sukses", f"Draft proyek berhasil disimpan ke:\n{os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Gagal Simpan", f"Terjadi kesalahan saat menyimpan draft: {e}")

    def load_draft_dialog(self):
        """Memuat draft proyek dari file JSON."""
        filepath = filedialog.askopenfilename(
            title="Buka Draft Proyek Laporan",
            filetypes=[("JSON Draft Proyek", "*.json")]
        )
        if not filepath:
            return

        try:
            loaded_proj = ReportProject.load_from_json(filepath)
            # Update atribut proyek aktif
            self.project.project_name = loaded_proj.project_name
            self.project.base_folder = loaded_proj.base_folder
            self.project.date_groups = loaded_proj.date_groups
            self.project.photo_width_cm = loaded_proj.photo_width_cm

            self.lbl_folder_path.configure(text=self.project.base_folder or "Belum memilih folder")
            self.refresh_date_list()

            if self.project.date_groups:
                self.select_date(self.project.date_groups[0].date_str)

            if self.on_project_changed:
                self.on_project_changed()

            messagebox.showinfo("Sukses", f"Draft proyek berhasil dimuat: {len(self.project.date_groups)} tanggal kegiatan.")
        except Exception as e:
            messagebox.showerror("Gagal Membuka", f"Gagal membaca file draft: {e}")

    def _on_generate_clicked(self):
        if self.on_generate_requested:
            self.on_generate_requested()
