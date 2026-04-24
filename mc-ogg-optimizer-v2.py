import os
import sys
import subprocess
import threading
import urllib.request
import zipfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# --- CONFIGURACIÓN DE AUTO-DESCARGA ---
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
BIN_DIR = os.path.join(os.getcwd(), "bin")
FFMPEG_EXE = os.path.join(BIN_DIR, "ffmpeg.exe")

def check_or_download_ffmpeg():
    """Descarga e instala FFmpeg portable si no existe."""
    if shutil.which("ffmpeg") or os.path.exists(FFMPEG_EXE):
        return True

    if not messagebox.askyesno("Requisito faltante", "No se detectó FFmpeg. ¿Deseas que el script lo descargue automáticamente? (Aprox. 90MB)"):
        sys.exit()

    try:
        if not os.path.exists(BIN_DIR): os.makedirs(BIN_DIR)
        
        print("📥 Descargando motor de audio (esto solo ocurre una vez)...")
        zip_path = os.path.join(BIN_DIR, "ffmpeg.zip")
        urllib.request.urlretrieve(FFMPEG_URL, zip_path)

        print("📦 Extrayendo archivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Buscamos el ffmpeg.exe dentro del zip
            for member in zip_ref.namelist():
                if member.endswith("ffmpeg.exe"):
                    filename = os.path.basename(member)
                    source = zip_ref.open(member)
                    target = open(os.path.join(BIN_DIR, filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
        
        os.remove(zip_path)
        print("✅ Motor instalado correctamente.")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar FFmpeg: {e}")
        return False

class MCUitraOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("OMEGA MC-Ultra (Compresor Autónomo)")
        self.root.geometry("700x550")
        self.files = []
        
        # Inyectar el bin local al PATH del script
        if os.path.exists(BIN_DIR):
            os.environ["PATH"] += os.pathsep + BIN_DIR

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="💎 Minecraft Audio Ultra-Compressor", font=("Arial", 16, "bold")).pack(pady=15)
        
        btn_f = ttk.Frame(self.root)
        btn_f.pack(fill=X, padx=20)
        ttk.Button(btn_f, text="📂 Seleccionar Audios", bootstyle=INFO, command=self.add).pack(side=LEFT, expand=True, fill=X, padx=5)
        ttk.Button(btn_f, text="💥 COMPRESIÓN MÁXIMA", bootstyle=DANGER, command=self.process).pack(side=LEFT, expand=True, fill=X, padx=5)

        self.listbox = tk.Listbox(self.root, bg="#1a1a1a", fg="#00ff00", font=("Consolas", 9))
        self.listbox.pack(fill=BOTH, expand=True, padx=20, pady=10)

        self.status = ttk.Label(self.root, text="Listo para procesar", bootstyle=SECONDARY)
        self.status.pack(pady=5)

    def add(self):
        paths = filedialog.askopenfilenames(filetypes=[("Audios", "*.mp3 *.wav *.ogg *.m4a *.aac *.flac")])
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert(tk.END, f"📦 {os.path.basename(p)}")

    def process(self):
        if not check_or_download_ffmpeg(): return
        if not self.files: return
        
        out_dir = os.path.join(os.getcwd(), "mc_sounds_optimized")
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        
        threading.Thread(target=self.worker, args=(out_dir,), daemon=True).start()

    def worker(self, out_dir):
        success = 0
        for i, path in enumerate(self.files):
            self.status.config(text=f"Procesando: {os.path.basename(path)}...")
            out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + ".ogg")

            # --- COMANDO DE REDUCCIÓN ABSOLUTA ---
            # Resolvemos el error 'Invalid argument' borrando carátulas y forzando flujos limpios
            cmd = [
                "ffmpeg", "-y", "-i", path,
                "-vn", "-sn", "-dn",         # Elimina carátulas/video/subtítulos
                "-map_metadata", "-1",       # Borra etiquetas de texto
                "-map", "0:a:0",             # Solo el primer canal de audio
                "-acodec", "libvorbis",
                "-q:a", "-1",                # Calidad mínima legal
                "-ac", "1",                  # Forzar MONO (Ahorro del 50%)
                "-ar", "16000",              # Frecuencia mínima (Ahorro del 75%)
                out_path
            ]

            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    success += 1
                    self.listbox.itemconfig(i, fg="gray")
            except: pass

        self.status.config(text="¡Finalizado!")
        messagebox.showinfo("Hecho", f"Se optimizaron {success} archivos.\nCarpeta: {out_dir}")

if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    # Auto-instalar dependencias de Python si faltan (como en tu script anterior)
    #
    MCUitraOptimizer(app)
    app.mainloop()