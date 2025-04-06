#!/usr/bin/env python3

import argparse
import pandas as pd
import os
import re
from plotnine import ggplot, aes, geom_bar, theme_classic, labs, element_text, theme

def read_csv_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_csv(filepath)

def merge_unique_entries(df1, df2):
    combined_df = pd.concat([df1, df2], ignore_index=True)
    unique_df = combined_df.drop_duplicates(subset='Title')
    
    # Fix Year formatting here
    unique_df['Year'] = unique_df['Year'].apply(lambda x: str(int(float(x))) if pd.notna(x) and str(x).replace('.', '', 1).isdigit() else 'Unknown')
    
    return unique_df


def count_publications_by_year(df):
    # Convert year to string and filter out non-numeric entries
    df = df[df['Year'].astype(str).str.fullmatch(r'\d{4}')]
    df['Year'] = df['Year'].astype(int)
    year_counts = df['Year'].value_counts().sort_index()
    return year_counts

def print_year_counts(dataframe):
    """Prints number of publications per year in sorted order, matching the plot."""
    print("\nPublications per Year:")
    filtered_df = dataframe[dataframe['Year'].astype(str).str.fullmatch(r'\d{4}')]
    filtered_df['Year'] = filtered_df['Year'].astype(int)
    year_counts = filtered_df['Year'].value_counts().sort_index()
    for year, count in year_counts.items():
        print(f"{year}: {count}")



def plot_year_counts(year_count, output_path):
    """Creates and saves a bar chart with every year shown on the x-axis."""
    # Filter and convert to DataFrame
    filtered_year_count = {int(year): count for year, count in year_count.items() if year != 'Unknown'}
    data = pd.DataFrame(list(filtered_year_count.items()), columns=['Year', 'Count'])

    # Fill in missing years
    full_range = pd.DataFrame({'Year': range(data['Year'].min(), data['Year'].max() + 1)})
    data = pd.merge(full_range, data, on='Year', how='left').fillna(0)
    data['Count'] = data['Count'].astype(int)
    data['Year'] = data['Year'].astype(str)  # Ensure discrete axis

    # Create plot
    plot = (ggplot(data, aes(x='Year', y='Count')) +
                geom_bar(stat='identity', fill='blue') +
                theme_classic() +
                labs(x='Year', y='Count of Papers Published Per Year') +
                theme(axis_text_x=element_text(rotation=90, hjust=1)))

    # Save
    plot.save(output_path, width=10, height=6, units='in')
    print(f'Plot saved to {output_path}')

    
def get_output_paths(csv1_path, csv2_path):
    # Base directory
    csv_dir = os.path.join('..', 'results', 'csv')
    plot_dir = os.path.join('..', 'results', 'plots')

    # Ensure output dirs exist
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Clean names
    base1 = os.path.splitext(os.path.basename(csv1_path))[0]
    base2 = os.path.splitext(os.path.basename(csv2_path))[0]
    base_name = f'merged_{base1}_and_{base2}'

    # Paths
    output_csv = os.path.join(csv_dir, f'{base_name}.csv')
    output_plot = os.path.join(plot_dir, f'{base_name}_year_counts.svg')
    return output_csv, output_plot

def main():
    parser = argparse.ArgumentParser(description="Merge two publication CSVs and output a deduplicated CSV + plot.")
    parser.add_argument('csv1', help='Path to the first CSV file')
    parser.add_argument('csv2', help='Path to the second CSV file')
    args = parser.parse_args()

    # Read
    df1 = read_csv_file(args.csv1)
    df2 = read_csv_file(args.csv2)

    # Merge
    merged_df = merge_unique_entries(df1, df2)

    # Output locations
    output_csv, output_plot = get_output_paths(args.csv1, args.csv2)

    # Save
    merged_df.to_csv(output_csv, index=False)
    print(f"Merged CSV saved to: {output_csv}")

    # Plot
    year_counts = count_publications_by_year(merged_df)
    print_year_counts(merged_df)
    plot_year_counts(year_counts, output_plot)

if __name__ == '__main__':
    main()
