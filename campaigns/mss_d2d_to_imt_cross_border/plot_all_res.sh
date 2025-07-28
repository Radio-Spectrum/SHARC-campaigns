
#!/bin/bash

# the existence of this file shows how bad this cli is

# NOTE: first you need to chmod +x this file
python ./plot_results.py --adj --mss 3.1
python ./plot_results.py --adj --mss 3.2
python ./plot_results.py --mss 3.1
python ./plot_results.py --mss 3.2
