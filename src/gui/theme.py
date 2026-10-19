"""Theme and styling configuration for DocuReport Windows."""

class Theme:
    # Mode
    APPEARANCE_MODE = "Dark"  # "System", "Dark", "Light"
    COLOR_THEME = "blue"

    # Palet Warna Slate & Tech Pro
    BG_DARK = "#0f172a"          # slate-900
    BG_CARD = "#1e293b"          # slate-800
    BG_CARD_HOVER = "#243248"
    BG_SIDEBAR = "#090d16"       # slate-950
    BG_INPUT = "#0f172a"
    
    # Border & Dividers
    BORDER_COLOR = "#334155"     # slate-700
    BORDER_LIGHT = "#475569"     # slate-600

    # Aksen & Status
    ACCENT_PRIMARY = "#3b82f6"   # blue-500
    ACCENT_PRIMARY_HOVER = "#2563eb" # blue-600
    ACCENT_SUCCESS = "#10b981"   # emerald-500
    ACCENT_SUCCESS_HOVER = "#059669"
    ACCENT_DANGER = "#ef4444"    # red-500
    ACCENT_DANGER_HOVER = "#dc2626"
    ACCENT_WARNING = "#f59e0b"   # amber-500

    # Tipografi Warna
    TEXT_PRIMARY = "#f8fafc"     # slate-50
    TEXT_SECONDARY = "#94a3b8"   # slate-400
    TEXT_MUTED = "#64748b"       # slate-500

    # Preset Keterangan Cepat (Sesuai Kebutuhan Proyek & Dokumen Sampel)
    PRESETS_KETERANGAN = [
        "Foto Bangunan Tampak Depan",
        "Foto Bangunan Tampak Samping Kiri Depan",
        "Foto Bangunan Tampak Samping Kanan Depan",
        "Foto Bangunan Tampak Samping Kiri",
        "Foto Bangunan Tampak Samping Kanan",
        "Foto Bangunan Tampak Belakang",
        "Foto Bangunan Tampak Pojok Belakang Kiri",
        "Foto Bangunan Tampak Pojok Belakang Kanan",
        "Foto Bangunan Tampak Belakang Samping Kiri",
        "Foto Bangunan Tampak Belakang Samping Kanan",
        "Foto Material yang Dibeli :",
        "Foto Peralatan yang Dibeli :",
        "Foto Pekerjaan Pengecoran Pondasi",
        "Foto Pekerjaan Pembesian Cor",
        "Foto Pekerjaan Pemasangan Dinding Bata",
        "Foto Pekerjaan Plesteran & Acian",
        "Foto Pekerjaan Rangka Atap",
        "Foto Pekerjaan Pengecatan",
        "Pemasangan Plafon & Kusen",
        "Dokumentasi Kunjungan & Monitoring",
    ]

    TEMPLATE_MATERIAL = (
        "Foto Material yang Dibeli :\n"
        "Semen\n"
        "Batu Bata\n"
        "Besi Cor\n"
        "Pasir\n"
        "Coral\n"
        "Kawat Bendrat"
    )

    TEMPLATE_PERALATAN = (
        "Foto Peralatan yang Dibeli :\n"
        "Gerobak Merk SAVIC\n"
        "Cangkul\n"
        "Sekop\n"
        "Ember Cor\n"
        "Kawat\n"
        "Paku UK 5 cm & 10 cm\n"
        "Tali Bangunan\n"
        "Helm Proyek & Sarung Tangan\n"
        "Sepatu Boots"
    )
