#!/bin/bash
pip install -r requirements.txt
pyinstaller --onefile --name "stest" "./src/main.py"