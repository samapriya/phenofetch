import argparse
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd


def parse_filename(filename: str) -> Dict[str, str]:
    """
    Parse a NEON filename to extract components.

    Args:
        filename: Filename like "NEON.D16.ABBY.DP1.00033_2021_01_01_073006.meta"

    Returns:
        Dictionary with extracted components
    """
    result = {}

    # Basic pattern matching for NEON filenames
    pattern = r'(NEON)\.([^.]+)\.([^.]+)\.([^_]+)_(\d{4})_(\d{2})_(\d{2})_(\d{6}).*'
    match = re.match(pattern, filename)

    if match:
        provider, domain, site_code, product_code, year, month, day, time_str = match.groups()

        # Format the date components
        date_str = f"{year}-{month}-{day}"

        # Convert time from HHMMSS to HH:MM:SS
        hour = time_str[0:2]
        minute = time_str[2:4]
        second = time_str[4:6]
        formatted_time = f"{hour}:{minute}:{second}"

        # Create datetime object for further conversions
        dt = datetime.strptime(f"{date_str} {formatted_time}", "%Y-%m-%d %H:%M:%S")

        # Get day of week
        day_of_week = dt.strftime("%A")

        # Get day of year
        day_of_year = dt.strftime("%j")

        # Get epoch time (seconds since 1970-01-01 00:00:00 UTC)
        epoch_time = int(dt.timestamp())

        result = {
            'provider': provider,
            'domain': domain,
            'site_code': site_code,
            'product_code': product_code,
            'date': date_str,
            'time': formatted_time,
            'time_zone': 'UTC',
            'epoch_time': str(epoch_time),
            'doy': day_of_year,
            'day': day_of_week
        }

    return result


def parse_metadata_file(file_path: str) -> Dict[str, str]:
    """
    Parse a metadata file and extract only the specified fields.

    Args:
        file_path: Path to the metadata file

    Returns:
        Dictionary containing selected key-value pairs and filename components
    """
    metadata_dict = {}
    selected_fields = ['exposure_limit', 'ip_addr', 'mac_addr']

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and '=' in line:
                    # Split only on the first equals sign
                    key, value = line.split('=', 1)
                    if key in selected_fields:
                        metadata_dict[key] = value

                    # Extract Camera Temperature from overlay_text but don't keep the overlay_text
                    elif key == 'overlay_text' and 'Camera Temperature:' in value:
                        temp_match = re.search(r'Camera Temperature:\s*(\d+\.\d+)', value)
                        if temp_match:
                            metadata_dict['camera_temperature'] = temp_match.group(1)

        # Get filename and parse its components
        filename = os.path.basename(file_path)
        metadata_dict['filename'] = filename  # Renamed from _source_file to filename

        # Merge filename components into the metadata
        filename_components = parse_filename(filename)
        metadata_dict.update(filename_components)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return metadata_dict


def process_files(input_path: str, file_pattern: Optional[str] = None) -> pd.DataFrame:
    """
    Process a single file or a directory of files.

    Args:
        input_path: Path to a file or directory
        file_pattern: Optional pattern to filter files in a directory

    Returns:
        DataFrame containing metadata from all processed files
    """
    all_metadata = []
    file_count = 0

    # Check if input path is a file or directory
    if os.path.isfile(input_path):
        # Process a single file
        metadata = parse_metadata_file(input_path)
        all_metadata.append(metadata)
        file_count = 1
        print(f"Processed file: {input_path}")

    elif os.path.isdir(input_path):
        # Process a directory of files
        for file_name in os.listdir(input_path):
            file_path = os.path.join(input_path, file_name)

            # Skip directories
            if os.path.isdir(file_path):
                continue

            # Skip files that don't match the pattern if a pattern is provided
            if file_pattern and not file_name.endswith(file_pattern):
                continue

            # Parse the metadata file
            metadata = parse_metadata_file(file_path)

            all_metadata.append(metadata)
            file_count += 1

        print(f"Processed {file_count} files from {input_path}")

    else:
        print(f"Error: Input path '{input_path}' is not a valid file or directory.")

    # Convert to DataFrame
    if not all_metadata:
        return pd.DataFrame()

    return pd.DataFrame(all_metadata)


def determine_export_format(output_path: str) -> str:
    """
    Determine the export format based on the output path extension.

    Args:
        output_path: Path where the output file will be saved

    Returns:
        Format string ('csv', 'json', or 'parquet')
    """
    lower_path = output_path.lower()

    if lower_path.endswith('.csv'):
        return 'csv'
    elif lower_path.endswith('.json'):
        return 'json'
    elif lower_path.endswith('.parquet'):
        return 'parquet'
    else:
        # Default format if no extension is provided
        return 'csv'


def export_dataframe(df: pd.DataFrame, output_path: str, format: Optional[str] = None) -> None:
    """
    Export DataFrame to the specified format.

    Args:
        df: DataFrame to export
        output_path: Path where the output file will be saved
        format: Format to export (csv, json, or parquet). If None, determined from output_path.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    # Determine format from output path if not specified
    if format is None:
        format = determine_export_format(output_path)

    # Add extension if not present
    if not output_path.lower().endswith(f'.{format}'):
        output_path = f"{output_path}.{format}"

    if format.lower() == 'csv':
        df.to_csv(output_path, index=False)
        print(f"Exported CSV to {output_path}")
    elif format.lower() == 'json':
        # Convert DataFrame to records format for better JSON structure
        records = df.to_dict(orient='records')
        with open(output_path, 'w') as f:
            json.dump(records, f, indent=2)
        print(f"Exported JSON to {output_path}")
    elif format.lower() == 'parquet':
        df.to_parquet(output_path, index=False)
        print(f"Exported Parquet to {output_path}")
    else:
        print(f"Unsupported format: {format}")


def process_metadata(input_path, output_path=None, output_format=None, file_pattern='.meta'):
    """
    Process metadata files and export the results.
    This function is called from the CLI command.

    Args:
        input_path: Path to the input file or directory
        output_path: Path to the output file
        output_format: Output format (csv, json, parquet, or all)
        file_pattern: File pattern to match

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Process the input file or directory
    df = process_files(input_path, file_pattern)

    if df.empty:
        print("No data was processed. Check your input file or directory.")
        return 1

    # Handle output
    if output_path:
        if output_format == "all":
            # Export to all formats
            base_path = output_path.rsplit('.', 1)[0] if '.' in output_path else output_path
            export_dataframe(df, f"{base_path}.csv", "csv")
            export_dataframe(df, f"{base_path}.json", "json")
            export_dataframe(df, f"{base_path}.parquet", "parquet")
        else:
            # Export to specified format or determine from output path
            export_dataframe(df, output_path, output_format)
    else:
        # Default output if no path specified
        print("\nNo output path specified. Using default 'extracted_metadata.csv'")
        export_dataframe(df, "extracted_metadata.csv", "csv")

    return 0


# This is kept for backward compatibility when running the module directly
def main():
    parser = argparse.ArgumentParser(description="Extract specific metadata fields and filename components")
    parser.add_argument("input", help="Input file or directory containing metadata files")
    parser.add_argument("--output", "-o", help="Output file path (with or without extension)")
    parser.add_argument("--format", "-f", choices=["csv", "json", "parquet", "all"],
                        help="Output format (csv, json, parquet, or all). If not specified, derived from output path extension.")
    parser.add_argument("--pattern", "-p", help="File pattern to match when processing directories (e.g., '.meta')")

    args = parser.parse_args()

    # Process metadata files
    return process_metadata(
        input_path=args.input,
        output_path=args.output,
        output_format=args.format,
        file_pattern=args.pattern
    )


if __name__ == "__main__":
    main()
