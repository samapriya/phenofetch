# PhenoFetch

A command-line tool for downloading and analyzing PhenoCam data from NEON (National Ecological Observatory Network) sites.


**This tool is not officially affiliated with the National Ecological Observatory Network (NEON) or the PhenoCam Network.**

## Table of Contents

- [PhenoFetch](#phenofetch)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Setup](#setup)
  - [Usage](#usage)
    - [List Available Sites](#list-available-sites)
    - [Download Data](#download-data)
    - [View Site Statistics](#view-site-statistics)
  - [Examples](#examples)
    - [List All Sites](#list-all-sites)
    - [Download Images for a Specific Date Range](#download-images-for-a-specific-date-range)
    - [View Site Statistics Example](#view-site-statistics-example)
  - [License](#license)
  - [Contact](#contact)

## Overview

PhenoFetch is a Python-based tool designed to facilitate the retrieval and analysis of PhenoCam data from the National Ecological Observatory Network (NEON). PhenoCam data consists of time-lapse images used to monitor vegetation phenology (seasonal changes) at various ecological sites across the United States.

This tool simplifies the process of downloading images and metadata from the PhenoCam web service, providing both batch download capabilities and summary statistics for data availability.

## Features

- **Site Discovery**: List all available NEON PhenoCam sites with their details
- **Data Download**: Efficiently download PhenoCam images and metadata for specified sites and date ranges
- **Site Statistics**: View comprehensive statistics about data availability for each site
- **Asynchronous Processing**: Fast, concurrent downloading using asynchronous I/O
- **Smart Concurrency**: Automatically adjusts download parallelism based on system resources
- **Progress Tracking**: Clear progress bars and status updates during operations

## Installation

### Requirements

- Python 3.7+
- Required Python packages (see `requirements.txt`)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/phenofetch.git
   cd phenofetch
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

PhenoFetch provides three main commands:

- `sites`: List all available PhenoCam sites
- `download`: Download data for a specific site and date range
- `stats`: Display statistics for a site

### List Available Sites

To see all available NEON PhenoCam sites:

```bash
python phenofetch.py sites
```

### Download Data

To download data for a specific site and date range:

```bash
python phenofetch.py download --site SITE_CODE --product PRODUCT_ID --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--download] [--output-dir DIR]
```

Required arguments:
- `--site`: NEON site code (e.g., ABBY, BART)
- `--product`: NEON product ID (e.g., DP1.00033)
- `--start-date`: Start date in YYYY-MM-DD format
- `--end-date`: End date in YYYY-MM-DD format

Optional arguments:
- `--download`: Flag to actually download files (if omitted, just shows a summary)
- `--output-dir`: Directory to save downloaded files (default: ./phenocam_data)
- `--batch-size`: Number of files to download in each batch (default: 50)
- `--concurrency`: Maximum number of concurrent downloads (default: auto-determined)
- `--timeout`: Connection timeout in seconds (default: 30)

### View Site Statistics

To view statistics for a specific site:

```bash
python phenofetch.py stats --site SITE_CODE --product PRODUCT_ID
```

## Examples

### List All Sites

```bash
python phenofetch.py sites
```

This will display a table of all available NEON PhenoCam sites, including their site codes, descriptions, domains, states, and types.

### Download Images for a Specific Date Range

```bash
python phenofetch.py download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31 --download --output-dir ./my_phenocam_data
```

This will:
1. Fetch all available PhenoCam data from the ABBY site for January 2022
2. Download all images, thumbnails, and metadata files to the specified directory
3. Show progress as the downloads proceed

### View Site Statistics Example

```bash
python phenofetch.py stats --site HARV --product DP1.00033
```

This will display:
1. A summary table showing data availability by year and month for the Harvard Forest site
2. Total image counts
3. Year-by-year statistics
4. Average images per month


## License

Apache License 2.0

## Contact

For questions or feedback, please contact:
- Samapriya Roy

---
