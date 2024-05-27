"""
Scholar Scrape

Author: Brandon Colelough, Kent O'Sullivan

Overview:
Scholar Scrape is a powerful tool designed for scraping scholarly data using various APIs and web scraping techniques. It supports multiple databases, including Google Scholar, IEEE, ArXiv, ACM, Springer, Semantic Scholar, and PubMed.

Features:
- Support for Multiple Databases: Interacts with different scholarly databases to fetch publication data.
- CLI and GUI Modes: Users can operate the tool via a command-line interface or a graphical user interface.
- Data Visualization: Generates visualizations for the distribution of publications over years.
- Flexible Query Options: Allows complex queries for advanced users, while also providing simple search options.

TODO:
1. Add functionality to scrape the remainder of the databases.
2. Finish the GUI.
3. Add functionality to sum results across multiple databases 
4. Determine why the API is so slow when using complex queries.
5. Make more robust.

To run simplest version, just paste the following to the command line: 
python3 ./scholar_scrape.py --CLI --scholar_API
A suitable query would be: 
'("Knowledge Gap Identification" AND ("neuro-symbolic" OR "neurosymbolic" OR "neuro symbolic" OR "neural-symbolic" OR "neuralsymbolic" OR "neural symbolic"))'
The above should produce ~1 result (as of 2024).
'("neuro-symbolic" OR "neurosymbolic" OR "neuro symbolic" OR "neural-symbolic" OR "neuralsymbolic" OR "neural symbolic")'
The above should produce ~950 results (as of 2024).
"""

# Core Imports 
import re
import os
import argparse
from datetime import datetime

# Library Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import matplotlib.pyplot as plt
from plotnine import ggplot, aes, geom_bar, theme_classic, labs, element_text, theme
import tkinter as tk
from tkinter import Toplevel, StringVar, Entry, Radiobutton, Button
from scholarly import scholarly

# User Imports

# Selenium imports are only required in the Selenium_Scholar_Scraper class
# to prevent errors if Selenium is not installed or needed by the user.

# Classes for different types of scholar scraping
class Selenium_Scholar_Scraper():
    """
    A class for scraping publication data from Google Scholar using Selenium.
    
    Attributes:
        output_directory (str): Path where the results will be saved.
        plot_directory (str): Path where plots will be saved.
        wait_time (int): How long Selenium will wait for a page to load before timing out.
    """
    def __init__(self, output_directory: os.path, plot_directory: os.path, wait_time: int=20):
        #self._output_directory = self.ensure_directory_exists(output_directory)
        #self._plot_directory = self.ensure_directory_exists(plot_directory)
        self._service = ChromeService(ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=self._service)
        self._wait = WebDriverWait(self._driver, wait_time)
        self.open_google_scholar()

    def open_google_scholar(self):
        """Navigates to the Google Scholar homepage."""
        self._driver.get('https://scholar.google.com/')

    def format_search_query(self, query:str):
        "formats search query as a string"
        return query
    
    def get_query_box(self):
        return self._driver.find_element(By.NAME,'q')

    def send_query(self, query:str):
        """Submits a search query to Google Scholar using Selenium."""
        search_box = self.get_query_box()
        print(f'Querying Google Scholar with: {query}')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        #if not self.wait_for_responses():
        #    print("Failed to load results in time. Please try again with a different query or check your network.")
        #    return []

    def wait_for_responses(self):
        """Waits for the search results page to load and verifies its presence."""
        try:
            print(f"Waiting {self._wait._timeout} seconds for a response")    
            results_container_present = self._wait.until(EC.presence_of_element_located((By.ID, 'gs_res_ccl_mid')))
            if not results_container_present:
                self._driver.quit()
                exit("The results container did not load in time.")
            return True
        except:
            return False
        
    def extract_results(self):
        print('Extracting Results...')
        results = []
        page_number = 1
        has_next_page = True

        while has_next_page:
            print(f"Processing page: {page_number}")
            # Extract publication titles and years on the current page
            articles = self._driver.find_elements(By.CSS_SELECTOR, '.gs_rt')
            years = self._driver.find_elements(By.CSS_SELECTOR, '.gs_a')

            for article in articles:
                print(article.get_attribute('.gs_rt'))

            results.extend(self.process_page(articles=articles, 
                                                years=years))  

            # Check if there is a next page
            try:
                print(f'Looking to see if page {page_number+1} exists')
                next_button = self._driver.find_element(By.LINK_TEXT, 'Next')
                next_button.click()
                # Wait for the next page to load
                self._wait.until(EC.presence_of_element_located((By.ID, 'gs_res_ccl_mid')))
                page_number += 1
            except Exception as e:
                print(f"No more pages. Stopping at page {page_number}")
                has_next_page = False

        self._driver.quit()
        return results

    def check_next_page(self, page_number):
        """Checks and navigates to the next page of results if available."""
        try:
            next_button = self._driver.find_element(self.By.LINK_TEXT, 'Next')
            next_button.click()
            self._wait.until(self.EC.presence_of_element_located((self.By.ID, 'gs_res_ccl_mid')))
            return True, page_number + 1
        except:
            print(f"No more pages. Stopping at page {page_number}")
            return False, page_number

    def process_page(self, articles, years):
        """Processes each article and year element found on the current page."""
        page_results = []
        for article, year in zip(articles, years):
            title = article.text
            year_text = year.text
            year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
            if year_match:
                pub_year = year_match.group()
                page_results.append((title, pub_year))
        return page_results

class Scholarly_Scholar_Scraper():
    """
    A class for scraping publication data from Google Scholar using the scholarly package.
    
    Attributes:
        None specific.
    """
    def search_publications(self, query:str):
        """Uses the scholarly package to fetch publications based on a query."""
        search_query = scholarly.search_pubs(query)
        results = []
        try:
            while True:
                pub = next(search_query)
                pub_year = pub['bib'].get('pub_year', 'No year')
                title = pub['bib'].get('title', 'No title')
                year_match = re.search(r'\b(19|20)\d{2}\b', pub_year)
                if year_match:
                    pub_year = year_match.group()
                results.append((title, pub_year))
        except StopIteration:
            pass
        return results

# Placeholder classes for other databases
class IEEE_Scraper:
    """Class to handle searches on the IEEE database."""
    def search_publications(self, query):
        print(f"Simulating IEEE search for: {query}")
        return [("Sample IEEE Paper 1", "2020"), ("Sample IEEE Paper 2", "2019")]

class ArXiv_Scraper:
    """Class to handle searches on the arXiv database."""
    def search_publications(self, query):
        print(f"Simulating arXiv search for: {query}")
        return [("Sample arXiv Paper 1", "2018"), ("Sample arXiv Paper 2", "2017")]

class ACM_Scraper:
    """Class to handle searches on the ACM database."""
    def search_publications(self, query):
        print(f"Simulating ACM search for: {query}")
        return [("Sample ACM Paper 1", "2016"), ("Sample ACM Paper 2", "2015")]

class Springer_Scraper:
    """Class to handle searches on the Springer database."""
    def search_publications(self, query):
        print(f"Simulating Springer search for: {query}")
        return [("Sample Springer Paper 1", "2014"), ("Sample Springer Paper 2", "2013")]

class SemanticScholar_Scraper:
    """Class to handle searches on the Semantic Scholar database."""
    def search_publications(self, query):
        print(f"Simulating Semantic Scholar search for: {query}")
        return [("Sample Semantic Scholar Paper 1", "2012"), ("Sample Semantic Scholar Paper 2", "2011")]

class PubMed_Scraper:
    """Class to handle searches on the PubMed database."""
    def search_publications(self, query):
        print(f"Simulating PubMed search for: {query}")
        return [("Sample PubMed Paper 1", "2010"), ("Sample PubMed Paper 2", "2009")]

class DisplayResults():
    """
    A class for displaying and saving the results of publication searches.
    
    Attributes:
        output_directory (str): Path where the CSV results will be saved.
        plot_directory (str): Path where plots will be saved.
    """
    def __init__(self, output_directory: os.path, plot_directory: os.path):
        self.output_directory = output_directory
        self.plot_directory = plot_directory

    def count_publications_by_year(self, results):
        """Counts publications per year from the provided results."""
        print("Counting publications by year...")
        year_count = {}
        for _, pub_year in results:
            if pub_year in year_count:
                year_count[pub_year] += 1
            else:
                year_count[pub_year] = 1
        return year_count

    def display_year_counts(self, year_count):
        """Displays the count of publications per year."""
        total_publications = sum(year_count.values())
        print("Number of publications per year:")
        for year in sorted(year_count.keys()):
            print(f"{year}: {year_count[year]}")
        print(f"Total number of publications found: {total_publications}")

    def save_results_to_csv(self, data, query, file_name_prefix='publications_data'):
        """Saves the provided data to a CSV file, naming the file based on the query."""
        # Extract words from the query and create a filename part
        query_parts = query.split()
        num_words_to_use = min(3, len(query_parts))  # Use up to three words or fewer if not available
        clean_query = "_".join(query_parts[:num_words_to_use])  # Join words

        # Clean the filename part by removing non-alphanumeric characters except underscores
        clean_query = re.sub(r'[^\w\s]', '', clean_query).lower()  # Clean up to use as a filename

        # Create a base file name
        base_file_name = f"{file_name_prefix}_{clean_query}.csv"

        # Ensure the file name is unique
        final_file_name = base_file_name
        count = 1
        while os.path.exists(os.path.join(self.output_directory, final_file_name)):
            final_file_name = f"{file_name_prefix}_{clean_query}_{count}.csv"
            count += 1

        # Save the CSV file
        file_path = os.path.join(self.output_directory, final_file_name)
        data.to_csv(file_path, index=False)
        print(f"Saved data to {file_path}")

    def plot_year_counts(self, year_count, query):
        """Creates and saves a bar chart of publication counts per year using the query to name the file."""
        # Extract words from the query and create a filename base
        query_parts = query.split()
        num_words_to_use = min(3, len(query_parts))  # Use up to three words or fewer if not available
        clean_query = "_".join(query_parts[:num_words_to_use])  # Join words

        # Clean the filename base by removing non-alphanumeric characters except underscores
        clean_query = re.sub(r'[^\w\s]', '', clean_query).replace(' ', '_').lower()

        # Create a DataFrame for plotting
        data = pd.DataFrame(list(year_count.items()), columns=['Year', 'Count'])
        plot = (ggplot(data, aes(x='Year', y='Count')) +
                geom_bar(stat='identity', fill='blue') +
                theme_classic() +
                labs(x='Year', y='Count of Papers Published Per Year') +
                theme(axis_text_x=element_text(rotation=90, hjust=1)))

        # Generate a unique filename by checking existing files
        plot_file_name = os.path.join(self.plot_directory, f'{clean_query}_year_counts_plot.svg')
        counter = 1
        while os.path.exists(plot_file_name):
            plot_file_name = os.path.join(self.plot_directory, f'{clean_query}_{counter}_year_counts_plot.svg')
            counter += 1

        # Save the plot
        plot.save(plot_file_name)
        print(f'Plot saved to {plot_file_name}')


def ensure_directory_exists(directory:os.path):
        """Ensures output directories exist"""
        if not os.path.exists(directory):
            print(f"Target Directory not Found, making new Directory at {directory}")
            os.makedirs(directory)
        else:
            print(f"Direcotry found at {directory}")

        return directory

def main(args):
    """Main function"""
    data_source = 'scholar_API' if args.scholar_API else 'scholar_Web'
    display = DisplayResults(args.results_location, args.plots_location)

    if args.GUI:
        # GUI mode
        root = tk.Tk()
        root.title("Scholarly Database Search")

        query_var = StringVar()
        entry = Entry(root, textvariable=query_var, width=50)
        entry.pack()

        databases = {'Scholarly': Scholarly_Scholar_Scraper(),
                    'IEEE': IEEE_Scraper(),
                    'arXiv': ArXiv_Scraper(),
                    'ACM': ACM_Scraper(),
                    'Springer': Springer_Scraper(),
                    'Semantic Scholar': SemanticScholar_Scraper(),
                    'PubMed': PubMed_Scraper()}

        database_vars = {db: IntVar(value=1) for db in databases}
        for db, var in database_vars.items():
            Checkbutton(root, text=db, variable=var).pack()

        def on_submit():
            query = query_var.get()
            results = []
            for db, scraper in databases.items():
                if database_vars[db].get():
                    results.extend(scraper.search_publications(query))
            year_count = display.count_publications_by_year(results)
            display.display_year_counts(year_count)
            display.save_results_to_csv(pd.DataFrame(results, columns=['Title', 'Year']), query)
            display.plot_year_counts(year_count, query)
            root.destroy()

        submit_button = Button(root, text="Submit", command=on_submit)
        submit_button.pack()
        root.mainloop()

    elif args.CLI:
        if data_source == 'scholar_API':
            sss = Scholarly_Scholar_Scraper()  # Default scraper for CLI for simplicity
        else:
            sss = Selenium_Scholar_Scraper(output_directory=args.results_location,
                                            plot_directory=args.plots_location,
                                            wait_time=args.wait_time)
        # CLI mode
        while True:
            query = input("Enter your search query for Scholarly Databases (type 'exit' to quit): ")
            if query.lower() == 'exit':
                break
            
            # this if statement is some hamburger ass code but It'll be fixed when the rest of the database scrapers are implemented
            # TODO - fix this 
            if data_source == 'scholar_API':
                results = sss.search_publications(query)
                year_count = display.count_publications_by_year(results)
                display.display_year_counts(year_count)
                display.save_results_to_csv(pd.DataFrame(results, columns=['Title', 'Year']), query)
                display.plot_year_counts(year_count, query)
            else:
                now = datetime.now()
                tn = now.strftime('%y%b%d-%H:%M:%S').upper()

                query = sss.format_search_query(query=query)
                sss.send_query(query=query)
                if sss.wait_for_responses():
                    results = sss.extract_results()
                else:
                    quit(f'Unable to Retrieve results for {query}, try again or try a simpler query')

                year_count = display.count_publications_by_year(results)
                display.display_year_counts(year_count)
                display.save_results_to_csv(pd.DataFrame(results, columns=['Title', 'Year']), query)
                display.plot_year_counts(year_count, query)
    else:
        print("No valid mode selected. Please use --GUI or --CLI.")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Search Google Scholar using either CLI or GUI mode. Use --GUI for graphical interface and --CLI for command line interface.")
    argparser.add_argument('--GUI', 
                            action='store_true', 
                            help='Run the program in graphical user interface (GUI) mode.')
    argparser.add_argument('--CLI', 
                            action='store_true', 
                            help='Run the program in command line interface (CLI) mode.')
    argparser.add_argument('--results_location', 
                            help='directory to output the results CSV to', 
                            type=str, 
                            default=os.path.join('..', 'results', 'csv'))
    argparser.add_argument('--plots_location', 
                            help='Directory to save plots to', 
                            type=str, 
                            default=os.path.join('..', 'results', 'plots'))
    argparser.add_argument('--wait_time', 
                            help='how long selenium should wait before abandoning the search', 
                            type=int, 
                            default=20)
    argparser.add_argument('--scholar_API', 
                            action='store_true', 
                            help='Use scholarly API for data retrieval.')
    argparser.add_argument('--scholar_Web', 
                            action='store_true', 
                            help='Use Selenium for data retrieval.')

    args = argparser.parse_args()
    
    output_directory = ensure_directory_exists(args.results_location)
    plot_directory = ensure_directory_exists(args.plots_location)
    
    main(args)
