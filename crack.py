#!/usr/bin/env python3
"""
PDF Password Remover - Fixed Version
Simple GUI to remove passwords from PDF files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
import os
import time
import shutil
import tempfile
import sys

# Try to import PDF libraries
try:
    import pikepdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class PDFUnlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Password Remover v2.0")
        self.root.geometry("800x650")
        
        # Variables
        self.pdf_file = ""
        self.password = ""
        self.unlocked_file = ""
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_unlocker_")
        
        # Common passwords to try
        self.common_passwords = [
            "", "123456", "password", "12345678", "qwerty",
            "123456789", "12345", "1234", "111111", "1234567",
            "dragon", "123123", "admin", "welcome", "monkey",
            "letmein", "password1", "abc123", "123", "login",
            "passw0rd", "master", "hello", "test", "demo",
            "admin123", "letmein123", "welcome123", "password123"
        ]
        
        # Setup UI
        self.setup_ui()
        
        # Check library
        if not PDF_AVAILABLE:
            self.show_library_error()
    
    def show_library_error(self):
        """Show library installation error"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        error_frame = ttk.Frame(self.root, padding="40")
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(error_frame, text="❌ Library Missing", 
                 font=('Arial', 16, 'bold'), foreground="red").pack(pady=(0, 20))
        
        error_msg = "Required library 'pikepdf' not found!\n\n"
        error_msg += "Please install it using one of these methods:\n\n"
        error_msg += "1. Open Command Prompt/Terminal and run:\n"
        error_msg += "   pip install pikepdf\n\n"
        error_msg += "2. Or click the button below to install automatically"
        
        ttk.Label(error_frame, text=error_msg, justify=tk.LEFT).pack(pady=(0, 30))
        
        btn_frame = ttk.Frame(error_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Install Library Now", 
                  command=self.install_library, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Exit", 
                  command=self.root.quit, width=20).pack(side=tk.LEFT, padx=5)
    
    def install_library(self):
        """Try to install the required library"""
        import subprocess
        
        install_dialog = tk.Toplevel(self.root)
        install_dialog.title("Installing Library")
        install_dialog.geometry("400x200")
        install_dialog.transient(self.root)
        install_dialog.grab_set()
        
        # Center dialog
        install_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (200 // 2)
        install_dialog.geometry(f"400x200+{x}+{y}")
        
        main_frame = ttk.Frame(install_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Installing pikepdf...", 
                 font=('Arial', 12)).pack(pady=20)
        
        progress = ttk.Progressbar(main_frame, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        status_label = ttk.Label(main_frame, text="Please wait...")
        status_label.pack(pady=10)
        
        install_dialog.update()
        
        def do_install():
            try:
                # Try to install
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pikepdf"])
                
                # Update UI in main thread
                self.root.after(0, lambda: self.on_install_success(install_dialog))
                
            except Exception as e:
                # Update UI in main thread
                self.root.after(0, lambda: self.on_install_failed(install_dialog, str(e)))
        
        # Run installation in thread to avoid freezing
        import threading
        thread = threading.Thread(target=do_install)
        thread.daemon = True
        thread.start()
    
    def on_install_success(self, dialog):
        dialog.destroy()
        messagebox.showinfo("Success", 
            "Library installed successfully!\n\n"
            "Please restart the application.")
        self.root.quit()
    
    def on_install_failed(self, dialog, error):
        dialog.destroy()
        messagebox.showerror("Installation Failed", 
            f"Failed to install library:\n\n{error}\n\n"
            "Please install manually using:\n"
            "pip install pikepdf")
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="🔓 PDF Password Remover", 
                 font=('Arial', 18, 'bold')).pack()
        
        ttk.Label(title_frame, text="Remove passwords from PDF files", 
                 font=('Arial', 10)).pack()
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="📁 Select PDF File", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File path
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="File:").pack(side=tk.LEFT)
        
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(path_frame, textvariable=self.file_var, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        ttk.Button(path_frame, text="Browse...", 
                  command=self.browse_file, width=10).pack(side=tk.LEFT)
        
        # File info
        self.file_info = ttk.Label(file_frame, text="No file selected", 
                                  foreground="gray")
        self.file_info.pack(anchor='w', pady=(5, 0))
        
        # Password options
        pass_frame = ttk.LabelFrame(main_frame, text="🔑 Password Options", padding="15")
        pass_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Try common passwords button
        ttk.Button(pass_frame, text="Try Common Passwords", 
                  command=self.try_common_passwords,
                  width=20).pack(pady=(0, 10))
        
        # Manual password entry
        manual_frame = ttk.Frame(pass_frame)
        manual_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(manual_frame, text="Or enter password:").pack(side=tk.LEFT)
        
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
        
        # Progress area
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progress", padding="15")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var,
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Status text
        self.status_text = scrolledtext.ScrolledText(progress_frame, 
                                                    height=10,
                                                    wrap=tk.WORD,
                                                    font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.unlock_btn = ttk.Button(action_frame, text="🔓 Unlock PDF", 
                                    command=self.unlock_pdf,
                                    state='disabled',
                                    width=15)
        self.unlock_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_btn = ttk.Button(action_frame, text="💾 Save Unlocked PDF", 
                                      command=self.save_unlocked_pdf,
                                      state='disabled',
                                      width=20)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_btn = ttk.Button(action_frame, text="📂 Open File Location", 
                                  command=self.open_file_location,
                                  state='disabled',
                                  width=20)
        self.open_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready - Select a PDF file to begin", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind Enter key to password entry
        self.pass_entry.bind('<Return>', lambda e: self.test_manual_password())
        
        # Initialize log
        self.log_message("Application started")
        self.log_message(f"Temp directory: {self.temp_dir}")
    
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
            
            # Get file info
            try:
                if os.path.exists(filename):
                    size = os.path.getsize(filename) / 1024  # KB
                    self.file_info.config(
                        text=f"✓ {os.path.basename(filename)} ({size:.1f} KB)",
                        foreground="green"
                    )
                    self.log_message(f"Selected: {os.path.basename(filename)}")
                    self.update_status(f"File selected: {os.path.basename(filename)}")
                    
                    # Check if file is encrypted
                    self.check_encryption()
                else:
                    self.file_info.config(text="✗ File not found", foreground="red")
                    self.log_message(f"Error: File not found - {filename}")
                    self.update_status("Error: File not found")
            except Exception as e:
                self.file_info.config(text=f"✗ Error: {str(e)}", foreground="red")
                self.log_message(f"Error reading file: {str(e)}")
    
    def check_encryption(self):
        """Check if PDF is encrypted"""
        if not PDF_AVAILABLE:
            return
        
        try:
            with open(self.pdf_file, 'rb') as f:
                try:
                    pdf = pikepdf.Pdf.open(f)
                    if pdf.is_encrypted:
                        self.log_message("File is encrypted ✓")
                    else:
                        self.log_message("File is NOT encrypted - no password needed")
                        messagebox.showinfo("Info", 
                            "This PDF is not encrypted.\n"
                            "No password needed to open it.")
                except pikepdf.PasswordError:
                    self.log_message("File is encrypted ✓ (password protected)")
        except Exception as e:
            self.log_message(f"Error checking file: {str(e)}")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
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
        self.log_message("Trying common passwords...")
        
        # Reset progress
        self.progress_var.set(0)
        
        # Disable buttons during process
        self.unlock_btn.config(state='disabled')
        
        # Try passwords
        found = False
        total = len(self.common_passwords)
        
        for i, password in enumerate(self.common_passwords):
            # Update progress
            progress = (i + 1) / total * 100
            self.progress_var.set(progress)
            self.update_status(f"Testing password {i+1}/{total}")
            
            # Show which password we're trying (masked for empty)
            display_pass = "''" if password == "" else f"'{password}'"
            self.log_message(f"Trying: {display_pass}")
            self.root.update()
            
            # Try the password
            if self.test_password(password):
                self.password = password
                self.log_message(f"✓ SUCCESS! Password found: {display_pass}")
                self.update_status(f"Password found: {display_pass}")
                found = True
                break
        
        self.progress_var.set(100)
        
        if found:
            self.unlock_btn.config(state='normal')
            messagebox.showinfo("Success", 
                f"Password found!\n\n"
                f"Password: {display_pass}\n\n"
                f"Click 'Unlock PDF' to remove the password.")
        else:
            self.log_message("✗ No common password worked")
            self.update_status("No password found")
            messagebox.showinfo("No Password Found", 
                "None of the common passwords worked.\n\n"
                "Please try entering the password manually in the field above.")
    
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
        
        if self.test_password(password):
            self.password = password
            self.log_message(f"✓ Password works!")
            self.unlock_btn.config(state='normal')
            self.update_status("Password verified - ready to unlock")
            messagebox.showinfo("Success", 
                "Password is correct!\n\n"
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
                    self.log_message(f"  Location: {self.unlocked_file}")
                    
                    # Test if unlocked file can be opened
                    try:
                        with pikepdf.Pdf.open(self.unlocked_file) as test_pdf:
                            page_count = len(test_pdf.pages)
                            self.log_message(f"  Pages: {page_count}")
                            self.log_message(f"  ✓ File verified and accessible")
                    except Exception as e:
                        self.log_message(f"  ⚠️ Warning: Could not verify file - {str(e)}")
                    
                    # Enable download button
                    self.download_btn.config(state='normal')
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
                "Please check:\n"
                "1. The PDF file is not corrupted\n"
                "2. You have the correct password\n"
                "3. You have permission to modify the file")
    
    def save_unlocked_pdf(self):
        """Save the unlocked PDF to a location chosen by user"""
        if not self.unlocked_file or not os.path.exists(self.unlocked_file):
            messagebox.showerror("Error", "No unlocked file available. Please unlock a PDF first.")
            return
        
        self.log_message("\n" + "="*50)
        self.log_message("Saving unlocked PDF...")
        
        # Get the original PDF's directory as default location
        default_dir = os.path.dirname(self.pdf_file) if self.pdf_file else ""
        
        # Suggest a filename
        suggested_name = os.path.basename(self.unlocked_file)
        
        # Ask for save location
        save_path = filedialog.asksaveasfilename(
            title="Save Unlocked PDF",
            defaultextension=".pdf",
            initialfile=suggested_name,
            initialdir=default_dir,  # Start in same directory as original
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if save_path:
            try:
                self.update_status("Saving file...")
                self.log_message(f"Attempting to save to: {save_path}")
                
                # Check if target directory exists
                target_dir = os.path.dirname(save_path)
                if target_dir and not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                    self.log_message(f"Created directory: {target_dir}")
                
                # Copy the file
                shutil.copy2(self.unlocked_file, save_path)
                
                # Verify the copy was successful
                if os.path.exists(save_path):
                    size = os.path.getsize(save_path) / 1024
                    self.log_message(f"✓ File saved successfully!")
                    self.log_message(f"  Location: {save_path}")
                    self.log_message(f"  Size: {size:.1f} KB")
                    
                    self.update_status(f"File saved: {os.path.basename(save_path)}")
                    
                    # Ask if user wants to open the file or folder
                    response = messagebox.askyesnocancel("Success", 
                        f"PDF saved successfully!\n\n"
                        f"Location: {save_path}\n"
                        f"Size: {size:.1f} KB\n\n"
                        f"What would you like to do?\n\n"
                        f"Yes = Open the PDF file\n"
                        f"No = Open the folder\n"
                        f"Cancel = Do nothing")
                    
                    if response is not None:  # User didn't click Cancel
                        if response:  # Yes - Open the PDF file
                            self.open_file(save_path)
                        else:  # No - Open the folder
                            self.open_folder(os.path.dirname(save_path))
                
                else:
                    raise Exception("File was not created at destination")
                
            except Exception as e:
                self.log_message(f"✗ Error saving file: {str(e)}")
                self.update_status(f"Error saving file")
                messagebox.showerror("Save Error", 
                    f"Failed to save file:\n\n{str(e)}\n\n"
                    "Please check:\n"
                    "1. You have write permission to the destination\n"
                    "2. The destination drive has enough space\n"
                    "3. The file is not open in another program")
    
    def open_file_location(self):
        """Open the folder containing the unlocked file"""
        if self.unlocked_file and os.path.exists(self.unlocked_file):
            folder = os.path.dirname(self.unlocked_file)
            self.open_folder(folder)
        else:
            messagebox.showinfo("Info", "No unlocked file available yet.")
    
    def open_folder(self, folder_path):
        """Open a folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS or Linux
                import subprocess
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', folder_path])
                else:  # Linux
                    subprocess.run(['xdg-open', folder_path])
            self.log_message(f"Opened folder: {folder_path}")
        except Exception as e:
            self.log_message(f"✗ Could not open folder: {str(e)}")
            messagebox.showerror("Error", f"Cannot open folder:\n{str(e)}")
    
    def open_file(self, file_path):
        """Open a file with default application"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS or Linux
                import subprocess
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', file_path])
                else:  # Linux
                    subprocess.run(['xdg-open', file_path])
            self.log_message(f"Opened file: {os.path.basename(file_path)}")
        except Exception as e:
            self.log_message(f"✗ Could not open file: {str(e)}")
            messagebox.showerror("Error", f"Cannot open file:\n{str(e)}")
    
    def on_closing(self):
        """Clean up on closing"""
        self.log_message("\n" + "="*50)
        self.log_message("Cleaning up...")
        
        try:
            # Clean up temp directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.log_message(f"Cleaned temp directory: {self.temp_dir}")
        except Exception as e:
            self.log_message(f"Error cleaning up: {str(e)}")
        
        self.log_message("Application closed")
        self.root.destroy()

def main():
    """Main function"""
    # Create main window
    root = tk.Tk()
    
    # Set window icon (optional)
    try:
        root.iconbitmap('pdf_icon.ico')
    except:
        pass
    
    # Create application
    app = PDFUnlockerApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Set minimum size
    root.minsize(700, 500)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    # Check for Python version
    import sys
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        print(f"Current version: {sys.version}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Run the application
    main()