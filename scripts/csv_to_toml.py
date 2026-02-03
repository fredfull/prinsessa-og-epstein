#!/bin/env python3

import csv
import tomlkit
from tomlkit import document, table, aot, string
import sys

input_csv = sys.argv[1]
output_toml = sys.argv[2]

doc = document()
items = aot()

with open(input_csv, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        t = table()
        for k, v in row.items():
            if "\n" in v:
                # force multiline TOML string
                t[k] = string(v, multiline=True)
            else:
                t[k] = v
        items.append(t)

doc["messages"] = items

with open(output_toml, "w", encoding="utf-8") as f:
    f.write(tomlkit.dumps(doc))
