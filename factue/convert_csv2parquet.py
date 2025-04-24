from pathlib import Path

import pandas as pd

# Define input and output base paths
raw_dir = Path("data/raw")
parquet_dir = Path("data/parquet/input")

# Find all CSV files recursively
csv_files = raw_dir.glob("**/*.csv")

for csv_file in csv_files:
    # Determine relative path to raw_dir
    relative_path = csv_file.relative_to(raw_dir).with_suffix(".parquet")

    # Construct the output path
    output_file = parquet_dir / relative_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Read CSV and write to Parquet
    df = pd.read_csv(csv_file)
    df.to_parquet(output_file, index=False)

    print(f"Converted {csv_file} -> {output_file}")
