# photo-import

A script for importing photos into the file structure I like

## Setup

Assuming you're using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) then:

```sh
# From the root
git submodule update --init
mkvirtualenv photoimport
pip install -r requirements.txt
```

## Usage
```sh
# Assuming you've activated the photoimport virtualenv from before
python photo-import.py --input <path to sdcard> --out <path to top level photos folder>
```
