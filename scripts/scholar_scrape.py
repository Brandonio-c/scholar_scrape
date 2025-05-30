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
from selenium.common.exceptions import TimeoutException
import requests

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
from sys import platform
# from selenium.webdriver.chrome.options import Options
import glob
import time
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

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
    def __init__(self, output_directory: os.path, plot_directory: os.path, wait_time: int=100):
        # Download the driver
        driver_dir = ChromeDriverManager().install()
        print(f"Driver directory: {driver_dir}")

        # Find the real chromedriver binary
        bin_path = os.path.join(os.path.dirname(driver_dir), "chromedriver")
        if not os.path.exists(bin_path):
            matches = glob.glob(os.path.join(os.path.dirname(driver_dir), "*chromedriver"))
            if matches:
                bin_path = matches[0]
            else:
                raise RuntimeError(f"Couldn't locate the actual chromedriver binary near {driver_dir}")

        # Sanity check and fix permissions if needed
        if not os.access(bin_path, os.X_OK):
            print(f"[WARNING] {bin_path} is not executable. Attempting to set permissions...")
            try:
                os.chmod(bin_path, 0o755)  # Make it executable
            except Exception as e:
                raise RuntimeError(f"Failed to chmod {bin_path} to 755: {e}")

            # Check again
            if not os.access(bin_path, os.X_OK):
                raise RuntimeError(f"{bin_path} is not executable even after attempting to chmod.")

        print(f"Using ChromeDriver binary at: {bin_path}")
        self._service = ChromeService(executable_path=bin_path)

        # Set up Chrome options for visible browser with real profile and bot evasion
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Use your real Chrome profile (Default on Mac)
        # options.add_argument("--user-data-dir=" + os.path.expanduser("~/Library/Application Support/Google/Chrome"))
        # options.add_argument("--profile-directory=Default")  # Use a different profile name if needed
        # options.add_argument("--profile-directory=Profile 1")  # or Profile 3, etc.
        # options.add_argument("--incognito")

        custom_profile_path = os.path.abspath("./selenium_profile")
        options.add_argument(f"--user-data-dir={custom_profile_path}")

        # Set realistic user agent
        # options.add_argument(
        #     "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        # )

        # Remove Selenium automation flags
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option("useAutomationExtension", False)

        # Modify navigator.webdriver to avoid detection
        # options.add_argument("--headless=new")  # Remove if you need visible browser for debugging

        # Initialize WebDriver
        # self._driver = webdriver.Chrome(service=self._service, options=options)
        self._driver = uc.Chrome(options=options)

        # Execute script to hide WebDriver details
        self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        # Optional: give you time to solve reCAPTCHA if it appears
        # time.sleep(5)
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

    def send_query_and_adjust_settings(self, query: str):
        """Submits a search query to Google Scholar and adjusts settings like unchecking the 'Include citations' checkbox."""
        search_box = self.get_query_box()
        print(f'Querying Google Scholar with: {query}')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Wait for the search results to be visible and then interact with settings
        try:
            WebDriverWait(self._driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'gs_res_ccl_mid'))  # Assumption: ID of the results container
            )
            print("Search results loaded.")
            self.adjust_search_settings()
        except Exception as e:
            print(f"Failed to load search results or interact with settings: {e}")

    def adjust_search_settings(self):
        """Adjusts search settings such as unchecking the 'Include citations' checkbox."""
        try:
            checkbox = WebDriverWait(self._driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.gs_cb_gen'))
            )
            if checkbox.get_attribute('aria-checked') == 'true':
                checkbox.click()
                print("Citations checkbox has been unchecked.")
            else:
                print("Citations checkbox is already unchecked.")
        except Exception as e:
            print(f"Failed to locate or interact with the 'Include citations' checkbox: {e}")

    def uncheck_include_citations(self):
        try:            
            # Find the checkbox link that includes citations by its aria-checked attribute
            checkbox_link = WebDriverWait(self._driver, 100).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.gs_bdy_sb_sec'))
                        )
            
            # Uncheck the checkbox if it is found to be checked
            if checkbox_link:
                checkbox_link.click()  # Click to uncheck
                print("Citations checkbox has been unchecked.")
            else:
                print("Citations checkbox was not found checked, no need to uncheck.")

        except TimeoutException:
            print("Failed to locate the citations checkbox within the given time.")
        except Exception as e:
            print(f"An error occurred while trying to uncheck the citations checkbox: {e}")



    # def wait_for_responses(self):
    #     """Waits for the search results page to load and verifies its presence."""
    #     try:
    #         print(f"Waiting {self._wait._timeout} seconds for a response")    
    #         results_container_present = self._wait.until(EC.presence_of_element_located((By.ID, 'gs_res_ccl_mid')))
    #         if not results_container_present:
    #             self._driver.quit()
    #             exit("The results container did not load in time.")
    #         return True
    #     except:
    #         return False


    def wait_for_responses(self, timeout=None):
        """
        Return True when at least one result title (.gs_rt) is present.
        """
        if timeout is None:
            timeout = self._wait._timeout          # default 40 s
        try:
            WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".gs_rt"))
            )
            return True
        except TimeoutException:
            return False

        
    def extract_results(self, query: str, start_page: int = 1):
        print(f"Extracting Results starting at page {start_page}...")

        results = []
        page_number = start_page
        has_next_page = True
        search_terms = [term.lower() for term in query.replace('"', '').split(' OR ')]

        # Construct direct URL jump using start_page
        start_index = (start_page - 1) * 10
        query_param = query.replace(' ', '+')
        scholar_url = f"https://scholar.google.com/scholar?start={start_index}&q={query_param}&hl=en&as_sdt=0,21"
        print(f"Navigating directly to: {scholar_url}")
        self._driver.get(scholar_url)

        while has_next_page:
            print(f"Processing page: {page_number}")              
            articles = self._driver.find_elements(By.CSS_SELECTOR, '.gs_rt')
            years = self._driver.find_elements(By.CSS_SELECTOR, '.gs_a')
            all_valid_data = []  # This will store tuples of (title, year)

            # List to hold articles and years without citations
            valid_articles = []
            valid_years = []

            for article, year in zip(articles, years):
            # Check if citation is present in the parent element of the title
                #parent_element = article.find_element(By.XPATH, '..')  # Get the parent div of the h3.gs_rt
                citation_present = article.find_elements(By.CSS_SELECTOR, 'span.gs_ctu span.gs_ct1')

                # If citation is present and matches '[CITATION]', skip processing this article
                if citation_present and '[CITATION]' in citation_present[0].text:
                    continue

                # For some reason not working and is causing issues now? 
                #article_text = article.text.lower()
                #if not any(term in article_text for term in search_terms):
                #    continue

                year_text = year.text
                # Attempt to extract the year after the last comma
                parts = year_text.split(', ')
                possible_year = parts[-1] if parts else 'Unknown'
                
                # Validate that the extracted part is a four-digit year
                if re.match(r'\d{4}', possible_year):
                    year = possible_year
                    year_match = re.search(r'\b(19|20)\d{2}\b', year)
                    year = year_match.group()
                else:
                    year = 'Unknown'  # Default to 'Unknown' if the format does not match

                valid_articles.append(article.text)  # Store the article title
                valid_years.append(year)  # Store the extracted year
                bibtex_str = ""
                try:
                    # click the “Cite” button
                    cite_btn = article.find_element(By.CSS_SELECTOR, "a.gs_or_cit")
                    cite_btn.click()

                    # wait for BibTeX link
                    bib_btn = self._wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.gs_citi"))
                    )
                    bib_url = bib_btn.get_attribute("href")
                    raw = requests.get(bib_url, timeout=10).text

                    # strip surrounding brackets
                    bib = raw.strip()
                    if bib.startswith("[") and bib.endswith("]"):
                        bib = bib[1:-1].strip()

                    # close popup
                    close_btn = self._driver.find_element(By.ID, "gs_cb_cit-x")
                    close_btn.click()

                    bibtex_str = bib

                except (TimeoutException, NoSuchElementException):
                    # no citation popup or took too long
                    bibtex_str = ""

                all_valid_data.append((article.text, year, bibtex_str))  # Add the valid data to list
            
            # Process only valid articles and years
            results.extend(all_valid_data)

            #Process only valid articles and years
            #if valid_articles and valid_years:
            #   results.extend(self.process_page(valid_articles, valid_years))

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
        with open('valid_articles_and_years.txt', 'w', encoding='utf-8') as file:
            for title, year, bibtex_str in all_valid_data:
                results.append((title, year, bibtex_str))
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
            # Bug fix! 
            # Skip citations and invalid years
            if "[CITATION]" in title or "N/A" in year_text:
                continue
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
                pub_filled = scholarly.fill(pub)
                bibtex_str = scholarly.bibtex(pub_filled)
                pub_year = pub['bib'].get('pub_year', 'No year')
                title = pub['bib'].get('title', 'No title')
                year_match = re.search(r'\b(19|20)\d{2}\b', pub_year)
                if year_match:
                    pub_year = year_match.group()
                results.append((title, pub_year, bibtex_str))
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
    def save_results_to_bib(self, bib_entries, query,
                            file_name_prefix="publications_bib"):
        """
        bib_entries : list[str] –­­ one BibTeX string per paper
        """
        # re-use the sane filename logic you already have
        query_parts = query.split()
        num_words_to_use = min(3, len(query_parts))
        clean_query = re.sub(r"[^\w\s]", "", "_".join(query_parts[:num_words_to_use])).lower()
        base_file = f"{file_name_prefix}_{clean_query}.bib"

        file_path = os.path.join(self.output_directory, base_file)
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(
                self.output_directory, f"{file_name_prefix}_{clean_query}_{counter}.bib"
            )
            counter += 1

        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write("\n\n".join(bib_entries))

        print(f"Saved BibTeX to {file_path}")


    def __init__(self, output_directory: os.path, plot_directory: os.path):
        self.output_directory = output_directory
        self.plot_directory = plot_directory

    def count_publications_by_year(self, results):
        """
            Counts publications per year from the provided results.
            Expects each result to be a (title, year, bibtex) tuple.
        """
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

        # Only keep years that are digits and not "Unknown"
        filtered_year_count = {
            year: count for year, count in year_count.items() 
            if str(year).isdigit() and year != 'Unknown'
        }

        # Convert to DataFrame
        data = pd.DataFrame(list(filtered_year_count.items()), columns=['Year', 'Count'])
        data['Year'] = data['Year'].astype(str)  # treat as categorical string

        # Only keep observed values
        plot = (
            ggplot(data, aes(x='Year', y='Count')) +
            geom_bar(stat='identity', fill='blue') +
            theme_classic() +
            labs(x='Year', y='Count of Papers Published Per Year') +
            theme(axis_text_x=element_text(rotation=90, hjust=1))
        )

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
            titles_years = [(t, y) for t, y, _ in results]
            display.save_results_to_csv(pd.DataFrame(titles_years, columns=['Title', 'Year']), query)
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

            input("Solve the CAPTCHA if it appears, then press Enter here to continue...")
            
            # this if statement is some hamburger ass code but It'll be fixed when the rest of the database scrapers are implemented
            # TODO - fix this 
            if data_source == 'scholar_API':
                # results = sss.search_publications(query, start_page=args.start_page)
                results = sss.search_publications(query)

                # Combine with previous CSV if provided
                if args.resume_from_csv and os.path.exists(args.resume_from_csv):
                    print(f"Combining with previous results from {args.resume_from_csv}")
                    prev_df = pd.read_csv(args.resume_from_csv)
                    new_df = pd.DataFrame(results, columns=["Title", "Year"])
                    combined_df = pd.concat([prev_df, new_df], ignore_index=True).drop_duplicates()
                else:
                    titles_years = [(t, y) for t, y, _ in results]
                    combined_df = pd.DataFrame(titles_years, columns=["Title", "Year"])

                bib_strings  = [b for _, _, b in results]
                year_count = display.count_publications_by_year(combined_df.values.tolist())
                display.display_year_counts(year_count)
                display.save_results_to_csv(combined_df, query)
                display.save_results_to_bib(bib_strings, query)
                display.plot_year_counts(year_count, query)

            else:
                now = datetime.now()
                tn = now.strftime('%y%b%d-%H:%M:%S').upper()

                query = sss.format_search_query(query=query)
                sss.send_query(query=query)
                input("If a CAPTCHA is showing in the browser, solve it now, then press Enter…")

                if sss.wait_for_responses():
                    #sss.uncheck_include_citations()  # Uncheck the checkbox after results load
                    results = sss.extract_results(query, start_page=args.start_page)
                else:
                    quit(f'Unable to Retrieve results for {query}, try again or try a simpler query')

                # Combine with previous CSV if provided
                if args.resume_from_csv and os.path.exists(args.resume_from_csv):
                    print(f"Combining with previous results from {args.resume_from_csv}")
                    prev_df = pd.read_csv(args.resume_from_csv)
                    new_df = pd.DataFrame(results, columns=["Title", "Year"])
                    combined_df = pd.concat([prev_df, new_df], ignore_index=True).drop_duplicates()
                else:
                    titles_years = [(t, y) for t, y, _ in results]
                    combined_df = pd.DataFrame(titles_years, columns=["Title", "Year"])

                year_count = display.count_publications_by_year(combined_df.values.tolist())
                display.display_year_counts(year_count)
                display.save_results_to_csv(combined_df, query)
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
                            default=40)
    argparser.add_argument('--scholar_API', 
                            action='store_true', 
                            help='Use scholarly API for data retrieval.')
    argparser.add_argument('--scholar_Web', 
                            action='store_true', 
                            help='Use Selenium for data retrieval.')
    argparser.add_argument('--start_page',
                            help='Page number to start scraping from (Google Scholar paginates every 10 results)',
                            type=int,
                            default=1)
    argparser.add_argument('--resume_from_csv',
                        help='Path to previous results CSV to resume and combine with',
                        type=str,
                        default=None)



    args = argparser.parse_args()
    
    output_directory = ensure_directory_exists(args.results_location)
    plot_directory = ensure_directory_exists(args.plots_location)
    
    main(args)
