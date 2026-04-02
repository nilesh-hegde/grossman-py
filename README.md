# grossman-py

> **Note:** This is an unofficial Python client. All datasets are hosted and maintained by Alexander Torgovitsky at [grossman-data](https://github.com/a-torgovitsky/grossman-data). This package is a Python equivalent of the R package [grossman](https://github.com/a-torgovitsky/grossman), built for students who prefer working in Python.

## Installation

```bash
pip install git+https://github.com/nilesh-hegde/grossman-py.git
```

## Usage

```python
import grossman

# See available datasets
grossman.list()

# Load a dataset
df = grossman.load("psid")

# Load a variant
df\_ub = grossman.load("psid", variant="unbalanced")

# Access variable labels
df.attrs\["labels"]

# Force re-download (clears cache for this dataset)
df = grossman.load("psid", refresh=True)

# Clear all cached data
grossman.clear\_cache()
```

**Important:** Always use the `grossman.` prefix — do NOT call `from grossman import list, load`. The package exports functions named `list` and `load`, which shadow Python builtins. This is the same pattern as the R package's `grossman::list()` and `grossman::load()`.

## Available Datasets

|Dataset|Description|Rows|Cols|Variants|
|-|-|-|-|-|
|`bureaucrats`|Bureaucrat quality (He \& Wang 2017)|2809|18||
|`childpen`|Child penalty (Cortés \& Pan 2023)|54365|12||
|`cigs`|Cigarette sales (Abadie et al. 2010)|1209|7||
|`cookstove`|Cookstove adoption in Kenya (Berkouwer \& Dean 2022)|7949|7||
|`cps`|CPS wage data|48371|16||
|`eskom`|South African rural electrification (Dinkelman 2011)|1816|18||
|`hurricane`|Hurricane fiscal costs (Deryugina 2017)|49698|7||
|`kenyagrid`|Kenya rural electrification (Lee et al. 2020)|4368|52||
|`kindy`|Kindergarten \& maternal labor (Gelbach 2002)|17817|23||
|`nit`|Negative income tax experiment (SIME/DIME)|9720|12||
|`olyset`|Mosquito net adoption (Dupas 2014)|1078|4||
|`pisa`|PISA incentive experiment (Gneezy et al. 2019)|1103|21||
|`psid`|PSID earnings \& consumption (Blundell et al. 2008)|4566|12|`unbalanced`|
|`queens`|Monarchs and wars (Dube \& Harish 2020)|3586|17||
|`redistribution`|Mobility \& redistribution (Alesina et al. 2018)|9792|105||
|`reservations`|Native American reservations (Dippel 2014)|182|19||
|`tenncare`|TennCare disenrollment (Garthwaite et al. 2014)|136|29|`micro`|
|`thirdkid`|Family size \& labor supply (Angrist \& Evans 1998)|254652|34||
|`unions`|Union wages (Vella \& Verbeek 1998)|4360|36||
|`widows`|Land inheritance in Zambia (Dillon \& Voena 2018)|7825|16||

## Running Tests

```bash
# Install dev dependencies
pip install -e ".\[dev]"

# Run offline tests only (no network needed)
pytest -m "not online"

# Run all tests including downloads
pytest

# Run the full parity check (downloads ALL 20 datasets)
pytest -m "online and slow" -v
```

## License

MIT

