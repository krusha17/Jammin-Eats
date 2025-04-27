# Jammin' Eats Project Requirements

## Prerequisites (external tools, not installed via pip)
- **Python 3.13** (or higher) is required.
- **PyCharm** (recommended) or **VSCode** as the IDE for development.
- **GitHub** for version control and collaboration.
- **Notion** for project documentation and organization.
- **SSMS (SQL Server Management Studio)** may be used for managing SQL Server databases (for future integration).
- **SQLite3** is the lightweight database used (included in the Python Standard Library).
- **Windows** is the primary supported OS (due to PowerShell scripts and build process).

## Python packages (install using pip)
- `pygame>=2.1.0`
- `pyodbc>=4.0.30`  # Optional: For connecting to SQL Server if needed.
- `pytmx`
- `pyinstaller`  # For building the standalone executable

## Project Structure Notes
- The project relies on a specific folder structure for assets, maps, sprites, and tilesets. Ensure the `assets/` directory and its subdirectories are not altered.
- The `.gitignore` is configured to exclude the `/Backups/` directory from version control.
- The backup script (`Tools/Scripts/backup_script.ps1`) is set up to avoid copying the `Backups` folder.

## How to Run the Game
1. Clone this repository:
   ```
   git clone https://github.com/YourUsername/JamminEats.git
   ```
2. Install dependencies:
   ```
   pip install pygame pyodbc pytmx pyinstaller
   ```
3. Launch the game:
   ```
   python main.py
   ```

## How to Build the Executable
1. Run the build script (PowerShell or batch file in `Tools/Scripts/build/`), or directly use PyInstaller:
   ```
   pyinstaller --onefile --windowed --add-data "assets;assets" --name "Jammin_Eats" main.py
   ```
2. The standalone executable will be found in the `dist/` folder.

## Additional Notes
- The project is structured for future SQL Server integration but currently uses SQLite3 for local storage.
- If you encounter asset path issues, check the folder structure and TMX/tileset references.
