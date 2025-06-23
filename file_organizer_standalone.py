#!/usr/bin/env python3
"""
File Organizer - Standalone Version
Automatically organizes downloaded files into categorized folders.
"""

import os
import json
import shutil
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading

# Imports for System Tray functionality
from PIL import Image
import pystray

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileOrganizerHandler(FileSystemEventHandler):
    """Handles file system events for the file organizer."""
    
    def __init__(self, organizer):
        self.organizer = organizer
    
    def on_created(self, event):
        """Triggered when a file is created."""
        if not event.is_directory:
            logging.info(f"File creation detected: {event.src_path}")
            # The actual waiting for file readiness is now handled in organize_file
            self.organizer.organize_file(event.src_path)
    
    def on_moved(self, event):
        """Triggered when a file is moved."""
        if not event.is_directory:
            logging.info(f"File moved: {event.src_path} to {event.dest_path}")
            # The actual waiting for file readiness is now handled in organize_file
            self.organizer.organize_file(event.dest_path)

class FileOrganizer:
    """Main file organizer class."""
    
    # File extensions by category
    FILE_CATEGORIES = {
        'Images': {
            'extensions': [
                'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'svg', 
                'ico', 'raw', 'cr2', 'nef', 'arw', 'dng', 'psd', 'ai', 'eps',
                'heic', 'heif', 'jfif', 'jp2', 'jpx', 'j2k', 'j2c'
            ],
            'default_folder': 'Images'
        },
        'Videos': {
            'extensions': [
                'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v', '3gp',
                'mpg', 'mpeg', 'mts', 'm2ts', 'vob', 'ogv', 'dv', 'f4v', 'asf',
                'rm', 'rmvb', 'ts', 'mxf', 'roq', 'nsv'
            ],
            'default_folder': 'Videos'
        },
        'Audio': {
            'extensions': [
                'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a', 'opus', 'aiff',
                'au', 'ra', 'dts', 'ac3', 'amr', 'ape', 'cda', 'mid', 'midi',
                'mka', 'mp2', 'mpa', 'mpc', 'oga', 'spx', 'tta', 'voc', 'vqf', 'w64'
            ],
            'default_folder': 'Music'
        },
        'Documents': {
            'extensions': [
                'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'pages', 'tex', 'wpd',
                'wps', 'xps', 'oxps', 'mobi', 'azw', 'azw3', 'epub', 'fb2', 'lit',
                'pdb', 'tcr', 'prc', 'djvu', 'djv', 'cbr', 'cbz', 'cb7', 'cbt'
            ],
            'default_folder': 'Documents'
        },
        'Code': {
            'extensions': [
                'py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'rb', 'go',
                'rs', 'swift', 'kt', 'ts', 'jsx', 'tsx', 'vue', 'scss', 'sass',
                'less', 'sql', 'sh', 'bat', 'ps1', 'vbs', 'pl', 'r', 'scala',
                'clj', 'hs', 'elm', 'dart', 'lua', 'groovy', 'coffee', 'cs',
                'vb', 'fs', 'ml', 'pas', 'dpr', 'asm', 's', 'forth', 'lisp',
                'scm', 'rkt', 'jl', 'nim', 'cr', 'd', 'zig'
            ],
            'default_folder': 'Code'
        },
        'Archives': {
            'extensions': [
                'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'lz', 'lzma', 'z',
                'cab', 'iso', 'dmg', 'pkg', 'deb', 'rpm', 'msi', 'exe', 'app',
                'apk', 'ipa', 'jar', 'war', 'ear', 'ace', 'arj', 'lha', 'lzh',
                'sit', 'sitx', 'sea', 'zoo', 'cpio', 'shar', 'lbr', 'mar',
                'sbx', 'tar.gz', 'tar.bz2', 'tar.xz', 'tgz', 'tbz', 'tbz2', 'txz'
            ],
            'default_folder': 'Archives'
        },
        'Spreadsheets': {
            'extensions': [
                'xlsx', 'xls', 'csv', 'ods', 'numbers', 'xlsm', 'xlsb', 'xlt',
                'xltx', 'xltm', 'ots', 'fods', 'uos', 'dif', 'sylk', 'slk',
                'pxl', 'wb1', 'wb2', 'wb3', 'qpw', '123', 'wk1', 'wk3', 'wk4', 'wks'
            ],
            'default_folder': 'Spreadsheets'
        },
        'Presentations': {
            'extensions': [
                'pptx', 'ppt', 'odp', 'key', 'pps', 'ppsx', 'pptm', 'ppsm',
                'pot', 'potx', 'potm', 'otp', 'fodp', 'uop', 'shf', 'show',
                'prez', 'sti', 'kth'
            ],
            'default_folder': 'Presentations'
        },
        'Fonts': {
            'extensions': [
                'ttf', 'otf', 'woff', 'woff2', 'eot', 'pfb', 'pfm', 'afm',
                'bdf', 'pcf', 'snf', 'pfa', 'gsf', 'fon', 'fnt', 'ttc', 'otc',
                'dfont', 'suit', 'lwfn', 'ffil', 'vfb', 'sfd', 'ufd'
            ],
            'default_folder': 'Fonts'
        },
        'Executables': {
            'extensions': [
                'exe', 'msi', 'dmg', 'pkg', 'deb', 'rpm', 'run', 'bin', 'app',
                'appimage', 'flatpak', 'snap', 'com', 'scr', 'gadget', 'msp',
                'msu', 'cab'
            ],
            'default_folder': 'Programs'
        }
    }
    
    def __init__(self, config_path='organizer_config.json'):
        self.config_path = config_path
        self.config = {}
        self.observer = None
        self.load_config()
    
    def load_config(self):
        """Loads configuration from a JSON file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logging.info("Configuration loaded successfully.")
            else:
                self.create_default_config()
                logging.info("Configuration file not found. Created a default one.")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}. Creating default configuration.")
            self.create_default_config()
    
    def create_default_config(self):
        """Creates default configuration."""
        downloads_path = str(Path.home() / "Downloads")
        
        self.config = {
            "downloads_folder": downloads_path,
            "enabled": True,
            "handle_duplicates": "rename",
            "categories": {}
        }
        
        # Initialize categories with their default folders within the user's home directory
        for category, info in self.FILE_CATEGORIES.items():
            self.config["categories"][category] = {
                "folder_path": str(Path.home() / info['default_folder']),
                "enabled": True,
                "extensions": info['extensions']
            }
        
        self.save_config()
    
    def save_config(self):
        """Saves configuration to a JSON file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info("Configuration saved successfully.")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
    
    def get_file_category(self, file_path):
        """Determines the category of a file based on its extension."""
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        
        for category, info in self.config.get("categories", {}).items():
            if info.get("enabled", True) and file_ext in info.get("extensions", []):
                return category
        
        return "Others" # If no category matches
    
    def get_destination_path(self, file_path, category):
        """Gets the destination path for a file."""
        if category in self.config.get("categories", {}):
            category_info = self.config["categories"][category]
            if category_info.get("folder_path"):
                dest_folder = Path(category_info["folder_path"])
            else:
                logging.warning(f"No folder configured for category '{category}' in configuration.")
                return None  # No folder configured for this category
        else:
            # For "Others" category or if category is not found
            downloads_folder = Path(self.config.get("downloads_folder", str(Path.home() / "Downloads")))
            others_folder = downloads_folder / "Others"
            others_folder.mkdir(parents=True, exist_ok=True)
            dest_folder = others_folder
        
        # Create destination folder if it doesn't exist
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        return dest_folder / Path(file_path).name
    
    def handle_duplicate(self, src_path, dest_path):
        """Handles duplicate files."""
        if not dest_path.exists():
            return dest_path
        
        handle_method = self.config.get("handle_duplicates", "rename")
        
        if handle_method == "skip":
            logging.info(f"Skipping duplicate file (config: skip): {src_path.name}")
            return None
        elif handle_method == "overwrite":
            logging.info(f"Overwriting duplicate file (config: overwrite): {dest_path.name}")
            return dest_path
        else:  # rename (default method)
            counter = 1
            file_stem = dest_path.stem
            file_suffix = dest_path.suffix
            
            original_dest_path = dest_path # Store original path for reference
            
            while dest_path.exists():
                new_name = f"{file_stem}_{counter}{file_suffix}"
                dest_path = original_dest_path.parent / new_name # Reconstruct path with new name
                counter += 1
            
            logging.info(f"Renaming duplicate file: {src_path.name} to {dest_path.name}")
            return dest_path

    def _is_file_ready(self, file_path, stability_period=2, check_interval=0.5, max_wait_time=30):
        """
        Checks if a file has finished being written by monitoring its size over time.
        
        Args:
            file_path (Path): The path to the file.
            stability_period (int): Duration in seconds the file size must remain stable.
            check_interval (float): Time in seconds between size checks.
            max_wait_time (int): Maximum total time to wait for the file to become ready.
        
        Returns:
            bool: True if the file is deemed ready, False otherwise.
        """
        if not file_path.exists():
            logging.warning(f"File not found during readiness check: {file_path}")
            return False

        last_size = -1
        stable_time = 0
        total_wait_time = 0

        logging.info(f"Checking readiness for file: {file_path.name}")

        while total_wait_time < max_wait_time:
            try:
                current_size = file_path.stat().st_size
                if current_size == last_size:
                    stable_time += check_interval
                    logging.debug(f"File {file_path.name} size stable for {stable_time:.1f}s.")
                    if stable_time >= stability_period:
                        logging.info(f"File {file_path.name} is ready.")
                        return True
                else:
                    stable_time = 0  # Reset stability if size changed
                    last_size = current_size
                    logging.debug(f"File {file_path.name} size changed to {current_size} bytes. Resetting stability.")
            except FileNotFoundError:
                logging.warning(f"File {file_path.name} disappeared during readiness check.")
                return False
            except Exception as e:
                logging.error(f"Error checking file readiness for {file_path.name}: {e}")
                return False

            time.sleep(check_interval)
            total_wait_time += check_interval
        
        logging.warning(f"File {file_path.name} did not become ready within {max_wait_time}s. Proceeding anyway.")
        return False # Or True, depending on desired behavior for timeout. Returning False might prevent moving partial files.
    
    def organize_file(self, file_path):
        """Organizes a single file."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logging.warning(f"File not found, skipping: {file_path.name}")
                return False
            
            # Skip hidden and temporary files/directories
            if file_path.name.startswith('.') or file_path.name.endswith('.tmp') or file_path.is_dir():
                logging.debug(f"Skipping temporary/hidden file/directory: {file_path.name}")
                return False
            
            # Ensure the file is in the downloads folder (to prevent organizing files already in destination)
            downloads_folder = Path(self.config.get("downloads_folder", str(Path.home() / "Downloads")))
            if file_path.parent == downloads_folder:
                pass # Continue only if the file is in the downloads folder
            else:
                logging.info(f"File '{file_path.name}' is not in the configured downloads folder. Skipping.")
                return False

            # *** NEW: Wait for file to be ready before proceeding ***
            if not self._is_file_ready(file_path):
                logging.warning(f"File '{file_path.name}' was not ready for organization. Skipping for now.")
                return False

            category = self.get_file_category(str(file_path))
            dest_path = self.get_destination_path(str(file_path), category)
            
            if dest_path is None:
                logging.warning(f"No configured or valid destination folder for category '{category}' for file '{file_path.name}'.")
                return False
            
            # Ensure destination is not the same as source parent (already organized)
            if file_path.parent == dest_path.parent:
                logging.info(f"File '{file_path.name}' is already in its organized folder. Skipping.")
                return False

            # Handle duplicates
            final_dest_path = self.handle_duplicate(file_path, dest_path)
            if final_dest_path is None:
                return False # Duplicate file skipped
            
            # Move the file
            shutil.move(str(file_path), str(final_dest_path))
            logging.info(f"Moved: {file_path.name} → {category} ({final_dest_path.parent})")
            return True
            
        except Exception as e:
            logging.error(f"Error organizing file {file_path.name}: {e}")
            return False
    
    def start_monitoring(self):
        """Starts monitoring the downloads folder."""
        downloads_folder = self.config.get("downloads_folder", "")
        
        if not downloads_folder or not os.path.exists(downloads_folder):
            logging.error("ERROR: Downloads folder does not exist or is not configured.")
            return False
        
        # Stop monitoring if already active
        self.stop_monitoring() 

        self.observer = Observer()
        event_handler = FileOrganizerHandler(self)
        self.observer.schedule(event_handler, downloads_folder, recursive=False)
        
        self.observer.start()
        logging.info(f"🔍 Monitoring folder: {downloads_folder}")
        return True
    
    def stop_monitoring(self):
        """Stops monitoring."""
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5) # Wait for the observer thread to finish
            if self.observer.is_alive():
                logging.warning("Observer did not stop correctly.")
            self.observer = None
            logging.info("👋 Monitoring stopped.")

class FileOrganizerGUI:
    def __init__(self):
        self.organizer = FileOrganizer()
        self.root = tk.Tk()
        self.root.title("File Organizer")
        # Set minimum window size
        self.root.geometry("800x600") 
        self.root.minsize(700, 500) # Minimum size

        self.is_monitoring = False
        self.tray_icon = None # For the system tray icon instance
        self._tray_thread = None # To explicitly store the tray icon thread

        # Configure close protocol to minimize to tray
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.setup_ui()
        self.load_config()

        # Start monitoring automatically if the app opens and config indicates it
        if self.organizer.config.get("enabled", False) and self.organizer.config.get("downloads_folder"):
            self.start_monitoring()
        else:
            self.status_var.set("Ready. Configure and then Start Monitoring.")
    
    def setup_ui(self):
        """Configures the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True) # Use pack for the main frame

        # Downloads folder configuration
        downloads_frame = ttk.LabelFrame(main_frame, text="Downloads Folder", padding="10")
        downloads_frame.pack(fill=tk.X, pady=(0, 10)) # Use pack for horizontal filling
        
        self.downloads_var = tk.StringVar()
        downloads_entry = ttk.Entry(downloads_frame, textvariable=self.downloads_var, width=60)
        downloads_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True) # expand to fill
        
        ttk.Button(downloads_frame, text="Select", 
                   command=self.select_downloads_folder).pack(side=tk.RIGHT)
        
        # Categories
        categories_frame = ttk.LabelFrame(main_frame, text="Destination Folders by Category", padding="10")
        categories_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10)) # Fill vertically

        # Canvas and scrollbar for categories
        canvas = tk.Canvas(categories_frame)
        scrollbar = ttk.Scrollbar(categories_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Variables for category folders
        self.category_vars = {}
        self.create_category_widgets()
        
        # Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(pady=10) # Center the buttons
        
        self.start_button = ttk.Button(controls_frame, text="Start Monitoring", 
                                       command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(controls_frame, text="Stop Monitoring", 
                                      command=self.stop_monitoring, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Save Configuration", 
                   command=self.save_config).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('Arial', 10, 'bold'))
        status_label.pack(pady=5)
    
    def create_category_widgets(self):
        """Creates widgets for each category."""
        row = 0
        for category in self.organizer.FILE_CATEGORIES.keys():
            # Frame for each category
            cat_frame = ttk.Frame(self.scrollable_frame)
            cat_frame.pack(fill=tk.X, pady=2, padx=5) # Fill horizontally
            
            # Category Name
            ttk.Label(cat_frame, text=f"{category}:", width=15).pack(side=tk.LEFT, anchor=tk.W)
            
            # Entry field for folder path
            var = tk.StringVar()
            self.category_vars[category] = var
            entry = ttk.Entry(cat_frame, textvariable=var, width=50)
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Button to select folder
            ttk.Button(cat_frame, text="Select", 
                       command=lambda cat=category: self.select_category_folder(cat)).pack(side=tk.RIGHT, padx=5)
            
            row += 1
    
    def select_downloads_folder(self):
        """Selects the downloads folder."""
        folder = filedialog.askdirectory(title="Select Downloads Folder")
        if folder:
            self.downloads_var.set(folder)
            logging.info(f"Downloads folder selected: {folder}")
    
    def select_category_folder(self, category):
        """Selects the folder for a specific category."""
        folder = filedialog.askdirectory(title=f"Select folder for {category}")
        if folder:
            self.category_vars[category].set(folder)
            logging.info(f"Folder for '{category}' selected: {folder}")
    
    def load_config(self):
        """Loads configuration into the GUI."""
        config = self.organizer.config
        
        self.downloads_var.set(config.get('downloads_folder', ''))
        
        for category, var in self.category_vars.items():
            category_info = config.get('categories', {}).get(category, {})
            var.set(category_info.get('folder_path', ''))
        logging.info("Configuration loaded into GUI.")
    
    def save_config(self):
        """Saves configuration from the GUI."""
        self.organizer.config['downloads_folder'] = self.downloads_var.get()
        
        for category, var in self.category_vars.items():
            if category in self.organizer.config['categories']:
                self.organizer.config['categories'][category]['folder_path'] = var.get()
            else:
                # If it's a new category or "Others" not defined in initial config
                self.organizer.config['categories'][category] = {
                    "folder_path": var.get(),
                    "enabled": True, # Assume enabled by default if added
                    "extensions": [] # Extensions would be managed in code or more complex UI
                }
        
        # Ensure the "enabled" status is maintained
        self.organizer.config["enabled"] = self.is_monitoring 
        
        self.organizer.save_config()
        self.status_var.set("Configuration Saved")
        self.show_message("Success", "Configuration saved successfully!")
        logging.info("Configuration saved from GUI.")
    
    def start_monitoring(self):
        """Starts monitoring."""
        # Ensure destination folders are configured before starting
        self.save_config() # Save current GUI configuration
        
        if self.organizer.start_monitoring():
            self.is_monitoring = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_var.set(f"Monitoring: {self.organizer.config.get('downloads_folder')}")
            logging.info("Monitoring started from GUI.")
        else:
            self.show_message("Error", "Could not start monitoring. Check downloads folder and category destination folders.")
            self.status_var.set("Error starting monitoring.")
            logging.error("Failed to start monitoring from GUI.")
    
    def stop_monitoring(self):
        """Stops monitoring."""
        self.organizer.stop_monitoring()
        self.is_monitoring = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("Monitoring Stopped.")
        logging.info("Monitoring stopped from GUI.")

    def show_message(self, title, message):
        """Displays a messagebox (replaces alert/confirm)."""
        messagebox.showinfo(title, message)
        logging.info(f"Message displayed: {title} - {message}")

    def minimize_to_tray(self):
        """Minimizes the window to the system tray."""
        self.root.withdraw() # Hides the window
        
        if self.tray_icon is None:
            self.create_tray_icon()
        
        # Start the tray icon thread only if it's not already running
        if not hasattr(self, '_tray_thread') or not self._tray_thread.is_alive():
            self._tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self._tray_thread.start()
            logging.info("Tray icon thread started.")
        else:
            logging.info("Tray icon thread already running.")

        logging.info("Window minimized to system tray.")

    def create_tray_icon(self):
        """Creates the system tray icon."""
        # Create a simple image for the icon. For a real .exe, you would include a .ico file.
        # This generates a simple blue square with a white center for demonstration.
        # If you have a custom .ico file, load it like this: Image.open("path/to/your/icon.ico")
        # Ensure to add this .ico file to PyInstaller using --add-data "path/to/your/icon.ico;."
        
        icon_image = Image.new('RGB', (64, 64), color = 'blue')
        for x in range(20, 44):
            for y in range(20, 44):
                icon_image.putpixel((x, y), (255, 255, 255))

        menu = (pystray.MenuItem('Show', self.show_window),
                pystray.MenuItem('Quit', self.quit_application))
        
        self.tray_icon = pystray.Icon("file_organizer", icon_image, "File Organizer", menu)
        logging.info("Tray icon created.")

    def show_window(self):
        """Shows the application window."""
        self.root.deiconify() # Shows the window
        
        # Stop the tray icon thread when the window is shown
        if hasattr(self, '_tray_thread') and self._tray_thread.is_alive():
            self.tray_icon.stop()
            self._tray_thread.join(timeout=1) # Give it a moment to stop
            logging.info("Tray icon thread stopped.")

        logging.info("Window restored from system tray.")

    def quit_application(self):
        """Closes the application completely."""
        # Stop the tray icon thread if it's running
        if hasattr(self, '_tray_thread') and self._tray_thread.is_alive():
            self.tray_icon.stop()
            self._tray_thread.join(timeout=1)
            logging.info("Tray icon thread stopped before quitting.")
        
        # Ensure the pystray icon is explicitly stopped if it was ever created
        if self.tray_icon:
            self.tray_icon.stop()
            
        self.organizer.stop_monitoring() # Ensure monitoring is stopped
        self.root.quit() # Closes the Tkinter application
        logging.info("Application closed from system tray.")

    def run(self):
        """Runs the application."""
        self.root.mainloop()

def main():
    """Main function."""
    print("=== FILE ORGANIZER ===")
    print("Starting graphical interface...")
    
    try:
        app = FileOrganizerGUI()
        app.run()
    except Exception as e:
        logging.critical(f"Fatal error in application: {e}", exc_info=True)
        # Display an error messagebox to the user before exiting
        messagebox.showerror("Critical Error", f"An unexpected error occurred: {e}\nThe application will close.")

if __name__ == "__main__":
    # The ImportError check is removed here, as it's not relevant for the end-user
    # running the compiled .exe. PyInstaller bundles all dependencies.
    main()
