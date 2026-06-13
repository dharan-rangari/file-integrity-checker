import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox

# --- LOGIC FUNCTIONS ---

def calculate_file_hash(file_path, algorithm):
    """
    Calculate the hash of a file using the specified hashing algorithm.
    """
    try:
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):  # Read the file in chunks
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except FileNotFoundError:
        messagebox.showerror("Error", f"The file '{file_path}' does not exist.")
        return None
    except ValueError:
        messagebox.showerror("Error", f"Unsupported hashing algorithm '{algorithm}'.")
        return None

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def verify_file_integrity():
    file_path = file_entry.get()
    algorithm = algorithm_var.get()
    # .lower() and .strip() ensure comparison works even with extra spaces or Caps Lock
    expected_hash = expected_hash_entry.get().strip().lower()

    if not file_path or not algorithm:
        messagebox.showerror("Error", "Please select a file and hashing algorithm.")
        return

    file_hash = calculate_file_hash(file_path, algorithm)
    if file_hash:
        result_text.set(f"Calculated {algorithm.upper()} Hash:\n{file_hash}")
        
        if expected_hash:
            if file_hash == expected_hash:
                result_label.config(fg="green")
                messagebox.showinfo("Verification Result", "✅ File integrity is intact!")
            else:
                result_label.config(fg="red")
                messagebox.showwarning("Verification Result", "❌ File integrity is compromised!")

def calculate_hash_only():
    file_path = file_entry.get()
    algorithm = algorithm_var.get()

    if not file_path or not algorithm:
        messagebox.showerror("Error", "Please select a file and hashing algorithm.")
        return

    file_hash = calculate_file_hash(file_path, algorithm)
    if file_hash:
        result_label.config(fg="blue")
        result_text.set(f"Calculated {algorithm.upper()} Hash:\n{file_hash}")

def copy_to_clipboard():
    # Extract the hash value from the result text
    content = result_text.get()
    if "Hash:\n" in content:
        hash_value = content.split("Hash:\n")[-1].strip()
        root.clipboard_clear()
        root.clipboard_append(hash_value)
        root.update()
        messagebox.showinfo("Copied", "Hash value copied to clipboard!")
    else:
        messagebox.showerror("Error", "No hash value to copy.")

def reset_fields():
    """
    Clears all inputs and resets the UI.
    """
    file_entry.delete(0, tk.END)
    expected_hash_entry.delete(0, tk.END)
    algorithm_var.set("sha256")
    result_text.set("")
    result_label.config(fg="blue")

# --- UI INITIALIZATION ---

root = tk.Tk()
root.title("Secure File Integrity Checker")
root.geometry("550x450")

# File selection section
tk.Label(root, text="Select File:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
file_entry = tk.Entry(root, width=50)
file_entry.pack(pady=5, fill="x", padx=20)
tk.Button(root, text="Browse", command=select_file).pack()

# Algorithm selection
tk.Label(root, text="Choose Hashing Algorithm:", font=("Arial", 10, "bold")).pack(pady=(15, 0))
algorithm_var = tk.StringVar(value="sha256")
algorithm_dropdown = tk.OptionMenu(root, algorithm_var, "md5", "sha1", "sha256", "sha512")
algorithm_dropdown.pack(pady=5)

# Expected hash input
tk.Label(root, text="Expected Hash (optional):", font=("Arial", 10, "bold")).pack(pady=(15, 0))
expected_hash_entry = tk.Entry(root, width=50)
expected_hash_entry.pack(pady=5, fill="x", padx=20)

# Button Frame for horizontal alignment
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

tk.Button(button_frame, text="Verify Integrity", command=verify_file_integrity, bg="#2ecc71", fg="white").grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Calculate Only", command=calculate_hash_only).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Reset", command=reset_fields, bg="#e74c3c", fg="white").grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Copy Hash", command=copy_to_clipboard).grid(row=0, column=3, padx=5)

# Result display

result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, fg="blue", font=("Courier", 9), wraplength=500, justify="center")
result_label.pack(pady=10, fill="x", padx=20)

root.mainloop()