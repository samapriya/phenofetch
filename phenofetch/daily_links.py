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
from datetime import datetime, timedelta
from pathlib import Path

import aiofiles
import aiohttp
import psutil
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from .site_info import site_all

# Add these lines for better progress bar display
try:
    import colorama

    colorama.init()
except ImportError:
    pass

# Set fixed width for progress bars
os.environ["TQDM_NCOLS"] = "100"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
            "image_url": f"https://phenocam.nau.edu/{img_link}",
            "thumbnail_url": f"https://phenocam.nau.edu/{thumbnail}",
            "metadata_url": f"https://phenocam.nau.edu/{metadata_link}",
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
    for date_str in tqdm(date_list, desc=f"Fetching data for {site_id}", unit="day"):
        # Extract year, month, day components
        year, month, day = date_str.split("/")

        # Format URL
        url = f"https://phenocam.nau.edu/webcam/browse/{site_id}/{year}/{month}/{day}/"

        try:
            # Removed the print statement
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                # Log error but don't print directly
                results["data_by_date"][date_str] = {
                    "error": f"HTTP {response.status_code}"
                }
                continue

            # Parse HTML and convert to JSON
            phenocam_data = convert_phenocam_daily_to_json(response.text)

            if not phenocam_data or not phenocam_data.get("images"):
                # Log error but don't print directly
                results["data_by_date"][date_str] = {"error": "No data found"}
                continue

            # Filter images based on requested file types
            filtered_images = []
            for img in phenocam_data["images"]:
                filtered_img = {"time": img["time"], "timezone": img["timezone"]}

                if "image" in file_types and img["image_url"]:
                    filtered_img["image_url"] = img["image_url"]
                    results["summary"]["file_urls"].append(img["image_url"])
                    results["summary"]["total_images"] += 1

                if "thumbnail" in file_types and img["thumbnail_url"]:
                    filtered_img["thumbnail_url"] = img["thumbnail_url"]
                    results["summary"]["file_urls"].append(img["thumbnail_url"])
                    results["summary"]["total_thumbnails"] += 1

                if "meta" in file_types and img["metadata_url"]:
                    filtered_img["metadata_url"] = img["metadata_url"]
                    results["summary"]["file_urls"].append(img["metadata_url"])
                    results["summary"]["total_metadata_files"] += 1

                filtered_images.append(filtered_img)

            phenocam_data["images"] = filtered_images
            results["data_by_date"][date_str] = phenocam_data
            results["summary"]["days_with_data"] += 1

        except Exception as e:
            # Log error but don't print directly
            results["data_by_date"][date_str] = {"error": str(e)}

    return results


def download_links(
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
            import sys

            sys.exit(f"File must be of type {base_file_types} or all")

    print(
        f"\nFetching data for {neon_site_identifier} from {start_date} to {end_date}..."
    )
    results = fetch_phenocam_data_for_date_range(
        neon_site_identifier, start_date, end_date, file_types
    )

    if summary is True:
        print("\nSummary:")
        print(f"Total days: {results['summary']['total_days']}")
        print(f"Days with data: {results['summary']['days_with_data']}")
        print(f"Total images: {results['summary']['total_images']}")
        print(f"Total thumbnails: {results['summary']['total_thumbnails']}")
        print(f"Total metadata files: {results['summary']['total_metadata_files']}")
        print(f"Total files: {len(results['summary']['file_urls'])}")

    return results["summary"]["file_urls"]


# Example usage
"""
Example fetch links only
final_urls = download_links(
    site_code="NEON.D16.ABBY.DP1.00033",
    start_date="2020-01-01",
    end_date="2020-01-15",
    summary=False,
    file_types="all",
)
print(len(final_urls))
# print(final_urls)
"""


async def download_file(session, url, output_dir, semaphore):
    """Download a single file asynchronously and maintain original path structure."""
    try:
        # Parse URL to determine if it's a thumbnail or regular image
        if "/thumbnails/" in url:
            # For thumbnails, create a subdirectory to avoid filename conflicts
            subdir = os.path.join(output_dir, "thumbnails")
        elif "/archive/" in url and url.endswith(".jpg"):
            # For archive files, create a subdirectory
            subdir = os.path.join(output_dir, "full_res")
        elif "/archive/" in url and url.endswith(".meta"):
            # For other files
            subdir = os.path.join(output_dir, "meta")

        # Extract filename from URL
        filename = os.path.basename(url)

        # Create full path
        filepath = os.path.join(subdir, filename)

        # Skip if file already exists
        if os.path.exists(filepath):
            return {
                "success": True,
                "url": url,
                "file": filepath,
                "status": "already exists",
            }

        async with semaphore:
            async with session.get(url) as response:
                if response.status == 200:
                    # Create directory if it doesn't exist
                    os.makedirs(subdir, exist_ok=True)

                    # Save file
                    async with aiofiles.open(filepath, "wb") as f:
                        await f.write(await response.read())

                    return {
                        "success": True,
                        "url": url,
                        "file": filepath,
                        "status": "downloaded",
                    }
                else:
                    return {
                        "success": False,
                        "url": url,
                        "error": f"HTTP {response.status}",
                    }
    except Exception as e:
        return {"success": False, "url": url, "error": str(e)}


async def download_batch(session, urls, output_dir, semaphore, progress_bar=None):
    """Download a batch of files."""
    tasks = []
    for url in urls:
        task = asyncio.create_task(download_file(session, url, output_dir, semaphore))
        tasks.append(task)

    if progress_bar:
        results = await tqdm_asyncio.gather(
            *tasks, desc="Downloading files", leave=False
        )
    else:
        results = await asyncio.gather(*tasks)

    return results


def determine_optimal_concurrency():
    """Determine the optimal number of concurrent downloads based on system resources."""
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


async def async_download_files(
    file_urls, output_dir, batch_size=50, concurrency=None, timeout=30
):
    """
    Download files asynchronously in batches.

    Args:
        file_urls: List of URLs to download
        output_dir: Directory to save downloaded files
        batch_size: Number of files to process in each batch
        concurrency: Maximum number of concurrent downloads (auto-determined if None)
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with download statistics
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Determine optimal concurrency if not specified
    if concurrency is None:
        concurrency = determine_optimal_concurrency()

    # Create semaphore to limit concurrent downloads
    semaphore = asyncio.Semaphore(concurrency)

    # Split URLs into batches
    batches = [
        file_urls[i : i + batch_size] for i in range(0, len(file_urls), batch_size)
    ]

    # Track statistics
    stats = {
        "total": len(file_urls),
        "successful": 0,
        "failed": 0,
        "already_existed": 0,
        "errors": [],
    }

    # Set up HTTP session with timeout
    timeout_obj = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        # Create master progress bar
        with tqdm(total=len(file_urls), desc="Overall progress") as master_pbar:
            # Process each batch
            for i, batch in enumerate(batches):
                print(
                    f"\rProcessing batch {i+1}/{len(batches)} ({len(batch)} files)",
                    end="",
                )

                # Download batch
                results = await download_batch(session, batch, output_dir, semaphore)

                # Update statistics
                for result in results:
                    if result["success"]:
                        if result.get("status") == "already exists":
                            stats["already_existed"] += 1
                        else:
                            stats["successful"] += 1
                    else:
                        stats["failed"] += 1
                        stats["errors"].append(result)

                # Update master progress bar
                master_pbar.update(len(batch))

                # Print batch summary on same line
                print(
                    f"\rBatch {i+1}/{len(batches)} complete: {len([r for r in results if r['success']])} successful, "
                    f"{len([r for r in results if not r['success']])} failed",
                    end="",
                )

                # Brief pause between batches to prevent overwhelming the server
                if i < len(batches) - 1:
                    await asyncio.sleep(1)
                print()  # Add newline at the end of each batch

    return stats


def download_phenocam_files(
    file_urls, output_dir, batch_size=50, concurrency=None, timeout=30
):
    """
    Download PhenoCam files to the specified directory.

    Args:
        file_urls: List of URLs to download
        output_dir: Directory to save downloaded files
        batch_size: Number of files to process in each batch
        concurrency: Maximum number of concurrent downloads (auto-determined if None)
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with download statistics
    """
    # Ensure output directory is a Path object
    output_dir = Path(output_dir)

    # Print summary of download task
    print(f"Preparing to download {len(file_urls)} files to {output_dir.absolute()}")
    print(f"Files will be processed in batches of {batch_size}")

    # Run the async download function
    try:
        stats = asyncio.run(
            async_download_files(
                file_urls=file_urls,
                output_dir=str(output_dir),
                batch_size=batch_size,
                concurrency=concurrency,
                timeout=timeout,
            )
        )

        # Print summary of results
        print("\nDownload Summary:")
        print(f"Total files: {stats['total']}")
        print(f"Successfully downloaded: {stats['successful']}")
        print(f"Already existed: {stats['already_existed']}")
        print(f"Failed: {stats['failed']}")

        if stats["failed"] > 0:
            print("\nFirst few errors:")
            for error in stats["errors"][:5]:
                print(f"  • {error['url']}: {error['error']}")

            if len(stats["errors"]) > 5:
                print(f"  ... and {len(stats['errors']) - 5} more errors")

        return stats

    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
        return None
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        return None


def fetch_download(site_code, product_id, download, start_date, end_date, output_dir):
    site_data = get_site_data(site_code)
    if site_data is None:
        return None

    site_code, domain_code = site_data

    if download is True:
        links = download_links(
            neon_site_identifier=f"NEON.{domain_code}.{site_code}.{product_id}",
            start_date=start_date,
            end_date=end_date,
            summary=False,
            file_types="all",
        )

        return download_phenocam_files(
            file_urls=links,
            output_dir=output_dir,
            batch_size=50,
            concurrency=None,
            timeout=30,
        )
    else:
        links = download_links(
            neon_site_identifier=f"NEON.{domain_code}.{site_code}.{product_id}",
            start_date=start_date,
            end_date=end_date,
            summary=True,
            file_types="all",
        )
        return links


# if __name__ == "__main__":
#     # Example usage
#     fetch_download(
#         site_code="ABBY",
#         product_id="DP1.00033",
#         download=False,
#         start_date="2024-01-01",
#         end_date="2024-05-01",
#         output_dir=r"C:\Users\samapriya\Documents\ph\phenocam_data",
#     )
