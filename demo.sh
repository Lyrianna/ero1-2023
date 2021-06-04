#!/bin/bash

python3.8 -m venv venv/
source 'venv/bin/activate'
pip install -r requirements.txt
pip install python-Levenshtein
python ./src/practical_app/main.py "Montreal, Canada" False
