#!/bin/bash

source 'venv/bin/activate'
pip install -r requirements.txt         
pip install python-Levenshtein 
python3 ./src/practical_app/main.py "Montreal, Canada" False
