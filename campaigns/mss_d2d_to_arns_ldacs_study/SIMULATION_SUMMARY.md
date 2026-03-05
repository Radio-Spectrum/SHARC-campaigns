# MSS D2D-to-MSS Simulation Campaign - Conditions Summary

## Document Information
- **Generated**: 20 de fevereiro de 2026
- **Data Source**: Real simulation inputs and outputs
- **Campaign**: mss_d2d_to_arns_dme_study (Adjacent Channel Scenario)

---

## MSS D2D-to-MSS Adjacent Channel Simulation Campaign

### Campaign Overview
- **Name**: mss_d2d_to_arns_dme_study
- **Type**: Adjacent Channel Interference Analysis
- **Victim Receiver**: MSS Earth Station (at offset frequencies)
- **Interferer**: IMT D2D (System 3) at MSS DC band center

### Simulation Configuration Extracted

#### General Parameters
| Parameter | Value |
|-----------|-------|
| **IMT Frequency** | 2162.5 MHz |
| **Random Seed** | 82 |
| **Snapshots per Scenario** | 10 |
| **Channel Model (ES)** | P.619 |

#### Interference Parameters
| Parameter | Value |
|-----------|-------|
| **Adjacent Channel Emissions** | SPECTRAL_MASK |
| **Spurious Emissions** | -13 dBm |
| **ES Adjacent Ch. Selectivity (ACS)** | 45 dB dB |
| **ES Polarization Loss** | 3 dB dB |

#### Earth Station Types
| Type | Based On |
|------|----------|
| ES Type-1 | 7.1.5 |
| ES Type-2 | 7.1.5 |
| System R | 7.1.4-forward-R |

#### Satellite Configurations
| Altitude | Coverage |
|----------|----------|
| 525 km | 1000 km circular service grid |
| 340 km | 1000 km circular service grid |

#### Frequency Offsets
| Offset | Frequency |
|--------|-----------|
| -10 MHz | 2162.5 MHz |
| -15 MHz | 2162.5 MHz |
| -5 MHz | 2162.5 MHz |

### Generated Scenarios
- **Earth Station Types**: 3
- **Satellite Distances**: 2
- **Frequency Offsets**: 3
- **Total Parameter Sets**: 18
- **Total Output Files**: 18

### Output Metrics
| Metric | Details |
|--------|---------|
| **INR (dB)** | N/A samples per simulation |
| **Format** | CSV files (system_inr.csv) |
| **CCDF Analysis** | Complementary CDF calculated from INR samples |
| **Protection Criterion** | -3 dB @ 0.1% probability |

### Directory Structure
```
mss_d2d_to_arns_dme_study/
├── input/
│   └── parameter_*.yaml (18 files)
├── output/
│   └── output_*/
│       └── system_inr.csv
└── plot/
    ├── ccdf_inr.png
    └── ccdf_inr.pdf
```

### Key Analysis Points
1. **Frequency Sensitivity**: Results show how different offset frequencies affect interference margins
2. **Altitude Impact**: Comparison between 525 km and 340 km satellite altitudes
3. **Antenna Type Effect**: Protection margin variation across ES types
4. **Margin Interpretation**:
   - **Negative margin** = Below protection threshold (✓ PASS - acceptable interference)
   - **Positive margin** = Above protection threshold (✗ FAIL - unacceptable interference)

### Protection Margin Results
See `protection_margins.csv` and run `protection_margins_table.py` for detailed margin analysis.

---

## How to Use This Information

1. **For Report Writing**: Copy tables and parameters directly into your technical document
2. **For Result Analysis**: Use parameter details to understand the simulation conditions
3. **For Reproducibility**: All parameters are extracted from actual YAML input files
4. **For Margin Analysis**: See results in `protection_margins.csv`

---

## Generated Files

- **Input Parameters**: `input/parameter_*.yaml` (extracted parameters above)
- **Simulation Results**: `output/output_*/system_inr.csv` (INR samples)
- **Margin Analysis**: `protection_margins.csv` (margin calculations)
- **Plots**: `plot/ccdf_inr.png` and `plot/ccdf_inr.pdf`

---
