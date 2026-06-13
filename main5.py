import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os
import sqlite3

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("file_integrity.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        file_path TEXT PRIMARY KEY,
        hash TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT,
        status TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_file_hash(file_path, file_hash):
    conn = sqlite3.connect("file_integrity.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO files (file_path, hash)
    VALUES (?, ?)
    """, (file_path, file_hash))

    conn.commit()
    conn.close()


def get_saved_hash(file_path):
    conn = sqlite3.connect("file_integrity.db")
    cursor = conn.cursor()

    cursor.execute("SELECT hash FROM files WHERE file_path=?", (file_path,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else None


def log_event(file_path, status):
    conn = sqlite3.connect("file_integrity.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO logs (file_path, status, timestamp)
    VALUES (?, ?, datetime('now'))
    """, (file_path, status))

    conn.commit()
    conn.close()


# ---------------- HASH ----------------
def calculate_file_hash(file_path):
    try:
        hash_func = hashlib.sha256()
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None


# ---------------- FILE SELECT ----------------
def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


# ---------------- STATUS ----------------
def update_status(text, color):
    status_label.config(text=f"Status: {text}", fg=color)


# ---------------- CALCULATE ----------------
def calculate_hash():
    file_path = file_entry.get()

    if not file_path:
        messagebox.showerror("Error", "Select file")
        return

    file_hash = calculate_file_hash(file_path)

    if file_hash:
        result_text.set(f"SHA-256:\n{file_hash}")
        save_file_hash(file_path, file_hash)
        update_status("HASH SAVED", "#00c3ff")


# ---------------- VERIFY ----------------
def verify_file():
    file_path = file_entry.get()

    saved_hash = get_saved_hash(file_path)
    current_hash = calculate_file_hash(file_path)

    if saved_hash and current_hash:
        if saved_hash == current_hash:
            update_status("SAFE", "#00ff9f")
            log_event(file_path, "SAFE")
        else:
            update_status("MODIFIED", "#ff4d4d")
            log_event(file_path, "MODIFIED")


# ---------------- PDF EXPORT ----------------
def export_logs():
    conn = sqlite3.connect("file_integrity.db")
    cursor = conn.cursor()

    cursor.execute("SELECT file_path, status, timestamp FROM logs")
    logs = cursor.fetchall()

    conn.close()

    doc = SimpleDocTemplate("logs.pdf")
    styles = getSampleStyleSheet()

    content = []

    for log in logs:
        text = f"{log[2]} | {log[0]} | {log[1]}"
        content.append(Paragraph(text, styles["Normal"]))

    doc.build(content)

    messagebox.showinfo("Export", "Logs exported to logs.pdf")


# ---------------- MONITOR ----------------
class Handler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = os.path.abspath(file_path)

    def check(self):
        new_hash = calculate_file_hash(self.file_path)
        saved_hash = get_saved_hash(self.file_path)

        if new_hash != saved_hash:
            root.after(0, lambda: update_status("MODIFIED", "#ff4d4d"))
            root.after(0, lambda: result_text.set("⚠️ Modified"))
            log_event(self.file_path, "MODIFIED")
        else:
            root.after(0, lambda: update_status("SAFE", "#00ff9f"))
            log_event(self.file_path, "SAFE")

    def on_modified(self, event):
        if not event.is_directory:
            self.check()


def monitor():
    file_path = file_entry.get()

    if not file_path:
        return

    observer = Observer()
    handler = Handler(file_path)

    observer.schedule(handler, os.path.dirname(file_path), recursive=False)
    observer.start()

    while True:
        time.sleep(1)


def start_monitor():
    threading.Thread(target=monitor, daemon=True).start()


# ---------------- GUI ----------------
root = tk.Tk()
root.title("File Integrity Checker")
root.geometry("600x450")
root.configure(bg="#121212")

tk.Label(root, text="File Integrity Checker",
         font=("Arial", 16, "bold"),
         bg="#121212", fg="white").pack(pady=10)

file_entry = tk.Entry(root, width=60, bg="#1e1e1e", fg="white")
file_entry.pack()

tk.Button(root, text="Browse", command=select_file, bg="#1f6feb", fg="white").pack(pady=5)

tk.Button(root, text="Calculate & Save Hash", command=calculate_hash,
          bg="#d29922").pack(pady=5)

tk.Button(root, text="Verify", command=verify_file,
          bg="#238636", fg="white").pack(pady=5)

tk.Button(root, text="Start Monitoring", command=start_monitor,
          bg="#2ea043", fg="white").pack(pady=5)

tk.Button(root, text="Export Logs PDF", command=export_logs,
          bg="#8957e5", fg="white").pack(pady=5)

result_text = tk.StringVar()
tk.Label(root, textvariable=result_text,
         bg="#1e1e1e", fg="#00c3ff",
         height=4).pack(fill="x", padx=10, pady=10)

status_label = tk.Label(root, text="Status: Waiting...",
                        bg="#121212", fg="#cccccc",
                        font=("Arial", 12, "bold"))
status_label.pack()

init_db()
root.mainloop()