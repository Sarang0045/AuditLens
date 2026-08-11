#!/bin/sh
set -e
python src/pipeline.py
uvicorn api.main:app --reload
