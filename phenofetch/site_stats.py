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

import json
import logging
import re
from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

from .site_info import site_all

console = Console()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Referer": "https://phenocam.nau.edu/webcam/browse/NEON.D08.DELA.DP1.00033/2017/11/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

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


def html_to_json(html_content):
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract site information
    site_info = {}
    site_info_div = soup.find(id="browse_siteinfo")
    if site_info_div:
        # Extract site name
        site_name_header = site_info_div.find("h4")
        if site_name_header:
            site_name_link = site_name_header.find("a")
            if site_name_link:
                site_info["site_name"] = site_name_link.text.strip()
                site_info["site_url"] = site_name_link["href"]

    # Extract available years
    years_data = []
    year_sections = soup.find_all("div", {"class": "container-fluid"})

    for section in year_sections:
        year_header = section.find("span", {"class": "h4"})
        if not year_header:
            continue

        year_link = year_header.find("a", href=True)
        if not year_link:
            continue

        year_match = re.search(r"\d{4}", year_link.text)
        if not year_match:
            continue

        year = year_match.group(0)
        year_url = year_link["href"]

        # Extract months for this year
        months_data = []
        month_divs = section.find_all(
            "div", {"class": "col-6 col-sm-4 col-md-3 col-lg-2 px-1"}
        )

        for month_div in month_divs:
            month_link = month_div.find("a")
            if not month_link:
                continue

            month_img = month_div.find("img")
            month_label = month_div.find("span", {"class": "imglabel"})

            if month_label:
                # Extract month name and image count
                label_text = month_label.text.strip()
                month_match = re.search(
                    r"([A-Za-z]+)\s*\(\s*N\s*=\s*(\d+)\s*\)", label_text
                )

                if month_match:
                    month_name = month_match.group(1)
                    image_count = int(month_match.group(2))

                    # Get month URL and thumbnail
                    month_url = month_link["href"] if month_link else None
                    thumbnail_url = month_img["src"] if month_img else None

                    months_data.append(
                        {
                            "month_name": month_name,
                            "image_count": image_count,
                            "url": month_url,
                            "thumbnail": thumbnail_url,
                        }
                    )

        # Add year data with its months
        if months_data:
            years_data.append({"year": year, "url": year_url, "months": months_data})

    # Construct the final JSON structure
    result = {"site_info": site_info, "years": years_data}

    return result


# Example usage
def process_phenocam_data(html_content):
    json_data = html_to_json(html_content)
    return json_data


# For direct use with requests
def get_phenocam_data(site_id):
    url = f"https://phenocam.nau.edu/webcam/browse/{site_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return process_phenocam_data(response.text)
    except Exception as e:
        return {"error": str(e)}


def process_summary_data(data):
    """Extract a list of records from the nested JSON structure"""
    summary = []

    for year_data in data["years"]:
        year = year_data["year"]

        for month_data in year_data["months"]:
            summary.append(
                {
                    "Year": year,
                    "Month": month_data["month_name"],
                    "Image Count": month_data["image_count"],
                    "URL": month_data["url"],
                }
            )

    return summary


def display_summary_table(site_info, data):
    """Display a summary table of the data"""
    # Extract summary records from the nested data
    summary = process_summary_data(data)

    # Sort by year and month
    month_order = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    summary.sort(key=lambda x: (x["Year"], month_order[x["Month"]]), reverse=True)

    # Create table
    table = Table(title=f"Summary for {site_info}")
    table.add_column("Year", style="cyan")
    table.add_column("Month", style="magenta")
    table.add_column("Image Count", style="green", justify="right")
    table.add_column("URL", style="blue")

    # Add rows
    for item in summary:
        table.add_row(
            item["Year"], item["Month"], str(item["Image Count"]), item["URL"]
        )

    # Print table
    console.print(table)


def display_statistics(data):
    """Display statistics about the data"""
    # Extract summary records
    summary = process_summary_data(data)

    # Calculate statistics
    total_images = sum(item["Image Count"] for item in summary)
    year_totals = defaultdict(int)
    month_totals = defaultdict(int)
    month_counts = defaultdict(int)

    for item in summary:
        year_totals[item["Year"]] += item["Image Count"]
        month_totals[item["Month"]] += item["Image Count"]
        month_counts[item["Month"]] += 1

    # Create year totals table
    year_table = Table(title="Images by Year")
    year_table.add_column("Year", style="cyan")
    year_table.add_column("Image Count", style="green", justify="right")

    for year, count in sorted(year_totals.items(), reverse=True):
        year_table.add_row(year, str(count))

    # Create month averages table
    month_table = Table(title="Average Images by Month")
    month_table.add_column("Month", style="magenta")
    month_table.add_column("Average Images", style="green", justify="right")

    for month in [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]:
        if month in month_totals:
            avg = month_totals[month] / month_counts[month]
            month_table.add_row(month, f"{avg:.1f}")

    # Print statistics
    console.print(f"\nTotal Images: [bold green]{total_images}[/bold green]")
    console.print(year_table)
    # console.print(month_table)


def site_aggregate_stats(site_code, product_id):
    site_data = get_site_data(site_code)
    if site_data is None:
        return None

    site_code, domain_code = site_data
    site_info = f"NEON.{domain_code}.{site_code}.{product_id}"
    data = get_phenocam_data(site_info)
    display_summary_table(site_info, data)
    display_statistics(data)
