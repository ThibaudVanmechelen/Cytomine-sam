# Cytomine SAM
Cytomine SAM API Server

# Requirements
Python 3.12+

# Development

## Using Poetry

```bash
poetry shell
poetry install
git lfs install
git lfs pull
uvicorn src.app:app --reload
```

Note: please ensure that the weights.pt file has indeed been downloaded, so that you are not using the lfs pointer file.

## Using Docker

```bash
docker build -t your-api .
docker run -v $(pwd)/keys.toml:/app/keys.toml -p 6000:6000 your-api # provide the keys.toml file for cytomine for the api to work
```

## Keys.toml format

```bash
title = "Cytomine API keys"
host = "your_host"
public_key = "your_public_key"
private_key = "your_private_key"
```

# License

Apache 2.0

# Contributions

- Great part of this code has been inspired by the [cbir](https://github.com/Cytomine-ULiege/Cytomine-cbir) repository.
