#!/usr/bin/env python
"""
PhenoFetch - Command-line tool for downloading PhenoCam data

Copyright 2025 Samapriya Roy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import importlib.metadata
import os
import sys
from collections import defaultdict
from datetime import datetime
from importlib.metadata import version

import pkg_resources
import requests
from colorama import Fore, Style, init
from packaging import version as pkg_version
from rich.console import Console
from rich.table import Table

from .daily_links import (download_links, download_phenocam_files,
                          fetch_download, get_site_data)
from .site_info import site_all
# Import site_stats functionality
from .site_stats import site_aggregate_stats
# Import size_estimate functionality
from .size_estimate import fetch_size_estimate


def compare_version(version1, version2):
    """
    Compare two version strings using the packaging.version module.
    Returns: 1 if version1 > version2, -1 if version1 < version2, 0 if equal
    """
    v1 = pkg_version.parse(version1)
    v2 = pkg_version.parse(version2)

    if v1 > v2:
        return 1
    elif v1 < v2:
        return -1
    else:
        return 0


def get_latest_version(package):
    """Get the latest version of a package from PyPI."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=5)
        response.raise_for_status()
        return response.json()["info"]["version"]
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching version for {package}: {e}")
        return None


def get_installed_version(package):
    """Get the installed version of a package using importlib.metadata."""
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        try:
            # Fallback to pkg_resources
            return pkg_resources.get_distribution(package).version
        except pkg_resources.DistributionNotFound:
            print(f"Package {package} is not installed")
            return None


def check_package_version(package_name):
    """Check if the installed version of a package is the latest."""
    installed_version = get_installed_version(package_name)
    latest_version = get_latest_version(package_name)

    if not installed_version or not latest_version:
        return

    result = compare_version(latest_version, installed_version)
    border = (
        Style.BRIGHT
        + "========================================================================="
    )

    if result == 1:
        print(f"\n{border}")
        print(
            Fore.RED + f"Current version of {package_name} is {installed_version} "
            f"upgrade to latest version: {latest_version}" + Style.RESET_ALL
        )
        print(f"{border}")
    elif result == -1:
        print(f"\n{border}")
        print(
            Fore.YELLOW + f"Possibly running staging code {installed_version} "
            f"compared to PyPI release {latest_version}" + Style.RESET_ALL
        )
        print(f"{border}")


check_package_version("phenofetch")


def valid_date(date_string):
    """Validate and convert date string to YYYY-MM-DD format."""
    try:
        # Parse the input date
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
        # Return the formatted date string
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: '{date_string}'. Please use YYYY-MM-DD format."
        )


def valid_output_dir(dir_path):
    """Validate if the output directory exists or can be created."""
    if os.path.isdir(dir_path):
        return dir_path
    elif not os.path.exists(dir_path):
        try:
            # Try to create the directory if it doesn't exist
            os.makedirs(dir_path, exist_ok=True)
            return dir_path
        except Exception as e:
            raise argparse.ArgumentTypeError(
                f"Cannot create directory '{dir_path}': {str(e)}"
            )
    else:
        raise argparse.ArgumentTypeError(f"'{dir_path}' exists but is not a directory")


def print_available_sites():
    """Print a table of all available sites."""
    console = Console()
    sites_data = site_all()["data"]["sites"]

    # Create rich table
    table = Table(title="Available PhenoCam Sites")
    table.add_column("Site Code", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Domain", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("Type", style="blue")

    # Group by domain for better organization
    sites_by_domain = defaultdict(list)
    for site in sites_data:
        sites_by_domain[site["domainCode"]].append(site)

    # Add rows to table, sorted by domain code
    for domain in sorted(sites_by_domain.keys()):
        domain_sites = sites_by_domain[domain]
        # Sort sites within each domain by site code
        for site in sorted(domain_sites, key=lambda x: x["siteCode"]):
            table.add_row(
                site["siteCode"],
                site["siteDescription"],
                site["domainCode"],
                site["stateCode"],
                site["siteType"],
            )

    # Print the table
    console.print(table)
    console.print(
        "\nUse the site code (e.g., ABBY) when specifying the --site parameter."
    )


def main():
    """Main function to parse arguments and execute PhenoCam data retrieval."""
    parser = argparse.ArgumentParser(
        description="Download PhenoCam data for NEON sites",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    sites_parser = subparsers.add_parser(
        "sites", help="List all available PhenoCam sites"
    )

    stats_parser = subparsers.add_parser(
        "stats", help="Display statistics for a PhenoCam site"
    )

    estimate_parser = subparsers.add_parser(
        "estimate", help="Estimate download size for a date range"
    )

    download_parser = subparsers.add_parser(
        "download", help="Download data from PhenoCam"
    )

    required_stats = stats_parser.add_argument_group("Required arguments")
    required_stats.add_argument(
        "--site",
        required=True,
        help="NEON site code (e.g., ABBY, BART)",
    )
    required_stats.add_argument(
        "--product",
        required=True,
        help="NEON product ID (e.g., DP1.00033)",
    )

    required_estimate = estimate_parser.add_argument_group("Required arguments")
    required_estimate.add_argument(
        "--site",
        required=True,
        help="NEON site code (e.g., ABBY, BART)",
    )
    required_estimate.add_argument(
        "--product",
        required=True,
        help="NEON product ID (e.g., DP1.00033)",
    )
    required_estimate.add_argument(
        "--start-date",
        required=True,
        type=valid_date,
        help="Start date in YYYY-MM-DD format",
    )
    required_estimate.add_argument(
        "--end-date",
        required=True,
        type=valid_date,
        help="End date in YYYY-MM-DD format",
    )

    optional_estimate = estimate_parser.add_argument_group("Optional arguments")
    optional_estimate.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of files to process in each batch (default: 50)",
    )
    optional_estimate.add_argument(
        "--concurrency",
        type=int,
        help="Maximum number of concurrent connections (default: auto-determined)",
    )
    optional_estimate.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Connection timeout in seconds (default: 30)",
    )

    required_download = download_parser.add_argument_group("Required arguments")
    required_download.add_argument(
        "--site",
        required=True,
        help="NEON site code (e.g., ABBY, BART)",
    )
    required_download.add_argument(
        "--product",
        required=True,
        help="NEON product ID (e.g., DP1.00033)",
    )
    required_download.add_argument(
        "--start-date",
        required=True,
        type=valid_date,
        help="Start date in YYYY-MM-DD format",
    )
    required_download.add_argument(
        "--end-date",
        required=True,
        type=valid_date,
        help="End date in YYYY-MM-DD format",
    )

    optional_download = download_parser.add_argument_group("Optional arguments")
    optional_download.add_argument(
        "--download",
        action="store_true",
        help="Download files (default: just list summary)",
    )
    optional_download.add_argument(
        "--output-dir",
        type=valid_output_dir,
        default=os.path.join(os.getcwd(), "phenocam_data"),
        help="Directory to save downloaded files (default: ./phenocam_data)",
    )
    optional_download.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of files to download in each batch (default: 50)",
    )
    optional_download.add_argument(
        "--concurrency",
        type=int,
        help="Maximum number of concurrent downloads (default: auto-determined)",
    )
    optional_download.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Connection timeout in seconds (default: 30)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "sites":
        print("\nListing all available PhenoCam sites:")
        print_available_sites()
        return 0

    if args.command == "stats":
        site_data = get_site_data(args.site)
        if site_data is None:
            print(
                f"\nError: Site code '{args.site}' not found in available sites. Please choose from the following:"
            )
            print_available_sites()
            return 1

        print(f"\nFetching statistics for site {args.site} (product {args.product})...")
        site_aggregate_stats(args.site, args.product)
        return 0

    elif args.command == "estimate":
        # Validate date range
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        if start_date > end_date:
            parser.error("Start date must be before or equal to end date")

        # Validate site code before proceeding
        site_data = get_site_data(args.site)
        if site_data is None:
            print(
                f"\nError: Site code '{args.site}' not found in available sites. Please choose from the following:"
            )
            print_available_sites()
            return 1
        try:
            # Run the size estimation
            fetch_size_estimate(
                site_code=args.site,
                product_id=args.product,
                start_date=args.start_date,
                end_date=args.end_date,
                batch_size=args.batch_size,
                concurrency=args.concurrency,
                timeout=args.timeout,
            )
            return 0
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 130
        except Exception as e:
            print(f"\nError: {str(e)}")
            return 1

    # Handle the 'download' command (original functionality)
    elif args.command == "download":
        # Validate date range
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        if start_date > end_date:
            parser.error("Start date must be before or equal to end date")

        # Validate site code before proceeding
        site_data = get_site_data(args.site)
        if site_data is None:
            print(
                f"\nError: Site code '{args.site}' not found in available sites. Please choose from the following:"
            )
            print_available_sites()
            return 1

        # Print configuration summary
        print(f"\nPhenoFetch Configuration:")
        print(f"  Site code: {args.site}")
        print(f"  Product ID: {args.product}")
        print(f"  Date range: {args.start_date} to {args.end_date}")
        print(f"  Download files: {'Yes' if args.download else 'No (summary only)'}")
        if args.download:
            print(f"  Output directory: {args.output_dir}")
            print(f"  Batch size: {args.batch_size}")
            print(
                f"  Concurrency: {'Auto' if args.concurrency is None else args.concurrency}"
            )
            print(f"  Timeout: {args.timeout} seconds")

        try:
            site_code, domain_code = site_data
            neon_site_identifier = f"NEON.{domain_code}.{args.site}.{args.product}"

            if args.download:
                try:
                    import colorama

                    colorama.init()
                except ImportError:
                    print(
                        "Note: For better progress bar display, consider installing colorama: pip install colorama"
                    )

                os.environ["TQDM_NCOLS"] = "100"

                print(
                    f"\nFetching links for {site_code} from {args.start_date} to {args.end_date}..."
                )

                links = download_links(
                    neon_site_identifier=neon_site_identifier,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    summary=True,  # Show summary
                    file_types="all",
                )

                if links and len(links) > 0:
                    print(f"\nStarting download of {len(links)} files...")
                    try:
                        result = download_phenocam_files(
                            file_urls=links,
                            output_dir=args.output_dir,
                            batch_size=args.batch_size,
                            concurrency=args.concurrency,
                            timeout=args.timeout,
                        )

                        # Print final summary with clean formatting
                        if result:
                            print("\nDownload Complete!")
                            print(f"Total files processed: {result.get('total', 0)}")
                            print(
                                f"Successfully downloaded: {result.get('successful', 0)}"
                            )
                            print(
                                f"Already existed: {result.get('already_existed', 0)}"
                            )
                            print(f"Failed: {result.get('failed', 0)}")
                    except Exception as e:
                        print(f"\nError during download: {str(e)}")
                else:
                    print("\nNo files found to download.")
            else:
                # Just get the summary
                download_links(
                    neon_site_identifier=neon_site_identifier,
                    start_date=args.start_date,
                    end_date=args.end_date,
                    summary=True,
                    file_types="all",
                )

            return 0
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 130
        except TypeError as e:
            if "object of type 'NoneType' has no len()" in str(e):
                print(
                    "\nError: No files found to download, or there was an issue retrieving the file list."
                )
                return 1
            elif "cannot unpack non-iterable NoneType object" in str(e):
                print(
                    f"\nError: Site code '{args.site}' not found in available sites. Please check the site code and try again."
                )
                return 1
            else:
                print(f"\nType Error: {str(e)}")
                return 1
        except Exception as e:
            print(f"\nError: {str(e)}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
