#!/bin/python3

import pdfplumber
import re
import csv
from pathlib import Path
import os
from dateutil import parser 
from datetime import timezone
from datetime import date
import json

PDF_DIR = os.environ['PDF_DIR']
CSV_FILE = os.environ['CSV_FILE']
STATS_FILE= os.environ['STATS_FILE']

def clean_text(text):
    # Remove soft line breaks, encoding artifacts
    text = text.replace("=br>", "\n")
    text = re.sub(r"=\d{2,3}", "", text)
    text = text.replace("=8E", "")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\r\n", "\n", text)
    return text.strip()

def normalize_date(date_str):
    try:
        dt = parser.parse(date_str, fuzzy=True)
        # If timezone is missing, assume UTC
        # TODO: fix warning
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.isoformat()
    except Exception:
        return None

def parse_first_email(text):
    """
    Extract From, To, Sent, Subject, and mail Content from the PDF text,
    regardless of header order. Returns the first occurrence of each header.
    """
    headers = {"From": "", "To": "", "Sent": "", "Subject": "", "Content": ""}
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Capture From
        if line.lower().startswith("from:") and not headers["From"]:
            headers["From"] = clean_text(line[5:].strip().strip('"'))
            continue

        # Capture To
        if line.lower().startswith("to:") and not headers["To"]:
            headers["To"] = clean_text(line[3:].strip().strip('"'))
            continue

        # Capture Sent / Date
        if (line.lower().startswith("sent:") or line.lower().startswith("date:")) and not headers["Sent"]:
            raw_date = clean_text(line.split(":", 1)[1].strip().strip('"'))
            utc_date = normalize_date(raw_date)
            headers["Sent"] = utc_date or raw_date
            continue

        # Capture Subject
        if line.lower().startswith("subject:") and not headers["Subject"]:
            headers["Subject"] = clean_text(line.split(":", 1)[1].strip().strip('"'))
            continue

        # If the princess has sent the mail and  we reach the norwegian line that is added for replies of the mail, we break:
        if headers["From"].lower().find("kronprinsessen") != -1 and line.lower().find("den") != -1 and line.lower().find("skrev") != -1: 
            break
        
        # If the epstein has sent the mail and we reach his disclaimer, we break:
        if headers["From"].lower().find("epstein") != -1 and (line.lower().find("*****************************") != -1 or line.lower().find("the information contained in this communication is") != -1):
            break

        # If all header fields are found, the rest is content baby
        if headers["From"] and headers["To"] and headers["Sent"]:
            headers["Content"] += " \n" + clean_text(line)
            continue

    # Return None if From or To or Sent is missing
    if not headers["From"] or not headers["To"] or not headers["Sent"]:
        return None
    return headers

# Process PDFs
emails = []
total_emails = 0
failed = []

for pdf_file in Path(PDF_DIR).rglob("*.pdf"):
    with pdfplumber.open(pdf_file) as pdf:

        total_emails += 1

        ## I assume that the first mail message exists within the first two pages of the pdf
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages[:2])

        # For transparancy, add a disclaimer that there are removed pages here:
        if len(pdf.pages) > 2:
            full_text += "\n ** Pages has been removed, see source for all pages **"

        email = parse_first_email(full_text)

        if not email:
            failed.append(f"{pdf_file}")
            print(f"Failed to parse {pdf_file}");
        else:
            #Add path to be used in md
            email["Path"] = pdf_file
            email["FileName"] = os.path.basename(pdf_file)

            # ungodly section for trying to remove in-line mail replies and signatures:
            if email["Content"]:
                # Remove all those stars in epsteins signature 
                email["Content"].replace("*", "")
                # Lets assume that kronprinsessen is the only norwegian her
                if email["From"].lower().find("kronprinsessen") != -1 or email["From"].lower().find("h.k.h.") != -1:
                    # Find the start of the "reply-section" of the mail
                    reply_regex = r"Den.*?kl\..*?skrev"

                # epstein is often the other one, he has a custom signature/disclaimer
                else:
                    disclaimer_index = email["Content"].lower().find("the information contained in this")
                    if disclaimer_index != -1:
                        email["Content"] = email["Content"][:disclaimer_index]

                        # The disclaimer sometimes begins with please note, so remove this as well.
                        please_note_index = email["Content"].lower().find("please note")
                        if please_note_index != -1:
                            email["Content"] = email["Content"][:please_note_index]

                    reply_regex = r"\bOn\s+.*?\bwrote:?\b"

                if reply_regex:
                    match = re.search(reply_regex, email["Content"], re.IGNORECASE)
                    if match:
                        email["Content"] = email["Content"][:match.span(0)[0]]
                
                # Remove after and including "Sent from my IPhone/IPad"
                iphone_index= email["Content"].lower().find("sent from my i")
                if iphone_index!= -1:
                    email["Content"] = email["Content"][:iphone_index]

            print(f"Successfully parsed {pdf_file} ");
            emails.append(email)

    ## Sort newest first:
    sorted_emails = sorted(emails, key=lambda email: email["Sent"], reverse=True);

# Save CSV
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Path","FileName","From", "To", "Sent", "Subject", "Content"], quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for email in sorted_emails:
        writer.writerow(email)

stats = {
    "pdf": {
        "successfull": len(sorted_emails),
        "total": total_emails,
        "failed": failed,
    }
}

with open(STATS_FILE, "w") as f:
    json.dump(stats, f, indent=4)


print(f"Parsed {len(sorted_emails)} emails into {CSV_FILE}")
