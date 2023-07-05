#!/usr/bin/env python3

# Runner exposes three global variables:
# - SPICE_CLIENT: a spice client initialised with our API key to allow us to run queries
# - QUERY_VARIABLES: a dictionary of available variables for running our queries
# - OUTPUT_DIR: where to write our results that can either be written as a .sql or .parquet file

try:
    reader = SPICE_CLIENT.query(
        "select number, hash from eth.recent_blocks limit 10")
    df = reader.read_pandas()

except Exception as e:
    print(f"Error running", file=sys.stderr)
    raise e

df.to_csv(OUTPUT_DIR / "results.csv")

with open(OUTPUT_DIR / "results.csv", "r") as file:
    content = file.read()

# Print the content of the .csv file to stdout
print(content)

print(f"done! {len(df)}")
