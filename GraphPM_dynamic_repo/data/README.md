# Data

This folder contains the normalized schema and small demo CSVs. Large public datasets should not be committed here.

## Public real dataset

Recommended starting source: **The Public Jira Dataset**, 2025 anonymized release, Zenodo DOI 10.5281/zenodo.15719919. It contains 2.7M issues, 32M changes, 9M comments and 1M issue links across 16 public Jira repositories.

Download a subset from:
https://zenodo.org/records/15719919

Then map the source fields into the GraphPM normalized schema.

## Why normalization?

Different Jira exports use different column names. GraphPM separates ingestion from the core graph/model layer so the UI and prediction code stay stable.
