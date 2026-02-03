#!/bin/env python3

import csv
from pytablewriter import TomlTableWriter
import sys

input_csv = sys.argv[1]
output_toml = sys.argv[2]

with open(input_csv, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader)
    rows = list(reader)

writer = TomlTableWriter(
    table_name="messages",
    headers=headers,
    value_matrix=rows,
)

with open(output_toml, "w", encoding="utf-8") as f:
    writer.stream = f
    writer.write_table()
