#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import re
import os

CSV_FILE = os.environ["CSV_FILE"]
csv_dir = os.path.dirname(CSV_FILE)

df = pd.read_csv(CSV_FILE)

known_people = {
    "boris": "Boris Nikolic",
    "jeff": "Jeffrey Epstein",
    "kpm": "H.K.H. Kronprinsessen",
    "kronprinsessen": "H.K.H. Kronprinsessen",
    "casanova": "Gerry Casanova",
    "lesley": "Lesley Groff",
}


def is_known(name):
    for alias in known_people.keys():
        if alias in name:
            return alias
    return ""


for i, row in df.iterrows():
    if isinstance(row["From"], str) and isinstance(row["To"], str):
        sender = row["From"].replace('"', "")
        recipient = row["To"].replace('"', "")
        if is_known(sender.lower()) != "":
            df.loc[i, "From"] = known_people[is_known(sender.lower())]
        if is_known(recipient.lower()) != "":
            df.loc[i, "To"] = known_people[is_known(recipient.lower())]

df[["From", "To"]]


df.loc[0, "Sent"] = str(datetime(2012, 12, 10))
df["Sent"] = pd.to_datetime(df["Sent"], format="mixed", utc=True)
for i, row in df.iterrows():
    date = row["Sent"]
    if date.year == 2026 or date.year == 2002:  # Remove Outliers
        df.loc[i, "Sent"] = pd.Timestamp(
            "NaT"
        )  # These dates are wrongly parsed so set them to NaT
df["Sent"]

filler_words = [
    "sendt",
    "wrote",
    "h",
    "kl",
    "b",
    "c",
    "y",
    "de",
    "o",
    "u",
    "f",
    "june",
    "propertylist",
    "label",
    "z",
    "la",
    "sg",
    "j",
    "f",
    "t",
    "q",
    "g",
    "n",
    "encoding",
    "utf",
    "let",
    "doctype",
    "tue",
    ";",
    "d",
    "array",
    "dtd",
    "efta_r1_01",
    "apple",
    "date",
    "l",
    "en",
    "id",
    "string",
    "dy",
    "le",
    "x",
    "00pm",
    "w",
    "je",
    "re",
    "s",
    "ce",
    "m",
    "p",
    "e",
    "kl.",
    "oct",
    "okt",
    "cc",
    "version",
    "xml",
    "version",
    "des",
    "tue",
    "thu",
    "mon",
    "dict",
    "den",
    "dec",
    "plist",
    "wed",
    "sun",
    "fri",
    "sat",
    "pm",
    "jan",
    "<jeevacation@gmail.com>:",
    "<jccvacationagmail.com>",
    "<mailto:jeevacation@gmail.com»:",
    "<jeevacation@gmail.com",
    "feb",
    "mar",
    "apr",
    "key",
    "integer",
    "sep",
    "mai",
    "jun",
    "jul",
    "aug",
    "novdes",
    "skrev",
    "gmail",
    "mailto",
    "subject",
    "sent",
    "sendt",
    "jeevacation",
]


def filter_text(text, words):
    return " ".join(w for w in re.findall(r"\b\w+\b", text) if w.lower() not in words)


all_content = ""
for i, row in df.iterrows():
    mail_content = str(row["Content"])
    filtered = filter_text(mail_content, [w.lower() for w in filler_words])
    all_content += filtered


def all_correspondence(p1, p2):
    q = f"((From == '{p1}' and To == '{p2}') or (From == '{p2}' and To == '{p1}')) and Sent.notna()"
    return df.query(q)


kmp_jeff = all_correspondence("Jeffrey Epstein", "H.K.H. Kronprinsessen")
lg_jeff = all_correspondence("Jeffrey Epstein", "Lesley Groff")
bor_jeff = all_correspondence("Boris Nikolic", "Jeffrey Epstein")
bor_kmp = all_correspondence("Boris Nikolic", "H.K.H. Kronprinsessen")
lg_kmp = all_correspondence("Lesley Groff", "H.K.H. Kronprinsessen")

kmp_jeff.to_csv(f"{csv_dir}/mette_jeff.csv", index=False)
lg_jeff.to_csv(f"{csv_dir}/lesley_jeff.csv", index=False)
bor_jeff.to_csv(f"{csv_dir}/boris_jeff.csv", index=False)
bor_kmp.to_csv(f"{csv_dir}/boris_mette.csv", index=False)
lg_kmp.to_csv(f"{csv_dir}/lesley_mette.csv", index=False)
