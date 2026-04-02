"""
Dataset registry for the grossman package.

This is the single source of truth for all available datasets.
It mirrors the dataset table from the R grossman package.
"""

DATASETS = {
    "bureaucrats": {
        "description": "Bureaucrat quality (He & Wang 2017)",
        "rows": 2809,
        "cols": 18,
        "variants": [],
    },
    "childpen": {
        "description": "Child penalty (Cortés & Pan 2023)",
        "rows": 54365,
        "cols": 12,
        "variants": [],
    },
    "cigs": {
        "description": "Cigarette sales (Abadie et al. 2010)",
        "rows": 1209,
        "cols": 7,
        "variants": [],
    },
    "cookstove": {
        "description": "Cookstove adoption in Kenya (Berkouwer & Dean 2022)",
        "rows": 7949,
        "cols": 7,
        "variants": [],
    },
    "cps": {
        "description": "CPS wage data",
        "rows": 48371,
        "cols": 16,
        "variants": [],
    },
    "eskom": {
        "description": "South African rural electrification (Dinkelman 2011)",
        "rows": 1816,
        "cols": 18,
        "variants": [],
    },
    "hurricane": {
        "description": "Hurricane fiscal costs (Deryugina 2017)",
        "rows": 49698,
        "cols": 7,
        "variants": [],
    },
    "kenyagrid": {
        "description": "Kenya rural electrification (Lee et al. 2020)",
        "rows": 4368,
        "cols": 52,
        "variants": [],
    },
    "kindy": {
        "description": "Kindergarten & maternal labor (Gelbach 2002)",
        "rows": 17817,
        "cols": 23,
        "variants": [],
    },
    "nit": {
        "description": "Negative income tax experiment (SIME/DIME)",
        "rows": 9720,
        "cols": 12,
        "variants": [],
    },
    "olyset": {
        "description": "Mosquito net adoption (Dupas 2014)",
        "rows": 1078,
        "cols": 4,
        "variants": [],
    },
    "pisa": {
        "description": "PISA incentive experiment (Gneezy et al. 2019)",
        "rows": 1103,
        "cols": 21,
        "variants": [],
    },
    "psid": {
        "description": "PSID earnings & consumption (Blundell et al. 2008)",
        "rows": 4566,
        "cols": 12,
        "variants": ["unbalanced"],
    },
    "queens": {
        "description": "Monarchs and wars (Dube & Harish 2020)",
        "rows": 3586,
        "cols": 17,
        "variants": [],
    },
    "redistribution": {
        "description": "Mobility & redistribution (Alesina et al. 2018)",
        "rows": 9792,
        "cols": 105,
        "variants": [],
    },
    "reservations": {
        "description": "Native American reservations (Dippel 2014)",
        "rows": 182,
        "cols": 19,
        "variants": [],
    },
    "tenncare": {
        "description": "TennCare disenrollment (Garthwaite et al. 2014)",
        "rows": 136,
        "cols": 29,
        "variants": ["micro"],
    },
    "thirdkid": {
        "description": "Family size & labor supply (Angrist & Evans 1998)",
        "rows": 254652,
        "cols": 34,
        "variants": [],
    },
    "unions": {
        "description": "Union wages (Vella & Verbeek 1998)",
        "rows": 4360,
        "cols": 36,
        "variants": [],
    },
    "widows": {
        "description": "Land inheritance in Zambia (Dillon & Voena 2018)",
        "rows": 7825,
        "cols": 16,
        "variants": [],
    },
}
