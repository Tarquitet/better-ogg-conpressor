import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class PrecisionOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("OMEGA Precision Optimizer")
        self.root.geometry("700x500")
        
        # Parámetros de objetivo
        self.target_size_kb = tk.IntVar(value=800) # Tu peso ideal
        self.files = []
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="Target Size Optimizer (Evita el sonido de teléfono)", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Configuración de Peso
        cfg_frame = ttk.Frame(self.root, padding=10)
        cfg_frame.pack(fill=X)
        ttk.Label(cfg_frame, text="Peso Objetivo por archivo (KB):").pack(side=LEFT, padx=5)
        ttk.Entry(cfg_frame, textvariable=self.target_size_kb, width=10).pack(side=LEFT)
        ttk.Label(cfg_frame, text="Sugerido: 700-900 KB", font=("Arial", 8, "italic")).pack(side=LEFT, padx=10)

        # Botones
        btn_f = ttk.Frame(self.root, padding=10)
        btn_f.pack(fill=X)
        ttk.Button(btn_f, text="📂 Cargar Audios", bootstyle=INFO, command=self.load).pack(side=LEFT, expand=True, fill=X, padx=5)
        ttk.Button(btn_f, text="🚀 OPTIMIZAR POR PESO", bootstyle=SUCCESS, command=self.process).pack(side=LEFT, expand=True, fill=X, padx=5)

        self.listbox = tk.Listbox(self.root, bg="#1a1a1a", fg="white")
        self.listbox.pack(fill=BOTH, expand=True, padx=20, pady=10)

    def load(self):
        paths = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav *.ogg *.m4a")])
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert(tk.END, os.path.basename(p))

    def get_duration(self, path):
        """Obtiene la duración exacta usando ffprobe"""
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return float(res.stdout) if res.stdout else 0

    def process(self):
        if not self.files: return
        out_dir = os.path.join(os.getcwd(), "optimized_precise")
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        threading.Thread(target=self.worker, args=(out_dir,), daemon=True).start()

    def worker(self, out_dir):
        success = 0
        target_bytes = self.target_size_kb.get() * 1024
        
        for i, path in enumerate(self.files):
            dur = self.get_duration(path)
            if dur == 0: continue

            # MATEMÁTICA: Bitrate (bps) = (Tamaño en bits) / Duración
            # Queremos el bitrate en kbps para FFmpeg
            calc_bitrate = int((target_bytes * 8) / dur / 1000)
            
            # Límites de seguridad para no perder demasiada calidad
            # Si el audio es muy largo, el bitrate bajará mucho.
            calc_bitrate = max(45, min(192, calc_bitrate)) 

            out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + ".ogg")

            # COMANDO BALANCEADO:
            # Mantenemos 32000Hz o 44100Hz para que NO suene a teléfono
            cmd = [
                "ffmpeg", "-y", "-i", path,
                "-vn", "-map_metadata", "-1",
                "-ac", "1",                  # Mono sigue siendo el mejor ahorro
                "-ar", "20000",              # 32kHz es el punto medio perfecto
                "-acodec", "libvorbis",
                "-b:a", f"{calc_bitrate}k",  # Usamos el bitrate calculado
                out_path
            ]

            res = subprocess.run(cmd, capture_output=True)
            if res.returncode == 0:
                success += 1
                self.listbox.itemconfig(i, fg="lightgreen")

        messagebox.showinfo("Proceso Terminado", f"Se optimizaron {success} archivos con el peso objetivo.")

if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    PrecisionOptimizer(app)
    app.mainloop()