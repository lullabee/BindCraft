#!/bin/bash

# Sync the results directory to GCS
gsutil -m rsync -r ./cas12a_small/ gs://atelasbio/results/cas12a_small/

# Generate and upload the summary page
python generate_summary.py

echo "Results synced and summary page generated!" 