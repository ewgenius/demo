#!/usr/bin/env python3

from spicepy import Client
import duckdb

def init_accumulator(duckdb: duckdb.DuckDBPyConnection):
  duckdb.sql("CREATE TABLE IF NOT EXISTS seen_blocks (num int)")
  existing_eigenpods_df = duckdb.sql("SELECT num from seen_blocks").df()
  if existing_eigenpods_df.empty:
    duckdb.sql("INSERT INTO seen_blocks VALUES (0)")

def process(context: dict, duckdb: duckdb.DuckDBPyConnection, spice_client: Client):
  data = spice_client.query(f"SELECT count(1) as cnt from eth.recent_blocks where number = {context['block_number']}")
  query_results = data.read_pandas()

  new_blocks = query_results["cnt"].iloc[0]

  # Set up the accumulator (only happens once)
  init_accumulator(duckdb)

  existing_blocks = duckdb.sql("SELECT num from seen_blocks").df()["num"].iloc[0]

  new_total_blocks = new_blocks + existing_blocks

  # Update the accumulator
  duckdb.sql(f"UPDATE seen_blocks SET num = {new_total_blocks}")

  # Temporary step
  duckdb.sql("""CREATE TABLE IF NOT EXISTS output.num_blocks (
                block_number BIGINT,
                blocks BIGINT
                )""")
  
  duckdb.sql(f"INSERT INTO output.num_blocks VALUES ({context['block_number']}, {new_total_blocks})")

  print("done!")
