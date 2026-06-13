'''import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="security_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- EMAIL CONFIG ----------------
SENDER_EMAIL = "rangaridharan676@gmail.com"
SENDER_PASSWORD = "vkavjtdtcffaimcw"
RECEIVER_EMAIL = "rangaridharan@gmail.com"

def send_email_alert(file_name, is_test=False):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        if is_test:
            msg['Subject'] = "Test Email"
            body = "Email working correctly!"
        else:
            msg['Subject'] = "⚠️ SECURITY ALERT"
            body = f"File Modified:\n{file_name}\nTime: {time.ctime()}"

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        if is_test:
            messagebox.showinfo("Success", "Test email sent!")

    except Exception as e:
        logging.error(str(e))
        messagebox.showerror("Error", "Email failed")

# ---------------- HASH ----------------
def calculate_file_hash(file_path, algorithm):
    try:
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except:
        return None

# ---------------- GUI ACTIONS ----------------
def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def test_connection():
    threading.Thread(target=send_email_alert, args=("test", True), daemon=True).start()

# ---------------- STATUS ----------------
def update_status(text, color):
    status_label.config(text=f"Status: {text}", fg=color)

# ---------------- MONITOR ----------------
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path, algorithm, original_hash):
        self.file_path = os.path.abspath(file_path)
        self.algorithm = algorithm
        self.original_hash = original_hash
        self.last_alert_time = 0

    def check_file(self, changed_path):
        if os.path.abspath(changed_path) == self.file_path:
            new_hash = calculate_file_hash(self.file_path, self.algorithm)

            if new_hash != self.original_hash:
                root.after(0, lambda: result_text.set("⚠️ MODIFIED! Alert Sent"))
                root.after(0, lambda: update_status("MODIFIED", "#ef4444"))

                logging.warning(f"MODIFIED: {self.file_path}")

                current_time = time.time()
                if current_time - self.last_alert_time > 15:
                    threading.Thread(target=send_email_alert,
                                     args=(self.file_path,),
                                     daemon=True).start()
                    self.last_alert_time = current_time
            else:
                root.after(0, lambda: update_status("SAFE", "#22c55e"))

    def on_modified(self, event):
        if not event.is_directory:
            self.check_file(event.src_path)

def start_monitoring():
    file_path = file_entry.get()

    if not file_path or not os.path.exists(file_path):
        messagebox.showerror("Error", "Select valid file first")
        return

    def run():
        original_hash = calculate_file_hash(file_path, algorithm_var.get())

        event_handler = FileChangeHandler(file_path, algorithm_var.get(), original_hash)
        observer = Observer()
        observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
        observer.start()

        logging.info(f"Monitoring started: {file_path}")
        messagebox.showinfo("Monitoring", "System Active!")

        while True:
            time.sleep(1)

    threading.Thread(target=run, daemon=True).start()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("File Integrity Checker")
root.geometry("620x520")
root.configure(bg="#0f172a")

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 10, "bold")

# HEADER
tk.Label(root, text="🔐 File Integrity Checker",
         font=FONT_TITLE, fg="white", bg="#0f172a").pack(pady=15)

# FILE SECTION
file_frame = tk.Frame(root, bg="#0f172a")
file_frame.pack(pady=10)

tk.Label(file_frame, text="Step 1: Select Target File",
         fg="#cbd5f5", bg="#0f172a").pack()

file_entry = tk.Entry(file_frame, width=60,
                      bg="#1e293b", fg="white",
                      insertbackground="white")
file_entry.pack(pady=5, ipady=6)

tk.Button(file_frame, text="📂 Browse File",
          command=select_file,
          bg="#2563eb", fg="white").pack()

# EMAIL SECTION
email_frame = tk.Frame(root, bg="#0f172a")
email_frame.pack(pady=15)

tk.Label(email_frame, text="Step 2: Setup Alerts",
         fg="#cbd5f5", bg="#0f172a").pack()

test_btn = tk.Button(email_frame, text="📧 Send Test Email",
                     command=test_connection,
                     bg="#0ea5e9", fg="white")
test_btn.pack(pady=5)

# ALGORITHM
tk.Label(root, text="Hash Algorithm",
         fg="#cbd5f5", bg="#0f172a").pack()

algorithm_var = tk.StringVar(value="sha256")
tk.OptionMenu(root, algorithm_var,
              "md5", "sha1", "sha256", "sha512").pack()

# START BUTTON
tk.Button(root, text="🛡️ START MONITORING",
          command=start_monitoring,
          bg="#22c55e", fg="white",
          font=("Segoe UI", 12, "bold"),
          padx=20, pady=10).pack(pady=20)

# STATUS
status_label = tk.Label(root,
                        text="Status: Waiting...",
                        fg="#94a3b8",
                        bg="#0f172a",
                        font=("Segoe UI", 11, "bold"))
status_label.pack()

# RESULT
result_text = tk.StringVar(value="Ready")
tk.Label(root, textvariable=result_text,
         fg="#38bdf8", bg="#0f172a").pack(pady=10)

root.mainloop()'''


import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import time
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="security_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- EMAIL CONFIG ----------------
SENDER_EMAIL = "rangaridharan676@gmail.com"
SENDER_PASSWORD = "vkavjtdtcffaimcw"
RECEIVER_EMAIL = "rangaridharan@gmail.com"

# Global reference for the log window text area
log_display = None

def write_to_live_log(message):
    """Helper to update the separate UI log window"""
    if log_display:
        log_display.after(0, lambda: log_display.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n"))
        log_display.after(0, lambda: log_display.see(tk.END))

def open_log_window():
    """Creates a separate UI window for Live Activity"""
    global log_display
    log_win = tk.Toplevel(root)
    log_win.title("Live Activity Monitor")
    log_win.geometry("500x400")
    log_win.configure(bg="#1e293b")
    
    tk.Label(log_win, text="🔴 LIVE SYSTEM ACTIVITY", fg="#ef4444", bg="#1e293b", font=("Segoe UI", 12, "bold")).pack(pady=5)
    
    log_display = scrolledtext.ScrolledText(log_win, bg="#0f172a", fg="#10b981", font=("Consolas", 10))
    log_display.pack(expand=True, fill='both', padx=10, pady=10)
    write_to_live_log("System Log Interface Started...")

def send_email_alert(file_name, is_test=False):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = "Test Email" if is_test else "⚠️ SECURITY ALERT"
        body = "Email working!" if is_test else f"File Modified: {file_name}\nTime: {time.ctime()}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        if is_test: messagebox.showinfo("Success", "Test email sent!")
    except Exception as e:
        logging.error(str(e))
        write_to_live_log(f"EMAIL ERROR: {str(e)}")

# ---------------- HASHING ----------------
def calculate_file_hash(file_path, algorithm):
    try:
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except:
        return None

# ---------------- FOLDER ACTIONS ----------------
def select_folder():
    path = filedialog.askdirectory()
    if path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, path)

# ---------------- MONITOR ----------------
class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, folder_path, algorithm):
        self.folder_path = os.path.abspath(folder_path)
        self.algorithm = algorithm
        self.baseline_hashes = {}
        self.last_alert_time = 0
        self.create_baseline()

    def create_baseline(self):
        """Scan folder and store initial hashes"""
        write_to_live_log(f"Creating baseline for: {self.folder_path}")
        for root_dir, _, files in os.walk(self.folder_path):
            for name in files:
                full_path = os.path.join(root_dir, name)
                self.baseline_hashes[full_path] = calculate_file_hash(full_path, self.algorithm)
        write_to_live_log(f"Baseline created for {len(self.baseline_hashes)} files.")

    def on_modified(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path or file_path.endswith(".py"):
                return
            new_hash = calculate_file_hash(file_path, self.algorithm)
            
            # Check if hash changed from baseline
            if file_path in self.baseline_hashes:
                if new_hash != self.baseline_hashes[file_path]:
                    write_to_live_log(f"MODIFIED: {os.path.basename(file_path)}")
                    logging.warning(f"MODIFIED: {file_path}")
                    
                    root.after(0, lambda: result_text.set(f"⚠️ Breach: {os.path.basename(file_path)}"))
                    
                    # Alert logic
                    curr = time.time()
                    if curr - self.last_alert_time > 15:
                        threading.Thread(target=send_email_alert, args=(file_path,), daemon=True).start()
                        self.last_alert_time = curr
                else:
                    write_to_live_log(f"Access: {os.path.basename(file_path)} (Integrity Intact)")

def start_monitoring():
    path = file_entry.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Select valid folder first")
        return

    # Open log window automatically if not open
    if not log_display:
        open_log_window()

    def run():
        event_handler = FolderChangeHandler(path, algorithm_var.get())
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True) # Set recursive=True for folder
        observer.start()
        
        root.after(0, lambda: status_label.config(text="Status: SHIELD ACTIVE", fg="#22c55e"))
        logging.info(f"Monitoring folder: {path}")
        
        while True:
            time.sleep(1)

    threading.Thread(target=run, daemon=True).start()

# ---------------- MAIN GUI ----------------
root = tk.Tk()
root.title("Advanced Folder Integrity Shield")
root.geometry("620x550")
root.configure(bg="#0f172a")

# HEADER
tk.Label(root, text="🔐 Folder Integrity Shield", font=("Segoe UI", 18, "bold"), fg="white", bg="#0f172a").pack(pady=15)

# FOLDER SECTION
file_frame = tk.Frame(root, bg="#0f172a")
file_frame.pack(pady=10)
tk.Label(file_frame, text="Target Folder to Protect", fg="#cbd5f5", bg="#0f172a").pack()
file_entry = tk.Entry(file_frame, width=60, bg="#1e293b", fg="white", insertbackground="white")
file_entry.pack(pady=5, ipady=6)
tk.Button(file_frame, text="📂 Browse Folder", command=select_folder, bg="#2563eb", fg="white").pack()

# ACTIONS
action_frame = tk.Frame(root, bg="#0f172a")
action_frame.pack(pady=10)
tk.Button(action_frame, text="📧 Test Email", command=lambda: threading.Thread(target=send_email_alert, args=("test", True), daemon=True).start(), bg="#0ea5e9", fg="white").grid(row=0, column=0, padx=5)
tk.Button(action_frame, text="📜 Open Activity Log", command=open_log_window, bg="#64748b", fg="white").grid(row=0, column=1, padx=5)

# ALGORITHM
tk.Label(root, text="Hash Algorithm", fg="#cbd5f5", bg="#0f172a").pack()
algorithm_var = tk.StringVar(value="sha256")
tk.OptionMenu(root, algorithm_var, "md5", "sha1", "sha256", "sha512").pack()

# START BUTTON
tk.Button(root, text="🛡️ START FOLDER SHIELD", command=start_monitoring, bg="#22c55e", fg="white", font=("Segoe UI", 12, "bold"), padx=20, pady=10).pack(pady=20)

status_label = tk.Label(root, text="Status: Waiting...", fg="#94a3b8", bg="#0f172a", font=("Segoe UI", 11, "bold"))
status_label.pack()

result_text = tk.StringVar(value="Ready")
tk.Label(root, textvariable=result_text, fg="#38bdf8", bg="#0f172a", wraplength=500).pack(pady=10)

root.mainloop()