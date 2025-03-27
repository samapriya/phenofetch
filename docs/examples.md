# Examples

This page provides practical examples of using PhenoFetch in various scenarios. These examples demonstrate common use cases and workflows to help you get the most out of the tool.

## Basic Examples

### Listing All Sites

To see all available PhenoCam sites:

```bash
phenofetch sites
```

### Viewing Site Statistics

To check data availability for the Harvard Forest site:

```bash
phenofetch stats --site HARV --product DP1.00033
```

### Estimating Download Size

To estimate the download size for a one-month period:

```bash
phenofetch estimate --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31
```

### Downloading Data

To download data for a specific site and date range:

```bash
phenofetch download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31 --download --output-dir ./abby_data
```

## Advanced Examples

### Finding Sites in a Specific State

Combine the `sites` command with grep to find sites in a specific state:

```bash
phenofetch sites | grep "CO"  # Find sites in Colorado
```

### Filtering for Specific Site Types

Find all core sites:

```bash
phenofetch sites | grep "CORE"
```

## Workflow Examples

### Complete Data Discovery and Download Workflow

This example shows a complete workflow from discovering sites to downloading data:

```bash
# 1. List all available sites
phenofetch sites

# 2. Check statistics for a site of interest
phenofetch stats --site HARV --product DP1.00033

# 3. Estimate download size for a specific period
phenofetch estimate --site HARV --product DP1.00033 --start-date 2023-06-01 --end-date 2023-06-30

# 4. Download the data
phenofetch download --site HARV --product DP1.00033 --start-date 2023-06-01 --end-date 2023-06-30 --download --output-dir ./harv_june_2023
```

### Seasonal Data Collection

This example shows how to download spring data from multiple years for phenological studies:

```bash
# Download spring data from 2021
phenofetch download --site KONZ --product DP1.00033 --start-date 2021-03-21 --end-date 2021-06-21 --download --output-dir ./konz_spring_2021

# Download spring data from 2022
phenofetch download --site KONZ --product DP1.00033 --start-date 2022-03-21 --end-date 2022-06-21 --download --output-dir ./konz_spring_2022

# Download spring data from 2023
phenofetch download --site KONZ --product DP1.00033 --start-date 2023-03-21 --end-date 2023-06-21 --download --output-dir ./konz_spring_2023
```

### Downloading Data for Multiple Sites

You can use a shell script to download data for multiple sites:

```bash
#!/bin/bash
# Download January 2023 data for three different sites

SITES=("HARV" "BART" "ABBY")
START_DATE="2023-01-01"
END_DATE="2023-01-31"
PRODUCT="DP1.00033"

for SITE in "${SITES[@]}"; do
    echo "Processing site: $SITE"
    phenofetch download --site $SITE --product $PRODUCT --start-date $START_DATE --end-date $END_DATE --download --output-dir "./data_${SITE}"
done
```

## Performance Optimization Examples

### Optimizing for Faster Downloads

For faster downloads on a powerful machine:

```bash
phenofetch download --site SOAP --product DP1.00033 --start-date 2023-01-01 --end-date 2023-01-31 --download --batch-size 100 --concurrency 16
```

### Optimizing for Limited Memory

For systems with limited memory:

```bash
phenofetch download --site SOAP --product DP1.00033 --start-date 2023-01-01 --end-date 2023-01-31 --download --batch-size 20 --concurrency 4
```

### Handling Slow Connections

For slower or less reliable internet connections:

```bash
phenofetch download --site SOAP --product DP1.00033 --start-date 2023-01-01 --end-date 2023-01-31 --download --timeout 60 --concurrency 2
```

## Integration Examples

### Using with Data Analysis Tools

This example shows a typical workflow integrating PhenoFetch with data analysis:

```bash
# Download data
phenofetch download --site HARV --product DP1.00033 --start-date 2023-06-01 --end-date 2023-06-30 --download --output-dir ./data

# Use Python for analysis (separate script)
python analyze_phenocam.py --data-dir ./data
```

Sample Python script for analysis (`analyze_phenocam.py`):

```python
import argparse
import glob
import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def analyze_phenocam_data(data_dir):
    # Find all full resolution images
    image_dir = os.path.join(data_dir, "full_res")
    image_files = sorted(glob.glob(os.path.join(image_dir, "*.jpg")))
    print(f"Found {len(image_files)} images to analyze")

    # Extract greenness index from images
    greenness_values = []
    timestamps = []

    for img_file in image_files:
        # Extract timestamp from filename
        filename = os.path.basename(img_file)
        # Parse the timestamp from NEON format
        # Example: NEON.D16.ABBY.DP1.00033_2024_01_01_080006
        parts = filename.split("_")
        if len(parts) >= 4:  # Make sure we have enough parts
            year = int(parts[-4])
            month = int(parts[-3])
            day = int(parts[-2])
            time_str = parts[-1].split(".")[0]  # Remove file extension if present

            # Parse time (HHMMSS format)
            hour = int(time_str[0:2])
            minute = int(time_str[2:4])
            second = int(time_str[4:6])

            # Create datetime object
            timestamp = datetime(year, month, day, hour, minute, second)
            timestamps.append(timestamp)

            # Open image and calculate greenness index
            img = Image.open(img_file)
            img_array = np.array(img)
            # Simple greenness index (G - R)
            r_channel = img_array[:, :, 0].mean()
            g_channel = img_array[:, :, 1].mean()
            greenness = g_channel - r_channel
            greenness_values.append(greenness)
        else:
            print(f"Skipping file with unexpected format: {filename}")

    # Make sure we have data to plot
    if not timestamps:
        print("No valid timestamps found. Check file naming pattern.")
        return

    # Create a list of (timestamp, greenness) tuples and sort by timestamp
    data_points = list(zip(timestamps, greenness_values))
    data_points.sort(key=lambda x: x[0])  # Sort by timestamp

    # Unzip the sorted data
    timestamps, greenness_values = zip(*data_points)

    # Plot results using datetime on x-axis
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, greenness_values, "o-")
    plt.title("Greenness Index Over Time")
    plt.xlabel("Date Time (UTC)")
    plt.ylabel("Greenness Index (G-R)")

    # Format x-axis to show dates nicely
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.gcf().autofmt_xdate()  # Rotate date labels

    # Add grid for better readability
    plt.grid(True, alpha=0.3)

    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(data_dir, "greenness_analysis_by_date.png"))
    plt.close()

    print(
        f"Analysis complete. Results saved to {os.path.join(data_dir, 'greenness_analysis_by_date.png')}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze PhenoCam images")
    parser.add_argument(
        "--data-dir", required=True, help="Directory containing PhenoCam data"
    )
    args = parser.parse_args()
    analyze_phenocam_data(args.data_dir)
```

This is just one example of how you might analyze PhenoCam data after downloading it with PhenoFetch.
