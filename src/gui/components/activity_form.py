import customtkinter as ctk
from typing import List, Optional, Callable
from ..theme import Theme
from ...core.models import ActivityItem, DateGroup

class ActivityForm(ctk.CTkFrame):
    """Panel manajemen entri kegiatan untuk tanggal yang sedang aktif:

    - Daftar kegiatan yang sudah dibuat pada tanggal tersebut
    - Pemilihan preset keterangan cepat (Tampak Depan, Material, dll.)
    - Textbox input kustom dengan multi-line support
    - Pengurutan (Move Up / Down) dan hapus kegiatan
    """
    def __init__(
        self,
        master,
        on_activity_selected: Optional[Callable[[Optional[ActivityItem]], None]] = None,
        on_activity_updated: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_CARD, corner_radius=8, **kwargs)
        self.on_activity_selected = on_activity_selected
        self.on_activity_updated = on_activity_updated

        self.current_date_group: Optional[DateGroup] = None
        self.active_activity: Optional[ActivityItem] = None

        self._init_ui()

    def _init_ui(self):
        # 1. Header Tanggal Aktif
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=14, pady=(12, 6))

        self.lbl_date_title = ctk.CTkLabel(
            header_frame,
            text="Kegiatan: (Belum memilih tanggal)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.lbl_date_title.pack(side="left")

        self.btn_add_activity = ctk.CTkButton(
            header_frame,
            text="+ Tambah Kegiatan",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            width=130,
            height=28,
            command=self.create_new_activity
        )
        self.btn_add_activity.pack(side="right")

        # 2. Daftar Kegiatan yang Sudah Ada (Scrollable)
        lbl_list = ctk.CTkLabel(
            self,
            text="Daftar Baris Kegiatan pada Tanggal Ini:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        lbl_list.pack(anchor="w", padx=14, pady=(6, 2))

        self.list_container = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.BG_DARK,
            corner_radius=6,
            height=140
        )
        self.list_container.pack(fill="x", padx=14, pady=4)

        # 3. Form Editor Keterangan
        editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        editor_frame.pack(fill="both", expand=True, padx=14, pady=(8, 12))

        lbl_edit_title = ctk.CTkLabel(
            editor_frame,
            text="Keterangan Kegiatan Terpilih:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        lbl_edit_title.pack(anchor="w", pady=(2, 4))

        # Preset Dropdown
        preset_frame = ctk.CTkFrame(editor_frame, fg_color="transparent")
        preset_frame.pack(fill="x", pady=2)

        preset_lbl = ctk.CTkLabel(
            preset_frame,
            text="Pilih Template Cepat:",
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED
        )
        preset_lbl.pack(side="left", padx=(0, 8))

        self.combo_presets = ctk.CTkComboBox(
            preset_frame,
            values=["-- Pilih Preset Keterangan --"] + Theme.PRESETS_KETERANGAN,
            command=self._on_preset_chosen,
            width=260,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.combo_presets.pack(side="left", fill="x", expand=True)

        # Textbox Keterangan
        self.txt_description = ctk.CTkTextbox(
            editor_frame,
            height=90,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            corner_radius=6
        )
        self.txt_description.pack(fill="both", expand=True, pady=6)
        self.txt_description.bind("<KeyRelease>", lambda e: self._on_text_changed())

        # Tombol Aksi Bawah
        action_bar = ctk.CTkFrame(editor_frame, fg_color="transparent")
        action_bar.pack(fill="x", pady=(4, 0))

        self.lbl_photo_status = ctk.CTkLabel(
            action_bar,
            text="0 Foto Dilampirkan",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Theme.ACCENT_SUCCESS
        )
        self.lbl_photo_status.pack(side="left")

        self.btn_delete = ctk.CTkButton(
            action_bar,
            text="Hapus Kegiatan",
            font=ctk.CTkFont(size=11),
            fg_color=Theme.ACCENT_DANGER,
            hover_color=Theme.ACCENT_DANGER_HOVER,
            width=100,
            height=26,
            command=self.delete_current_activity
        )
        self.btn_delete.pack(side="right", padx=(6, 0))

        self.btn_save_desc = ctk.CTkButton(
            action_bar,
            text="Simpan Keterangan",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            width=120,
            height=26,
            command=self.save_description_from_textbox
        )
        self.btn_save_desc.pack(side="right")

    def load_date_group(self, date_group: Optional[DateGroup]):
        """Memuat kelompok tanggal ke dalam form."""
        self.current_date_group = date_group
        if not date_group:
            self.lbl_date_title.configure(text="Kegiatan: (Belum memilih tanggal)")
            self.active_activity = None
            self._render_activity_list()
            self._update_editor_ui()
            return

        self.lbl_date_title.configure(text=f"Kegiatan: {date_group.display_date}")

        # Jika belum ada kegiatan, otomatis buatkan satu kegiatan awal
        if not date_group.activities:
            first_act = ActivityItem(description="Foto Bangunan Tampak Depan")
            date_group.activities.append(first_act)

        # Aktifkan kegiatan pertama secara default
        self.active_activity = date_group.activities[0] if date_group.activities else None
        self._render_activity_list()
        self._update_editor_ui()

        if self.on_activity_selected:
            self.on_activity_selected(self.active_activity)

    def _render_activity_list(self):
        """Merender tombol-tombol kegiatan yang sudah ada."""
        for w in self.list_container.winfo_children():
            w.destroy()

        if not self.current_date_group or not self.current_date_group.activities:
            empty = ctk.CTkLabel(
                self.list_container,
                text="Belum ada kegiatan. Klik '+ Tambah Kegiatan'.",
                font=ctk.CTkFont(size=11),
                text_color=Theme.TEXT_MUTED
            )
            empty.pack(pady=10)
            return

        for idx, act in enumerate(self.current_date_group.activities):
            is_active = (self.active_activity and self.active_activity.id == act.id)

            item_frame = ctk.CTkFrame(
                self.list_container,
                fg_color="#1e3a5f" if is_active else Theme.BG_CARD,
                border_width=1,
                border_color=Theme.ACCENT_PRIMARY if is_active else Theme.BORDER_COLOR,
                corner_radius=6,
                height=32
            )
            item_frame.pack(fill="x", padx=4, pady=2)

            # Judul keterangan singkat
            first_line = act.description.splitlines()[0] if act.description else "(Keterangan Kosong)"
            if len(first_line) > 35:
                first_line = first_line[:32] + "..."

            btn_select = ctk.CTkButton(
                item_frame,
                text=f"{idx + 1}. {first_line}",
                anchor="w",
                font=ctk.CTkFont(size=11, weight="bold" if is_active else "normal"),
                fg_color="transparent",
                hover_color=Theme.BORDER_LIGHT,
                text_color=Theme.TEXT_PRIMARY,
                height=26,
                command=lambda a=act: self.select_activity(a)
            )
            btn_select.pack(side="left", fill="x", expand=True, padx=6)

            # Badge Jumlah Foto
            count_lbl = ctk.CTkLabel(
                item_frame,
                text=f"{len(act.photo_paths)} Foto",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=Theme.ACCENT_SUCCESS if act.photo_paths else Theme.TEXT_MUTED,
                width=50
            )
            count_lbl.pack(side="right", padx=6)

    def select_activity(self, activity: ActivityItem):
        """Memilih kegiatan untuk diedit dan ditampilkan fotonya di galeri."""
        self.active_activity = activity
        self._render_activity_list()
        self._update_editor_ui()
        if self.on_activity_selected:
            self.on_activity_selected(activity)

    def create_new_activity(self):
        """Menambahkan baris kegiatan baru pada tanggal aktif."""
        if not self.current_date_group:
            return

        new_act = ActivityItem(description="Foto Bangunan")
        self.current_date_group.activities.append(new_act)
        self.select_activity(new_act)
        if self.on_activity_updated:
            self.on_activity_updated()

    def delete_current_activity(self):
        """Menghapus baris kegiatan aktif."""
        if not self.current_date_group or not self.active_activity:
            return

        if self.active_activity in self.current_date_group.activities:
            self.current_date_group.activities.remove(self.active_activity)

        # Pilih kegiatan berikutnya atau None
        self.active_activity = self.current_date_group.activities[0] if self.current_date_group.activities else None
        self._render_activity_list()
        self._update_editor_ui()

        if self.on_activity_selected:
            self.on_activity_selected(self.active_activity)
        if self.on_activity_updated:
            self.on_activity_updated()

    def _on_preset_chosen(self, choice: str):
        """Handler saat pengguna memilih template preset keterangan."""
        if not self.active_activity or choice == "-- Pilih Preset Keterangan --":
            return

        if "Material" in choice:
            text_to_set = Theme.TEMPLATE_MATERIAL
        elif "Peralatan" in choice:
            text_to_set = Theme.TEMPLATE_PERALATAN
        else:
            text_to_set = choice

        self.txt_description.delete("1.0", "end")
        self.txt_description.insert("1.0", text_to_set)
        self.save_description_from_textbox()

    def _on_text_changed(self):
        if self.active_activity:
            content = self.txt_description.get("1.0", "end-1c")
            self.active_activity.description = content

    def save_description_from_textbox(self):
        if not self.active_activity:
            return
        content = self.txt_description.get("1.0", "end-1c")
        self.active_activity.description = content
        self._render_activity_list()
        if self.on_activity_updated:
            self.on_activity_updated()

    def update_selected_photos_for_active(self, photo_paths: List[str]):
        """Memperbarui daftar foto yang dilampirkan pada kegiatan aktif."""
        if not self.active_activity:
            return
        self.active_activity.photo_paths = photo_paths
        self._update_editor_ui()
        self._render_activity_list()
        if self.on_activity_updated:
            self.on_activity_updated()

    def _update_editor_ui(self):
        if not self.active_activity:
            self.txt_description.delete("1.0", "end")
            self.txt_description.configure(state="disabled")
            self.lbl_photo_status.configure(text="0 Foto Dilampirkan")
            self.btn_delete.configure(state="disabled")
            self.btn_save_desc.configure(state="disabled")
            return

        self.txt_description.configure(state="normal")
        self.txt_description.delete("1.0", "end")
        self.txt_description.insert("1.0", self.active_activity.description)

        num_photos = len(self.active_activity.photo_paths)
        self.lbl_photo_status.configure(text=f"{num_photos} Foto Dilampirkan pada Kegiatan Ini")
        self.btn_delete.configure(state="normal")
        self.btn_save_desc.configure(state="normal")
