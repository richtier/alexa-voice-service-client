#!/bin/bash
flake8 --exclude=.venv,venv,snowboy,build,**/fixtures.py &&
pytest --ignore=build --ignore=venv --ignore=.venv --cov=./ --cov-config=.coveragerc
