import os
import hashlib
from typing import Tuple, Optional, Dict
from PIL import Image, ImageOps

class ImageProcessor:
    """Modul untuk memproses foto dokumentasi:

    - Koreksi rotasi orientasi EXIF otomatis
    - Pembuatan thumbnail cepat dengan in-memory cache
    - Penskalaan proporsional presisi untuk tabel Microsoft Word
    - Optimalisasi kompresi agar dokumen Word tidak membengkak
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self._thumb_cache: Dict[str, Image.Image] = {}
        self.cache_dir = cache_dir

    @staticmethod
    def fix_orientation(img: Image.Image) -> Image.Image:
        """Memperbaiki orientasi foto berdasarkan metadata EXIF."""
        try:
            return ImageOps.exif_transpose(img)
        except Exception:
            return img

    @classmethod
    def load_image_safe(cls, image_path: str) -> Optional[Image.Image]:
        """Membuka file gambar dengan aman dan mengoreksi orientasi."""
        if not os.path.exists(image_path):
            return None
        try:
            with Image.open(image_path) as img:
                # Load data ke memori agar file handle tidak terkunci
                img_copy = img.copy()
                return cls.fix_orientation(img_copy)
        except Exception as e:
            print(f"[ImageProcessor] Gagal memuat gambar {image_path}: {e}")
            return None

    def get_thumbnail(self, image_path: str, size: Tuple[int, int] = (150, 110)) -> Optional[Image.Image]:
        """Mengambil atau membuat thumbnail gambar untuk antarmuka GUI."""
        if not os.path.exists(image_path):
            return None

        # Gunakan mtime dan size sebagai cache key
        try:
            mtime = os.path.getmtime(image_path)
            cache_key = f"{image_path}_{mtime}_{size[0]}x{size[1]}"
        except OSError:
            cache_key = f"{image_path}_{size[0]}x{size[1]}"

        if cache_key in self._thumb_cache:
            return self._thumb_cache[cache_key]

        img = self.load_image_safe(image_path)
        if img is None:
            return None

        # Gunakan thumbnail proporsional dengan resampling berkualitas tinggi
        img.thumbnail(size, Image.Resampling.LANCZOS)
        self._thumb_cache[cache_key] = img
        return img

    @staticmethod
    def get_scaled_dimensions(
        original_w: int, 
        original_h: int, 
        target_width_cm: float = 7.5
    ) -> Tuple[float, float]:
        """Menghitung dimensi proporsional (lebar x tinggi dalam cm) untuk Word."""
        if original_w <= 0:
            return target_width_cm, target_width_cm * 0.75

        aspect_ratio = original_h / original_w
        target_height_cm = target_width_cm * aspect_ratio
        return target_width_cm, target_height_cm

    @classmethod
    def prepare_image_for_word(
        cls, 
        image_path: str, 
        temp_dir: str, 
        max_dimension: int = 1600, 
        quality: int = 85
    ) -> Optional[str]:
        """Menyiapkan gambar teroptimasi untuk disisipkan ke Word.

        Memastikan orientasi EXIF tegak lurus dan ukuran file proporsional
        sehingga dokumen Word tidak membengkak ratusan megabyte.
        """
        img = cls.load_image_safe(image_path)
        if img is None:
            return None

        os.makedirs(temp_dir, exist_ok=True)
        # Nama file hash untuk mencegah collision
        name_hash = hashlib.md5(image_path.encode("utf-8")).hexdigest()[:12]
        out_filename = f"img_{name_hash}.jpg"
        out_path = os.path.join(temp_dir, out_filename)

        if os.path.exists(out_path):
            return out_path

        # Resize jika gambar asli sangat besar (> 1600px)
        w, h = img.size
        if w > max_dimension or h > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        # Simpan ke format RGB JPEG
        if img.mode != "RGB":
            img = img.convert("RGB")

        img.save(out_path, "JPEG", quality=quality, optimize=True)
        return out_path
