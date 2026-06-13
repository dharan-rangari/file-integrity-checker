'''import hashlib
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

log_display = None

def write_to_live_log(message):
    if log_display:
        log_display.after(0, lambda: log_display.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n"))
        log_display.after(0, lambda: log_display.see(tk.END))

def open_log_window():
    global log_display
    if log_display and tk.Toplevel.winfo_exists(log_display.master):
        log_display.master.lift()
        return
        
    log_win = tk.Toplevel(root)
    log_win.title("Live Activity Monitor")
    log_win.geometry("600x450")
    log_win.configure(bg="#1e293b")
    
    tk.Label(log_win, text="🔴 LIVE SYSTEM ACTIVITY", fg="#ef4444", bg="#1e293b", font=("Segoe UI", 12, "bold")).pack(pady=5)
    log_display = scrolledtext.ScrolledText(log_win, bg="#0f172a", fg="#10b981", font=("Consolas", 10))
    log_display.pack(expand=True, fill='both', padx=10, pady=10)

def send_email_alert(file_name, is_test=False):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = "✅ Connection Test" if is_test else "⚠️ SECURITY ALERT"
        body = "SMTP Connection Successful!" if is_test else f"Security Event Detected!\nFile: {file_name}\nTime: {time.ctime()}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        if is_test:
            root.after(0, lambda: messagebox.showinfo("Success", "Test email sent successfully!"))
            write_to_live_log("SUCCESS: SMTP handshake complete.")
    except Exception as e:
        err = str(e)
        logging.error(f"Email Error: {err}")
        write_to_live_log(f"❌ EMAIL FAILURE: {err}")
        # ✅ FIX 1: Show popup even from background thread
        root.after(0, lambda: messagebox.showerror("Email Error", f"Failed to send email.\n\nError: {err}"))

# ---------------- MONITORING LOGIC ----------------
class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, folder_path, algorithm):
        self.folder_path = os.path.abspath(folder_path)
        self.algorithm = algorithm
        self.baseline_hashes = {}
        self.last_alert_time = 0
        self.create_baseline()

    def create_baseline(self):
        self.baseline_hashes = {}
        for root_dir, _, files in os.walk(self.folder_path):
            for name in files:
                full_path = os.path.join(root_dir, name)
                if "security_log.txt" in name: continue
                self.baseline_hashes[full_path] = calculate_file_hash(full_path, self.algorithm)

    # ✅ FIX 3: Detect Creation
    def on_created(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path: return
            
            write_to_live_log(f"🆕 CREATED: {os.path.basename(file_path)}")
            self.baseline_hashes[file_path] = calculate_file_hash(file_path, self.algorithm)
            self.trigger_alert(file_path, "NEW FILE ADDED")

    # ✅ FIX 3: Detect Deletion
    def on_deleted(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path: return
            
            write_to_live_log(f"🗑️ DELETED: {os.path.basename(file_path)}")
            if file_path in self.baseline_hashes:
                del self.baseline_hashes[file_path]
            self.trigger_alert(file_path, "FILE REMOVED")

    def on_modified(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path or file_path.endswith(".py"): return
            
            new_hash = calculate_file_hash(file_path, self.algorithm)
            if file_path in self.baseline_hashes:
                if new_hash != self.baseline_hashes[file_path]:
                    write_to_live_log(f"📝 MODIFIED: {os.path.basename(file_path)}")
                    self.baseline_hashes[file_path] = new_hash
                    self.trigger_alert(file_path, "CONTENT CHANGED")

    def trigger_alert(self, file_path, msg_type):
        logging.warning(f"{msg_type}: {file_path}")
        root.after(0, lambda: result_text.set(f"⚠️ {msg_type}: {os.path.basename(file_path)}"))
        
        curr = time.time()
        if curr - self.last_alert_time > 15:
            threading.Thread(target=send_email_alert, args=(file_path,), daemon=True).start()
            self.last_alert_time = curr

def calculate_file_hash(file_path, algorithm):
    try:
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except: return None

def start_monitoring():
    path = file_entry.get()
    algo = algorithm_var.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Select valid folder first")
        return

    if not log_display: open_log_window()

    # ✅ FIX 2: Show Algorithm in Live Activity Log
    write_to_live_log(f"🛡️ Shield Initialized using {algo.upper()} algorithm.")
    write_to_live_log(f"📂 Monitoring Target: {path}")

    def run():
        event_handler = FolderChangeHandler(path, algo)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        root.after(0, lambda: status_label.config(text="Status: SHIELD ACTIVE", fg="#22c55e"))
        while True: time.sleep(1)

    threading.Thread(target=run, daemon=True).start()

# ---------------- MAIN GUI ----------------
root = tk.Tk()
root.title("Advanced Integrity Shield v3.0")
root.geometry("620x550")
root.configure(bg="#0f172a")

tk.Label(root, text="🛡️ Folder Integrity Shield", font=("Segoe UI", 18, "bold"), fg="white", bg="#0f172a").pack(pady=15)

file_frame = tk.Frame(root, bg="#0f172a")
file_frame.pack(pady=10)
file_entry = tk.Entry(file_frame, width=60, bg="#1e293b", fg="white", insertbackground="white")
file_entry.pack(pady=5, ipady=6)
tk.Button(file_frame, text="📂 Browse Folder", command=lambda: file_entry.insert(0, filedialog.askdirectory()), bg="#2563eb", fg="white").pack()

action_frame = tk.Frame(root, bg="#0f172a")
action_frame.pack(pady=10)
tk.Button(action_frame, text="📧 Test Email", command=lambda: threading.Thread(target=send_email_alert, args=("test", True), daemon=True).start(), bg="#0ea5e9", fg="white").grid(row=0, column=0, padx=5)
tk.Button(action_frame, text="📜 Live Activity Log", command=open_log_window, bg="#64748b", fg="white").grid(row=0, column=1, padx=5)

tk.Label(root, text="Algorithm", fg="#cbd5f5", bg="#0f172a").pack()
algorithm_var = tk.StringVar(value="sha256")
tk.OptionMenu(root, algorithm_var, "md5", "sha1", "sha256", "sha512").pack()

tk.Button(root, text="🛡️ START SHIELD", command=start_monitoring, bg="#22c55e", fg="white", font=("Segoe UI", 12, "bold"), padx=20, pady=10).pack(pady=20)
status_label = tk.Label(root, text="Status: Waiting...", fg="#94a3b8", bg="#0f172a", font=("Segoe UI", 11, "bold"))
status_label.pack()

result_text = tk.StringVar(value="Ready")
tk.Label(root, textvariable=result_text, fg="#38bdf8", bg="#0f172a", wraplength=500).pack(pady=10)

root.mainloop()'''

'''import hashlib
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

log_display = None

def write_to_live_log(message):
    if log_display:
        log_display.after(0, lambda: log_display.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n"))
        log_display.after(0, lambda: log_display.see(tk.END))

def open_log_window():
    global log_display
    if log_display and tk.Toplevel.winfo_exists(log_display.master):
        log_display.master.lift()
        return
        
    log_win = tk.Toplevel(root)
    log_win.title("Live Activity Monitor")
    log_win.geometry("600x450")
    log_win.configure(bg="#1e293b")
    
    tk.Label(log_win, text="🔴 LIVE SYSTEM ACTIVITY", fg="#ef4444", bg="#1e293b", font=("Segoe UI", 12, "bold")).pack(pady=5)
    log_display = scrolledtext.ScrolledText(log_win, bg="#0f172a", fg="#10b981", font=("Consolas", 10))
    log_display.pack(expand=True, fill='both', padx=10, pady=10)

# --- UPDATED EMAIL FUNCTION ---
def send_email_alert(file_name, event_type, is_test=False):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        if is_test:
            msg['Subject'] = "✅ Connection Test"
            body = "SMTP Connection Successful! Your alert system is online."
        else:
            # Displays the specific event in the Subject Line
            msg['Subject'] = f"⚠️ SECURITY ALERT: File {event_type}"
            body = (f"An integrity event has been detected.\n\n"
                    f"Event Action: {event_type}\n"
                    f"File Name: {os.path.basename(file_name)}\n"
                    f"Full Path: {file_name}\n"
                    f"Time of Event: {time.ctime()}")

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        if is_test:
            root.after(0, lambda: messagebox.showinfo("Success", "Test email sent successfully!"))
            write_to_live_log("SUCCESS: SMTP handshake complete.")
    except Exception as e:
        err = str(e)
        logging.error(f"Email Error: {err}")
        write_to_live_log(f"❌ EMAIL FAILURE: {err}")
        # Error popup will now show even if triggered from background thread
        root.after(0, lambda: messagebox.showerror("Email Error", f"Failed to send email.\n\nError: {err}"))

# ---------------- MONITORING LOGIC ----------------
class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, folder_path, algorithm):
        self.folder_path = os.path.abspath(folder_path)
        self.algorithm = algorithm
        self.baseline_hashes = {}
        self.last_alert_time = 0
        self.create_baseline()

    def create_baseline(self):
        self.baseline_hashes = {}
        for root_dir, _, files in os.walk(self.folder_path):
            for name in files:
                full_path = os.path.join(root_dir, name)
                if "security_log.txt" in name: continue
                self.baseline_hashes[full_path] = calculate_file_hash(full_path, self.algorithm)

    def on_created(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path: return
            
            write_to_live_log(f"🆕 CREATED: {os.path.basename(file_path)}")
            self.baseline_hashes[file_path] = calculate_file_hash(file_path, self.algorithm)
            self.trigger_alert(file_path, "NEW FILE CREATED")

    def on_deleted(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path: return
            
            write_to_live_log(f"🗑️ DELETED: {os.path.basename(file_path)}")
            if file_path in self.baseline_hashes:
                del self.baseline_hashes[file_path]
            self.trigger_alert(file_path, "FILE DELETED")

    def on_modified(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path or file_path.endswith(".py"): return
            
            new_hash = calculate_file_hash(file_path, self.algorithm)
            if file_path in self.baseline_hashes:
                if new_hash != self.baseline_hashes[file_path]:
                    write_to_live_log(f"📝 MODIFIED: {os.path.basename(file_path)}")
                    self.baseline_hashes[file_path] = new_hash
                    self.trigger_alert(file_path, "CONTENT MODIFIED")

    # --- UPDATED TRIGGER ALERT ---
    def trigger_alert(self, file_path, msg_type):
        logging.warning(f"{msg_type}: {file_path}")
        root.after(0, lambda: result_text.set(f"⚠️ {msg_type}: {os.path.basename(file_path)}"))
        
        curr = time.time()
        # Throttling to prevent spamming emails (15 second cooldown)
        if curr - self.last_alert_time > 15:
            # Passes the msg_type (CREATED/DELETED/MODIFIED) to the email function
            threading.Thread(target=send_email_alert, args=(file_path, msg_type), daemon=True).start()
            self.last_alert_time = curr

def calculate_file_hash(file_path, algorithm):
    try:
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except: return None

def start_monitoring():
    path = file_entry.get()
    algo = algorithm_var.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Select valid folder first")
        return

    if not log_display: open_log_window()

    # Activity panel now displays chosen algorithm
    write_to_live_log(f"🛡️ Shield Initialized using {algo.upper()} algorithm.")
    write_to_live_log(f"📂 Monitoring Target: {path}")

    def run():
        event_handler = FolderChangeHandler(path, algo)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        root.after(0, lambda: status_label.config(text="Status: SHIELD ACTIVE", fg="#22c55e"))
        while True: time.sleep(1)

    threading.Thread(target=run, daemon=True).start()

# ---------------- MAIN GUI ----------------
root = tk.Tk()
root.title("Advanced Integrity Shield v3.1")
root.geometry("620x550")
root.configure(bg="#0f172a")

tk.Label(root, text="🛡️ Folder Integrity Shield", font=("Segoe UI", 18, "bold"), fg="white", bg="#0f172a").pack(pady=15)

file_frame = tk.Frame(root, bg="#0f172a")
file_frame.pack(pady=10)
file_entry = tk.Entry(file_frame, width=60, bg="#1e293b", fg="white", insertbackground="white")
file_entry.pack(pady=5, ipady=6)
tk.Button(file_frame, text="📂 Browse Folder", command=lambda: file_entry.insert(0, filedialog.askdirectory()), bg="#2563eb", fg="white").pack()

action_frame = tk.Frame(root, bg="#0f172a")
action_frame.pack(pady=10)
# Updated Test Email call to include dummy event_type
tk.Button(action_frame, text="📧 Test Email", command=lambda: threading.Thread(target=send_email_alert, args=("test", "TEST", True), daemon=True).start(), bg="#0ea5e9", fg="white").grid(row=0, column=0, padx=5)
tk.Button(action_frame, text="📜 Live Activity Log", command=open_log_window, bg="#64748b", fg="white").grid(row=0, column=1, padx=5)

tk.Label(root, text="Algorithm", fg="#cbd5f5", bg="#0f172a").pack()
algorithm_var = tk.StringVar(value="sha256")
tk.OptionMenu(root, algorithm_var, "md5", "sha1", "sha256", "sha512").pack()

tk.Button(root, text="🛡️ START SHIELD", command=start_monitoring, bg="#22c55e", fg="white", font=("Segoe UI", 12, "bold"), padx=20, pady=10).pack(pady=20)
status_label = tk.Label(root, text="Status: Waiting...", fg="#94a3b8", bg="#0f172a", font=("Segoe UI", 11, "bold"))
status_label.pack()

result_text = tk.StringVar(value="Ready")
tk.Label(root, textvariable=result_text, fg="#38bdf8", bg="#0f172a", wraplength=500).pack(pady=10)

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
SENDER_PASSWORD = "sriaythirqspukla"
RECEIVER_EMAIL = "rangaridharan@gmail.com"

log_display = None
current_observer = None # Global to track the running monitor

def write_to_live_log(message):
    if log_display:
        log_display.after(0, lambda: log_display.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n"))
        log_display.after(0, lambda: log_display.see(tk.END))

def open_log_window():
    global log_display
    log_win = tk.Toplevel(root)
    log_win.title("Live Activity Monitor")
    log_win.geometry("600x450")
    log_win.configure(bg="#1e293b")
    
    tk.Label(log_win, text="🔴 LIVE SYSTEM ACTIVITY", fg="#ef4444", bg="#1e293b", font=("Segoe UI", 12, "bold")).pack(pady=5)
    log_display = scrolledtext.ScrolledText(log_win, bg="#0f172a", fg="#10b981", font=("Consolas", 10))
    log_display.pack(expand=True, fill='both', padx=10, pady=10)
    
    # Add a Clear Button to the Log Window
    tk.Button(log_win, text="Clear Logs", command=lambda: log_display.delete('1.0', tk.END), bg="#475569", fg="white").pack(pady=5)

def send_email_alert(file_name, event_type, is_test=False):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"✅ Connection Test" if is_test else f"⚠️ SECURITY ALERT: File {event_type}"
        
        body = "SMTP Connection Successful!" if is_test else f"Event: {event_type}\nFile: {os.path.basename(file_name)}\nPath: {file_name}\nTime: {time.ctime()}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        if is_test:
            root.after(0, lambda: messagebox.showinfo("Success", "Test email sent!"))
    except Exception as e:
        err = str(e)
        root.after(0, lambda: messagebox.showerror("Email Error", f"Failed: {err}"))

# ---------------- MONITORING LOGIC ----------------
class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, folder_path, algorithm):
        self.folder_path = os.path.abspath(folder_path)
        self.algorithm = algorithm
        self.baseline_hashes = {}
        self.last_alert_time = 0
        self.processed_events = {} # Prevent duplicate firing within 1 second
        self.create_baseline()

    def create_baseline(self):
        self.baseline_hashes = {}
        for root_dir, _, files in os.walk(self.folder_path):
            for name in files:
                full_path = os.path.join(root_dir, name)
                if "security_log.txt" in name: continue
                self.baseline_hashes[full_path] = calculate_file_hash(full_path, self.algorithm)

    def is_duplicate(self, path, event_type):
        """Filters out multiple OS signals for the same action"""
        current_time = time.time()
        key = (path, event_type)
        if key in self.processed_events:
            if current_time - self.processed_events[key] < 1.0: # 1 second debounce
                return True
        self.processed_events[key] = current_time
        return False

    def on_created(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)

            if "security_log.txt" in file_path or self.is_duplicate(file_path, "created"):
                return

            new_hash = calculate_file_hash(file_path, self.algorithm)

            # ✅ If file existed before → treat as modified
            if file_path in self.baseline_hashes:
                write_to_live_log(f"📝 MODIFIED: {os.path.basename(file_path)}")
                self.baseline_hashes[file_path] = new_hash
                self.trigger_alert(file_path, "MODIFIED")

            else:
                write_to_live_log(f"🆕 NEW FILE: {os.path.basename(file_path)}")
                self.baseline_hashes[file_path] = new_hash
                self.trigger_alert(file_path, "CREATED")

    def on_deleted(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path or self.is_duplicate(file_path, "deleted"): return
            write_to_live_log(f"🗑️ DELETED: {os.path.basename(file_path)}")
            self.baseline_hashes.pop(file_path, None)
            self.trigger_alert(file_path, "DELETED")

    def on_modified(self, event):
        if not event.is_directory:
            file_path = os.path.abspath(event.src_path)
            if "security_log.txt" in file_path or file_path.endswith(".py"): return
            if self.is_duplicate(file_path, "modified"): return

            new_hash = calculate_file_hash(file_path, self.algorithm)
            if file_path in self.baseline_hashes:
                if new_hash != self.baseline_hashes[file_path]:
                    write_to_live_log(f"📝 MODIFIED: {os.path.basename(file_path)}")
                    self.baseline_hashes[file_path] = new_hash
                    self.trigger_alert(file_path, "MODIFIED")
                else:
                    write_to_live_log(f"✔️ SAFE: {os.path.basename(file_path)} (Integrity Intact)")
                    root.after(0, lambda: result_text.set(f"✅ Intact: {os.path.basename(file_path)}"))
                    root.after(0, lambda: status_label.config(text="Status: SHIELD ACTIVE", fg="#22c55e"))

    def trigger_alert(self, file_path, msg_type):
        logging.warning(f"{msg_type}: {file_path}")
        root.after(0, lambda: result_text.set(f"⚠️ {msg_type}: {os.path.basename(file_path)}"))
        curr = time.time()
        if curr - self.last_alert_time > 15:
            threading.Thread(target=send_email_alert, args=(file_path, msg_type), daemon=True).start()
            self.last_alert_time = curr

def calculate_file_hash(file_path, algorithm):
    try:
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except: return None

def start_monitoring():
    global current_observer
    path = file_entry.get()
    algo = algorithm_var.get()
    
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Select valid folder first")
        return

    # ✅ STOP existing observer if it's already running (Fixes multiple outputs)
    if current_observer:
        current_observer.stop()
        write_to_live_log("Stopping previous monitor...")

    if not log_display: open_log_window()
    write_to_live_log(f"🛡️ Shield Initialized [{algo.upper()}] on {os.path.basename(path)}")

    def run():
        global current_observer
        event_handler = FolderChangeHandler(path, algo)
        current_observer = Observer()
        current_observer.schedule(event_handler, path, recursive=True)
        current_observer.start()
        root.after(0, lambda: status_label.config(text="Status: SHIELD ACTIVE", fg="#22c55e"))
        try:
            while True: time.sleep(1)
        except:
            current_observer.stop()
        current_observer.join()

    threading.Thread(target=run, daemon=True).start()

# ---------------- MAIN GUI ----------------
root = tk.Tk()
root.title("Integrity Shield Pro v3.2")
root.geometry("620x550")
root.configure(bg="#0f172a")

tk.Label(root, text="🛡️ Folder Integrity Shield", font=("Segoe UI", 18, "bold"), fg="white", bg="#0f172a").pack(pady=15)

file_frame = tk.Frame(root, bg="#0f172a")
file_frame.pack(pady=10)
file_entry = tk.Entry(file_frame, width=50, bg="#1e293b", fg="white", insertbackground="white")
file_entry.pack(side=tk.LEFT, padx=5, ipady=6)
tk.Button(file_frame, text="📂 Browse", command=lambda: (file_entry.delete(0, tk.END), file_entry.insert(0, filedialog.askdirectory())), bg="#2563eb", fg="white").pack(side=tk.LEFT)

action_frame = tk.Frame(root, bg="#0f172a")
action_frame.pack(pady=10)
tk.Button(action_frame, text="📧 Test Email", command=lambda: threading.Thread(target=send_email_alert, args=("test", "TEST", True), daemon=True).start(), bg="#0ea5e9", fg="white").grid(row=0, column=0, padx=5)
tk.Button(action_frame, text="📜 Activity Log", command=open_log_window, bg="#64748b", fg="white").grid(row=0, column=1, padx=5)

tk.Label(root, text="Security Algorithm", fg="#cbd5f5", bg="#0f172a").pack()
algorithm_var = tk.StringVar(value="sha256")
tk.OptionMenu(root, algorithm_var, "md5", "sha1", "sha256", "sha512").pack()

tk.Button(root, text="🛡️ START MONITORING", command=start_monitoring, bg="#22c55e", fg="white", font=("Segoe UI", 12, "bold"), padx=20, pady=10).pack(pady=20)
status_label = tk.Label(root, text="Status: Waiting...", fg="#94a3b8", bg="#0f172a", font=("Segoe UI", 11, "bold"))
status_label.pack()

result_text = tk.StringVar(value="System Ready")
tk.Label(root, textvariable=result_text, fg="#38bdf8", bg="#0f172a", wraplength=500).pack(pady=10)

root.mainloop()

