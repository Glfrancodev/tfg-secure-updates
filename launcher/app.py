"""Interfaz mínima del launcher (Tkinter). Toda la lógica está en updater.py.

Uso: python launcher/app.py
"""
import queue
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from updater import Launcher, format_control, load_config

PWNED_TEXT = "El juego ejecutó código malicioso (simulado)"


class App:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.results = queue.Queue()
        self.busy = False

        root.title("Launcher — Mi Juego de Prueba")
        root.minsize(560, 420)
        frame = ttk.Frame(root, padding=12)
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame)
        top.pack(fill="x")
        ttk.Label(top, text="Modo:").pack(side="left")
        self.mode = tk.StringVar(value="baseline")
        for value, text in (("baseline", "Baseline"), ("secure", "Seguro")):
            ttk.Radiobutton(top, text=text, value=value, variable=self.mode,
                            command=self.on_mode_change).pack(side="left", padx=(6, 0))
        self.audit = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Modo auditoría", variable=self.audit).pack(side="left", padx=(18, 0))

        versions = ttk.Frame(frame)
        versions.pack(fill="x", pady=(10, 0))
        self.installed_label = ttk.Label(versions)
        self.installed_label.pack(side="left")
        self.available_label = ttk.Label(versions, text="Versión disponible: ?")
        self.available_label.pack(side="left", padx=(24, 0))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=10)
        self.buttons = [
            ttk.Button(buttons, text="Buscar actualización", command=lambda: self.run("check")),
            ttk.Button(buttons, text="Actualizar", command=lambda: self.run("update")),
            ttk.Button(buttons, text="Jugar", command=lambda: self.run("play")),
        ]
        for button in self.buttons:
            button.pack(side="left", padx=(0, 6))

        self.banner = tk.Label(frame, text="", bg="#c62828", fg="white", font=("Segoe UI", 12, "bold"), pady=8)

        self.log = ScrolledText(frame, height=14, state="disabled", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)

        self.on_mode_change()
        root.after(100, self.poll_results)

    # --- utilidades ---------------------------------------------------------

    def launcher(self):
        return Launcher(self.mode.get(), self.config)

    def write(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def show_banner(self, text):
        self.banner.configure(text=text)
        self.banner.pack(fill="x", before=self.log, pady=(0, 8))

    def refresh_installed(self):
        installed = self.launcher().installed_version()
        self.installed_label.configure(text=f"Versión instalada: {installed or '—'}")

    def on_mode_change(self):
        self.banner.pack_forget()
        self.available_label.configure(text="Versión disponible: ?")
        self.refresh_installed()

    # --- acciones en segundo plano (la ventana no se congela) ---------------

    def run(self, action):
        if self.busy:
            return
        if self.audit.get():
            self.write("El modo auditoría se implementa en la Fase 5.")
            return
        self.busy = True
        for button in self.buttons:
            button.state(["disabled"])
        launcher = self.launcher()
        self.write(f"[{launcher.mode}] {action}…")

        def worker():
            try:
                self.results.put((action, getattr(launcher, action)(), None))
            except Exception as e:  # se muestra en el registro
                self.results.put((action, None, e))

        threading.Thread(target=worker, daemon=True).start()

    def poll_results(self):
        try:
            action, result, error = self.results.get_nowait()
        except queue.Empty:
            self.root.after(100, self.poll_results)
            return

        if error is not None:
            self.write(f"Error: {error}")
        elif action == "check":
            installed, available = result
            self.available_label.configure(text=f"Versión disponible: {available}")
            self.write(f"Instalada: {installed or '—'} · Disponible: {available}")
        elif action == "update":
            for control in result.controls:
                self.write(format_control(control))
            self.write(result.message)
        elif action == "play":
            self.write(f"El juego terminó (código {result.returncode}).")
            for marker in result.pwned:
                self.write(f"🚨 {PWNED_TEXT}: {marker.name}")
            if result.pwned:
                self.show_banner(PWNED_TEXT)

        self.refresh_installed()
        self.busy = False
        for button in self.buttons:
            button.state(["!disabled"])
        self.root.after(100, self.poll_results)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
