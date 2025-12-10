#!/usr/bin/env python3
"""
PDF Password Remover
A GUI application to remove passwords from PDF files
GitHub: https://github.com/yourusername/pdf-password-remover
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
import os
import time
import shutil
import tempfile
import sys
import webbrowser
from datetime import datetime

# Try to import PDF libraries
try:
    import pikepdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Version
VERSION = "1.0.0"
GITHUB_URL = "https://github.com/yourusername/pdf-password-remover"

class PDFUnlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"PDF Password Remover v{VERSION}")
        self.root.geometry("850x700")
        
        # Set icon if available
        self.set_icon()
        
        # Variables
        self.pdf_file = ""
        self.password = ""
        self.unlocked_file = ""
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_unlocker_")
        
        # Common passwords to try
        self.common_passwords = self.load_common_passwords()
        
        # Setup UI
        self.setup_ui()
        
        # Check library
        if not PDF_AVAILABLE:
            self.show_library_error()
    
    def set_icon(self):
        """Try to set window icon"""
        icon_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico'),
            os.path.join(os.path.dirname(__file__), 'icon.ico'),
            'icon.ico'
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                    break
                except:
                    pass
    
    def load_common_passwords(self):
        """Load common passwords for brute force attack"""
        passwords = [
            # Most common passwords worldwide
            "", "123456", "password", "12345678", "qwerty",
            "123456789", "12345", "1234", "111111", "1234567",
            "dragon", "123123", "admin", "welcome", "monkey",
            "letmein", "password1", "abc123", "123", "login",
            
            # Common variations
            "passw0rd", "master", "hello", "test", "demo",
            "admin123", "letmein123", "welcome123", "password123",
            "123qwe", "1q2w3e4r", "qazwsx", "password@123",
            
            # Year based
            "2020", "2021", "2022", "2023", "2024", "2025",
            "2019", "2018", "2017",
            
            # Simple words
            "sunshine", "iloveyou", "trustno1", "superman",
            "mustang", "football", "baseball", "starwars",
            "computer", "corona2020", "covid19",
            
            # Business/Office
            "company", "business", "work", "office", "home",
            "user", "client", "customer", "member", "guest",
            "employee", "staff", "manager", "director", "owner",
            
            # Common defaults
            "changeme", "default", "temp", "temp123", "pass",
            "access", "secret", "private", "god", "love",
        ]
        
        # Add some variations
        variations = []
        for pwd in passwords:
            if pwd:  # Skip empty for variations
                variations.extend([
                    pwd,
                    pwd.upper(),
                    pwd + "!",
                    pwd + "@",
                    pwd + "#",
                    pwd + "$",
                    pwd + "123",
                    pwd + "456",
                    pwd + "789",
                ])
        
        # Add empty password
        variations.append("")
        
        # Remove duplicates and return
        return list(set(variations))[:200]  # Limit to 200 passwords
    
    def show_library_error(self):
        """Show library installation error"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        error_frame = ttk.Frame(self.root, padding="30")
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(error_frame, text="🔧 Setup Required", 
                 font=('Arial', 18, 'bold')).pack(pady=(0, 20))
        
        error_msg = "Required library 'pikepdf' is not installed.\n\n"
        error_msg += "This library is needed to process PDF files.\n\n"
        error_msg += "Installation methods:\n"
        error_msg += "1. Click 'Auto Install' button below\n"
        error_msg += "2. Run in terminal: pip install pikepdf\n"
        error_msg += "3. See GitHub page for more help"
        
        ttk.Label(error_frame, text=error_msg, justify=tk.LEFT).pack(pady=(0, 30))
        
        btn_frame = ttk.Frame(error_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="🔄 Auto Install", 
                  command=self.install_library, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="📖 View GitHub", 
                  command=lambda: webbrowser.open(GITHUB_URL), width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🚪 Exit", 
                  command=self.root.quit, width=15).pack(side=tk.LEFT, padx=5)
    
    def install_library(self):
        """Try to install the required library"""
        import subprocess
        
        install_dialog = tk.Toplevel(self.root)
        install_dialog.title("Installing Library")
        install_dialog.geometry("450x200")
        install_dialog.transient(self.root)
        install_dialog.grab_set()
        
        # Center dialog
        install_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (450 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (200 // 2)
        install_dialog.geometry(f"450x200+{x}+{y}")
        
        main_frame = ttk.Frame(install_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Installing pikepdf library...", 
                 font=('Arial', 12)).pack(pady=20)
        
        progress = ttk.Progressbar(main_frame, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        self.status_label = ttk.Label(main_frame, text="Please wait...")
        self.status_label.pack(pady=10)
        
        install_dialog.update()
        
        def do_install():
            try:
                # Update status
                self.root.after(0, lambda: self.status_label.config(text="Downloading..."))
                
                # Try to install
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pikepdf"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.on_install_success(install_dialog))
                else:
                    self.root.after(0, lambda: self.on_install_failed(
                        install_dialog, 
                        result.stderr or "Unknown error"
                    ))
                    
            except Exception as e:
                self.root.after(0, lambda: self.on_install_failed(install_dialog, str(e)))
        
        # Run installation in thread
        import threading
        thread = threading.Thread(target=do_install)
        thread.daemon = True
        thread.start()
    
    def on_install_success(self, dialog):
        dialog.destroy()
        messagebox.showinfo("Success", 
            "Library installed successfully!\n\n"
            "The application will now restart.")
        
        # Restart the application
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def on_install_failed(self, dialog, error):
        dialog.destroy()
        
        error_msg = f"Failed to install library:\n\n{error[:200]}...\n\n"
        error_msg += "Please try manual installation:\n"
        error_msg += "1. Open Command Prompt/Terminal\n"
        error_msg += "2. Run: pip install pikepdf\n"
        error_msg += "3. Restart this application"
        
        messagebox.showerror("Installation Failed", error_msg)
    
    def setup_ui(self):
        # Configure styles
        self.setup_styles()
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title bar
        self.setup_title_bar(main_frame)
        
        # File selection
        self.setup_file_section(main_frame)
        
        # Password options
        self.setup_password_section(main_frame)
        
        # Progress area
        self.setup_progress_section(main_frame)
        
        # Action buttons
        self.setup_action_buttons(main_frame)
        
        # Status bar
        self.setup_status_bar()
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        
        # Configure colors
        style.configure("Title.TLabel", font=('Arial', 16, 'bold'))
        style.configure("Subtitle.TLabel", font=('Arial', 10))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")
        style.configure("Warning.TLabel", foreground="orange")
        
        # Configure buttons
        style.configure("Primary.TButton", font=('Arial', 10, 'bold'))
        style.configure("Accent.TButton", font=('Arial', 10, 'bold'), padding=5)
    
    def setup_title_bar(self, parent):
        """Setup title and menu bar"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        ttk.Label(title_frame, text="🔓 PDF Password Remover", 
                 style="Title.TLabel").pack(side=tk.LEFT)
        
        # Version label
        ttk.Label(title_frame, text=f"v{VERSION}", 
                 font=('Arial', 9)).pack(side=tk.LEFT, padx=10)
        
        # GitHub button
        ttk.Button(title_frame, text="GitHub", 
                  command=lambda: webbrowser.open(GITHUB_URL),
                  width=8).pack(side=tk.RIGHT)
        
        # Help button
        ttk.Button(title_frame, text="Help", 
                  command=self.show_help,
                  width=8).pack(side=tk.RIGHT, padx=5)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=5)
    
    def setup_file_section(self, parent):
        """Setup file selection section"""
        file_frame = ttk.LabelFrame(parent, text="📁 Select PDF File", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File path
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="PDF File:").pack(side=tk.LEFT)
        
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(path_frame, textvariable=self.file_var, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        ttk.Button(path_frame, text="Browse...", 
                  command=self.browse_file, width=10).pack(side=tk.LEFT)
        
        # File info
        self.file_info = ttk.Label(file_frame, text="No file selected", 
                                  foreground="gray")
        self.file_info.pack(anchor='w', pady=(5, 0))
    
    def setup_password_section(self, parent):
        """Setup password options section"""
        pass_frame = ttk.LabelFrame(parent, text="🔑 Password Options", padding="15")
        pass_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quick actions frame
        quick_frame = ttk.Frame(pass_frame)
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(quick_frame, text="Try Common Passwords", 
                  command=self.try_common_passwords,
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(quick_frame, text="Check If Encrypted", 
                  command=self.check_encryption,
                  width=18).pack(side=tk.LEFT)
        
        # Manual password entry
        manual_frame = ttk.Frame(pass_frame)
        manual_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(manual_frame, text="Manual Password:").pack(side=tk.LEFT)
        
        self.pass_var = tk.StringVar()
        self.pass_entry = ttk.Entry(manual_frame, textvariable=self.pass_var, 
                                   show="•", width=25)
        self.pass_entry.pack(side=tk.LEFT, padx=10)
        
        self.show_pass_var = tk.BooleanVar()
        ttk.Checkbutton(manual_frame, text="Show", 
                       variable=self.show_pass_var,
                       command=self.toggle_password).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(manual_frame, text="Test Password", 
                  command=self.test_manual_password).pack(side=tk.LEFT)
        
        # Password stats
        self.pass_stats = ttk.Label(pass_frame, 
                                   text=f"Common passwords loaded: {len(self.common_passwords)}",
                                   font=('Arial', 9))
        self.pass_stats.pack(anchor='w', pady=(5, 0))
    
    def setup_progress_section(self, parent):
        """Setup progress and log section"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Progress & Log", padding="15")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var,
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status labels
        status_frame = ttk.Frame(progress_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready", 
                                     font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(status_frame, text="", 
                                   font=('Arial', 9))
        self.time_label.pack(side=tk.RIGHT)
        
        # Log text area
        self.status_text = scrolledtext.ScrolledText(progress_frame, 
                                                    height=12,
                                                    wrap=tk.WORD,
                                                    font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Log controls
        log_controls = ttk.Frame(progress_frame)
        log_controls.pack(fill=tk.X)
        
        ttk.Button(log_controls, text="Clear Log", 
                  command=self.clear_log, width=10).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(log_controls, text="Copy Log", 
                  command=self.copy_log, width=10).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(log_controls, text="Save Log", 
                  command=self.save_log, width=10).pack(side=tk.RIGHT, padx=5)
    
    def setup_action_buttons(self, parent):
        """Setup action buttons"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.unlock_btn = ttk.Button(action_frame, text="🔓 Unlock PDF", 
                                    command=self.unlock_pdf,
                                    state='disabled',
                                    width=15,
                                    style="Primary.TButton")
        self.unlock_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_btn = ttk.Button(action_frame, text="💾 Save Unlocked PDF", 
                                  command=self.save_unlocked_pdf,
                                  state='disabled',
                                  width=20)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_btn = ttk.Button(action_frame, text="📂 Open File Location", 
                                  command=self.open_file_location,
                                  state='disabled',
                                  width=20)
        self.open_btn.pack(side=tk.LEFT)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = ttk.Label(self.root, 
                                   text="Ready - Select a PDF file to begin", 
                                   relief=tk.SUNKEN, 
                                   anchor=tk.W,
                                   font=('Arial', 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_help(self):
        """Show help dialog"""
        help_text = f"""PDF Password Remover v{VERSION}

Features:
1. Remove passwords from PDF files
2. Try common passwords automatically
3. Manual password entry
4. Save unlocked PDFs

How to Use:
1. Click 'Browse' to select a PDF file
2. Click 'Try Common Passwords' or enter password manually
3. Click 'Unlock PDF' to remove password
4. Click 'Save Unlocked PDF' to save the file

Requirements:
- Python 3.6 or higher
- pikepdf library (will auto-install)

GitHub: {GITHUB_URL}

Note: Use only on PDF files you own or have permission to unlock.
"""
        
        messagebox.showinfo("Help & About", help_text)
    
    def toggle_password(self):
        """Toggle password visibility"""
        if self.show_pass_var.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="•")
    
    def browse_file(self):
        """Browse for PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            self.pdf_file = filename
            self.file_var.set(filename)
            
            # Update file info
            self.update_file_info()
    
    def update_file_info(self):
        """Update file information display"""
        if not self.pdf_file:
            return
        
        try:
            if os.path.exists(self.pdf_file):
                size = os.path.getsize(self.pdf_file) / 1024  # KB
                mod_time = time.ctime(os.path.getmtime(self.pdf_file))
                
                info_text = f"✓ {os.path.basename(self.pdf_file)} "
                info_text += f"({size:.1f} KB, Modified: {mod_time})"
                
                self.file_info.config(text=info_text, foreground="green")
                self.log_message(f"Selected: {os.path.basename(self.pdf_file)}")
                self.update_status(f"File selected: {os.path.basename(self.pdf_file)}")
            else:
                self.file_info.config(text="✗ File not found", foreground="red")
                self.log_message(f"Error: File not found")
        except Exception as e:
            self.file_info.config(text=f"✗ Error: {str(e)[:50]}", foreground="red")
    
    def check_encryption(self):
        """Check if PDF is encrypted"""
        if not self.pdf_file:
            messagebox.showerror("Error", "Please select a PDF file first")
            return
        
        if not os.path.exists(self.pdf_file):
            messagebox.showerror("Error", "Selected file does not exist")
            return
        
        if not PDF_AVAILABLE:
            messagebox.showerror("Error", "PDF library not available")
            return
        
        self.log_message("\n" + "="*50)
        self.log_message("Checking PDF encryption...")
        
        try:
            with open(self.pdf_file, 'rb') as f:
                try:
                    pdf = pikepdf.Pdf.open(f)
                    if pdf.is_encrypted:
                        self.log_message("✓ File is ENCRYPTED (password protected)")
                        messagebox.showinfo("Encryption Check", 
                            "This PDF is ENCRYPTED.\n\n"
                            "You need a password to unlock it.")
                    else:
                        self.log_message("✓ File is NOT ENCRYPTED")
                        messagebox.showinfo("Encryption Check", 
                            "This PDF is NOT ENCRYPTED.\n\n"
                            "No password needed to open it.")
                except pikepdf.PasswordError:
                    self.log_message("✓ File is ENCRYPTED (password protected)")
                    messagebox.showinfo("Encryption Check", 
                        "This PDF is ENCRYPTED.\n\n"
                        "You need a password to unlock it.")
        except Exception as e:
            self.log_message(f"✗ Error checking file: {str(e)}")
            messagebox.showerror("Error", f"Could not check file:\n{str(e)}")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=f"Status: {message}")
    
    def clear_log(self):
        """Clear the log"""
        self.status_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
    
    def copy_log(self):
        """Copy log to clipboard"""
        log_content = self.status_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        self.log_message("Log copied to clipboard")
    
    def save_log(self):
        """Save log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Log File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.status_text.get(1.0, tk.END))
                self.log_message(f"Log saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log:\n{str(e)}")
    
    def try_common_passwords(self):
        """Try common passwords"""
        if not self.pdf_file:
            messagebox.showerror("Error", "Please select a PDF file first")
            return
        
        if not os.path.exists(self.pdf_file):
            messagebox.showerror("Error", "Selected file does not exist")
            return
        
        if not PDF_AVAILABLE:
            messagebox.showerror("Error", "PDF library not available")
            return
        
        self.log_message("\n" + "="*50)
        self.log_message("Starting common password test...")
        self.log_message(f"Testing {len(self.common_passwords)} passwords")
        
        # Reset progress
        self.progress_var.set(0)
        self.start_time = time.time()
        
        # Disable buttons during process
        self.unlock_btn.config(state='disabled')
        
        # Try passwords
        found = False
        
        for i, password in enumerate(self.common_passwords):
            # Update progress
            progress = (i + 1) / len(self.common_passwords) * 100
            self.progress_var.set(progress)
            
            # Update time
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"Time: {elapsed:.1f}s")
            
            # Show which password we're trying
            display_pass = "''" if password == "" else f"'{password}'"
            self.update_status(f"Testing: {display_pass}")
            self.root.update()
            
            # Try the password
            if self.test_password(password):
                self.password = password
                elapsed = time.time() - self.start_time
                
                self.log_message(f"\n✓ SUCCESS! Password found: {display_pass}")
                self.log_message(f"✓ Found at attempt #{i+1}")
                self.log_message(f"✓ Time taken: {elapsed:.1f} seconds")
                
                self.update_status(f"Password found: {display_pass}")
                found = True
                break
        
        self.progress_var.set(100)
        
        if found:
            self.unlock_btn.config(state='normal')
            messagebox.showinfo("Success", 
                f"Password found!\n\n"
                f"Password: {display_pass}\n"
                f"Attempts: {i+1}\n"
                f"Time: {elapsed:.1f}s\n\n"
                f"Click 'Unlock PDF' to remove the password.")
        else:
            elapsed = time.time() - self.start_time
            self.log_message(f"\n✗ No password found after {len(self.common_passwords)} attempts")
            self.log_message(f"✗ Time spent: {elapsed:.1f} seconds")
            self.update_status("No password found")
            
            messagebox.showinfo("No Password Found", 
                f"No common password worked.\n\n"
                f"Tested: {len(self.common_passwords)} passwords\n"
                f"Time: {elapsed:.1f} seconds\n\n"
                "Please try entering the password manually.")
    
    def test_password(self, password):
        """Test if password works"""
        try:
            with open(self.pdf_file, 'rb') as f:
                pdf = pikepdf.Pdf.open(f, password=password)
                # Try to access something to verify
                _ = len(pdf.pages)
                return True
        except:
            return False
    
    def test_manual_password(self):
        """Test manually entered password"""
        password = self.pass_var.get()
        
        if not self.pdf_file:
            messagebox.showerror("Error", "Please select a PDF file first")
            return
        
        if not os.path.exists(self.pdf_file):
            messagebox.showerror("Error", "Selected file does not exist")
            return
        
        if not password:
            messagebox.showwarning("Warning", "Please enter a password")
            return
        
        self.log_message(f"\nTesting manual password: '{password}'")
        self.update_status(f"Testing password...")
        
        start_time = time.time()
        
        if self.test_password(password):
            elapsed = time.time() - start_time
            self.password = password
            self.log_message(f"✓ Password verified in {elapsed:.2f}s")
            self.unlock_btn.config(state='normal')
            self.update_status("Password verified - ready to unlock")
            
            messagebox.showinfo("Success", 
                f"Password is correct!\n\n"
                f"Verified in {elapsed:.2f} seconds\n\n"
                "Click 'Unlock PDF' to remove the password protection.")
        else:
            self.log_message("✗ Password incorrect")
            self.update_status("Password incorrect")
            messagebox.showerror("Error", "Incorrect password!")
    
    def unlock_pdf(self):
        """Unlock the PDF file"""
        if not self.password:
            messagebox.showerror("Error", "No password available")
            return
        
        if not self.pdf_file:
            messagebox.showerror("Error", "No PDF file selected")
            return
        
        if not os.path.exists(self.pdf_file):
            messagebox.showerror("Error", "Selected file does not exist")
            return
        
        try:
            self.log_message("\n" + "="*50)
            self.log_message("Starting PDF unlock process...")
            self.update_status("Opening encrypted PDF...")
            
            # Open encrypted PDF
            with open(self.pdf_file, 'rb') as f:
                pdf = pikepdf.Pdf.open(f, password=self.password)
                
                self.log_message("✓ PDF opened successfully")
                self.update_status("Creating unlocked file...")
                
                # Create unlocked filename
                original_name = os.path.basename(self.pdf_file)
                base_name, ext = os.path.splitext(original_name)
                if not ext or ext.lower() != '.pdf':
                    ext = '.pdf'
                
                unlocked_name = f"{base_name}_unlocked{ext}"
                self.unlocked_file = os.path.join(self.temp_dir, unlocked_name)
                
                # Save without encryption
                self.log_message(f"Saving as: {unlocked_name}")
                pdf.save(self.unlocked_file)
                
                # Verify file was created
                if os.path.exists(self.unlocked_file):
                    size = os.path.getsize(self.unlocked_file) / 1024
                    self.log_message(f"✓ PDF unlocked successfully!")
                    self.log_message(f"  File: {unlocked_name}")
                    self.log_message(f"  Size: {size:.1f} KB")
                    
                    # Test if unlocked file can be opened
                    try:
                        with pikepdf.Pdf.open(self.unlocked_file) as test_pdf:
                            page_count = len(test_pdf.pages)
                            self.log_message(f"  Pages: {page_count}")
                            self.log_message(f"  ✓ File verified and accessible")
                    except Exception as e:
                        self.log_message(f"  ⚠️ Warning: Could not verify file - {str(e)}")
                    
                    # Enable buttons
                    self.save_btn.config(state='normal')
                    self.open_btn.config(state='normal')
                    self.unlock_btn.config(state='disabled')
                    
                    self.update_status("PDF unlocked - ready to save")
                    
                    messagebox.showinfo("Success", 
                        f"PDF unlocked successfully!\n\n"
                        f"Original: {original_name}\n"
                        f"Unlocked: {unlocked_name}\n"
                        f"Size: {size:.1f} KB\n\n"
                        f"Click 'Save Unlocked PDF' to save the file.")
                else:
                    raise Exception("Failed to create unlocked file")
                    
        except pikepdf.PasswordError:
            self.log_message("✗ Password error - incorrect password")
            self.update_status("Error: Incorrect password")
            messagebox.showerror("Error", 
                "Password error!\n\n"
                "The password appears to be incorrect.\n"
                "Please try a different password.")
            
        except Exception as e:
            self.log_message(f"✗ Error: {str(e)}")
            self.update_status(f"Error: {str(e)[:50]}")
            messagebox.showerror("Error", 
                f"Failed to unlock PDF:\n\n{str(e)}\n\n"
                "Please check the file and try again.")
    
    def save_unlocked_pdf(self):
        """Save the unlocked PDF"""
        if not self.unlocked_file or not os.path.exists(self.unlocked_file):
            messagebox.showerror("Error", "No unlocked file available")
            return
        
        self.log_message("\n" + "="*50)
        self.log_message("Saving unlocked PDF...")
        
        # Get default directory
        default_dir = os.path.dirname(self.pdf_file) if self.pdf_file else ""
        
        # Suggest filename
        suggested_name = os.path.basename(self.unlocked_file)
        
        # Ask for save location
        save_path = filedialog.asksaveasfilename(
            title="Save Unlocked PDF",
            defaultextension=".pdf",
            initialfile=suggested_name,
            initialdir=default_dir,
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if save_path:
            try:
                self.update_status("Saving file...")
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                # Copy file
                shutil.copy2(self.unlocked_file, save_path)
                
                if os.path.exists(save_path):
                    size = os.path.getsize(save_path) / 1024
                    self.log_message(f"✓ File saved: {save_path}")
                    self.log_message(f"  Size: {size:.1f} KB")
                    
                    self.update_status(f"File saved successfully")
                    
                    # Ask user what to do next
                    choice = messagebox.askyesnocancel(
                        "Success",
                        f"PDF saved successfully!\n\n"
                        f"Location: {save_path}\n"
                        f"Size: {size:.1f} KB\n\n"
                        "What would you like to do?\n\n"
                        "Yes = Open the PDF file\n"
                        "No = Open containing folder\n"
                        "Cancel = Close this message"
                    )
                    
                    if choice is True:
                        self.open_file(save_path)
                    elif choice is False:
                        self.open_folder(os.path.dirname(save_path))
                
            except Exception as e:
                self.log_message(f"✗ Error saving: {str(e)}")
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")
    
    def open_file_location(self):
        """Open the folder containing unlocked file"""
        if self.unlocked_file and os.path.exists(self.unlocked_file):
            self.open_folder(os.path.dirname(self.unlocked_file))
        else:
            messagebox.showinfo("Info", "No unlocked file available")
    
    def open_folder(self, folder_path):
        """Open folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                if sys.platform == 'darwin':
                    subprocess.run(['open', folder_path])
                else:
                    subprocess.run(['xdg-open', folder_path])
            self.log_message(f"Opened folder: {folder_path}")
        except Exception as e:
            self.log_message(f"✗ Cannot open folder: {str(e)}")
    
    def open_file(self, file_path):
        """Open file with default application"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                if sys.platform == 'darwin':
                    subprocess.run(['open', file_path])
                else:
                    subprocess.run(['xdg-open', file_path])
            self.log_message(f"Opened file: {os.path.basename(file_path)}")
        except Exception as e:
            self.log_message(f"✗ Cannot open file: {str(e)}")
    
    def on_closing(self):
        """Cleanup on closing"""
        self.log_message("\n" + "="*50)
        self.log_message("Closing application...")
        
        try:
            if os.path.exists(self.temp_dir):
                shutil