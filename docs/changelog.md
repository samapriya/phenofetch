# Changelog

This page documents the version history and notable changes to PhenoFetch.

#### Version 0.2.0 (Current)

Released: 2025

#### Added

- New metadata command to extract and process information from downloaded metadata files
- Support for exporting metadata in multiple formats (CSV, JSON, Parquet)
- Filename parsing to extract date, time, and site information
- Batch processing capability for large metadata collections

#### Updated

- Documentation to include metadata command usage and examples
- Command-line interface with metadata subcommand

### Version 0.1.1

Released: 2025

#### Added
- New `estimate` command to check download size before committing to large downloads
- Size estimation for full-resolution images and thumbnails
- Detailed breakdown of file sizes by type (full-res, thumbnail, metadata)
- Better error handling and reporting in size estimation

#### Updated
- Documentation to include size estimation workflow
- Progress bar display for better visibility during batch operations

#### Improved
- Terminal output formatting with Rich library

### Version 0.1.0 (Initial Release)

Released: 2025

#### Features
- Initial implementation of PhenoFetch tool
- Basic commands: `sites`, `stats`, and `download`
- Asynchronous downloading capabilities
- Site information retrieval
- Data availability statistics
