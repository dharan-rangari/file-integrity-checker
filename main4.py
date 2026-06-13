'''import hashlib
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

        if changed_path == self.file_path:
            new_hash = calculate_file_hash(self.file_path, self.algorithm)

        if new_hash != self.original_hash:
            
            # ✅ Thread-safe popup
            def show_alert():
                messagebox.showwarning("ALERT", "⚠️ File has been modified!")

            root.after(0, show_alert)

            # ✅ Update GUI text
            root.after(0, lambda: result_text.set("⚠️ File Modified!"))

        else:
            root.after(0, lambda: result_text.set("✅ File is Safe"))

    def on_modified(self, event):
        if not event.is_directory:
            print("Modified event detected:", event.src_path)  # ✅ FIX 3 HERE
            self.check_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            print("Created event detected:", event.src_path)  # ✅ FIX 3 HERE
            self.check_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            print("Moved event detected:", event.dest_path)  # ✅ FIX 3 HERE
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

root.mainloop()'''



import hashlib
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

# ---------------- LOGGING CONFIGURATION ----------------
logging.basicConfig(
    filename="security_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ---------------- EMAIL CONFIGURATION ----------------
# REPLACE THESE WITH YOUR ACTUAL DATA
SENDER_EMAIL = "rangaridharan676@gmail.com" 
SENDER_PASSWORD = "vkavjtdtcffaimcw" 
RECEIVER_EMAIL = "gunjeshnayak12@gmail.com"

def send_email_alert(file_name, is_test=False):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        if is_test:
            msg['Subject'] = "✅ Integrity Tool: Connection Test"
            body = "This is a test email. Your Python script is successfully connected to Gmail!"
        else:
            msg['Subject'] = "⚠️ SECURITY ALERT: File Modification"
            body = f"Alert! The following file was modified:\n\nPath: {file_name}\nTime: {time.ctime()}"

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        if is_test:
            messagebox.showinfo("Success", "Test email sent! Check your inbox.")
    except Exception as e:
        error_msg = f"Email Error: {str(e)}"
        logging.error(error_msg)
        messagebox.showerror("Email Failed", "Could not send email. Check your App Password and Internet.")

# ---------------- HASH FUNCTION ----------------
def calculate_file_hash(file_path, algorithm):
    try:
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logging.error(f"Hash Error: {e}")
        return None

# ---------------- GUI ACTIONS ----------------
def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def test_connection():
    """Triggered by the Test Email button"""
    threading.Thread(target=send_email_alert, args=("None", True), daemon=True).start()

# ---------------- REAL-TIME MONITOR ----------------
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path, algorithm, original_hash):
        self.file_path = os.path.abspath(file_path)
        self.algorithm = algorithm
        self.original_hash = original_hash
        self.last_alert_time = 0 

    def check_file(self, changed_path):
        if os.path.abspath(changed_path) == self.file_path:
            new_hash = calculate_file_hash(self.file_path, self.algorithm)
            
            if new_hash and new_hash != self.original_hash:
                root.after(0, lambda: result_text.set("⚠️ MODIFIED! Alert Sent & Logged."))
                logging.warning(f"MODIFICATION DETECTED: {self.file_path}")
                
                current_time = time.time()
                if current_time - self.last_alert_time > 15: # 15s cooldown
                    threading.Thread(target=send_email_alert, args=(self.file_path,), daemon=True).start()
                    self.last_alert_time = current_time
            else:
                root.after(0, lambda: result_text.set(" File is Safe"))

    def on_modified(self, event):
        if not event.is_directory:
            self.check_file(event.src_path)

def start_monitoring():
    file_path = file_entry.get()
    if not file_path or not os.path.exists(file_path):
        messagebox.showerror("Error", "Select a valid file first")
        return

    def run_observer():
        orig_hash = calculate_file_hash(file_path, algorithm_var.get())
        event_handler = FileChangeHandler(file_path, algorithm_var.get(), orig_hash)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(file_path), recursive=False)
        observer.start()
        logging.info(f"Started monitoring: {file_path}")
        messagebox.showinfo("Monitoring", "System Active!")
        try:
            while True: time.sleep(1)
        except: observer.stop()
        observer.join()

    threading.Thread(target=run_observer, daemon=True).start()

# ---------------- GUI SETUP ----------------
root = tk.Tk()
root.title("File Integrity Checker")
root.geometry("520x450")
root.configure(bg="#f0f0f0")

tk.Label(root, text="Step 1: Select Target File", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=5)
file_entry = tk.Entry(root, width=60)
file_entry.pack()
tk.Button(root, text="Browse File", command=select_file).pack(pady=5)

tk.Label(root, text="Step 2: Setup Alerts", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=5)
tk.Button(root, text="📧 Send Test Email", command=test_connection, bg="#3498db", fg="white").pack()

tk.Label(root, text="Algorithm", bg="#f0f0f0").pack()
algorithm_var = tk.StringVar(value="sha256")
tk.OptionMenu(root, algorithm_var, "md5", "sha1", "sha256", "sha512").pack()

tk.Button(root, text="🛡️ START MONITORING", command=start_monitoring, 
          bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), height=2).pack(pady=20)

result_text = tk.StringVar(value="Status: Ready")
tk.Label(root, textvariable=result_text, fg="#c0392b", font=("Arial", 10, "italic"), bg="#f0f0f0").pack()

root.mainloop()