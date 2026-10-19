import os
import shutil
import tempfile
from typing import Optional, Callable
from docx import Document
from docx.shared import Inches, Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT, WD_SECTION_START
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from .models import ReportProject, DateGroup, ActivityItem
from .image_processor import ImageProcessor

class DocxGenerator:
    """Mesin penyusun dokumen Word (.docx) laporan dokumentasi kegiatan

    Mereplikasi secara presisi format dari file standar:
    - Orientasi Landscape (Letter / A4)
    - Lebar 4 Kolom: No (0.95cm), Tanggal (4.80cm), Keterangan (6.23cm), Dokumentasi (11.34cm)
    - Foto diskalakan proporsional ~7.5 cm dan terpusat rapi
    - Font konsisten: Arial 11pt
    - Penomoran dan pengelompokan tanggal otomatis
    """

    # Definisi lebar kolom dalam centimeter
    COL_WIDTHS_CM = [0.95, 4.80, 6.23, 11.34]

    @staticmethod
    def _set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
        """Mengatur margin internal (padding) pada sel tabel (dalam dxa)."""
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            m = OxmlElement(f'w:{side}')
            m.set(qn('w:w'), str(val))
            m.set(qn('w:type'), 'dxa')
            tcMar.append(m)
        tcPr.append(tcMar)

    @staticmethod
    def _set_table_borders(table):
        """Membuat border tabel garis tunggal hitam rapi."""
        tblPr = table._tbl.tblPr
        borders_xml = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            f'</w:tblBorders>'
        )
        tblPr.append(borders_xml)

    @classmethod
    def _apply_row_cant_split(cls, row):
        """Mencegah pemotongan baris di tengah-tengah halaman (Word cantSplit)."""
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    @classmethod
    def generate_report(
        cls,
        project: ReportProject,
        output_filepath: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> str:
        """Menghasilkan file .docx dari objek ReportProject."""

        temp_dir = tempfile.mkdtemp(prefix="docureport_")
        try:
            doc = Document()

            # 1. Konfigurasi Halaman (Landscape Letter)
            section = doc.sections[0]
            section.orientation = WD_ORIENT.LANDSCAPE
            section.page_width = Cm(27.94)
            section.page_height = Cm(21.59)
            section.left_margin = Cm(2.0)
            section.right_margin = Cm(2.0)
            section.top_margin = Cm(2.0)
            section.bottom_margin = Cm(2.0)

            # Hitung total foto untuk pelacakan progress bar
            total_photos = sum(
                len(act.photo_paths)
                for dg in project.date_groups
                for act in dg.activities
            )
            processed_photos = 0

            # 2. Inisialisasi Tabel
            table = doc.add_table(rows=1, cols=4)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            cls._set_table_borders(table)

            # 3. Header Tabel (No., Tanggal, Keterangan, Dokumentasi)
            hdr_cells = table.rows[0].cells
            hdr_titles = ["No.", "Tanggal", "Keterangan", "Dokumentasi"]
            for idx, title in enumerate(hdr_titles):
                cell = hdr_cells[idx]
                cell.width = Cm(cls.COL_WIDTHS_CM[idx])
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                cls._set_cell_margins(cell, top=160, bottom=160, left=140, right=140)

                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.0

                run = p.add_run(title)
                run.font.name = project.font_name
                run.font.size = Pt(project.font_size_pt)
                run.font.bold = True

            # Set header row agar berulang di setiap halaman Word jika panjang
            trPr = table.rows[0]._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            cls._apply_row_cant_split(table.rows[0])

            # 4. Iterasi Kelompok Tanggal dan Kegiatan
            date_counter = 1

            for dg in project.date_groups:
                if not dg.activities:
                    continue

                is_first_activity_of_date = True

                for act in dg.activities:
                    row = table.add_row()
                    cls._apply_row_cant_split(row)
                    cells = row.cells

                    # Set lebar tetap pada setiap sel
                    for c_idx, width_cm in enumerate(cls.COL_WIDTHS_CM):
                        cells[c_idx].width = Cm(width_cm)
                        cls._set_cell_margins(cells[c_idx], top=120, bottom=120, left=140, right=140)

                    # --- KOLOM 0: No. ---
                    c0_p = cells[0].paragraphs[0]
                    c0_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    c0_p.paragraph_format.space_before = Pt(2)
                    c0_p.paragraph_format.space_after = Pt(2)
                    if is_first_activity_of_date:
                        r_no = c0_p.add_run(f"{date_counter}.")
                        r_no.font.name = project.font_name
                        r_no.font.size = Pt(project.font_size_pt)
                    cells[0].vertical_alignment = WD_ALIGN_VERTICAL.TOP

                    # --- KOLOM 1: Tanggal ---
                    c1_p = cells[1].paragraphs[0]
                    c1_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    c1_p.paragraph_format.space_before = Pt(2)
                    c1_p.paragraph_format.space_after = Pt(2)
                    if is_first_activity_of_date:
                        r_date = c1_p.add_run(dg.display_date)
                        r_date.font.name = project.font_name
                        r_date.font.size = Pt(project.font_size_pt)
                    cells[1].vertical_alignment = WD_ALIGN_VERTICAL.TOP

                    # --- KOLOM 2: Keterangan ---
                    c2_p = cells[2].paragraphs[0]
                    c2_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    c2_p.paragraph_format.space_before = Pt(2)
                    c2_p.paragraph_format.space_after = Pt(2)
                    c2_p.paragraph_format.line_spacing = 1.15

                    desc_text = act.description.strip()
                    if act.custom_notes.strip():
                        desc_text += f"\n{act.custom_notes.strip()}"

                    # Pisahkan berdasarkan baris baru agar tampil seperti daftar
                    lines = desc_text.splitlines()
                    for line_idx, line in enumerate(lines):
                        if line_idx > 0:
                            c2_p = cells[2].add_paragraph()
                            c2_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            c2_p.paragraph_format.space_before = Pt(0)
                            c2_p.paragraph_format.space_after = Pt(2)
                            c2_p.paragraph_format.line_spacing = 1.15
                        r_line = c2_p.add_run(line)
                        r_line.font.name = project.font_name
                        r_line.font.size = Pt(project.font_size_pt)

                    cells[2].vertical_alignment = WD_ALIGN_VERTICAL.TOP

                    # --- KOLOM 3: Dokumentasi (Foto) ---
                    cells[3].vertical_alignment = WD_ALIGN_VERTICAL.TOP
                    photo_paragraphs = []

                    # Hapus paragraf default kosong sel jika ada foto
                    first_p = cells[3].paragraphs[0]

                    if not act.photo_paths:
                        first_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        r_empty = first_p.add_run("-\n(Tidak ada foto)")
                        r_empty.font.name = project.font_name
                        r_empty.font.size = Pt(9.0)
                        r_empty.font.italic = True
                    else:
                        for p_idx, photo_path in enumerate(act.photo_paths):
                            if progress_callback:
                                processed_photos += 1
                                progress_callback(
                                    processed_photos,
                                    max(total_photos, 1),
                                    f"Menyisipkan foto ({processed_photos}/{total_photos}): {os.path.basename(photo_path)}"
                                )

                            if not os.path.exists(photo_path):
                                continue

                            # Siapkan gambar teroptimasi
                            opt_img_path = ImageProcessor.prepare_image_for_word(
                                photo_path, temp_dir=temp_dir
                            )
                            if not opt_img_path:
                                continue

                            # Gunakan first_p untuk foto pertama, add_paragraph untuk foto berikutnya
                            curr_p = first_p if p_idx == 0 else cells[3].add_paragraph()
                            curr_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            curr_p.paragraph_format.space_before = Pt(2)
                            curr_p.paragraph_format.space_after = Pt(8) # Jarak antar foto rapi

                            # Masukkan gambar dengan lebar proporsional (~7.5 cm)
                            run_img = curr_p.add_run()
                            run_img.add_picture(opt_img_path, width=Cm(project.photo_width_cm))

                    is_first_activity_of_date = False

                date_counter += 1

            # 5. Simpan Dokumen
            os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
            doc.save(output_filepath)

            if progress_callback:
                progress_callback(total_photos, total_photos, "Laporan Word berhasil dibuat!")

            return output_filepath

        finally:
            # Bersihkan file temporer
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
