## Fregate
Author: TonyChG
Contributor: Dauliac

## Requirements

- You simply need `virtualbox` installed

## Installation

```
# From pip repository
pip3 install -U --user http://pypi.dotfile.eu/fregate/fregate-0.0.1.tar.gz

# From git repository
virtualenv -p python3 venv
source venv/bin/activate
pip install -e .
```

## Usage

```
fregate -c <configfile> up
fregate -c <configfile> ssh fregate-001
```
