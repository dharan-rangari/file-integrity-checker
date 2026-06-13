import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os

class FileIntegrityChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro File Integrity Checker")
        self.root.geometry("550x450")
        
        # UI Setup
        self.create_widgets()

    def create_widgets(self):
        # File Selection
        tk.Label(self.root, text="File Path:", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        self.file_entry = tk.Entry(self.root, width=60)
        self.file_entry.pack(pady=5, padx=20)
        tk.Button(self.root, text="Browse File", command=self.select_file).pack()

        # Algorithm Selection
        tk.Label(self.root, text="Select Algorithm:", font=('Arial', 10, 'bold')).pack(pady=(15, 0))
        self.algo_var = tk.StringVar(value="sha256")
        self.algo_menu = ttk.Combobox(self.root, textvariable=self.algo_var, state="readonly")
        self.algo_menu['values'] = ("md5", "sha1", "sha256", "sha512")
        self.algo_menu.pack(pady=5)

        # Expected Hash
        tk.Label(self.root, text="Expected Hash (Check against):", font=('Arial', 10, 'bold')).pack(pady=(15, 0))
        self.expected_entry = tk.Entry(self.root, width=60)
        self.expected_entry.pack(pady=5, padx=20)

        # Progress Bar (For better UX)
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="indeterminate")
        self.progress.pack(pady=10)

        # Action Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.verify_btn = tk.Button(btn_frame, text="Verify Integrity", bg="#2ecc71", fg="white", 
                                    command=self.start_verification_thread, width=15)
        self.verify_btn.grid(row=0, column=0, padx=5)
        
        tk.Button(btn_frame, text="Copy Result", command=self.copy_to_clipboard, width=15).grid(row=0, column=1, padx=5)

        # Result Display
        self.result_var = tk.StringVar(value="Status: Waiting for input...")
        self.result_label = tk.Label(self.root, textvariable=self.result_var, wraplength=500, font=('Courier', 9))
        self.result_label.pack(pady=20)

    def select_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, path)

    def start_verification_thread(self):
        # Start hashing in a background thread so the UI doesn't freeze
        thread = threading.Thread(target=self.run_verification)
        thread.start()

    def run_verification(self):
        file_path = self.file_entry.get()
        algo = self.algo_var.get()
        expected = self.expected_entry.get().strip().lower()

        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Selected file does not exist.")
            return

        self.verify_btn.config(state="disabled")
        self.progress.start()
        self.result_var.set("Calculating hash... please wait.")
        self.result_label.config(fg="black")

        try:
            # Hashing Logic
            hasher = hashlib.new(algo)
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            
            calculated = hasher.hexdigest().lower()
            
            # Comparison Logic
            if not expected:
                self.result_var.set(f"Calculated Hash:\n{calculated}")
                self.result_label.config(fg="blue")
            elif calculated == expected:
                self.result_var.set(f"MATCH! ✅\n{calculated}")
                self.result_label.config(fg="green")
            else:
                self.result_var.set(f"MISMATCH! ❌\nCalculated: {calculated}")
                self.result_label.config(fg="red")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.progress.stop()
            self.verify_btn.config(state="normal")

    def copy_to_clipboard(self):
        res = self.result_var.get()
        if "Calculated:" in res:
            final_hash = res.split("Calculated: ")[1]
        elif "\n" in res:
            final_hash = res.split("\n")[1]
        else:
            final_hash = res
            
        self.root.clipboard_clear()
        self.root.clipboard_append(final_hash)
        messagebox.showinfo("Success", "Hash copied to clipboard!")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileIntegrityChecker(root)
    root.mainloop()