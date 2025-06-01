#!/bin/bash

nohup python -u bindcraft.py --settings ./settings_target/cas_medium.json --filters ./settings_filters/relaxed_filters.json --advanced \
 ./settings_advanced/default_4stage_multimer_flexible_hardtarget.json > bindcraft.log 2>&1 &