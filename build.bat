pyinstaller -y --windowed --add-data="%~dp0.venv\Lib\site-packages\customtkinter;customtkinter" --add-data="%~dp0assets;assets" --add-data="%~dp0backups;backups" --icon="%~dp0assets/AppIcon.ico" "KSL-Hax.py"