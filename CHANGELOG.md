# Changelog

All notable changes to this project should be documented in this file.

## v2.0.0 - 2026-03-18

- Switched the data source from user-uploaded SIROS CSV files to the public SIROS API endpoint.
- Kept the SSIM output structure already used by the project.
- Added Streamlit filters for airline, one or more airports, start date and end date.
- Added direct mapping from the live SIROS dataset to SSIM fields.
- Added UTC-to-local time conversion based on airport timezone data.
- Added support for generating SSIM for multiple airports from the same airline in a single run.

## v1.0.1 - 2025-12-10

- Updated the carrier record prefix in line type `2` from `2U` to `2L`.

## v1.0.0

- Initial public version of the Streamlit SSIM generator based on uploaded SIROS CSV files.
