# cimis

Python wrapper for CIMIS API

## Development

### Update development environment

Development requirements are documented in `requirements.txt`. If using `conda`,
the following commands will create an environment:

```sh
conda create -n cimis
conda config --append channels conda-forge
```

To update the environment:

```sh
conda env update -n cimis -f requirements.txt
```

### Document

Documentation is done using `pyment`. For example:

```sh
pyment -w -o numpydoc cimis/cimis.py
```