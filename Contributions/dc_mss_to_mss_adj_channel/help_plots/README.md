# Help plots, adjacent-channel illustration

This folder contains helper scripts to generate conceptual figures for ITU contribution text.

## Script

- `plot_adjacent_channel_interference.py`

Generates a figure that illustrates:

- DC-MSS occupied channel bandwidth
- MSS generic receive bandwidth
- Adjacent-channel offsets, -5 MHz, -10 MHz, -15 MHz
- Conceptual unwanted-emission coupling into victim MSS channels

## Run

From workspace root:

`python campaigns/mss_d2d_to_mss_adj_study/help_plots/plot_adjacent_channel_interference.py`

Output file:

- `campaigns/mss_d2d_to_mss_adj_study/help_plots/output/adjacent_channel_interference_illustration.png`

## Adjust generic MSS bandwidth

You can edit the value of `mss_generic_bandwidth_mhz` in the script call:

- default: `1.25`

This value is intentionally generic, to represent more than one MSS Earth-station type.
