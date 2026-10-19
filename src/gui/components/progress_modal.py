import os
import subprocess
import customtkinter as ctk
from typing import Optional
from ..theme import Theme

class ProgressModal(ctk.CTkToplevel):
    """Dialog progres saat proses ekspor laporan Word berlangsung."""
    def __init__(self, parent, title="Menyusun Dokumen Word..."):
        super().__init__(parent)
        self.title(title)
        self.geometry("520x260")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set() # Modal behavior

        self.doc_path: Optional[str] = None

        self._init_ui()

    def _init_ui(self):
        self.lbl_title = ctk.CTkLabel(
            self,
            text="Sedang Menyusun Laporan Word...",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.lbl_title.pack(pady=(24, 10))

        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=440,
            height=14,
            corner_radius=7,
            progress_color=Theme.ACCENT_PRIMARY
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(
            self,
            text="Menginisialisasi tabel dan format dokumen...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Theme.TEXT_SECONDARY,
            wraplength=460
        )
        self.lbl_status.pack(pady=6)

        # Container Tombol Aksi Selesai (awalnya tersembunyi/disabled)
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", side="bottom", padx=20, pady=20)

        self.btn_open_file = ctk.CTkButton(
            self.action_frame,
            text="📄 Buka File Word",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Theme.ACCENT_SUCCESS,
            hover_color=Theme.ACCENT_SUCCESS_HOVER,
            command=self._open_file,
            state="disabled"
        )
        self.btn_open_file.pack(side="left", fill="x", expand=True, padx=4)

        self.btn_open_folder = ctk.CTkButton(
            self.action_frame,
            text="📁 Buka Folder",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            command=self._open_folder,
            state="disabled"
        )
        self.btn_open_folder.pack(side="left", fill="x", expand=True, padx=4)

        self.btn_close = ctk.CTkButton(
            self.action_frame,
            text="Tutup",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            command=self.destroy,
            width=80,
            state="disabled"
        )
        self.btn_close.pack(side="right", padx=4)

    def update_progress(self, current: int, total: int, message: str):
        """Memperbarui nilai progress bar dan teks status."""
        ratio = current / max(total, 1)
        self.progress_bar.set(ratio)
        self.lbl_status.configure(text=message)

    def finish_success(self, doc_path: str):
        """Menampilkan status sukses dan mengaktifkan tombol buka file."""
        self.doc_path = doc_path
        self.progress_bar.set(1.0)
        self.progress_bar.configure(progress_color=Theme.ACCENT_SUCCESS)
        self.lbl_title.configure(text="✓ Laporan Word Berhasil Dibuat!", text_color=Theme.ACCENT_SUCCESS)
        self.lbl_status.configure(text=f"Tersimpan di: {os.path.basename(doc_path)}")

        self.btn_open_file.configure(state="normal")
        self.btn_open_folder.configure(state="normal")
        self.btn_close.configure(state="normal")

    def finish_error(self, err_message: str):
        """Menampilkan status gagal jika terjadi exception."""
        self.progress_bar.configure(progress_color=Theme.ACCENT_DANGER)
        self.lbl_title.configure(text="⚠ Gagal Menyusun Dokumen", text_color=Theme.ACCENT_DANGER)
        self.lbl_status.configure(text=f"Terjadi kesalahan: {err_message}", text_color=Theme.ACCENT_DANGER)
        self.btn_close.configure(state="normal")

    def _open_file(self):
        if self.doc_path and os.path.exists(self.doc_path):
            try:
                os.startfile(self.doc_path)
            except Exception as e:
                print(f"Gagal membuka file: {e}")

    def _open_folder(self):
        if self.doc_path and os.path.exists(self.doc_path):
            folder = os.path.dirname(os.path.abspath(self.doc_path))
            try:
                subprocess.Popen(f'explorer "{folder}"')
            except Exception as e:
                print(f"Gagal membuka folder: {e}")
