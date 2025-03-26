# PhenoFetch

<p align="center">
  <img src="https://github.com/user-attachments/assets/6e777aab-e4ff-480c-9128-2d115cb07f83" width="200" alt="Logo">
</p>

A command-line tool for downloading and analyzing PhenoCam data from NEON (National Ecological Observatory Network) sites. PhenoFetch is a Python-based tool designed to facilitate the retrieval and analysis of PhenoCam data from the National Ecological Observatory Network (NEON). PhenoCam data consists of time-lapse images used to monitor vegetation phenology (seasonal changes) at various ecological sites across the United States. This tool simplifies the process of downloading images and metadata from the PhenoCam web service, providing both batch download capabilities and summary statistics for data availability.

**This tool is not officially affiliated with the National Ecological Observatory Network (NEON) or the PhenoCam Network.**

## Table of Contents

- [PhenoFetch](#phenofetch)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Setup](#setup)
  - [Usage](#usage)
    - [List Available Sites](#list-available-sites)
    - [View Site Statistics](#view-site-statistics)
    - [Estimate Download Size](#estimate-download-size)
    - [Download Data](#download-data)
  - [Examples](#examples)
    - [List All Sites](#list-all-sites)
    - [View Site Statistics Example](#view-site-statistics-example)
    - [Estimate Download Size Example](#estimate-download-size-example)
    - [Download Images for a Specific Date Range](#download-images-for-a-specific-date-range)
  - [License](#license)
  - [Contact](#contact)
  - [PhenoFetch Changelog](#phenofetch-changelog)
    - [Version 0.0.2](#version-002)

## Features

- **Site Discovery**: List all available NEON PhenoCam sites with their details
- **Data Download**: Efficiently download PhenoCam images and metadata for specified sites and date ranges
- **Site Statistics**: View comprehensive statistics about data availability for each site
- **Size Estimation**: Estimate the total download size before starting a large download
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

PhenoFetch provides four main commands:

- `sites`: List all available PhenoCam sites
- `stats`: Display statistics for a site
- `estimate`: Estimate download size for a date range
- `download`: Download data for a specific site and date range

### List Available Sites

To see all available NEON PhenoCam sites:

```bash
python phenofetch.py sites
```

### View Site Statistics

To view statistics for a specific site:

```bash
python phenofetch.py stats --site SITE_CODE --product PRODUCT_ID
```

### Estimate Download Size

To estimate the download size for a specific site and date range:

```bash
python phenofetch.py estimate --site SITE_CODE --product PRODUCT_ID --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Optional arguments:
- `--batch-size`: Number of files to process in each batch (default: 50)
- `--concurrency`: Maximum number of concurrent connections (default: auto-determined)
- `--timeout`: Connection timeout in seconds (default: 30)

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

## Examples

### List All Sites

```bash
python phenofetch.py sites
```

This will display a table of all available NEON PhenoCam sites, including their site codes, descriptions, domains, states, and types.

### View Site Statistics Example

```bash
python phenofetch.py stats --site HARV --product DP1.00033
```

This will display:
1. A summary table showing data availability by year and month for the Harvard Forest site
2. Total image counts
3. Year-by-year statistics
4. Average images per month

### Estimate Download Size Example

```bash
python phenofetch.py estimate --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31
```

This will:
1. Fetch all available PhenoCam data links from the ABBY site for January 2022
2. Check the size of each file without downloading it
3. Display a summary of the estimated total download size, broken down by file type
4. Help you make an informed decision before starting a large download

### Download Images for a Specific Date Range

```bash
python phenofetch.py download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31 --download --output-dir ./my_phenocam_data
```

This will:
1. Fetch all available PhenoCam data from the ABBY site for January 2022
2. Download all images, thumbnails, and metadata files to the specified directory
3. Show progress as the downloads proceed

## License

Apache License 2.0

## Contact

For questions or feedback, please contact:
- Samapriya Roy

---

## PhenoFetch Changelog

### Version 0.0.2
- **Added**: New `estimate` command to check download size before committing to large downloads
- **Added**: Size estimation for full-resolution images and thumbnails
- **Added**: Detailed breakdown of file sizes by type (full-res, thumbnail, metadata)
- **Added**: Better error handling and reporting in size estimation
- **Updated**: Documentation to include size estimation workflow
- **Fixed**: Progress bar display for better visibility during batch operations
- **Improved**: Terminal output formatting with Rich library
