#!/bin/bash
pyinstaller --onefile --windowed --add-data "./stest/*:stest" --name "stest" --clean --distpath "./dist" "./stest/main.py"
