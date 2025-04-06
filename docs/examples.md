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

### Processing Metadata

To extract and analyze metadata from downloaded files:

```bash
phenofetch metadata --input-dir ./abby_data/meta --output-meta ./abby_analysis
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

### Exporting Metadata in Multiple Formats

Process metadata files and export in all available formats:

```bash
phenofetch metadata --input-dir ./phenocam_data/meta --format all --output-meta ./analysis/metadata
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

# 5. Process metadata from downloaded files
phenofetch metadata --input-dir ./harv_june_2023/meta --output-meta ./harv_metadata_june_2023
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

# Process metadata from all years
phenofetch metadata --input-dir ./konz_spring_2021/meta --output-meta ./konz_meta_2021
phenofetch metadata --input-dir ./konz_spring_2022/meta --output-meta ./konz_meta_2022
phenofetch metadata --input-dir ./konz_spring_2023/meta --output-meta ./konz_meta_2023

# For combined analysis, you can merge the CSV files in your analysis script
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

    # Process metadata for each site
    phenofetch metadata --input-dir "./data_${SITE}/meta" --output-meta "./metadata_${SITE}"
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

## Metadata Processing Examples

### Processing Metadata for Camera Temperature Analysis

Extract metadata for analyzing temperature patterns:

```bash
# Extract metadata to CSV format
phenofetch metadata --input-dir ./phenocam_data/meta --output-meta ./temperature_analysis

# Example Python script for temperature analysis (separate file)
```

Sample Python script for temperature analysis (`analyze_temperature.py`):

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Load the metadata CSV
df = pd.read_csv('./temperature_analysis.csv')

# Convert date and time columns to datetime
df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])

# Convert camera_temperature to float
df['camera_temperature'] = pd.to_numeric(df['camera_temperature'], errors='coerce')

# Drop rows with missing temperature data
df = df.dropna(subset=['camera_temperature'])

# Sort by datetime
df = df.sort_values('datetime')

# Create a plot
plt.figure(figsize=(12, 6))
plt.plot(df['datetime'], df['camera_temperature'], 'o-', markersize=2)
plt.title('Camera Temperature Over Time')
plt.xlabel('Date and Time')
plt.ylabel('Temperature (°C)')

# Format x-axis as dates
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate()  # Rotate date labels

# Add grid for better readability
plt.grid(True, alpha=0.3)

# Save the plot
plt.tight_layout()
plt.savefig('camera_temperature_trend.png')
plt.close()

print(f"Analysis complete. Results saved to camera_temperature_trend.png")
```

### Exporting Metadata for External Analysis

Export metadata for use in external tools like R or Excel:

```bash
# Export as CSV for Excel
phenofetch metadata --input-dir ./phenocam_data/meta --format csv --output-meta ./excel_analysis

# Export as JSON for web applications
phenofetch metadata --input-dir ./phenocam_data/meta --format json --output-meta ./web_analysis

# Export as Parquet for efficient processing in R or Python
phenofetch metadata --input-dir ./phenocam_data/meta --format parquet --output-meta ./big_data_analysis
```

## Integration Examples

### Using with Data Analysis Tools

This example shows a typical workflow integrating PhenoFetch with data analysis:

```bash
# Download data
phenofetch download --site HARV --product DP1.00033 --start-date 2023-06-01 --end-date 2023-06-30 --download --output-dir ./data

# Extract metadata
phenofetch metadata --input-dir ./data/meta --output-meta ./data/metadata_analysis

# Use Python for combined image and metadata analysis (separate script)
python analyze_phenocam.py --data-dir ./data --metadata ./data/metadata_analysis.csv
```

Sample Python script for combined analysis (`analyze_phenocam.py`):

```python
import argparse
import glob
import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


def analyze_phenocam_data(data_dir, metadata_file):
    # Find all full resolution images
    image_dir = os.path.join(data_dir, "full_res")
    image_files = sorted(glob.glob(os.path.join(image_dir, "*.jpg")))
    print(f"Found {len(image_files)} images to analyze")

    # Load metadata
    metadata_df = pd.read_csv(metadata_file)
    print(f"Loaded metadata with {len(metadata_df)} entries")

    # Create a dictionary for fast lookup of metadata by filename
    metadata_dict = {os.path.basename(row['filename']): row for _, row in metadata_df.iterrows()}

    # Extract greenness index from images and merge with metadata
    data_points = []

    for img_file in image_files:
        filename = os.path.basename(img_file)
        meta_filename = filename.replace('.jpg', '.meta')

        # Skip if we don't have matching metadata
        if meta_filename not in metadata_dict:
            continue

        # Get metadata for this image
        meta = metadata_dict[meta_filename]

        # Parse timestamp
        timestamp = datetime.strptime(f"{meta['date']} {meta['time']}", "%Y-%m-%d %H:%M:%S")

        # Open image and calculate greenness index
        img = Image.open(img_file)
        img_array = np.array(img)
        # Simple greenness index (G - R)
        r_channel = img_array[:, :, 0].mean()
        g_channel = img_array[:, :, 1].mean()
        greenness = g_channel - r_channel

        # Extract camera temperature if available
        camera_temp = meta.get('camera_temperature', None)

        # Store the data point
        data_points.append({
            'timestamp': timestamp,
            'greenness': greenness,
            'camera_temp': camera_temp,
            'filename': filename,
            'day_of_year': meta['doy'],
            'day_of_week': meta['day']
        })

    # Convert to DataFrame
    analysis_df = pd.DataFrame(data_points)

    # Sort by timestamp
    analysis_df = analysis_df.sort_values('timestamp')

    # Plot results using datetime on x-axis
    plt.figure(figsize=(12, 8))

    # Create two subplots
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(analysis_df['timestamp'], analysis_df['greenness'], 'o-', color='green')
    ax1.set_title("Greenness Index Over Time")
    ax1.set_ylabel("Greenness Index (G-R)")
    ax1.grid(True, alpha=0.3)

    # Add temperature subplot if available
    if 'camera_temp' in analysis_df and not analysis_df['camera_temp'].isna().all():
        ax2 = plt.subplot(2, 1, 2, sharex=ax1)
        ax2.plot(analysis_df['timestamp'], analysis_df['camera_temp'], 'o-', color='red')
        ax2.set_title("Camera Temperature")
        ax2.set_ylabel("Temperature (°C)")
        ax2.set_xlabel("Date Time (UTC)")
        ax2.grid(True, alpha=0.3)

    # Format x-axis to show dates nicely
    plt.gcf().autofmt_xdate()  # Rotate date labels

    # Save plot
    plt.tight_layout()
    output_file = os.path.join(data_dir, "combined_analysis.png")
    plt.savefig(output_file)
    plt.close()

    print(f"Analysis complete. Results saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze PhenoCam images with metadata")
    parser.add_argument("--data-dir", required=True, help="Directory containing PhenoCam data")
    parser.add_argument("--metadata", required=True, help="Path to metadata CSV file")
    args = parser.parse_args()
    analyze_phenocam_data(args.data_dir, args.metadata)
```

This is just one example of how you might analyze PhenoCam data and metadata after downloading it with PhenoFetch.
