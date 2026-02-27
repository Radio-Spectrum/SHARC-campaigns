# Compatibility between DC-MSS-IMT in space-to-Earth operation in 2 110–2 180 MHz and MSS Earth stations in downlink operation in 2 110–2 200 MHz

This study assesses the interference from space-to-Earth, downlink, transmissions of a DC-MSS-IMT system, System 3, into MSS Earth station receivers under adjacent-channel conditions, considering the simulation scenarios currently implemented for this analysis.

The compatibility scenarios between DC-MSS-IMT and MSS under study are in accordance with the assumptions considered in Document 4C/356. The scenarios involve the downlink operation of a DC-MSS-IMT system over South America and an MSS Earth station operating in the space-to-Earth, s-E, direction. For contextual purposes, the reference simulation area is centered at Asunción, Paraguay, while the Earth station is randomly positioned within the service area according to the adopted network constraints; however, given the broad applicability of the adopted methodology, the study could be conducted for other locations and is therefore of interest to other administrations. Furthermore, the simulations use MSS Earth station parameters derived from ITU-R recommendations, which provides representativeness to this study.

The study addresses adjacent-channel interference caused by the DC-MSS-IMT downlink at a reference frequency of 2162.5 MHz, on MSS Earth station receivers evaluated at adjacent offsets of -5 MHz, -10 MHz, and -15 MHz, corresponding to 2157.5, 2152.5, and 2147.5 MHz, with victim receiver characteristics consistent with the considered system parameters. The analysis considers two orbital configurations, 340 km and 525 km, two loading conditions, 0.2 and 0.5, and three MSS Earth station profiles, System R, ES Type-1, and ES Type-2, with propagation modeled according to ITU-R P.619 and 3 dB polarization loss.

# Technical and operational characteristics of DC-MSS-IMT operating in the frequency band 2 110-2 200 MHz

For this study, the DC-MSS-IMT system, System 3, is modeled as the interfering system in downlink operation, using a 5 MHz channel and adjacent-channel emission modeling. The interfering reference frequency is set to 2162.5 MHz, while the victim MSS Earth station is assessed at adjacent receive frequencies corresponding to -5 MHz, -10 MHz, and -15 MHz offsets. The analysis is performed for two orbital configurations, 340 km and 525 km, and two network loading conditions, 0.2 and 0.5, with the objective of characterizing interference behavior under representative operational conditions.

The simulation adopts a South America service deployment centered in Asunción, Paraguay, with a circular service grid of 1000 km radius and satellite activation constrained by minimum elevation from the Earth station. For adjacent-channel assessment, co-channel mode is disabled and adjacent-channel mode is enabled, including a spectral-mask-based unwanted emission model and dedicated out-of-band antenna handling for System 3.

Table 1 summarizes the main technical and operational characteristics of the DC-MSS-IMT interferer used in the simulations.

| Parameter | Value used in this study |
|---|---|
| System | DC-MSS-IMT, System 3, downlink, space-to-Earth |
| Role in sharing study | Interfering system |
| Interfering reference frequency | 2162.5 MHz |
| Channel bandwidth | 5 MHz |
| Resource block bandwidth | 0.1 MHz |
| Guard band ratio | 0 |
| Adjacent-channel emissions model | SPECTRAL_MASK |
| Spurious emissions | -13 dBm/MHz |
| Spectral mask used in adjacent runs | STEPPED, System 3 OOBE implementation |
| BS antenna, co-channel reference | ITU-R S.1528-Taylor, maximum gain 34.1 dBi |
| OOB antenna in adjacent runs | Enabled, pattern "Antenna System3 OOB", gain 0.0 dBi |
| BS load probability values | 0.2 and 0.5 |
| Number of snapshots per scenario | 5000 |

Table 2 presents the orbital and deployment assumptions for the DC-MSS-IMT system.

| Parameter | 340 km configuration | 525 km configuration |
|---|---:|---:|
| Orbit altitude, perigee and apogee | 340/340 km | 525/525 km |
| Number of orbital planes | 48 | 28 |
| Satellites per plane | 110 | 120 |
| Inclination | 53.0 degrees | 53.0 degrees |
| Phasing | 1.636 degrees | 1.5 degrees |
| Maximum number of active beams in simulation | 105 | 90 |

Table 3 summarizes scenario-level assumptions that affect DC-MSS-IMT interference generation in the adjacent-channel analysis.

| Parameter | Value used in this study |
|---|---|
| Simulation center | Asunción, Paraguay |
| Reference coordinates | Latitude -25.2637 degrees, Longitude -57.5759 degrees, altitude 200 m |
| Service grid | Circular grid, 1000 km radius |
| Satellite activation criterion | Minimum elevation from Earth station = 5 degrees |
| Channel model for victim link | ITU-R P.619 |
| Polarization loss | 3 dB |
| Adjacent/co-channel simulation flags | Adjacent channel enabled; co-channel disabled |
| Victim ES receive frequencies, adjacent offsets | 2157.5 MHz, offset -5 MHz, 2152.5 MHz, offset -10 MHz, 2147.5 MHz, offset -15 MHz |


# Technical and operational characteristics of MSS, s-E, in the frequency band 2 170-2 200 MHz

In this study, MSS Earth stations are modeled as victim receivers in the space-to-Earth, s-E, direction, using three receiver profiles derived from Document 4C/356 assumptions, System R, ES Type-1 and ES Type-2. These profiles are used to represent different receive bandwidth, antenna gain and receiver-noise conditions for the adjacent-channel compatibility assessment.

Although the MSS Earth-station templates are defined with nominal operation in the 2 170-2 200 MHz range, with nominal center frequency 2172.5 MHz, the simulations evaluate adjacent-channel conditions by setting victim receive frequencies at 2157.5 MHz, 2152.5 MHz and 2147.5 MHz, corresponding to -5 MHz, -10 MHz and -15 MHz offsets from the DC-MSS-IMT interfering reference frequency, 2162.5 MHz.

Table 4 summarizes the MSS Earth-station receiver profiles considered in this study.

| Parameter | System R, 7.1.4 forward | ES Type-1, 7.1.5 | ES Type-2, 7.1.5 |
|---|---:|---:|---:|
| Nominal template center frequency | 2172.5 MHz | 2172.5 MHz | 2172.5 MHz |
| Receiver bandwidth | 1.25 MHz | 0.0216 MHz | 0.0216 MHz |
| Receiver noise temperature | 273 K | 150 K | 150 K |
| Antenna pattern | OMNI | OMNI | OMNI |
| Antenna gain | 6.36 dBi | 2 dBi | 10 dBi |
| Adjacent-channel selectivity in template | 20 dB | 30 dB | 20 dB |
| Operational role in this study | Victim Earth station | Victim Earth station | Victim Earth station |

Table 5 presents the common operational assumptions applied to MSS Earth stations in the simulations.

| Parameter | Value used in this study |
|---|---|
| Link direction | Space-to-Earth, s-E |
| Geometry height | 1.5 m |
| Location model | NETWORK, random location within service area constraints |
| Minimum ES distance to active beam | Equal to simulated MSS-DC beam radius |
| Azimuth pointing distribution | Uniform from -180 to 180 degrees |
| Elevation pointing distribution | Uniform from 5 to 90 degrees |
| Propagation model | ITU-R P.619 |
| Polarization loss | 3 dB |
| Mean clutter height, P.619 | low |
| Below-rooftop flag, P.619 | 0, no clutter-loss application |

In spatial terms, MSS Earth stations are not fixed to a single coordinate in the compatibility assessment. For each simulation realization, the victim Earth-station position is sampled within the service area according to the NETWORK location model, constrained by the minimum distance to the active MSS-DC beam footprint and by the adopted pointing distributions. This procedure allows the study to capture representative geometrical variability of the Earth-station deployment within the covered region.

Figure 1 shows the adopted geometry for MSS Earth-station distribution, including the circular service area, service points, and the relative position of active satellites and the victim reference point.

<img src="plot/scenario.png" alt="Figure 1 – Spatial distribution framework for MSS Earth-station simulations" />

Table 6 summarizes MSS Earth-station receiving frequencies used in the adjacent-channel analysis.

| Case | Victim ES receive frequency | Offset relative to 2162.5 MHz interferer |
|---|---:|---:|
| Adjacent case 1 | 2157.5 MHz | -5 MHz |
| Adjacent case 2 | 2152.5 MHz | -10 MHz |
| Adjacent case 3 | 2147.5 MHz | -15 MHz |




# Propagation models for sharing and compatibility studies in the frequency band 2 110-2 200 MHz

The propagation modelling adopted in this study is summarized in Table A4.3.1.1-4. The propagation path between the MSS Earth station, ES, and the DC-MSS-IMT satellite is modeled using Recommendation ITU-R P.619, including free-space and atmospheric effects. In line with the implemented simulation setup, a polarization loss of 3 dB is applied. No additional statistical clutter-loss term is applied in the analyzed runs.

Recommendation ITU-R P.835 provides the reference standard atmosphere used within the ITU-R P.619 propagation calculation framework. This enables consistent atmospheric parameter representation in the Earth-to-space and space-to-Earth path modeling.

| Model/Recommendation | Path type | Application in this study |
|---|---|---|
| Rec. ITU-R P.619 | Earth-to-space / space-to-Earth satellite path | Main propagation model used for the ES–satellite link, with 3 dB polarization loss |
| Rec. ITU-R P.835 | Reference atmosphere | Atmospheric reference used in the P.619 calculation |



# Methodology
## Interference Scenario

The interference scenario is modeled as an adjacent-channel downlink sharing case in which the DC-MSS-IMT system, System 3, operates as the interfering network and MSS Earth stations operate as victim receivers in the space-to-Earth direction. The analysis focuses on out-of-band and adjacent-channel energy coupling from the DC-MSS-IMT emissions into MSS receiving channels.

To isolate adjacent-channel effects, co-channel operation is disabled and only adjacent-channel coupling is enabled in the simulations. The interfering system is represented by a 5 MHz DC-MSS-IMT carrier at 2162.5 MHz, while victim MSS Earth-station receiving frequencies are evaluated at 2157.5 MHz, 2152.5 MHz and 2147.5 MHz, corresponding to frequency offsets of -5 MHz, -10 MHz and -15 MHz relative to the interferer.

The emission behavior of the interfering system is modeled through a spectral-mask approach, including unwanted-emission treatment for adjacent-channel analysis and a dedicated out-of-band antenna representation consistent with the System 3 implementation assumptions. Victim-receiver susceptibility is represented through MSS Earth-station receiver profiles, System R, ES Type-1, ES Type-2, including their respective receiver bandwidth and antenna characteristics.

The scenario is evaluated over two orbital configurations, 340 km and 525 km, and two loading conditions, 0.2 and 0.5, with Earth-station geometry and pointing sampled over repeated realizations. For each parameter combination, the interference statistics are obtained from Monte Carlo snapshots, 5000 snapshots per case, allowing the derivation of INR distributions and compatibility trends as a function of frequency offset, load condition, and Earth-station profile.

Table 7 summarizes the interference-scenario implementation used in this contribution.

| Item | Implementation in this study |
|---|---|
| Sharing case | Adjacent-channel, downlink |
| Interfering system | DC-MSS-IMT, System 3 |
| Victim system | MSS Earth station, s-E |
| Interferer reference frequency | 2162.5 MHz |
| Victim receive frequencies | 2157.5, 2152.5, 2147.5 MHz |
| Frequency offsets | -5, -10, -15 MHz |
| Adjacent-channel mode | Enabled |
| Emission representation | Spectral-mask-based adjacent-channel modeling |
| Network load cases | 0.2 and 0.5 |
| Orbital cases | 340 km and 525 km |
| Statistical evaluation | 5000 snapshots per case |

Figure 2 shows the frequency-domain arrangement used in adjacent-channel analysis. Out-of-band regions are referenced to the DC-MSS channel edge and expressed in multiples of the DC-MSS channel bandwidth.

<img src="help_plots/output/adjacent_channel_interference_illustration.png" alt="Figure 2 – Frequency-domain arrangement for adjacent-channel interference analysis" />

## Interference Calculation Methodology

The total interference power at the victim MSS Earth-station receiver is calculated as the aggregate contribution from all visible DC-MSS satellites, considering the minimum elevation condition of 5 degrees used in the scenario definition.

For each Monte Carlo snapshot, the linear interference power, in watts, from one visible satellite indexed by $i$ is calculated as the sum of transmitter-side and receiver-side adjacent-channel contributions:

$$
P_{i,\mathrm{linear}} = P_{\mathrm{tx},i,\mathrm{linear}} + P_{\mathrm{rx},i,\mathrm{linear}},
$$

where $P_{\mathrm{tx},i,\mathrm{linear}}$ is the linear power in watts corresponding to the transmitter unwanted emissions into the victim band, and $P_{\mathrm{rx},i,\mathrm{linear}}$ is the linear power in watts corresponding to the victim receiver adjacent-channel susceptibility to the interfering signal.

The per-satellite interference in dBW is then obtained by

$$
I_i = 10\log_{10}\!\left(P_{i,\mathrm{linear}}\right).
$$

Equivalently, if the transmitter and receiver components are initially expressed in dBW as $I_{\mathrm{tx},i}$ and $I_{\mathrm{rx},i}$, the formulation becomes

$$
I_i = 10\log_{10}\!\left(10^{0.1 I_{\mathrm{tx},i}} + 10^{0.1 I_{\mathrm{rx},i}}\right).
$$

In this expression, $I_{\mathrm{tx},i}$ represents the adjacent-channel component driven by the interfering satellite unwanted emissions, obtained from spectral-mask integration over the non-overlapping victim receive band. This term depends on transmit power, off-axis transmit antenna gain in the direction of the victim Earth station, and path attenuation for the corresponding interferer-victim geometry.

The term $I_{\mathrm{rx},i}$ represents the adjacent-channel component associated with victim receiver susceptibility, using the victim adjacent-channel selectivity and the non-overlapping portion of the interfering bandwidth. Propagation loss and antenna discrimination are applied consistently with the same geometry realization.

The aggregate interference for each snapshot is then obtained by linear summation across all visible satellites:

$$
I_{\mathrm{agg}} = 10\log_{10}\!\left(\sum_{i=1}^{N_{\mathrm{vis}}} 10^{0.1 I_i}\right),
$$

where $N_{\mathrm{vis}}$ is the number of satellites satisfying the visibility condition in that snapshot.

The victim receiver noise power is calculated in dBW as

$$
N = 10\log_{10}(k T B),
$$

where $k$ is Boltzmann constant, $T$ is receiver noise temperature, and $B$ is victim receiver bandwidth. In this study, the MSS receiver profiles use $T=273\ \mathrm{K}$ and $B=1.25\ \mathrm{MHz}$ for System R, and $T=150\ \mathrm{K}$ and $B=0.0216\ \mathrm{MHz}$ for ES Type-1 and ES Type-2.

The interference-to-noise ratio for each snapshot is finally obtained as

$$
\mathrm{INR} = I_{\mathrm{agg}} - N.
$$

The above procedure is repeated for all snapshots of each scenario, and the resulting INR samples are used to derive the distribution statistics and CCDF values applied in the compatibility assessment.

### Per-Snapshot Calculation Flow

For each Monte Carlo snapshot, the interference calculation is performed in the following sequence:

1. **Geometry Determination**: The orbital positions of all constellation satellites are computed from the randomized angular state variables $M$ and $\Omega$. The victim MSS Earth-station position is sampled according to the NETWORK location model. Satellite-to-Earth-station distance, elevation angle, and azimuth are then calculated for each satellite.

2. **Visibility Filtering**: Satellites with elevation angle below the minimum threshold of 5 degrees are excluded from the interference calculation. Only satellites satisfying the visibility condition contribute to the aggregate interference for that snapshot.

3. **Per-Satellite Interference Power**: For each visible satellite $i$, the transmitter-side and receiver-side adjacent-channel interference components are calculated in linear scale, and their sum is converted to dBW to yield $I_i$.

4. **Linear Aggregation**: The per-satellite interference powers $I_i$ are converted back to linear scale, summed across all visible satellites, and the resulting aggregate power is converted to dBW to yield $I_{\mathrm{agg}}$.

5. **INR Computation**: The victim receiver noise power $N$ is calculated from the receiver noise temperature and bandwidth. The interference-to-noise ratio is obtained as $\mathrm{INR} = I_{\mathrm{agg}} - N$.

This procedure is applied independently for each of the 5000 snapshots per scenario, providing a statistical representation of the interference environment.

Table 8 summarizes the main variables used in the interference calculation.

| Symbol | Description | Unit | Value/Source |
|---|---|---|---|
| $P_{i,\mathrm{linear}}$ | Linear interference power from satellite $i$ | W | Calculated per snapshot per satellite |
| $P_{\mathrm{tx},i,\mathrm{linear}}$ | Transmitter unwanted emission component | W | From spectral mask over victim band |
| $P_{\mathrm{rx},i,\mathrm{linear}}$ | Receiver susceptibility component | W | From ACS over interfering band |
| $I_i$ | Per-satellite interference power | dBW | $10\log_{10}(P_{i,\mathrm{linear}})$ |
| $I_{\mathrm{tx},i}$ | Transmitter component in dB | dBW | Unwanted emissions into victim band |
| $I_{\mathrm{rx},i}$ | Receiver component in dB | dBW | Victim ACS applied to interferer |
| $I_{\mathrm{agg}}$ | Aggregate interference power | dBW | Linear sum over all visible satellites |
| $N_{\mathrm{vis}}$ | Number of visible satellites | - | Satellites with elevation ≥ 5 degrees |
| $N$ | Receiver noise power | dBW | $10\log_{10}(kTB)$ |
| $k$ | Boltzmann constant | J/K | $1.38 \times 10^{-23}$ |
| $T$ | Receiver noise temperature | K | 273 (System R), 150 (ES Type-1/2) |
| $B$ | Receiver bandwidth | MHz | 1.25 (System R), 0.0216 (ES Type-1/2) |
| $\mathrm{INR}$ | Interference-to-noise ratio | dB | $I_{\mathrm{agg}} - N$ |

## Non-GSO Constellation Modelling

The NGSO constellations are modeled from their Keplerian elements, including orbital altitude, inclination, number of orbital planes, and number of satellites per plane.

To perform a statistical analysis independent of a specific time epoch, a snapshot-based Monte Carlo methodology is applied. In this approach, satellite positions are not propagated through a continuous time simulation. Instead, the initial angular state of the constellation is randomized at each snapshot.

A reference satellite and a reference orbital plane are defined. The mean anomaly, $M$, of the reference satellite and the right ascension of the ascending node, $\Omega$, of the reference orbital plane are modeled as independent random variables with uniform distribution in the interval from 0 degrees to 360 degrees. For each Monte Carlo snapshot, new values of $M$ and $\Omega$ are drawn, and the angular positions of the remaining satellites and orbital planes are then derived according to the orbital parameters adopted for the DC-MSS-IMT system.

This formulation preserves the constellation geometry and relative phasing while ensuring statistically representative sampling of viewing conditions for interference assessment.

Figure 3 shows the orbital-geometry angles used in the NGSO constellation modelling framework.

<img src="help_plots/output/ngso_orbit_plane_angles.png" alt="Figure 3 – Orbit-plane angles used in NGSO constellation modelling" />


## Satellite Beam Generation and Pointing Methodology

To model service deployment for the DC-MSS-IMT system, a Service Grid methodology is used for beam generation and beam pointing. The method is designed to provide systematic coverage of the intended service area while respecting visibility and operational constraints.

The implementation is defined by the following steps.

1. Service grid generation

The service area is discretized into a hexagonal grid of service points. In this campaign, the grid is generated inside a circular zone centered at Asunción, Paraguay, with radius equal to 1000 km. The grid is randomly transformed at each snapshot, with random rotation and translation, so that the spatial sampling is not locked to a fixed grid orientation.

The grid spacing is driven by the beam service radius, which is set from the minus 7 dB contour of the adopted satellite antenna pattern. For the simulated System 3 configurations, the resulting beam-radius values in the generated inputs are 39.684 km for the 525 km orbit and 25.700 km for the 340 km orbit.

Figure 4 shows the hexagonal service grid layout within the circular service area.

<img src="help_plots/output/service_grid_hexagonal.png" alt="Figure 4 – Hexagonal service grid layout within circular service area" />

2. Definition of eligible service points and satellites

At each snapshot, candidate satellites and service points are filtered by geometric constraints. The active-satellite condition applied in this campaign requires minimum elevation from the Earth station equal to 5 degrees. In addition, the service-grid eligibility zone for serving satellites uses a dedicated margin parameter, equal to minus 200 km in this study, which allows satellites outside the strict service border to serve edge service points when geometrically favorable.

Figure 5 shows the eligibility zone concept with the margin parameter visualization.

<img src="help_plots/output/satellite_eligibility.png" alt="Figure 5 – Satellite eligibility zone with margin parameter" />

3. Beam assignment and pointing

For each service point in the grid, the serving satellite is selected using a best-server rule based on elevation angle. The satellite that provides the highest elevation at that service point is selected, and the corresponding beam is pointed to that point. A minimum service angle criterion is then applied to accept only links with sufficient geometry quality.

This procedure produces a snapshot-dependent beam layout that follows the constellation geometry and the service-grid constraints. Figure 1 shows one representative spatial snapshot with service points and active satellites. The total number of beams per satellite is also limited by system configuration, with maximum values equal to 105 for the 340 km case and 90 for the 525 km case.

Figure 6 shows the beam assignment methodology with best-server selection based on elevation angle.

<img src="help_plots/output/beam_assignment.png" alt="Figure 6 – Beam assignment using best-server selection by elevation angle" />

Table 9 summarizes the service grid parameters for the two orbital configurations analyzed in this study.

| Parameter | 340 km configuration | 525 km configuration |
|---|---:|---:|
| Service area shape | Circular | Circular |
| Service area radius | 1000 km | 1000 km |
| Service area center | Asunción, Paraguay | Asunción, Paraguay |
| Grid topology | Hexagonal | Hexagonal |
| Beam radius (from -7 dB antenna contour) | 25.700 km | 39.684 km |
| Hexagonal grid spacing | ~25.7 km | ~39.7 km |
| Eligibility margin parameter | -200 km | -200 km |
| Effective eligibility radius | 1200 km | 1200 km |
| Minimum elevation for satellite activation | 5 degrees | 5 degrees |
| Best-server selection criterion | Highest elevation angle | Highest elevation angle |
| Maximum beams per satellite | 105 | 90 |
| Grid random transformation per snapshot | Rotation + translation | Rotation + translation |

## Satellite System Load Factor

To model realistic network usage conditions, a satellite system load factor is applied in the simulation. The load factor defines the probability that any given beam is active and transmitting during a single simulation snapshot. This statistical approach represents the fact that not all beams are simultaneously active in actual network operation, as traffic demand varies across the service area.

For this analysis, two load factor values were considered: 0.2 (20%) and 0.5 (50%). These values represent different network utilization scenarios, from moderate traffic conditions (20%) to higher demand scenarios (50%). The load factor is applied independently to each beam at each Monte Carlo snapshot, with the activation state determined by a random draw from a Bernoulli distribution.

The actual number of active beams per satellite varies randomly across snapshots, following a binomial distribution. For a satellite with maximum capacity of $n_{\mathrm{max}}$ beams and load factor $p$, the expected number of active beams is $p \cdot n_{\mathrm{max}}$, with variance $p(1-p) n_{\mathrm{max}}$.

In the 340 km configuration with maximum 105 beams per satellite, the 20% load factor yields an expected 21 active beams per satellite, while the 50% load factor yields approximately 52.5 active beams. For the 525 km configuration with maximum 90 beams, the corresponding expected values are 18 and 45 active beams, respectively.

This load-factor implementation allows the study to capture representative interference conditions under different traffic scenarios, providing a more realistic assessment than assuming all beams are always active at maximum power.



# Results of the study

This study addresses an adjacent-channel interference scenario involving the DC-MSS-IMT, downlink, system and MSS, s-E, Earth station receivers. The victim MSS Earth station is located at a fixed position. In each simulation snapshot, an elevation angle and an azimuth angle of the receiving antenna are randomly selected, representing the variability of the antenna orientation with respect to the non-GSO DC-MSS-IMT satellites. These elevation and azimuth angles are modeled as independent random variables uniformly distributed over the range from 5 to 90 degrees and from -180 to 180 degrees, respectively. The results are presented for the case of adjacent-channel interference from the DC-MSS-IMT system.

Two protection criteria are applied to the INR distribution obtained from the Monte Carlo simulation:

- Criterion 1: INR shall not exceed -6 dB for more than 0.1% of the time.
- Criterion 2: INR shall not exceed -12 dB for more than 20% of the time.

The protection margin is defined as the difference between the INR value at the specified probability level and the corresponding threshold. A negative margin indicates that the protection criterion is met, PASS, while a positive margin indicates that the criterion is exceeded, FAIL.

## Protection Margin Results for ES Type-1

Table 10 presents the protection margins for ES Type-1 (7.1.5), antenna gain 2 dBi, receiver bandwidth 0.0216 MHz, ACS 30 dB.

| Orbit | Load | Frequency Offset | Margin at -6 dB / 0.1% (dB) | Margin at -12 dB / 80% (dB) |
|---|---|---|---:|---:|
| 340 km | 0.1 | -5 MHz (2157.5 MHz) | -6.05 | -1.00 |
| 340 km | 0.1 | -10 MHz (2152.5 MHz) | -24.05 | -19.00 |
| 340 km | 0.1 | -15 MHz (2147.5 MHz) | -34.05 | -29.00 |
| 340 km | 0.2 | -5 MHz (2157.5 MHz) | -5.97 | -0.87 |
| 340 km | 0.2 | -10 MHz (2152.5 MHz) | -23.97 | -18.87 |
| 340 km | 0.2 | -15 MHz (2147.5 MHz) | -33.97 | -28.87 |
| 340 km | 0.5 | -5 MHz (2157.5 MHz) | -0.33 | 4.17 |
| 340 km | 0.5 | -10 MHz (2152.5 MHz) | -18.33 | -13.83 |
| 340 km | 0.5 | -15 MHz (2147.5 MHz) | -28.33 | -23.83 |
| 525 km | 0.1 | -5 MHz (2157.5 MHz) | -9.59 | -4.73 |
| 525 km | 0.1 | -10 MHz (2152.5 MHz) | -27.59 | -22.73 |
| 525 km | 0.1 | -15 MHz (2147.5 MHz) | -37.59 | -32.73 |
| 525 km | 0.2 | -5 MHz (2157.5 MHz) | -9.41 | -4.43 |
| 525 km | 0.2 | -10 MHz (2152.5 MHz) | -27.41 | -22.43 |
| 525 km | 0.2 | -15 MHz (2147.5 MHz) | -37.41 | -32.43 |
| 525 km | 0.5 | -5 MHz (2157.5 MHz) | -4.83 | -0.90 |
| 525 km | 0.5 | -10 MHz (2152.5 MHz) | -22.83 | -18.90 |
| 525 km | 0.5 | -15 MHz (2147.5 MHz) | -32.83 | -28.90 |

For ES Type-1, the -6 dB / 0.1% criterion is met in all 18 evaluated scenarios. The -12 dB / 80% criterion is met in 17 out of 18 scenarios. The single exceedance occurs at -5 MHz offset with the 340 km orbit and 0.5 load factor, with a margin of +4.17 dB. In all other configurations, the margins range from -0.87 dB at -5 MHz offset (340 km, 0.2 load) to -32.73 dB at -15 MHz offset (525 km, 0.1 load). The 525 km orbit yields margins that are 3 to 5 dB lower than the corresponding 340 km cases.

## Protection Margin Results for ES Type-2

Table 11 presents the protection margins for ES Type-2 (7.1.5), antenna gain 10 dBi, receiver bandwidth 0.0216 MHz, ACS 20 dB.

| Orbit | Load | Frequency Offset | Margin at -6 dB / 0.1% (dB) | Margin at -12 dB / 80% (dB) |
|---|---|---|---:|---:|
| 340 km | 0.1 | -5 MHz (2157.5 MHz) | 1.95 | 7.00 |
| 340 km | 0.1 | -10 MHz (2152.5 MHz) | -16.05 | -11.00 |
| 340 km | 0.1 | -15 MHz (2147.5 MHz) | -26.05 | -21.00 |
| 340 km | 0.2 | -5 MHz (2157.5 MHz) | 2.03 | 7.13 |
| 340 km | 0.2 | -10 MHz (2152.5 MHz) | -15.97 | -10.87 |
| 340 km | 0.2 | -15 MHz (2147.5 MHz) | -25.97 | -20.87 |
| 340 km | 0.5 | -5 MHz (2157.5 MHz) | 7.67 | 12.17 |
| 340 km | 0.5 | -10 MHz (2152.5 MHz) | -10.33 | -5.83 |
| 340 km | 0.5 | -15 MHz (2147.5 MHz) | -20.33 | -15.83 |
| 525 km | 0.1 | -5 MHz (2157.5 MHz) | -1.59 | 3.27 |
| 525 km | 0.1 | -10 MHz (2152.5 MHz) | -19.59 | -14.73 |
| 525 km | 0.1 | -15 MHz (2147.5 MHz) | -29.59 | -24.73 |
| 525 km | 0.2 | -5 MHz (2157.5 MHz) | -1.41 | 3.57 |
| 525 km | 0.2 | -10 MHz (2152.5 MHz) | -19.41 | -14.43 |
| 525 km | 0.2 | -15 MHz (2147.5 MHz) | -29.41 | -24.43 |
| 525 km | 0.5 | -5 MHz (2157.5 MHz) | 3.17 | 7.10 |
| 525 km | 0.5 | -10 MHz (2152.5 MHz) | -14.83 | -10.90 |
| 525 km | 0.5 | -15 MHz (2147.5 MHz) | -24.83 | -20.90 |

For ES Type-2, the -6 dB / 0.1% criterion is exceeded in 4 out of 18 scenarios, all at -5 MHz offset. At the 340 km orbit, exceedances occur at all three load factors, with margins ranging from +1.95 dB (0.1 load) to +7.67 dB (0.5 load). At the 525 km orbit, the exceedance occurs only at 0.5 load factor (+3.17 dB), while load factors 0.1 and 0.2 yield negative margins of -1.59 dB and -1.41 dB.

The -12 dB / 80% criterion is exceeded in 6 out of 18 scenarios, all at -5 MHz offset. At this offset, the criterion is exceeded for all orbital configurations and all load factors evaluated.

At -10 MHz and -15 MHz offsets, both protection criteria are met in all configurations, with margins ranging from -5.83 dB to -29.59 dB.

## Protection Margin Results for System R

Table 12 presents the protection margins for System R (7.1.4 forward), antenna gain 6.36 dBi, receiver bandwidth 1.25 MHz, ACS 20 dB.

| Orbit | Load | Frequency Offset | Margin at -6 dB / 0.1% (dB) | Margin at -12 dB / 80% (dB) |
|---|---|---|---:|---:|
| 340 km | 0.1 | -5 MHz (2157.5 MHz) | -4.29 | 0.76 |
| 340 km | 0.1 | -10 MHz (2152.5 MHz) | -22.29 | -17.24 |
| 340 km | 0.1 | -15 MHz (2147.5 MHz) | -32.29 | -27.24 |
| 340 km | 0.2 | -5 MHz (2157.5 MHz) | -4.21 | 0.89 |
| 340 km | 0.2 | -10 MHz (2152.5 MHz) | -22.21 | -17.11 |
| 340 km | 0.2 | -15 MHz (2147.5 MHz) | -32.21 | -27.11 |
| 340 km | 0.5 | -5 MHz (2157.5 MHz) | 1.43 | 5.93 |
| 340 km | 0.5 | -10 MHz (2152.5 MHz) | -16.57 | -12.07 |
| 340 km | 0.5 | -15 MHz (2147.5 MHz) | -26.57 | -22.07 |
| 525 km | 0.1 | -5 MHz (2157.5 MHz) | -7.84 | -2.98 |
| 525 km | 0.1 | -10 MHz (2152.5 MHz) | -25.84 | -20.98 |
| 525 km | 0.1 | -15 MHz (2147.5 MHz) | -35.84 | -30.98 |
| 525 km | 0.2 | -5 MHz (2157.5 MHz) | -7.65 | -2.68 |
| 525 km | 0.2 | -10 MHz (2152.5 MHz) | -25.65 | -20.68 |
| 525 km | 0.2 | -15 MHz (2147.5 MHz) | -35.65 | -30.68 |
| 525 km | 0.5 | -5 MHz (2157.5 MHz) | -3.07 | 0.86 |
| 525 km | 0.5 | -10 MHz (2152.5 MHz) | -21.07 | -17.14 |
| 525 km | 0.5 | -15 MHz (2147.5 MHz) | -31.07 | -27.14 |

For System R, the -6 dB / 0.1% criterion is exceeded in 1 out of 18 scenarios: 340 km orbit, 0.5 load factor, -5 MHz offset, with a margin of +1.43 dB. All other configurations meet this criterion.

The -12 dB / 80% criterion is exceeded in 3 out of 18 scenarios, all at -5 MHz offset: 340 km with 0.1 load (+0.76 dB), 340 km with 0.2 load (+0.89 dB), and 525 km with 0.5 load (+0.86 dB). At the 525 km orbit with 0.1 and 0.2 load, the margin is -2.98 dB and -2.68 dB, meeting the criterion.

At -10 MHz and -15 MHz offsets, both protection criteria are met in all configurations for System R, with margins ranging from -12.07 dB to -35.84 dB.


# Conclusion of study

This study evaluated adjacent-channel interference from the DC-MSS-IMT System 3 downlink into MSS Earth station receivers operating in the space to Earth direction. The analysis covered frequency offsets of -5, -10, and -15 MHz, orbital configurations of 340 km and 525 km, load factors of 0.1, 0.2, and 0.5, and MSS Earth station profiles System R, ES Type-1, and ES Type-2. A total of 54 scenario configurations were assessed against two protection criteria, INR not exceeding -6 dB for more than 0.1 percent of the time, and INR not exceeding -12 dB for more than 20 percent of the time.

At -10 MHz and -15 MHz offsets, both protection criteria are met in all 36 evaluated configurations, with margins from -5.83 dB to -37.59 dB. At -5 MHz offset, exceedances are observed in a subset of configurations, with the number and magnitude of exceedances varying by ES type, orbital altitude, and load factor.

At -5 MHz offset, ES Type-2, antenna gain 10 dBi, ACS 20 dB, has 4 out of 6 configurations exceeding the -6 dB criterion at 0.1 percent and 6 out of 6 exceeding the -12 dB criterion at 20 percent. System R, antenna gain 6.36 dBi, ACS 20 dB, has 1 out of 6 configurations exceeding the -6 dB criterion at 0.1 percent and 3 out of 6 exceeding the -12 dB criterion at 20 percent. ES Type-1, antenna gain 2 dBi, ACS 30 dB, has no exceedances for the -6 dB criterion at 0.1 percent and 1 out of 6 exceedances for the -12 dB criterion at 20 percent.

The adjacent-channel compatibility between DC-MSS-IMT System 3 and MSS Earth stations depends on the frequency offset. At -10 MHz and -15 MHz offsets, both protection criteria are met in all evaluated configurations. At -5 MHz offset, the protection criteria are not met in a subset of configurations, concentrated in scenarios with higher antenna gain, lower adjacent-channel selectivity, lower orbital altitude, and higher load factor.
