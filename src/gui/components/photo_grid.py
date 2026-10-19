import os
import queue
import threading
from typing import List, Set, Callable, Optional, Dict
import customtkinter as ctk
from PIL import Image

from ..theme import Theme
from ...core.image_processor import ImageProcessor

class PhotoPreviewWindow(ctk.CTkToplevel):
    """Jendela pop-up pratinjau foto resolusi penuh."""
    def __init__(self, parent, photo_path: str):
        super().__init__(parent)
        self.title(f"Pratinjau Foto: {os.path.basename(photo_path)}")
        self.geometry("900x700")
        self.configure(fg_color=Theme.BG_DARK)
        self.attributes("-topmost", True)
        self._preview_ctk_img = None

        filename = os.path.basename(photo_path)
        header_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=0, height=50)
        header_frame.pack(fill="x", side="top", padx=0, pady=0)

        lbl_title = ctk.CTkLabel(
            header_frame,
            text=filename,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        lbl_title.pack(side="left", padx=16, pady=12)

        lbl_path = ctk.CTkLabel(
            header_frame,
            text=photo_path,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Theme.TEXT_MUTED
        )
        lbl_path.pack(side="left", padx=10, pady=12)

        # Container Gambar
        img_container = ctk.CTkScrollableFrame(self, fg_color=Theme.BG_DARK)
        img_container.pack(fill="both", expand=True, padx=16, pady=16)

        try:
            pil_img = ImageProcessor.load_image_safe(photo_path)
            if pil_img:
                orig_w, orig_h = pil_img.size
                max_w, max_h = 840, 580
                ratio = min(max_w / orig_w, max_h / orig_h, 1.0)
                display_w = int(orig_w * ratio)
                display_h = int(orig_h * ratio)

                self._preview_ctk_img = ctk.CTkImage(
                    light_image=pil_img, 
                    dark_image=pil_img, 
                    size=(display_w, display_h)
                )
                lbl_img = ctk.CTkLabel(img_container, image=self._preview_ctk_img, text="")
                lbl_img.pack(expand=True, pady=10)

                lbl_info = ctk.CTkLabel(
                    img_container,
                    text=f"Resolusi Asli: {orig_w} x {orig_h} px | Ukuran File: {os.path.getsize(photo_path)/1024:.1f} KB",
                    font=ctk.CTkFont(family="Segoe UI", size=11),
                    text_color=Theme.TEXT_SECONDARY
                )
                lbl_info.pack(pady=5)
        except Exception as e:
            err_lbl = ctk.CTkLabel(img_container, text=f"Gagal memuat gambar: {e}", text_color=Theme.ACCENT_DANGER)
            err_lbl.pack(expand=True, pady=40)


class PhotoCard(ctk.CTkFrame):
    """Komponen kartu foto individual di dalam galeri."""
    def __init__(
        self,
        master,
        photo_path: str,
        is_selected: bool,
        on_toggle: Callable[[str], None],
        on_preview: Callable[[str], None],
        image_processor: ImageProcessor,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=8,
            fg_color=Theme.BG_CARD if not is_selected else "#14532d",
            border_width=2,
            border_color=Theme.ACCENT_SUCCESS if is_selected else Theme.BORDER_COLOR,
            width=165,
            height=165,
            **kwargs
        )
        self.photo_path = photo_path
        self.is_selected = is_selected
        self.on_toggle = on_toggle
        self.on_preview = on_preview
        self.image_processor = image_processor
        self._ctk_img = None  # Reference agar gambar tidak di-garbage collect!

        self.pack_propagate(False)

        # Gambar Thumbnail
        self.lbl_thumb = ctk.CTkLabel(
            self,
            text="Memuat...",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=Theme.TEXT_MUTED,
            width=150,
            height=100,
            corner_radius=6
        )
        self.lbl_thumb.pack(padx=5, pady=(5, 2))

        # Nama File Singkat
        filename = os.path.basename(photo_path)
        short_name = filename if len(filename) <= 18 else f"{filename[:8]}...{filename[-7:]}"
        self.lbl_name = ctk.CTkLabel(
            self,
            text=short_name,
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=Theme.TEXT_MUTED,
            height=14
        )
        self.lbl_name.pack(padx=4, pady=(0, 2))

        # Tombol Pilih / Terpilih
        self.btn_select = ctk.CTkButton(
            self,
            text="✓ Terpilih" if is_selected else "+ Pilih Foto",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=Theme.ACCENT_SUCCESS if is_selected else Theme.BORDER_COLOR,
            hover_color=Theme.ACCENT_SUCCESS_HOVER if is_selected else Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY,
            height=24,
            command=self._handle_click
        )
        self.btn_select.pack(fill="x", padx=6, pady=(0, 5))

        # Bind event klik
        self.lbl_thumb.bind("<Button-1>", lambda e: self._handle_click())
        self.lbl_thumb.bind("<Double-Button-1>", lambda e: self.on_preview(self.photo_path))
        self.lbl_name.bind("<Button-1>", lambda e: self._handle_click())
        self.lbl_name.bind("<Double-Button-1>", lambda e: self.on_preview(self.photo_path))
        self.bind("<Button-1>", lambda e: self._handle_click())
        self.bind("<Double-Button-1>", lambda e: self.on_preview(self.photo_path))

    def _handle_click(self):
        self.on_toggle(self.photo_path)

    def set_thumbnail_image(self, ctk_img: ctk.CTkImage):
        """Memperbarui visual thumbnail dan menyimpan referensinya secara persisten."""
        self._ctk_img = ctk_img
        self.lbl_thumb.configure(image=self._ctk_img, text="")

    def update_selection(self, is_selected: bool):
        """Memperbarui status visual terpilih / tidak."""
        self.is_selected = is_selected
        self.configure(
            fg_color=Theme.BG_CARD if not is_selected else "#14532d",
            border_color=Theme.ACCENT_SUCCESS if is_selected else Theme.BORDER_COLOR
        )
        self.btn_select.configure(
            text="✓ Terpilih" if is_selected else "+ Pilih Foto",
            fg_color=Theme.ACCENT_SUCCESS if is_selected else Theme.BORDER_COLOR,
            hover_color=Theme.ACCENT_SUCCESS_HOVER if is_selected else Theme.BORDER_LIGHT
        )


class PhotoGrid(ctk.CTkFrame):
    """Panel galeri foto yang menampilkan thumbnail foto per tanggal."""
    def __init__(
        self,
        master,
        image_processor: ImageProcessor,
        on_selection_changed: Optional[Callable[[List[str]], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        self.image_processor = image_processor
        self.on_selection_changed = on_selection_changed

        self.current_photos: List[str] = []
        self.selected_photos: Set[str] = set()
        self.cards: Dict[str, PhotoCard] = {}

        # Queue untuk transfer thumbnail antar worker thread dan UI thread
        self._thumb_queue = queue.Queue()
        self._queue_poll_active = False
        self._current_load_id = 0

        self._init_ui()

    def _init_ui(self):
        # Header Toolbar
        self.toolbar = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, height=45, corner_radius=8)
        self.toolbar.pack(fill="x", padx=10, pady=(10, 6))

        self.lbl_info = ctk.CTkLabel(
            self.toolbar,
            text="Galeri Foto: 0 Foto | 0 Terpilih",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.lbl_info.pack(side="left", padx=14, pady=8)

        # Petunjuk Zoom
        lbl_hint = ctk.CTkLabel(
            self.toolbar,
            text="(Tips: Klik ganda foto untuk zoom pratinjau)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Theme.TEXT_MUTED
        )
        lbl_hint.pack(side="left", padx=6, pady=8)

        # Tombol Batch Select
        self.btn_select_all = ctk.CTkButton(
            self.toolbar,
            text="Pilih Semua",
            font=ctk.CTkFont(size=11),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            width=90,
            height=28,
            command=self.select_all
        )
        self.btn_select_all.pack(side="right", padx=6, pady=8)

        self.btn_clear_sel = ctk.CTkButton(
            self.toolbar,
            text="Reset Pilihan",
            font=ctk.CTkFont(size=11),
            fg_color=Theme.BORDER_COLOR,
            hover_color=Theme.BORDER_LIGHT,
            width=90,
            height=28,
            command=self.clear_selection
        )
        self.btn_clear_sel.pack(side="right", padx=6, pady=8)

        # Kontainer Scrollable untuk Thumbnail Grid
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=6, pady=6)

        # Konfigurasi kolom grid (responsif 4 kolom)
        for c in range(4):
            self.scroll_frame.grid_columnconfigure(c, weight=1, pad=8)

    def load_photos(self, photo_paths: List[str], pre_selected: Optional[List[str]] = None):
        """Memuat daftar foto ke dalam galeri."""
        self._current_load_id += 1
        load_id = self._current_load_id

        self.current_photos = photo_paths
        self.selected_photos = set(pre_selected or [])
        self.cards.clear()

        # Kosongkan queue lama
        while not self._thumb_queue.empty():
            try:
                self._thumb_queue.get_nowait()
            except queue.Empty:
                break

        # Bersihkan widget lama
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self._update_counter_label()

        if not photo_paths:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="Tidak ada foto di folder tanggal ini.\nPilih folder foto yang valid di panel kiri.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=Theme.TEXT_MUTED
            )
            empty_lbl.grid(row=0, column=0, columnspan=4, pady=60)
            return

        # Render Kartu Foto
        num_cols = 4
        for idx, path in enumerate(photo_paths):
            row = idx // num_cols
            col = idx % num_cols

            is_sel = path in self.selected_photos
            card = PhotoCard(
                self.scroll_frame,
                photo_path=path,
                is_selected=is_sel,
                on_toggle=self.toggle_photo,
                on_preview=self.open_preview,
                image_processor=self.image_processor
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self.cards[path] = card

        # Mulai poll queue di thread utama
        if not self._queue_poll_active:
            self._queue_poll_active = True
            self.after(30, self._process_thumb_queue)

        # Jalankan background thread murni untuk memproses PIL thumbnail tanpa menyentuh Tkinter
        threading.Thread(
            target=self._pure_pillow_worker,
            args=(photo_paths, load_id),
            daemon=True
        ).start()

    def _pure_pillow_worker(self, photo_paths: List[str], load_id: int):
        """Background thread murni (hanya membaca file dan kalkulasi PIL, bebas error Tkinter)."""
        for path in photo_paths:
            if load_id != self._current_load_id:
                # User sudah pindah tanggal/folder, batalkan loading lama
                break

            pil_thumb = self.image_processor.get_thumbnail(path, size=(150, 100))
            if pil_thumb and load_id == self._current_load_id:
                self._thumb_queue.put((load_id, path, pil_thumb))

    def _process_thumb_queue(self):
        """Memproses hasil thumbnail di thread utama secara berkala."""
        batch_size = 8  # Proses hingga 8 gambar per tick agar UI tetap 60fps
        processed = 0

        while not self._thumb_queue.empty() and processed < batch_size:
            try:
                item = self._thumb_queue.get_nowait()
                load_id, path, pil_thumb = item

                if load_id == self._current_load_id and path in self.cards:
                    ctk_img = ctk.CTkImage(
                        light_image=pil_thumb,
                        dark_image=pil_thumb,
                        size=(pil_thumb.width, pil_thumb.height)
                    )
                    self.cards[path].set_thumbnail_image(ctk_img)

                processed += 1
            except queue.Empty:
                break

        # Terus polling selama masih ada kartu yang belum selesai atau masih ada queue
        try:
            if self.winfo_exists():
                self.after(30, self._process_thumb_queue)
            else:
                self._queue_poll_active = False
        except Exception:
            self._queue_poll_active = False

    def toggle_photo(self, photo_path: str):
        """Membalikkan status pemilihan foto."""
        if photo_path in self.selected_photos:
            self.selected_photos.remove(photo_path)
        else:
            self.selected_photos.add(photo_path)

        if photo_path in self.cards:
            self.cards[photo_path].update_selection(photo_path in self.selected_photos)

        self._update_counter_label()
        if self.on_selection_changed:
            self.on_selection_changed(list(self.selected_photos))

    def set_selected_photos(self, selected_list: List[str]):
        """Memperbarui set foto yang terpilih dari luar (misal saat berganti kegiatan)."""
        self.selected_photos = set(selected_list)
        for path, card in self.cards.items():
            card.update_selection(path in self.selected_photos)
        self._update_counter_label()

    def select_all(self):
        self.selected_photos = set(self.current_photos)
        for card in self.cards.values():
            card.update_selection(True)
        self._update_counter_label()
        if self.on_selection_changed:
            self.on_selection_changed(list(self.selected_photos))

    def clear_selection(self):
        self.selected_photos.clear()
        for card in self.cards.values():
            card.update_selection(False)
        self._update_counter_label()
        if self.on_selection_changed:
            self.on_selection_changed([])

    def _update_counter_label(self):
        total = len(self.current_photos)
        selected = len(self.selected_photos)
        self.lbl_info.configure(text=f"Galeri Foto: {total} Foto | {selected} Terpilih untuk Kegiatan Ini")

    def open_preview(self, photo_path: str):
        PhotoPreviewWindow(self, photo_path)
