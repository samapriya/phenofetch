# Frequently Asked Questions

This page addresses common questions about PhenoFetch and its usage.

## General Questions

### What is PhenoFetch?

PhenoFetch is a command-line tool for downloading and analyzing PhenoCam data from NEON (National Ecological Observatory Network) sites. It simplifies the process of retrieving time-lapse images used for monitoring vegetation phenology.

### Is PhenoFetch affiliated with NEON or the PhenoCam Network?

No, PhenoFetch is not officially affiliated with the National Ecological Observatory Network (NEON) or the PhenoCam Network. It is an independent tool developed to facilitate access to publicly available PhenoCam data.

### What license is PhenoFetch released under?

PhenoFetch is released under the Apache License 2.0.

## Installation Questions

### What are the system requirements for PhenoFetch?

PhenoFetch requires:
- Python 3.9 or higher
- Internet connection to download data
- Sufficient disk space for downloaded images

### Why am I getting an error during installation?

Common installation issues include:
- Insufficient permissions (try using `pip install --user phenofetch`)
- Outdated pip (try `pip install --upgrade pip` first)
- Missing dependencies (ensure you have all required packages)

### Can I use PhenoFetch on Windows/Mac/Linux?

Yes, PhenoFetch is compatible with all major operating systems including Windows, macOS, and Linux.

## Usage Questions

### What is a NEON site code?

A NEON site code is a unique identifier for each site in the National Ecological Observatory Network. Examples include "HARV" for Harvard Forest, "ABBY" for Abby Road, etc. You can see all available site codes using the `phenofetch sites` command.

### What is a NEON product ID?

A NEON product ID identifies a specific data product. For PhenoCam images, the product ID is typically "DP1.00033".

### How much disk space will the downloaded data require?

The disk space required depends on the site and date range. Full-resolution images are typically 2-4 MB each, and there are usually 24-48 images per day. You can use the `estimate` command to calculate the expected download size before committing to a full download.

### Are the downloaded images georeferenced?

PhenoCam images are not georeferenced in the traditional GIS sense. However, each site has fixed latitude and longitude coordinates which are available in the site metadata.

## Data Questions

### What types of files does PhenoFetch download?

PhenoFetch can download three types of files:
- Full-resolution images (.jpg)
- Thumbnail images (.jpg)
- Metadata files (.meta)

### What information is contained in the metadata files?

Metadata files typically include:
- Camera information
- Capture time and conditions
- Site information
- Technical settings (exposure, white balance, etc.)

### How frequently are images captured at NEON PhenoCam sites?

Most NEON PhenoCam sites capture images every 30 minutes during daylight hours, but this can vary by site. Some sites may have more frequent or less frequent capture intervals.

### What file organization should I expect in the downloaded data?

Downloaded files are organized into three subdirectories:
- `full_res/`: Contains full-resolution images
- `thumbnails/`: Contains thumbnail images
- `meta/`: Contains metadata files

The original filenames are preserved.

## Performance Questions

### How can I speed up downloads?

To speed up downloads:
- Increase the batch size (`--batch-size` option)
- Increase concurrency if you have a fast connection (`--concurrency` option)
- Ensure you have a stable internet connection
- Download smaller date ranges at a time

### Why are my downloads slow or failing?

Possible reasons include:
- Slow or unstable internet connection
- Server-side limitations
- Too many concurrent connections
- High server load

Try reducing concurrency, using smaller batch sizes, or retrying during off-peak hours.

### How does PhenoFetch determine the optimal concurrency?

PhenoFetch automatically determines the optimal concurrency based on your system's CPU cores and available memory. This auto-tuning helps ensure efficient downloads without overwhelming your system or the server.

## Troubleshooting

### Error: "No data found for the specified date range"

This error occurs when there are no PhenoCam images available for the site and date range you specified. Use the `stats` command to see what data is available for your site of interest.

### Error: "Site code not found in available sites"

This error means you've specified an invalid site code. Use the `phenofetch sites` command to see a list of all valid site codes.

### Downloads start but then stall or time out

If downloads stall:
- Try increasing the timeout value (`--timeout` option)
- Reduce concurrency (`--concurrency` option)
- Try smaller batch sizes
- Check your internet connection
- Retry during off-peak hours

### Some files failed to download

Failed downloads are reported at the end of the process. Common causes include:
- Temporary server issues
- Network interruptions
- Files that exist on the server index but aren't actually available

You can retry the download for the same date range; PhenoFetch will skip files that were already successfully downloaded.
