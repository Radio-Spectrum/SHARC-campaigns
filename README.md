This is a repository for organizing and running parameters for different scenarios in
Sharing and Compatibility Studies.

It is based on the https://github.com/Radio-Spectrum/SHARC simulator,
so you should set it up before trying to use this repository.

After setting it up, you need to run this same command for this repository as well:
```
pip install -e .
```

The nomenclature used here should always be based on the simulator.


Project structure:
```
.
├── from-docs
│   ├── imt
│   │   ├── imt.frequency.topology.equipment-spec.yaml
│   │   └── imt.1-3GHz.single-bs.aas-macro-bs.yaml
│   └── system
│       └── mss-dc
│           └── system-A.some-other.stuff
│       └── eess-es
│           └── some-stuff.some-other.stuff
└── campaigns
    └── mss_dc_to_imt
        ├── readme.md
        └── run.py
```

