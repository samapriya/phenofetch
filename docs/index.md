# PhenoFetch

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
