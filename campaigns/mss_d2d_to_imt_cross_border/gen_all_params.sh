#!/bin/bash

# the existence of this file shows how bad this cli is

# NOTE: first you need to chmod +x this file
# generate adjacent channel
python ./generate_params.py --adj
# generate co-channel without clearing input folder
python ./generate_params.py --dont-clear
