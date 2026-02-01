#!/bin/python3
import csv
from pathlib import Path
import os

CSV_FILE = os.environ["CSV_FILE"]
MD_FILE = os.environ["MD_FILE"]


def safe(val):
    return val.strip() if val else ""


rows = []


def find_data_set(file_name):
    # I assume that the second digit, fifth char, is correlated with the dataset
    # the pdf comes from
    data_sets = ["DataSet+9", "DataSet+10", "DataSet+11"]
    second_digit = int(file_name[5])
    return data_sets[second_digit]


with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        rows.append(
            {
                "From": safe(row.get("From")),
                "To": safe(row.get("To")),
                "Sent": safe(row.get("Sent")),
                "Subject": safe(row.get("Subject")),
                "Path": safe(row.get("Path")),
                "Content": safe(row.get("Content")),
                "FileName": safe(row.get("FileName")),
            }
        )

with open(MD_FILE, "w", encoding="utf-8") as f:
    f.write("# Email Correspondence\n\n")

    for r in rows:
        f.write(f"### {r['Sent']}\n\n")
        f.write(f"**From:** {r['From']}\n\n")
        f.write(f"**To:** {r['To']}\n\n")
        (f.write(f"**Subject**: {r['Subject']}\n\n"),)
        f.write(f"{r['Content']}\n\n")
        f.write(f"[PDF]({r['Path']}) ")
        f.write(
            f"[Source](https://www.justice.gov/epstein/files/{find_data_set(r['FileName'])}/{r['FileName']})\n\n"
        )
        f.write("---\n\n")

print(f"Wrote {len(rows)} messages to {MD_FILE}")
