🔐Folder Integrity Shield Pro

A Python-based File & Folder Integrity Monitoring System that detects unauthorized file changes in real time using cryptographic hashing and sends instant email alerts.

🚀 Features
1)Real-time folder monitoring
2)Integrity verification using:
	(i)MD5
	(ii)SHA-1
	(iii)SHA-256
	(iv)SHA-512
3)Email alerts for security events
4)Live Activity Log window
5)Automatic security logging
6)Detection of:
	(i)File Creation
	(ii)File Modification
	(iii)File Deletion
7)Recursive monitoring of subfolders
8)Duplicate event filtering

Technologies Used:
•Python
•Tkinter
•Watchdog
•Hashlib
•SMTP (Gmail)
•Logging
•Threading

📂 Project Workflow:
Select Folder -> arrow Generate Baseline Hashes -> Start Monitoring -> Detect File Events -> Verify Integrity -> Log Activity + Send Email Alert

📧 Email Alert System
The project uses Gmail SMTP to send notifications whenever a file is:
•Created
•Modified
•Deleted

Each alert contains:
•Event Type
•File Name
•File Path
•Timestamp

⚙️ Installation
Clone Repository
git clone https://github.com/yourusername/folder-integrity-shield.git
cd folder-integrity-shield
Install Required Libraries: pip install watchdog
Tkinter is included with most Python installations.

📧 Gmail Configuration
This project uses Gmail SMTP for email alerts.
Enable Two-Step Verification
Go to:
https://myaccount.google.com/security

Enable:
2-Step Verification

Generate App Password
Go to:
https://myaccount.google.com/apppasswords

Generate an App Password and update:

SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
RECEIVER_EMAIL = "receiver@gmail.com"

▶️ How to Run : python main.py
