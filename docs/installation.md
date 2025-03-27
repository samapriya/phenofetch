# Installation

PhenoFetch can be installed easily using pip, or directly from the source code.

## Prerequisites

Before installing PhenoFetch, ensure you have the following prerequisites:

- Python 3.9 or higher
- pip (Python package installer)

## Install via pip

The simplest way to install PhenoFetch is through pip:

```bash
pip install phenofetch
```

To upgrade to the latest version:

```bash
pip install --upgrade phenofetch
```

## Install from source

If you prefer to install from source or want to contribute to the development:

1. Clone the repository:
   ```bash
   git clone https://github.com/samapriya/phenofetch.git
   cd phenofetch
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

## Dependencies

PhenoFetch relies on the following Python packages (these will be automatically installed with pip):

- requests >= 2.28.0
- beautifulsoup4 >= 4.11.0
- aiofiles >= 0.8.0
- aiohttp >= 3.8.0
- psutil >= 5.9.0
- rich >= 12.0.0
- tqdm >= 4.64.0
- colorama >= 0.4.4

## Verification

To verify that PhenoFetch was installed correctly, run:

```bash
phenofetch --help
```

You should see the help menu with all available commands.

## Common Installation Issues

### Permission denied errors

If you encounter permission errors while installing, try using:

```bash
pip install --user phenofetch
```

### Package not found after installation

If the `phenofetch` command is not found after installation, ensure that your Python scripts directory is in your system PATH.

For most systems, you can check where pip installs executables with:

```bash
pip show phenofetch
```

Then add the relevant bin directory to your PATH if necessary.

### Incompatible Python version

PhenoFetch requires Python 3.9 or higher. If you're using an older version, you'll need to upgrade your Python installation.
