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

import asyncio
import logging
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp
import psutil
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from .site_info import site_all

# Create a Rich console
console = Console()

# Add these lines for better progress bar display
try:
    import colorama

    colorama.init()
except ImportError:
    pass

# Set fixed width for progress bars and disable leave to ensure clean output
os.environ["TQDM_NCOLS"] = "100"

# Configure tqdm to clear progress bars properly
tqdm.monitor_interval = 0
# Get the terminal width
terminal_width = shutil.get_terminal_size().columns
# Configure logging with a cleaner format (removed module name)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Helper function to format file sizes
def format_size(size_bytes):
    """
    Format size in bytes to a human-readable format
    """
    if size_bytes is None:
        return "Unknown"

    # Define size units
    units = ["B", "KB", "MB", "GB", "TB"]

    # Choose appropriate unit
    unit_index = 0
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1

    # Format with 2 decimal places if not bytes
    if unit_index == 0:
        return f"{int(size_bytes)} {units[unit_index]}"
    else:
        return f"{size_bytes:.2f} {units[unit_index]}"


def get_site_data(site_code):
    """
    Retrieve and process data for a specific site code.
    Returns site information or None if site not found.
    """
    sites_data = site_all()["data"]["sites"]

    # Find the matching site (if any)
    matching_site = next(
        (site for site in sites_data if site["siteCode"] == site_code), None
    )

    if not matching_site:
        logger.warning(f"Site code {site_code} not found in available sites")
        return None

    logger.info(f"Site Found {site_code}: {matching_site['siteDescription']}")
    return site_code, matching_site["domainCode"]


def convert_phenocam_daily_to_json(html_content):
    """
    Convert a PhenoCam daily page HTML to structured JSON

    Args:
        html_content: HTML content of the daily page

    Returns:
        Dictionary containing the structured data
    """
    # Parse the HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract site information
    site_info = soup.find("div", {"id": "browse_siteinfo"})
    if not site_info:
        return None  # Page might not have data or have a different structure

    site_name = site_info.find("a").text.strip() if site_info.find("a") else "Unknown"

    # Extract date information
    date_info = site_info.find_all("a")
    year = date_info[1].text.strip() if len(date_info) > 1 else ""
    month = date_info[2].text.strip() if len(date_info) > 2 else ""

    # Extract day from the text - it's between month and next day link
    day_text = site_info.get_text()
    day_match = re.search(r"\/(\d+)\s+<", day_text)
    if not day_match:
        day_match = re.search(r"\/(\d+)\s*$", day_text)

    day = day_match.group(1).strip() if day_match else None

    # Extract day of year
    doy_text = site_info.find(string=re.compile("Day-of-Year:"))
    doy = doy_text.split(":")[1].strip() if doy_text else None

    # Extract number of images
    img_count_text = site_info.find(string=re.compile("Number of Images:"))
    img_count = img_count_text.split(":")[1].strip() if img_count_text else "0"

    # Create structured data dictionary with proper error handling
    phenocam_data = {
        "site_name": site_name,
        "date": {
            "year": int(year) if year and year.strip() else None,
            "month": int(month) if month and month.strip() else None,
            "day": int(day) if day and day.strip() else None,
            "day_of_year": int(doy) if doy and doy.strip() else None,
        },
        "total_images": int(img_count) if img_count and img_count.strip() else 0,
        "images": [],
    }

    # Extract image information
    image_divs = soup.find_all("div", class_="col-6 col-sm-4 col-md-3 col-lg-2 px-1")

    for img_div in image_divs:
        # Get image link and thumbnail
        img_link = img_div.find("a")["href"] if img_div.find("a") else None
        thumbnail = img_div.find("img")["src"] if img_div.find("img") else None

        # Extract time information
        time_text = img_div.find("span", class_="imglabel")
        if time_text and time_text.find("small"):
            time_str = time_text.find("small").get_text().strip()
            # Extract time from format like "07:00:06 UTC-8"
            time_match = re.search(r"(\d+:\d+:\d+)\s+(.+)", time_str)
            if time_match:
                time = time_match.group(1)
                timezone = time_match.group(2)
            else:
                time = time_str
                timezone = None
        else:
            time = None
            timezone = None

        # Extract metadata link
        metadata_link = None
        metadata_a = img_div.find("a", href=re.compile(r"\.meta$"))
        if metadata_a:
            metadata_link = metadata_a["href"]

        # Create image info dict
        image_info = {
            "time": time,
            "timezone": timezone,
            "image_url": f"https://phenocam.nau.edu/{img_link}" if img_link else None,
            "thumbnail_url": f"https://phenocam.nau.edu/{thumbnail}"
            if thumbnail
            else None,
            "metadata_url": f"https://phenocam.nau.edu/{metadata_link}"
            if metadata_link
            else None,
        }

        # Add to images list
        phenocam_data["images"].append(image_info)

    return phenocam_data


def get_date_range(start_date_str, end_date_str):
    """
    Generate a list of dates between start_date and end_date, inclusive.

    Args:
        start_date_str: Start date in format 'YYYY-MM-DD'
        end_date_str: End date in format 'YYYY-MM-DD'

    Returns:
        List of date strings in format 'YYYY/MM/DD'
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    date_list = []
    current_date = start_date

    while current_date <= end_date:
        # Format date as 'YYYY/MM/DD' for URL
        date_str = current_date.strftime("%Y/%m/%d")
        date_list.append(date_str)
        current_date += timedelta(days=1)

    return date_list


def fetch_phenocam_data_for_date_range(site_id, start_date, end_date, file_types=None):
    """
    Fetch PhenoCam data for a range of dates.

    Args:
        site_id: PhenoCam site ID
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        file_types: List of file types to include ('image', 'thumbnail', 'meta')
                   If None, include all file types

    Returns:
        Dictionary with date-specific data and summary statistics
    """
    if file_types is None:
        file_types = ["image", "thumbnail", "meta"]

    # Validate file_types
    valid_types = ["image", "thumbnail", "meta"]
    for file_type in file_types:
        if file_type not in valid_types:
            raise ValueError(
                f"Invalid file type: {file_type}. Valid types are: {valid_types}"
            )

    # Get list of dates to fetch
    date_list = get_date_range(start_date, end_date)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    results = {
        "site_id": site_id,
        "date_range": {"start": start_date, "end": end_date},
        "file_types": file_types,
        "data_by_date": {},
        "summary": {
            "total_days": len(date_list),
            "days_with_data": 0,
            "total_images": 0,
            "total_thumbnails": 0,
            "total_metadata_files": 0,
            "file_urls": [],
        },
    }

    # Use tqdm to create a progress bar
    for date_str in tqdm(
        date_list, desc=f"Fetching data for {site_id}", unit="day", leave=True
    ):
        # Extract year, month, day components
        year, month, day = date_str.split("/")

        # Format URL
        url = f"https://phenocam.nau.edu/webcam/browse/{site_id}/{year}/{month}/{day}/"

        try:
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                # Log error with appropriate level
                logger.debug(f"HTTP {response.status_code} for URL: {url}")
                results["data_by_date"][date_str] = {
                    "error": f"HTTP {response.status_code}"
                }
                continue

            # Parse HTML and convert to JSON
            phenocam_data = convert_phenocam_daily_to_json(response.text)

            if not phenocam_data or not phenocam_data.get("images"):
                # Log error with appropriate level
                logger.debug(f"No data found for date: {date_str}")
                results["data_by_date"][date_str] = {"error": "No data found"}
                continue

            # Filter images based on requested file types
            filtered_images = []
            for img in phenocam_data["images"]:
                filtered_img = {"time": img["time"], "timezone": img["timezone"]}

                if "image" in file_types and img.get("image_url"):
                    filtered_img["image_url"] = img["image_url"]
                    results["summary"]["file_urls"].append(img["image_url"])
                    results["summary"]["total_images"] += 1

                if "thumbnail" in file_types and img.get("thumbnail_url"):
                    filtered_img["thumbnail_url"] = img["thumbnail_url"]
                    results["summary"]["file_urls"].append(img["thumbnail_url"])
                    results["summary"]["total_thumbnails"] += 1

                if "meta" in file_types and img.get("metadata_url"):
                    filtered_img["metadata_url"] = img["metadata_url"]
                    results["summary"]["file_urls"].append(img["metadata_url"])
                    results["summary"]["total_metadata_files"] += 1

                filtered_images.append(filtered_img)

            phenocam_data["images"] = filtered_images
            results["data_by_date"][date_str] = phenocam_data
            results["summary"]["days_with_data"] += 1

        except Exception as e:
            # Log error with appropriate level
            logger.error(f"Error processing date {date_str}: {str(e)}")
            results["data_by_date"][date_str] = {"error": str(e)}

    return results


def get_links(
    neon_site_identifier,
    start_date,
    end_date,
    summary,
    file_types="all",
):
    if file_types == "all":
        file_types = ["image", "thumbnail", "meta"]
    else:
        base_file_types = ["image", "thumbnail", "meta"]
        if file_types in base_file_types:
            file_types = [file_types]
        else:
            logger.error(f"File must be of type {base_file_types} or all")
            import sys

            sys.exit(f"File must be of type {base_file_types} or all")

    logger.info(
        f"Fetching data for {neon_site_identifier} from {start_date} to {end_date}..."
    )
    results = fetch_phenocam_data_for_date_range(
        neon_site_identifier, start_date, end_date, file_types
    )

    if summary is True:
        # Create a rich table for the summary
        table = Table(title="Data Summary", show_header=True, header_style="bold cyan")

        # Add columns
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right")

        # Add rows with data
        table.add_row("Total days", str(results["summary"]["total_days"]))
        table.add_row("Days with data", str(results["summary"]["days_with_data"]))
        table.add_row("Total images", str(results["summary"]["total_images"]))
        table.add_row("Total thumbnails", str(results["summary"]["total_thumbnails"]))
        table.add_row(
            "Total metadata files", str(results["summary"]["total_metadata_files"])
        )
        table.add_row("Total files", str(len(results["summary"]["file_urls"])))

        # Print the table
        console.print("\n")
        console.print(table)

    return results["summary"]["file_urls"]


async def get_file_size(session, url, semaphore):
    """Get file size using HEAD request asynchronously."""
    try:
        # Determine file type first (in case the request fails)
        file_type = "unknown"
        if "/thumbnails/" in url:
            file_type = "thumbnail"
        elif "/archive/" in url and url.endswith(".jpg"):
            file_type = "full_res"
        elif "/archive/" in url and url.endswith(".meta"):
            file_type = "meta"
            # Skip metadata files - they typically don't have Content-Length
            return {
                "success": True,
                "url": url,
                "size": 0,  # Use 0 as placeholder
                "formatted_size": "N/A for metadata",
                "file_type": file_type,
            }

        async with semaphore:
            async with session.head(url, allow_redirects=True) as response:
                if response.status == 200:
                    # Get content length from headers
                    content_length = response.headers.get("Content-Length")

                    # Convert to integer if available
                    if content_length:
                        content_length = int(content_length)

                    return {
                        "success": True,
                        "url": url,
                        "size": content_length,
                        "formatted_size": format_size(content_length),
                        "file_type": file_type,
                    }
                else:
                    return {
                        "success": False,
                        "url": url,
                        "error": f"HTTP {response.status}",
                        "file_type": file_type,
                        "size": None,
                    }
    except Exception as e:
        logger.debug(f"Error getting size for {url}: {str(e)}")
        return {
            "success": False,
            "url": url,
            "error": str(e),
            "file_type": file_type,
            "size": None,
        }


async def process_batch(session, urls, semaphore, progress_bar=None):
    """Process a batch of file URLs to get size information."""
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_file_size(session, url, semaphore))
        tasks.append(task)

    if progress_bar:
        results = await tqdm_asyncio.gather(
            *tasks, desc="Checking file sizes", leave=False, position=1
        )
    else:
        results = await asyncio.gather(*tasks)

    return results


def determine_optimal_concurrency():
    """Determine the optimal number of concurrent connections based on system resources."""
    try:
        cpu_count = os.cpu_count() or 4
        mem_gb = psutil.virtual_memory().total / (1024 * 1024 * 1024)  # Convert to GB

        # Base concurrency on available resources
        # Use fewer connections on systems with less RAM
        if mem_gb < 4:
            concurrency = max(2, cpu_count // 2)
        elif mem_gb < 8:
            concurrency = max(4, cpu_count)
        else:
            concurrency = max(8, cpu_count * 2)

        # Cap at reasonable limits to prevent overloading
        return min(32, concurrency)
    except:
        # Fallback to a reasonable default if unable to determine
        return 8


async def async_estimate_sizes(file_urls, batch_size=50, concurrency=None, timeout=30):
    """
    Estimate file sizes asynchronously in batches.

    Args:
        file_urls: List of URLs to check
        batch_size: Number of files to process in each batch
        concurrency: Maximum number of concurrent requests (auto-determined if None)
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with file size statistics
    """
    # Determine optimal concurrency if not specified
    if concurrency is None:
        concurrency = determine_optimal_concurrency()

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(concurrency)

    # Split URLs into batches
    batches = [
        file_urls[i : i + batch_size] for i in range(0, len(file_urls), batch_size)
    ]

    # Track statistics
    stats = {
        "total": {"count": len(file_urls), "size": 0, "formatted_size": "0 B"},
        "full_res": {"count": 0, "size": 0, "formatted_size": "0 B"},
        "thumbnail": {"count": 0, "size": 0, "formatted_size": "0 B"},
        "meta": {"count": 0, "size": 0, "formatted_size": "0 B"},
        "successful": 0,
        "failed": 0,
        "errors": [],
        "files": [],
    }

    # Set up HTTP session with timeout
    timeout_obj = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        # Create master progress bar
        with tqdm(
            total=len(file_urls), desc="Overall progress", leave=True
        ) as master_pbar:
            # Process each batch
            for i, batch in enumerate(batches):
                logger.info(
                    f"Processing batch {i+1}/{len(batches)} ({len(batch)} files)"
                )

                # Process batch
                results = await process_batch(session, batch, semaphore)

                # Update statistics
                for result in results:
                    # Store the full result for detailed reporting
                    stats["files"].append(result)

                    if result["success"] and result["size"] is not None:
                        stats["successful"] += 1

                        # Update total size
                        stats["total"]["size"] += result["size"]

                        # Update by file type
                        file_type = result["file_type"]
                        if file_type in ["full_res", "thumbnail", "meta"]:
                            stats[file_type]["count"] += 1
                            stats[file_type]["size"] += result["size"]
                    else:
                        stats["failed"] += 1
                        stats["errors"].append(result)

                # Update master progress bar
                master_pbar.update(len(batch))

                # Log batch summary on the same line as the progress bar
                print(
                    f"\rBatch {i+1}/{len(batches)} complete: {len([r for r in results if r['success']])} successful, "
                    f"{len([r for r in results if not r['success']])} failed",
                    end="\n",
                )

                # Brief pause between batches to prevent overwhelming the server
                if i < len(batches) - 1:
                    await asyncio.sleep(1)

    # Format all sizes
    stats["total"]["formatted_size"] = format_size(stats["total"]["size"])
    stats["full_res"]["formatted_size"] = format_size(stats["full_res"]["size"])
    stats["thumbnail"]["formatted_size"] = format_size(stats["thumbnail"]["size"])
    stats["meta"]["formatted_size"] = format_size(stats["meta"]["size"])

    return stats


def estimate_phenocam_sizes(file_urls, batch_size=50, concurrency=None, timeout=30):
    """
    Estimate sizes of PhenoCam files.

    Args:
        file_urls: List of URLs to check
        batch_size: Number of files to process in each batch
        concurrency: Maximum number of concurrent requests (auto-determined if None)
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with file size statistics
    """
    # Log summary of task
    logger.info(f"Preparing to estimate sizes for {len(file_urls)} files")
    logger.info(f"Files will be processed in batches of {batch_size}")

    # Run the async function
    try:
        stats = asyncio.run(
            async_estimate_sizes(
                file_urls=file_urls,
                batch_size=batch_size,
                concurrency=concurrency,
                timeout=timeout,
            )
        )

        # Create a rich table for the size estimate summary
        print("#" * terminal_width)
        table = Table(
            title="Size Estimate Summary", show_header=True, header_style="bold green"
        )

        # Add columns
        table.add_column("Category", style="dim")
        table.add_column("Count", justify="right")
        table.add_column("Size", justify="right")

        # Add rows with data
        table.add_row(
            "Full resolution images",
            str(stats["full_res"]["count"]),
            stats["full_res"]["formatted_size"],
        )
        table.add_row(
            "Thumbnails",
            str(stats["thumbnail"]["count"]),
            stats["thumbnail"]["formatted_size"],
        )

        # Special handling for metadata files
        if stats["meta"]["count"] > 0:
            table.add_row(
                "Metadata files",
                str(stats["meta"]["count"]),
                "size estimate not available",
            )
        else:
            table.add_row("Metadata files", "0", "0 B")

        # Calculate total excluding metadata since we can't estimate their size
        if stats["meta"]["count"] > 0:
            total_size_no_meta = stats["full_res"]["size"] + stats["thumbnail"]["size"]
            table.add_row(
                "TOTAL (excluding metadata)",
                str(stats["total"]["count"] - stats["meta"]["count"]),
                format_size(total_size_no_meta),
            )
        else:
            table.add_row(
                "TOTAL", str(stats["total"]["count"]), stats["total"]["formatted_size"]
            )

        # Add summary rows
        table.add_row("Successfully checked", str(stats["successful"]), "", style="dim")
        table.add_row("Failed", str(stats["failed"]), "", style="dim")

        # Print the table
        console.print("\n")
        console.print(table)

        if stats["failed"] > 0:
            # Group errors by error type for better reporting
            error_types = {}
            for error in stats["errors"]:
                error_msg = error.get("error", "Unknown error")
                if error_msg not in error_types:
                    error_types[error_msg] = []
                error_types[error_msg].append(error["url"])

            # Create an error summary table
            error_table = Table(
                title="Error Summary", show_header=True, header_style="bold red"
            )
            error_table.add_column("Error Type")
            error_table.add_column("Count", justify="right")

            for error_type, urls in error_types.items():
                error_table.add_row(error_type, str(len(urls)))
                # Log example URLs for each error type
                if len(urls) > 0:
                    logger.debug(f"    Example: {urls[0]}")

            console.print(error_table)

        return stats

    except KeyboardInterrupt:
        logger.warning("Process interrupted by user.")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())  # Log full traceback for better debugging
        return None


def fetch_size_estimate(
    site_code,
    product_id,
    start_date,
    end_date,
    batch_size=50,
    concurrency=None,
    timeout=30,
):
    """
    Fetch and estimate sizes for PhenoCam files for a given site and date range.

    Args:
        site_code: PhenoCam site code
        product_id: Product ID (e.g., "DP1.00033")
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        batch_size: Number of files to process in each batch
        concurrency: Maximum number of concurrent requests (auto-determined if None)
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with file size statistics
    """
    site_data = get_site_data(site_code)
    if site_data is None:
        logger.error(f"Error: Site code '{site_code}' not found")
        return None

    site_code, domain_code = site_data

    # Get file links
    logger.info(f"Getting file links for {site_code}...")
    links = get_links(
        neon_site_identifier=f"NEON.{domain_code}.{site_code}.{product_id}",
        start_date=start_date,
        end_date=end_date,
        summary=True,
        file_types="all",
    )

    if not links:
        logger.warning(f"No files found for the specified date range")
        return None

    # Estimate sizes
    print("*" * terminal_width)
    logger.info(f"Estimating file sizes for {len(links)} files...")
    return estimate_phenocam_sizes(
        file_urls=links,
        batch_size=batch_size,
        concurrency=concurrency,
        timeout=timeout,
    )


# fetch_size_estimate(
#     site_code="ABBY",
#     product_id="DP1.00033",
#     start_date="2025-01-01",
#     end_date="2025-02-01",
#     batch_size=500,
# )
