# Installation Guide

## Prerequisites

- **Python**: 3.11 or higher
- **Conda** or **venv** environment manager
- **RDKit**: 2024.3.5 or compatible version

## Setup Environment

### Option A: Using Conda (Recommended)

```bash
conda create -n asd_env python=3.11 -y
conda activate asd_env
conda install -c conda-forge rdkit -y
pip install -e .
```

### Option B: Using Pip & Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Verify Installation

Check that the CLI tool runs cleanly:

```bash
python -m asd_mcda.cli --version
```
