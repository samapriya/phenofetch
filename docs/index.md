# PhenoFetch

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=plastic&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/samapriya/)
[![CI phenofetch](https://github.com/samapriya/phenofetch/actions/workflows/package-ci.yml/badge.svg)](https://github.com/samapriya/phenofetch/actions/workflows/package-ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15207693.svg)](https://doi.org/10.5281/zenodo.15207693)
![PyPI - Version](https://img.shields.io/pypi/v/phenofetch)
![PyPI - Downloads](https://img.shields.io/pypi/dm/phenofetch)
![GitHub Release](https://img.shields.io/github/v/release/samapriya/phenofetch)
[![Donate](https://img.shields.io/badge/Donate-Buy%20me%20a%20Coffee-teal)](https://www.buymeacoffee.com/samapriya)
[![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/samapriya)


<p align="center">
  <img src="https://github.com/user-attachments/assets/6e777aab-e4ff-480c-9128-2d115cb07f83" width="200" alt="PhenoFetch Logo">
</p>

[![CI phenofetch](https://github.com/samapriya/phenofetch/actions/workflows/package-ci.yml/badge.svg)](https://github.com/samapriya/phenofetch/actions/workflows/package-ci.yml)

A command-line tool for downloading and analyzing PhenoCam data from NEON (National Ecological Observatory Network) sites. PhenoFetch simplifies the process of retrieving and analyzing time-lapse images used to monitor vegetation phenology (seasonal changes) across various ecological sites in the United States.

## What is PhenoFetch?

PhenoFetch is a Python-based tool designed to facilitate the retrieval and analysis of PhenoCam data from the National Ecological Observatory Network (NEON). It provides both batch download capabilities and summary statistics for data availability, making it easier for researchers, students, and data scientists to work with phenological data.

!!! note
    This tool is not officially affiliated with the National Ecological Observatory Network (NEON) or the PhenoCam Network.

## Key Features

- **Site Discovery**: List all available NEON PhenoCam sites with their details
- **Data Download**: Efficiently download PhenoCam images and metadata for specified sites and date ranges
- **Site Statistics**: View comprehensive statistics about data availability for each site
- **Size Estimation**: Estimate the total download size before starting a large download
- **Asynchronous Processing**: Fast, concurrent downloading using asynchronous I/O
- **Smart Concurrency**: Automatically adjusts download parallelism based on system resources
- **Progress Tracking**: Clear progress bars and status updates during operations

## Citation

```
Samapriya Roy. (2025). samapriya/phenofetch: PhenoCam Command Line Tool (0.2.1).
Zenodo. https://doi.org/10.5281/zenodo.15207693
```

## Quick Start

```bash
# Install the package
pip install phenofetch

# List all available sites
phenofetch sites

# Download images for a specific site and date range
phenofetch download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31 --download
```

For more detailed documentation, please explore the other sections of this site:

- [Installation](installation.md) - How to install PhenoFetch
- [Usage](usage.md) - Detailed usage instructions
- [Commands](commands/index.md) - Documentation for all commands
- [Examples](examples.md) - Example use cases
- [FAQ](faq.md) - Frequently asked questions
- [Changelog](changelog.md) - Version history and changes
