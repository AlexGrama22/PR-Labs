import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ftplib import FTP


# Function to send an email
def send_email(destination_email, subject, email_text, file_link):
    sender_email = "alexgrama836@gmail.com"
    sender_password = " "

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = destination_email
    message['Subject'] = subject
    message.attach(MIMEText(email_text + "\n\nFile link: " + file_link, 'plain'))

    session = smtplib.SMTP('smtp.gmail.com', 587)  # Use Gmail's SMTP server
    session.starttls()  # Enable security
    session.login(sender_email, sender_password)  # Login with email and password
    session.sendmail(sender_email, destination_email, message.as_string())
    session.quit()


# Function to upload a file via FTP
def upload_file_ftp(file_path):
    ftp_server = "138.68.98.108"  # FTP server IP
    username = "yourusername"
    password = "yourusername"
    remote_path = "/home/somedirectory/FAF-211/grama/"  # FTP remote path

    remote_file_path = remote_path + file_path.split('/')[-1]

    ftp = FTP(ftp_server)
    ftp.login(username, password)
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {remote_file_path}', file)
    ftp.quit()

    web_accessible_path = "/FAF-211/grama/" + file_path.split('/')[-1]
    return "http://138.68.98.108" + web_accessible_path


# GUI functions
def browse_file():
    filename = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, filename)


def submit():
    destination_email = destination_email_entry.get()
    subject = subject_entry.get()
    email_text = email_text_entry.get("1.0", tk.END)
    file_path = file_path_entry.get()

    # Upload the file and send the email
    try:
        file_link = upload_file_ftp(file_path)
        send_email(destination_email, subject, email_text, file_link)
        messagebox.showinfo("Success", "Email has been sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Tkinter GUI setup
# Tkinter GUI setup with a modern theme
root = ThemedTk(theme="equilux")
root.title("Email Sender UI")

# Use a frame for better layout control
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Custom Font
custom_font = ('Arial', 12)

# Widgets with improved styling
ttk.Label(main_frame, text="Enter destination email:", font=custom_font).pack(fill=tk.X)
destination_email_entry = ttk.Entry(main_frame, width=50, font=custom_font)
destination_email_entry.pack(fill=tk.X, pady=5)

ttk.Label(main_frame, text="Enter email subject:", font=custom_font).pack(fill=tk.X)
subject_entry = ttk.Entry(main_frame, width=50, font=custom_font)
subject_entry.pack(fill=tk.X, pady=5)

ttk.Label(main_frame, text="Enter email text:", font=custom_font).pack(fill=tk.X)
email_text_entry = tk.Text(main_frame, height=10, width=50, font=custom_font)
email_text_entry.pack(fill=tk.BOTH, expand=True, pady=5)

ttk.Label(main_frame, text="Enter path to the file to upload:", font=custom_font).pack(fill=tk.X)
file_path_entry = ttk.Entry(main_frame, width=50, font=custom_font)
file_path_entry.pack(fill=tk.X, pady=5)

browse_button = ttk.Button(main_frame, text="Browse", command=browse_file)
browse_button.pack(side=tk.LEFT, pady=5)

submit_button = ttk.Button(main_frame, text="Send Email", command=submit)
submit_button.pack(side=tk.RIGHT, pady=5)

root.mainloop()