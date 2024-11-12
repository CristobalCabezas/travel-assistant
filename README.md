# Travel Assistant

## Installation

### 1) With Poetry

#### Install poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Verify that Poetry is correctly installed:

```bash
poetry --version
```

#### Install dependencies

```bash
poetry install
```

#### Run script

```bash
poetry run python main.py
```

### 2) With Docker

#### Install

```bash
docker build -t travel-assistant .
```

#### Run

```bash
docker run -p 8100:8100 travel-assistant
```