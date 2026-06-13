import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ---------------- HASH FUNCTION ----------------
def calculate_file_hash(file_path, algorithm):
    try:
        hash_func = hashlib.new(algorithm)
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


# ---------------- VERIFY ----------------
def verify_file_integrity():
    file_path = file_entry.get()
    algorithm = algorithm_var.get()
    expected_hash = expected_hash_entry.get().strip()

    if not file_path:
        messagebox.showerror("Error", "Select a file")
        return

    file_hash = calculate_file_hash(file_path, algorithm)

    if file_hash:
        result_text.set(f"{algorithm.upper()} Hash:\n{file_hash}")

        if expected_hash:
            if file_hash == expected_hash:
                messagebox.showinfo("Result", "✅ File integrity intact")
            else:
                messagebox.showwarning("Result", "❌ File modified!")


# ---------------- CALCULATE ONLY ----------------
def calculate_hash_only():
    file_path = file_entry.get()
    algorithm = algorithm_var.get()

    if not file_path:
        messagebox.showerror("Error", "Select a file")
        return

    result_text.set("Calculating... Please wait")
    root.update()

    file_hash = calculate_file_hash(file_path, algorithm)

    if file_hash:
        result_text.set(f"{algorithm.upper()} Hash:\n{file_hash}")


# ---------------- COPY ----------------
def copy_to_clipboard():
    hash_value = result_text.get().split("\n")[-1]
    if hash_value:
        root.clipboard_clear()
        root.clipboard_append(hash_value)
        root.update()
        messagebox.showinfo("Copied", "Hash copied!")


# ---------------- REAL-TIME MONITOR ----------------
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path, algorithm, original_hash):
        self.file_path = os.path.abspath(file_path)  # ✅ Normalize path
        self.algorithm = algorithm
        self.original_hash = original_hash

    def check_file(self, changed_path):
        changed_path = os.path.abspath(changed_path)

        # ✅ Match only selected file
        if changed_path == self.file_path:
            new_hash = calculate_file_hash(self.file_path, self.algorithm)

            if new_hash != self.original_hash:
                messagebox.showwarning("ALERT", "⚠️ File has been modified!")
            else:
                print("No change detected")

    def on_modified(self, event):
        if not event.is_directory:
            self.check_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.check_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.check_file(event.dest_path)


def monitor_file():
    file_path = file_entry.get()
    algorithm = algorithm_var.get()

    if not file_path:
        messagebox.showerror("Error", "Select a file first")
        return

    # ✅ Normalize path before monitoring
    file_path = os.path.abspath(file_path)

    original_hash = calculate_file_hash(file_path, algorithm)

    event_handler = FileChangeHandler(file_path, algorithm, original_hash)
    observer = Observer()

    folder_path = os.path.dirname(file_path)

    observer.schedule(event_handler, path=folder_path, recursive=False)
    observer.start()

    messagebox.showinfo("Monitoring", "Real-time monitoring started!")

    try:
        while True:
            time.sleep(1)
    except:
        observer.stop()
    observer.join()


# Run monitoring in background thread
def start_monitoring():
    thread = threading.Thread(target=monitor_file, daemon=True)
    thread.start()


# ---------------- GUI ----------------
root = tk.Tk()
root.title("Real-Time File Integrity Checker")
root.geometry("520x420")

# File input
tk.Label(root, text="Select File").pack()
file_entry = tk.Entry(root, width=60)
file_entry.pack(pady=5)
tk.Button(root, text="Browse", command=select_file).pack()

# Algorithm
tk.Label(root, text="Algorithm").pack()
algorithm_var = tk.StringVar(value="sha256")
tk.OptionMenu(root, algorithm_var, "md5", "sha1", "sha256", "sha512").pack()

# Expected hash
tk.Label(root, text="Expected Hash (Optional)").pack()
expected_hash_entry = tk.Entry(root, width=60)
expected_hash_entry.pack(pady=5)

# Buttons
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="Verify", command=verify_file_integrity).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Calculate", command=calculate_hash_only).grid(row=0, column=1, padx=5)
tk.Button(frame, text="Copy", command=copy_to_clipboard).grid(row=0, column=2, padx=5)

# Real-time monitoring button
tk.Button(root, text="Start Real-Time Monitoring", command=start_monitoring, bg="lightgreen").pack(pady=10)

# Result display
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, fg="blue", wraplength=480).pack()

root.mainloop()