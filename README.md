This is a repository for organizing and running parameters for different scenarios in
Sharing and Compatibility Studies.

It is based on the https://github.com/Radio-Spectrum/SHARC simulator,
so you should set it up before trying to use this repository.

After setting it up, you need to run this same command for this repository as well:
```
pip install -e .
```

The nomenclature used here should always be based on the simulator. Since the simulator


Project structure:
.
├── from-docs
│   ├── imt
│   │   ├── macro
│   │   │   └── 7.1-8.4GHz
│   │   │       ├── readme.md
│   │   │       └── imt_params.yaml
│   │   ├── hotspot
│   │   │   └── 7.1-8.4GHz
│   │   │       ├── readme.md
│   │   │       └── imt_params.yaml
│   │   └── mss-dc
│   │       └── 7.1-8.4GHz
│   │           ├── readme.md
│   │           └── imt_params.yaml
│   └── system
│       └── mss-dc
│           ├── readme.md
│           └── system-A
│               └── 2.1GHz
│                   ├── readme.md
│                   └── mss_d2d_params.yaml
└── campaigns
    └── mss_dc_to_imt
        ├── readme.md
        └── run.py

