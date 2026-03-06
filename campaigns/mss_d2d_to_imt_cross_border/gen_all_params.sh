#!/bin/bash

# the existence of this file shows how bad this cli is

# NOTE: first you need to chmod +x this file

# generate cochannel
python ./generate_params.py --band_id B1 --mss_ids system-2.694MHz.698-960MHz.500km system-3.698-960MHz.340km system-3.698-960MHz.525km system-4.698-960MHz.block2.690km --power_control
# python ./generate_params.py --dont-clear --band_id B2 --mss_ids system-2.1427-1518MHz.500km system-3.1427-1518MHz.340km system-3.1427-1518MHz.525km system-4.1427-2690MHz.690km --power_control
python ./generate_params.py --dont-clear --band_id B3 --mss_ids system-2.1805-1920MHz.2110-2170MHz.500km system-3.2110-2200MHz.340km system-3.2110-2200MHz.525km system-4.1427-2690MHz.690km --power_control
# python ./generate_params.py --dont-clear --band_id B4 --mss_ids system-2.2300-2400MHz.500km system-3.2300-2690MHz.340km system-3.2300-2690MHz.525km system-4.1427-2690MHz.690km --power_control
# python ./generate_params.py --dont-clear --band_id B5 --mss_ids system-2.2500-2690MHz.500km system-3.2300-2690MHz.340km system-3.2300-2690MHz.525km system-4.1427-2690MHz.690km --power_control

# adj chan
python ./generate_params.py --dont-clear --adj --band_id B1 --mss_ids system-2.694MHz.698-960MHz.500km system-3.698-960MHz.340km system-3.698-960MHz.525km system-4.698-960MHz.block2.690km
# python ./generate_params.py --dont-clear --adj --band_id B2 --mss_ids system-2.1427-1518MHz.500km system-3.1427-1518MHz.340km system-3.1427-1518MHz.525km system-4.1427-2690MHz.690km
python ./generate_params.py --dont-clear --adj --band_id B3 --mss_ids system-2.1805-1920MHz.2110-2170MHz.500km system-3.2110-2200MHz.340km system-3.2110-2200MHz.525km system-4.1427-2690MHz.690km
# python ./generate_params.py --dont-clear --adj --band_id B4 --mss_ids system-2.2300-2400MHz.500km system-3.2300-2690MHz.340km system-3.2300-2690MHz.525km system-4.1427-2690MHz.690km
# python ./generate_params.py --dont-clear --adj --band_id B5 --mss_ids system-2.2500-2690MHz.500km system-3.2300-2690MHz.340km system-3.2300-2690MHz.525km system-4.1427-2690MHz.690km

# python ./generate_params.py --band_id B1 --mss_ids system-2.694MHz.698-960MHz.500km
# python ./generate_params.py --dont-clear --band_id B3 --mss_ids system-2.1805-1920MHz.2110-2170MHz.500km

