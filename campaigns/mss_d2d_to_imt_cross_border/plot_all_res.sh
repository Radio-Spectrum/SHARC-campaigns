#!/bin/bash
set -e

# the existence of this file shows how bad this cli is

# NOTE: first you need to chmod +x this file
# python ./plot_results.py --adj --mss 3.1
# python ./plot_results.py --adj --mss 3.2
# python ./plot_results.py --mss 3.1
# python ./plot_results.py --mss 3.2
# python ./plot_results.py --band_id B1 --mss_ids system-2.694MHz.698-960MHz.500km
# python ./plot_results.py --band_id B3 --mss_ids system-2.1805-1920MHz.2110-2170MHz.500km

python ./plot_results.py --band_id B1 --mss_ids system-2.694MHz.698-960MHz.500km system-3.698-960MHz.340km system-3.698-960MHz.525km system-4.698-960MHz.block2.690km
python ./plot_results.py --band_id B3 --mss_ids system-2.1805-1920MHz.2110-2170MHz.500km system-3.2110-2200MHz.340km system-3.2110-2200MHz.525km system-4.1427-2690MHz.690km
# python ./plot_results.py --band_id B1 --mss_ids system-2.694MHz.698-960MHz.500km system-3.698-960MHz.340km system-3.698-960MHz.525km system-4.698-960MHz.block2.690km --adj
# python ./plot_results.py --band_id B3 --mss_ids system-2.1805-1920MHz.2110-2170MHz.500km system-3.2110-2200MHz.340km system-3.2110-2200MHz.525km system-4.1427-2690MHz.690km --adj

python ./plot_results.py --band_id B1 --mss_ids system-2.694MHz.698-960MHz.500km system-3.698-960MHz.340km system-3.698-960MHz.525km system-4.698-960MHz.block2.690km --plot_type ccdf
python ./plot_results.py --band_id B3 --mss_ids system-2.1805-1920MHz.2110-2170MHz.500km system-3.2110-2200MHz.340km system-3.2110-2200MHz.525km system-4.1427-2690MHz.690km --plot_type ccdf
# python ./plot_results.py --band_id B1 --mss_ids system-2.694MHz.698-960MHz.500km system-3.698-960MHz.340km system-3.698-960MHz.525km system-4.698-960MHz.block2.690km --adj --plot_type ccdf
# python ./plot_results.py --band_id B3 --mss_ids system-2.1805-1920MHz.2110-2170MHz.500km system-3.2110-2200MHz.340km system-3.2110-2200MHz.525km system-4.1427-2690MHz.690km --adj --plot_type ccdf
