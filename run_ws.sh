#!/bin/bash

cd /home/appuser/chess-rating-updater
source .venv/bin/activate

/home/appuser/chess-rating-updater/.venv/bin/python webscraper.py >> /home/appuser/chess-rating-updater/run.log
deactivate

echo $(date +"%Y-%m-%d %T") >> run.log