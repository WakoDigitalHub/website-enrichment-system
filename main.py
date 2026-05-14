import os

import pandas as pd

from config.settings import CONFIG
from exporters.excel_exporter import save_to_excel
from processors.enrich import run_combined
from utils.helpers import merge_values


def main():
    input_file = CONFIG["input_file"]
    output_file = CONFIG["output_file"]

    # Show only the file name, not the full path
    print(f"Loading Excel file: {os.path.basename(input_file)}")
    print(f"Output will be saved as: {os.path.basename(output_file)}")

    df = pd.read_excel(CONFIG["input_file"])
    df.columns = df.columns.str.strip().str.lower()

    print("Total rows:", len(df))
    if "website" in df.columns:
        print("Rows with websites:", df["website"].notna().sum())
    else:
        print("No 'website' column found in Excel!")

    # Ensure enrichment columns exist
    for col in ["email", "facebook", "instagram", "linkedin", "twitter", "whatsapp"]:
        if col not in df.columns:
            df[col] = None

    print("Starting enrichment...")
    scraped_df, enriched_count = run_combined(df)

    # Align scraped_df with df
    scraped_df = scraped_df.reindex(df.index)

    # Merge enrichment results
    for col in ["email", "facebook", "instagram", "linkedin", "twitter", "whatsapp"]:
        df[col] = df[col].combine(scraped_df[col], merge_values)

    save_to_excel(df, CONFIG["output_file"])
    print(f"Enrichment complete. Total websites enriched: {enriched_count}")


if __name__ == "__main__":
    main()
