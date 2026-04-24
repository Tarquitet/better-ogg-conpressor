import os
import subprocess
import threading
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# --- AUTO-INSTALADOR DE DEPENDENCIAS ---
def setup_dependencies():
    try:
        import ttkbootstrap
    except ImportError:
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ttkbootstrap"])
        os.execv(sys.executable, ['python'] + sys.argv)

setup_dependencies()

class MinecraftAudioOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("OMEGA Minecraft Audio Optimizer (Ultra-Compresor)")
        self.root.geometry("800x500")
        
        self.files_to_process = []
        self.output_path = tk.StringVar(value=os.path.join(os.getcwd(), "minecraft_sounds"))
        
        self.setup_ui()

    def setup_ui(self):
        # Panel Superior
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=X)
        ttk.Button(top, text="➕ Seleccionar Audios", bootstyle=SUCCESS, command=self.add_files).pack(side=LEFT, padx=5)
        ttk.Button(top, text="🗑️ Limpiar", bootstyle=DANGER, command=self.clear_list).pack(side=LEFT, padx=5)

        # Lista de archivos
        self.listbox = tk.Listbox(self.root, bg="#1a1a1a", fg="white", font=("Consolas", 10))
        self.listbox.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Controles de Compresión Extrema
        ctrl = ttk.LabelFrame(self.root, text=" Configuración de Optimización para Minecraft ", padding=15)
        ctrl.pack(fill=X, padx=10, pady=10)

        self.mode = tk.StringVar(value="extreme")
        ttk.Radiobutton(ctrl, text="Compresión Extrema (Mono, 22kHz, Mínimo Peso)", variable=self.mode, value="extreme").pack(anchor=W)
        ttk.Radiobutton(ctrl, text="Balanceado (Mono, 44kHz, Calidad Media)", variable=self.mode, value="balanced").pack(anchor=W)

        # Salida y Botón
        out_frame = ttk.Frame(self.root, padding=10)
        out_frame.pack(fill=X)
        ttk.Entry(out_frame, textvariable=self.output_path).pack(side=LEFT, fill=X, expand=True, padx=5)
        ttk.Button(out_frame, text="🚀 OPTIMIZAR TODO", bootstyle=PRIMARY, command=self.start_process).pack(side=RIGHT)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac")])
        for f in files:
            if f not in self.files_to_process:
                self.files_to_process.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def clear_list(self):
        self.files_to_process.clear()
        self.listbox.delete(0, tk.END)

    def start_process(self):
        if not self.files_to_process:
            return messagebox.showwarning("Aviso", "No hay archivos en la lista.")
        
        if not os.path.exists(self.output_path.get()):
            os.makedirs(self.output_path.get())
            
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        success = 0
        total = len(self.files_to_process)
        
        # Configuración según modo
        if self.mode.get() == "extreme":
            q_scale = "-1" # Calidad más baja de Vorbis
            rate = "22050" # Mitad de frecuencia
        else:
            q_scale = "1"
            rate = "44100"

        for file_path in self.files_to_process:
            out_name = os.path.splitext(os.path.basename(file_path))[0] + ".ogg"
            final_out = os.path.join(self.output_path.get(), out_name)

            # COMANDO AGRESIVO: 
            # -vn -sn -dn: Elimina carátulas y datos basura
            # -map_metadata -1: Borra tags de artista/álbum
            # -ac 1: Fuerza MONO (Vital para ahorrar 50%)
            cmd = [
                "ffmpeg", "-y", "-i", file_path,
                "-vn", "-sn", "-dn",
                "-map_metadata", "-1",
                "-map", "0:a:0",
                "-acodec", "libvorbis",
                "-q:a", q_scale,
                "-ac", "1",
                "-ar", rate,
                final_out
            ]

            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    success += 1
            except Exception as e:
                print(f"Error en {file_path}: {e}")

        messagebox.showinfo("Proceso Terminado", f"Se optimizaron {success} de {total} archivos.\nGuardados en: {self.output_path.get()}")

if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    MinecraftAudioOptimizer(app)
    app.mainloop()