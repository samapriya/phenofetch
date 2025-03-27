# Sites Command

The `sites` command lists all available NEON PhenoCam sites, providing a comprehensive overview of where data can be collected.

## Description

When executed, this command displays a table with information about all available PhenoCam sites in the NEON network, including site codes, descriptions, domain codes, state information, and site types. This is useful for discovering sites of interest for further investigation.

## Usage

```bash
phenofetch sites
```

No additional arguments are required for this command.

## Output

The command generates a formatted table with the following columns:

- **Site Code**: The unique identifier for the site (e.g., ABBY, BART)
- **Description**: A brief description of the site location
- **Domain**: The NEON domain code (e.g., D01, D02)
- **State**: The US state where the site is located
- **Type**: The site type (CORE or GRADIENT)

Example output:

```
┌────────┬───────────────────────┬────────┬───────┬──────────┐
│ Site   │ Description           │ Domain │ State │ Type     │
│ Code   │                       │        │       │          │
├────────┼───────────────────────┼────────┼───────┼──────────┤
│ ABBY   │ Abby Road NEON        │ D16    │ WA    │ GRADIENT │
│ ARIK   │ Arikaree River NEON   │ D10    │ CO    │ CORE     │
│ BARC   │ Lake Barco NEON       │ D03    │ FL    │ CORE     │
│ ...    │ ...                   │ ...    │ ...   │ ...      │
└────────┴───────────────────────┴────────┴───────┴──────────┘

```

Use the site code (e.g., ABBY) when specifying the --site parameter.


## Notes

- The sites are grouped and sorted by domain code for easier navigation.
- Use the site codes displayed in this table for other PhenoFetch commands that require a `--site` parameter.
- The table is color-coded for better readability thanks to the Rich library.
- The site list is pulled from a local database included with PhenoFetch and doesn't require internet access.

## Examples

Basic usage:

```bash
phenofetch sites
```

You can pipe the output to grep to search for specific sites:

```bash
phenofetch sites | grep "Colorado"
```

Or search by state code:

```bash
phenofetch sites | grep "FL"
```

## Workflow

After identifying a site of interest with the `sites` command, you can proceed to:

1. Check data availability with the `stats` command:
   ```bash
   phenofetch stats --site ABBY --product DP1.00033
   ```

2. Estimate download size with the `estimate` command:
   ```bash
   phenofetch estimate --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31
   ```

3. Download data with the `download` command:
   ```bash
   phenofetch download --site ABBY --product DP1.00033 --start-date 2022-01-01 --end-date 2022-01-31 --download
   ```
