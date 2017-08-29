#!/bin/bash
flake8 --exclude=.venv,snowboy,build,**/fixtures.py &&
pytest --ignore=build
