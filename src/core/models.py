import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any

# Pemetaan Hari dan Bulan dalam Bahasa Indonesia
HARI_INDONESIA = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu"
}

BULAN_INDONESIA = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
}

def format_indonesian_date(date_val: Any) -> str:
    """Mengubah objek date/datetime atau string YYYY-MM-DD menjadi format Indonesia: Hari, DD Bulan YYYY."""
    if isinstance(date_val, str):
        date_str = date_val.strip()
        # Coba format ISO YYYY-MM-DD
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                dt = datetime.strptime(date_str, "%Y/%m/%d")
            except ValueError:
                # Jika string sudah terformat khusus, kembalikan langsung
                return date_str
    elif isinstance(date_val, (datetime, )):
        dt = date_val
    else:
        return str(date_val)

    hari = HARI_INDONESIA.get(dt.weekday(), "")
    bulan = BULAN_INDONESIA.get(dt.month, "")
    return f"{hari}, {dt.day:02d} {bulan} {dt.year}"


@dataclass
class ActivityItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    photo_paths: List[str] = field(default_factory=list)
    custom_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "photo_paths": self.photo_paths,
            "custom_notes": self.custom_notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityItem":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            description=data.get("description", ""),
            photo_paths=data.get("photo_paths", []),
            custom_notes=data.get("custom_notes", "")
        )


@dataclass
class DateGroup:
    date_str: str  # Format: YYYY-MM-DD
    display_date: str = ""
    activities: List[ActivityItem] = field(default_factory=list)

    def __post_init__(self):
        if not self.display_date and self.date_str:
            self.display_date = format_indonesian_date(self.date_str)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date_str": self.date_str,
            "display_date": self.display_date,
            "activities": [act.to_dict() for act in self.activities]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DateGroup":
        activities = [ActivityItem.from_dict(item) for item in data.get("activities", [])]
        return cls(
            date_str=data.get("date_str", ""),
            display_date=data.get("display_date", ""),
            activities=activities
        )


@dataclass
class ReportProject:
    project_name: str = "Laporan Dokumentasi Kegiatan"
    base_folder: str = ""
    date_groups: List[DateGroup] = field(default_factory=list)
    output_path: str = ""
    photo_width_cm: float = 7.5
    font_name: str = "Arial"
    font_size_pt: float = 11.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_or_create_date_group(self, date_str: str) -> DateGroup:
        for group in self.date_groups:
            if group.date_str == date_str:
                return group
        new_group = DateGroup(date_str=date_str)
        self.date_groups.append(new_group)
        # Urutkan tanggal
        self.date_groups.sort(key=lambda g: g.date_str)
        return new_group

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "base_folder": self.base_folder,
            "date_groups": [dg.to_dict() for dg in self.date_groups],
            "output_path": self.output_path,
            "photo_width_cm": self.photo_width_cm,
            "font_name": self.font_name,
            "font_size_pt": self.font_size_pt,
            "created_at": self.created_at,
            "updated_at": datetime.now().isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReportProject":
        date_groups = [DateGroup.from_dict(dg) for dg in data.get("date_groups", [])]
        return cls(
            project_name=data.get("project_name", "Laporan Dokumentasi Kegiatan"),
            base_folder=data.get("base_folder", ""),
            date_groups=date_groups,
            output_path=data.get("output_path", ""),
            photo_width_cm=data.get("photo_width_cm", 7.5),
            font_name=data.get("font_name", "Arial"),
            font_size_pt=data.get("font_size_pt", 11.0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )

    def save_to_json(self, filepath: str) -> None:
        """Menyimpan draft proyek ke format JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_json(cls, filepath: str) -> "ReportProject":
        """Memuat draft proyek dari file JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
