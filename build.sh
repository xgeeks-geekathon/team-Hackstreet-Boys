#!/bin/bash
pyinstaller --onefile --windowed --add-data "./src/*:stest" --name "stest" --clean --distpath "./dist" "./src/main.py"
