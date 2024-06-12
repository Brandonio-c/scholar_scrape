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
## Development
This project is still presenty under development!

## Contribution
Contributions are welcome! Please fork the repository and open a pull request with your additions.

## License
Distributed under the MIT License. See LICENSE for more information.

## Authors
- Brandon Colelough
- Kent O'Sullivan

## Acknowledgments
Thanks to the developers of scholarly and selenium for making the automation of scholarly searches possible.
