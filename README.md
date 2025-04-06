# Scholar Scrape

## Overview
Scholar Scrape is a tool designed to automate the process of extracting publication data from Google Scholar and other scholarly databases. This tool provides both a Command Line Interface (CLI) and a Graphical User Interface (GUI) mode, allowing users to perform searches using the scholarly API or Selenium WebDriver.

## Installation

### Prerequisites
- Python 3.6 or newer
- pip
- Dependencies from `requirements.txt`
- Necessary Python libraries in requirements.txt are: `selenium`, `pandas`, `matplotlib`, `plotnine`, `scholarly`
- C++ 14.0 devl SDK or newer if compiling on windows 

### Setup
Clone this repository or download the source code. Navigate to the project directory and install the required Python packages using:

```bash
pip install -r requirements.txt
```

## Usage
### Running the Tool with the CLI
To run the tool in CLI mode with the scholarly API:

```bash
python3 scholar_scrape.py --CLI --scholar_API
```

### For GUI mode, use:
```bash
python scholar_search.py --GUI
```

## Example Queries
### Small result set:
```bash
'("Knowledge Gap Identification" AND ("neuro-symbolic" OR "neurosymbolic" OR "neuro symbolic" OR "neural-symbolic" OR "neuralsymbolic" OR "neural symbolic"))'
```
### Larger result set:
```bash
'("neuro-symbolic" OR "neurosymbolic" OR "neuro symbolic" OR "neural-symbolic" OR "neuralsymbolic" OR "neural symbolic")'
```

### Continuing from a Specific Page and Combining with Previous Results

You can now **resume scraping from a specific page** and **merge the results** with a previously saved CSV file. This is especially useful when scraping large result sets in batches to avoid timeouts or rate limiting.

#### Example:
To continue scraping using the Selenium web scraper starting at page 92 and append the results to an existing CSV file:

```bash
python3 scholar_scrape.py --CLI --scholar_Web \
  --start_page 92 \
  --resume_from_csv "/path/to/existing/publications_data.csv"
```

- `--start_page`: Sets the page number to begin scraping from (Google Scholar paginates every 10 results, so page 92 starts at result #910).
- `--resume_from_csv`: Path to an existing CSV file to which the new results will be appended. Duplicates will automatically be removed based on the title.

#### Result:
The tool will:
- Start scraping from the specified page,
- Combine new results with the existing dataset,
- Save a deduplicated, updated CSV file,
- Update the visual plot based on the combined results.


### Merging and Visualizing Existing CSV Results

If you've already performed multiple search runs and saved their results to separate CSV files, you can now **merge and deduplicate** those CSVs into a single file with a **summary plot of publication counts by year**.

#### Script: `combine_csv_entries.py`

This utility script allows you to:
- Merge two publication CSVs.
- Remove duplicates based on publication title.
- Fix improperly formatted year entries (e.g., `2022.0` → `2022`).
- Generate a combined CSV file in `./results/csv/`.
- Produce a publication distribution plot in `./results/plots/`.
- Print a summary of publication counts by year.

#### Example Usage:
```bash
python3 combine_csv_entries.py \
  "results/old/csv/publications_data_neurosymbolic.csv" \
  "results/csv/publications_data_neurosymbolic.csv"
```

#### Output:
- A deduplicated merged CSV file:  
  `results/csv/merged_publications_data_neurosymbolic_and_publications_data_neurosymbolic.csv`
- A visual plot of publication counts by year:  
  `results/plots/merged_publications_data_neurosymbolic_and_publications_data_neurosymbolic_year_counts.svg`
- A printed summary in the terminal like:
  ```
  Publications per Year:
  2001: 1
  2008: 3
  2022: 87
  2023: 121
  ...
  ```

This tool is ideal for consolidating large-scale scraping sessions and ensuring consistent formatting and visualization.


## Development
This project is still presenty under development!

## Contribution
Contributions are welcome! Please fork the repository and open a pull request with your additions.

## License
Distributed under the MIT License. See LICENSE for more information.

## Authors
- Brandon Colelough

## Acknowledgments
Thanks to the developers of scholarly and selenium for making the automation of scholarly searches possible.
