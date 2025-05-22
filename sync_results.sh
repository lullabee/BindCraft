#!/bin/bash

# Set the working directory
cd /home/clairedelaunay/BindCraft2

# Activate conda environment (if needed)
source /opt/conda/etc/profile.d/conda.sh
conda activate base

# Sync the results directory to GCS
gsutil -m rsync -r ./cas12a_small/ gs://atelasbio/results/cas12a_small/

# Generate and upload the summary page
python /home/clairedelaunay/BindCraft2/generate_summary.py

echo "$(date): Results synced and summary page generated!" >> /home/clairedelaunay/BindCraft2/sync.log 