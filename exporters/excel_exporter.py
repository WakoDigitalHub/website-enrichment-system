def save_to_excel(df, output_path):
    df.to_excel(output_path, index=False)
    print(f"✅ Saved enriched data to {output_path}")
