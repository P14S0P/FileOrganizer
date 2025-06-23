Automatic File Organizer for Windows
Description
This desktop application automatically organizes your downloaded files into predefined category folders (images, documents, videos, etc.). Developed in Python with Tkinter and Watchdog, it monitors your downloads folder in real-time, keeping it clean and tidy. Distributed as a portable .exe, it doesn't require Python installation and minimizes to the system tray for discreet background operation.

Key Features
Automated Classification: Automatically organizes files into predefined categories like images, videos, documents, code, audio, compressed archives, spreadsheets, presentations, fonts, and executables.

Real-time Monitoring: Continuously watches your designated downloads folder for new files.

Portable Executable: Distributed as a self-contained .exe file for Windows, allowing for easy execution without the need to install Python or its dependencies.

User-Friendly Interface (GUI): A simple and easy-to-use graphical interface (Tkinter) allows you to configure your downloads folder and the destination paths for each file category.

System Tray Integration: Minimizes to the system tray, running discreetly in the background.

Duplicate Handling: Configure how the application should handle files with duplicate names (rename, skip, or overwrite).

Persistent Configuration: Saves your configuration settings so you don't have to reconfigure them every time you start the application.

How to Use
Download the Executable:

Go to the Releases section of this repository.

Download the file_organizer_standalone.exe file from the "Assets" section of the latest version.

Run the Application:

Double-click the file_organizer_standalone.exe file you downloaded.

Note: Windows SmartScreen might display an initial security warning as the executable is not digitally signed. You can click "More info" and then "Run anyway" to proceed.

Configure Your Folders:

In the user interface, first select your "Downloads Folder" (usually the Windows default).

Then, for each category (Images, Videos, Documents, etc.), select the "Destination Folder" where you want those file types to be moved.

(Optional) You can edit the organizer_config.json file if you need advanced adjustments, such as enabling/disabling categories or changing extensions.

Save Configuration:

Click the "Save Configuration" button to ensure your changes are saved for future sessions.

Start Monitoring:

Click the "Start Monitoring" button. The application will begin watching your downloads folder in real-time and automatically move new files to their destinations.

Stop Monitoring:

Click "Stop Monitoring" to pause automatic organization.

Auto-Start with Windows
To have the File Organizer automatically run every time Windows starts, follow these steps:

Locate the Executable: Find your file_organizer_standalone.exe file (it's typically in the dist/ folder after compilation).

Create a Shortcut: Right-click on file_organizer_standalone.exe and select "Create shortcut".

Open the Startup Folder:

Press Win + R to open the "Run" dialog.

Type shell:startup and press Enter. This will open the Startup folder for your current user.

(Optional) If you want the application to start for all users on the computer, type shell:common startup in the "Run" dialog and press Enter instead.

Move the Shortcut: Drag the shortcut you created in step 2 into the "Startup" folder you just opened.

The next time you start your PC, the File Organizer will launch automatically and minimize to the system tray.

License
This project is licensed under the MIT License. See the LICENSE file for more details.

We hope this tool helps you maintain a cleaner and more efficient digital workspace. Thank you for using it!
