#!/bin/bash

python3.8 -m venv venv/
source 'venv/bin/activate'
pip install -r requirements.txt
python ./src/theoric_app/main.py
