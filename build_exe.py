"""Skrip kompilasi otomatis aplikasi DocuReport Windows menjadi SATU FILE (.EXE) mandiri
menggunakan PyInstaller (--onefile).
"""
import os
import sys
import shutil
import subprocess

def build():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(root_dir, "dist")
    build_dir = os.path.join(root_dir, "build")

    print("=" * 65)
    print("  MEMULAI BUILD SINGLE FILE EXECUTABLE (.EXE) DOCUREPORT")
    print("=" * 65)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",             # Satu file .exe mandiri tanpa folder eksternal
        "--windowed",            # GUI murni tanpa konsol hitam
        "--name", "DocuReport_Auto",
        "--collect-all", "customtkinter",
        "--collect-all", "docx",
        "--collect-all", "PIL",
        "--hidden-import", "PIL._imagingtk",
        "--hidden-import", "PIL.ImageTk",
        "run.py"
    ]

    print(f"Menjalankan perintah PyInstaller...\n")
    result = subprocess.run(cmd, cwd=root_dir)

    if result.returncode == 0:
        exe_in_dist = os.path.join(dist_dir, "DocuReport_Auto.exe")
        target_root_exe = os.path.join(root_dir, "DocuReport_Auto.exe")

        # Salin file .exe langsung ke folder root proyek agar mudah ditemukan
        if os.path.exists(exe_in_dist):
            shutil.copy2(exe_in_dist, target_root_exe)

        print("\n" + "=" * 65)
        print("  [OK] BUILD BERHASIL 100%!")
        print(f"  File .EXE Mandiri telah disalin ke:")
        print(f"  -> {target_root_exe}")
        print("=" * 65)
    else:
        print("\n" + "=" * 65)
        print(f"  [GAGAL] Build gagal dengan kode error: {result.returncode}")
        print("=" * 65)

if __name__ == "__main__":
    build()
