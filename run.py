"""DocuReport Auto — Generator Laporan Dokumentasi Kegiatan ke Word (.docx)
Entrypoint utama aplikasi Windows.
"""
import sys
import os
import traceback

# Pastikan folder root ada di sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows High-DPI Awareness
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

def main():
    try:
        from src.gui.app import DocuReportApp
        app = DocuReportApp()
        app.mainloop()
    except Exception as e:
        error_msg = traceback.format_exc()
        try:
            with open("error_startup.log", "w", encoding="utf-8") as f:
                f.write(error_msg)
        except Exception:
            pass
        try:
            import tkinter.messagebox as mb
            mb.showerror("Error Startup", f"Aplikasi mengalami kendala saat dibuka:\n\n{e}\n\nDetail disimpan di error_startup.log")
        except Exception:
            pass

if __name__ == "__main__":
    main()
