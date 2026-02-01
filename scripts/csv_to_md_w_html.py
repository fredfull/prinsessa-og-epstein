#!/bin/python3
import csv
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
        f.write("<table>\n")

        f.write("<tr>\n")
        f.write(f'<td align="left"> From: {r["From"]} </td>\n')
        f.write(f'<td align="right"> To: {r["To"]} </td>\n')
        f.write("</tr>\n")

        f.write("<tr>\n")
        f.write(f'<td colspan="2">Subject: {r["Subject"]}</td>\n')
        f.write("</tr>\n")

        f.write("<tr>\n")
        f.write(f'<td colspan="2">{r["Content"]}</td>\n')
        f.write("</tr>\n")

        f.write("<tr>\n")
        f.write(f'<td align="left"><a href=../{r["Path"]}> PDF </a></td>\n')
        f.write(
            f'<td align="left"><a href=https://www.justice.gov/epstein/files/{find_data_set(r["FileName"])}/{r["FileName"]}> Source</a></td>\n'
        )
        f.write("</tr>\n")
        f.write("</table>\n\n")

print(f"Wrote {len(rows)} messages to {MD_FILE}")
