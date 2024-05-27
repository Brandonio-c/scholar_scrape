# Author: Brandon Colelough, Kent O'Sullivan

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

# User Imports

class Selenium_Scholar_Scraper():
    def __init__(self, output_directory:os.path, plot_directory:os.path, wait_time:int=20):
        
        
        self._output_directory = self.ensure_directory_exists(output_directory)
        self._plot_directory = self.ensure_directory_exists(plot_directory)

        self._service = ChromeService(ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=self._service)
        self._wait = WebDriverWait(self._driver, wait_time)

        self.open_google_scholar()
        
    def open_google_scholar(self):
        self._driver.get('https://scholar.google.com/')
    
    def format_search_query(self, query:str):
        return query
    
    def get_query_box(self):
        return self._driver.find_element(By.NAME,'q')
    
    def send_query(self, search_box, query:str):
        print(f'Querying Google Schola with: {query}')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
    
    def wait_for_responses(self):
        print(f"Waiting {self._wait._timeout} seconds for a response")    
        results_container_present = self._wait.until(EC.presence_of_element_located((By.ID, 'gs_res_ccl_mid')))
        if not results_container_present:
            self._driver.quit()
            exit("The results container did not load in time.")
        return True
    
    def process_page(self, articles, years):
        page_results = []
        for article, year in zip(articles, years):
            title = article.text
            year_text = year.text
            print(title,year_text)
            year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
            if year_match:
                pub_year = year_match.group()
                page_results.append((title, pub_year))
        
        return page_results
    
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
                next_button = self.driver.find_element(By.LINK_TEXT, 'Next')
                next_button.click()
                # Wait for the next page to load
                self._wait.until(EC.presence_of_element_located((By.ID, 'gs_res_ccl_mid')))
                page_number += 1
            except Exception as e:
                print(f"No more pages. Stopping at page {page_number}")
                has_next_page = False

        self._driver.quit()
        return results

    def count_publications_by_year(self, results):
        # Count publications per year
        print("Counting publications by year...")
        year_count = {}
        for _, pub_year in results:
            if pub_year in year_count:
                year_count[pub_year] += 1
            else:
                year_count[pub_year] = 1

        return year_count
    
    def display_year_counts(self, year_count:dict):
        total_publications = len(results)
        print("Number of publications per year:")
        for year in sorted(year_count.keys()):
            print(f"{year}: {year_count[year]}")
        print(f"Total number of publications found: {total_publications}")

    def convert_year_counts_to_data_frame(self, year_count):
        # Convert the year_count dictionary to a DataFrame
        print("Converting year counts to dataframe...")
        return(pd.DataFrame(list(year_count.items()), columns=['Year', 'Count']))
    
    def save_dataframe_to_csv(self, data:pd.DataFrame, file_name:str='publications_data.csv'):
        print(f'Saving Dataframe to {os.path.join(self._output_directory,file_name)}')
        data.to_csv(os.path.join(self._output_directory, file_name), index=False)

    def plot_bar_chart_of_year_counts(self, data:pd.DataFrame):
        # Plot the data using plotnine
        bar_plot = (ggplot(data, aes(x='Year', y='Count', fill='Year')) +
                geom_bar(stat='identity') +
                theme_classic() +
                labs(x='Year', y='Count of Papers Published Per Year') +
                theme(axis_text_x=element_text(rotation=90, hjust=1)))
        return(bar_plot)
        
    def save_plot_to_file(self, plot, file_name:str):
        # Save the plot as an SVG file
        print(f'Saving Plot to {os.path.join(self._plot_directory ,file_name)}')
        plot.save(os.path.join(self._plot_directory,file_name))

    def ensure_directory_exists(self, directory:os.path):
        if not os.path.exists(directory):
            print(f"Target Directory not Found, making new Directory at {directory}")
            os.makedirs(directory)
        else:
            print(f"Direcotry found at {directory}")

        return directory


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()

    argparser.add_argument('--results_location',
                           help='directory to output the results CSV to',
                           type=str,
                           required=False,
                           default=os.path.join('..','results','csv'))
    argparser.add_argument('--plots_location',
                           help='Directory to save plots to',
                           type=str,
                           required=False,
                           default=os.path.join('..','results','plots'))
    argparser.add_argument('--wait_time',
                           help='how long selenium should wait before abandoning the search',
                           type=int,
                           required=False,
                           default=20)
    argparser.add_argument('--query',
                          help='Query term for google scholar. Use boolean searches e.g. X AND Y OR X, with parentheses to clarify meaning e.g. X AND Y AND (A or B)', 
                          type = str, 
                          required=True)
    
    flags = argparser.parse_args()

    sss = Selenium_Scholar_Scraper(output_directory     =   flags.results_location, 
                                   plot_directory       =   flags.plots_location,
                                   wait_time            =   flags.wait_time
                                   )
    
    now = datetime.now()
    tn = now.strftime('%y%b%d-%H:%M:%S').upper()

    query = sss.format_search_query(query=flags.query)
    query_box = sss.get_query_box()
    sss.send_query(search_box=query_box, query=query)
    if sss.wait_for_responses():
        results = sss.extract_results()
    else:
        quit(f'Unable to Retrieve results for {query}, try again or try a simpler query')

    counts_by_year = sss.count_publications_by_year(results=results)
    sss.display_year_counts(counts_by_year)

    yc_df = sss.convert_year_counts_to_data_frame(year_count=counts_by_year)

    print(yc_df)

    sss.save_dataframe_to_csv(data=yc_df,file_name=f'publications_data_{tn}.csv')
    
    plot = sss.plot_bar_chart_of_year_counts(data=yc_df)
    sss.save_plot_to_file(plot=plot,file_name="plot"+tn+".svg")


# To run simplest version, just paste the following to the command line: 
    # python scholar_search_v2.py --query '("Knowledge Gap Identification" AND ("neuro-symbolic" OR "neurosymbolic" OR "neuro symbolic" OR "neural-symbolic" OR "neuralsymbolic" OR "neural symbolic"))'

