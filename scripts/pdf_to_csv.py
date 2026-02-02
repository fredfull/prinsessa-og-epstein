#!/bin/python3

from logging import WARN, log
import pdfplumber
import re
import csv
from pathlib import Path
import os
from dateutil import parser
from datetime import timezone
import json
from timezone_info import whois_timezone_info
from bs4 import BeautifulSoup

PDF_DIR = os.environ["PDF_DIR"]
CSV_FILE = os.environ["CSV_FILE"]
STATS_FILE = os.environ["STATS_FILE"]


def clean_text(text):
    # Remove soft line breaks, encoding artifacts
    text = text.replace("=br>", "\n")
    text = re.sub(r"=\d{2,3}", "", text)
    text = text.replace("=8E", "")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\r\n", "\n", text)
    return text.strip()


def normalize_date(date_str):
    # Create a new timestamp using a dict with offset information:
    # example: November 26, 2012 5:05:31 PM EST -> 2012-11-26 17:05:31-05:00
    try:
        timestamp = parser.parse(date_str, tzinfos=whois_timezone_info, fuzzy=True)
    # if parsing fails, we try to clean up the date string by removing white
    # spaces and try again
    except ValueError:
        date_str = re.sub(r"\s*:\s*", ":", date_str)
        try:
            timestamp = parser.parse(date_str, tzinfos=whois_timezone_info, fuzzy=True)
        except ValueError:
            log(WARN, f"Could not parse date string ${date_str}")
            return

    # Convert to UTC. Alphabetical sort = chronological sort now
    timestamp_utc = timestamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    return timestamp_utc


def remove_html_keep_urls(text):
    # Parse the HTML content
    soup = BeautifulSoup(text, "html.parser")

    # Find all anchor tags (links)
    for a_tag in soup.find_all("a"):
        # Get the URL from the 'href' attribute
        url = a_tag.get("href")
        if url:
            # Replace the anchor tag with its text content followed by the URL
            new_text = f"{a_tag.get_text(strip=True)} [{url}]"
            a_tag.replace_with(new_text)

    # After processing links, get all the remaining text, which strips all other tags
    clean_text = soup.get_text(separator=" ", strip=True)

    return clean_text


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
            headers["From"] = (
                clean_text(line[5:].strip().strip('"'))
                .replace(">", "")
                .replace("<", "")
            ) or "N/A"
            continue

        # If colon is missing:
        elif line.lower().startswith("from") and not headers["From"]:
            headers["From"] = (
                clean_text(line[4:].strip().strip('"'))
                .replace(">", "")
                .replace("<", "")
            ) or "N/A"
            continue

        # Capture To
        if line.lower().startswith("to:") and not headers["To"]:
            headers["To"] = (
                clean_text(line[3:].strip().strip('"'))
                .replace(">", "")
                .replace("<", "")
            ) or "N/A"
            continue

        elif line.lower().startswith("to") and not headers["To"]:
            headers["To"] = (
                clean_text(line[2:].strip().strip('"'))
                .replace(">", "")
                .replace("<", "")
            ) or "N/A"
            continue

        # Capture Sent / Date
        raw_date = ""

        if (
            line.lower().startswith("sent:") or line.lower().startswith("date:")
        ) and not headers["Sent"]:
            raw_date = (
                clean_text((line[5:]).strip().strip('"'))
                .replace(">", "")
                .replace("<", "")
            )
        elif (
            line.lower().startswith("sent") or line.lower().startswith("date")
        ) and not headers["Sent"]:
            raw_date = (
                clean_text((line[4:]).strip().strip('"'))
                .replace(">", "")
                .replace("<", "")
            )
        if raw_date:
            utc_date = normalize_date(raw_date)
            headers["Sent"] = utc_date or raw_date or "N/A"
            continue

        # Capture Subject

        if (line.lower().startswith("subject:")) and not headers["Subject"]:
            line = (
                clean_text((line[8:]).strip().strip('"'))
                .replace(">", "")
                .replace("<", "")
            ) or "N/A"
            headers["Subject"] = line
            continue

        elif (line.lower().startswith("subject")) and not headers["Subject"]:
            line = (
                clean_text((line[7:]).strip().strip('"'))
                .replace(">", "")
                .replace("<", "")
            ) or "N/A"
            headers["Subject"] = line
            continue

        # If all header fields are found, the rest is content baby
        if headers["From"] and headers["To"] and headers["Sent"]:
            headers["Content"] += "\n\n" + clean_text(line)
            continue

    # Return None if From or To or Sent is missing
    if not headers["Sent"]:
        return None
    return headers


# Process PDFs
emails = []
total_emails = 0
sorted_emails = []
failed = []


def remove_trailing_text(full_email):
    # epstein has a custom signature/disclaimer we remove for readability
    disclaimer_index = full_email.lower().find("the information contained in this")
    if disclaimer_index != -1:
        full_email = full_email[:disclaimer_index]
        # The disclaimer sometimes begins with please note, so remove this as well.
        please_note_index = full_email.lower().find("please note")
        if please_note_index != -1:
            full_email = full_email[:please_note_index]

    # Remove after and including "Sent from my IPhone/IPad/Windows Phone"
    sent_from_index = full_email.lower().find("sent from my ")
    if sent_from_index != -1:
        full_email = full_email[:sent_from_index]

    # Remove after and including "Sent fra min Iphone/IPad/Windows Phone"
    sent_from_index = full_email.lower().find("sendt fra min ")
    if sent_from_index != -1:
        full_email = full_email[:sent_from_index]

    # This is a list of regex patterns we want to find and then
    # remove everything including and after the firs groups match
    reply_patterns = []

    # Start of reply-section of mails sent in norwegian:
    reply_patterns.append(r"Den.*?kl\..*?skrev")

    # Start of reply-section of mails in english
    reply_patterns.append(r"\bOn\s+.*?\bwrote:?\b")

    for p in reply_patterns:
        match = re.search(p, full_email, re.IGNORECASE)
        if match:
            full_email = full_email[: match.span(0)[0]]

    # Remove all those stars in epsteins signature
    full_email = full_email.replace("*", "")

    # Finally remove html as markdown supports some html:
    full_email = remove_html_keep_urls(full_email)

    return full_email


for pdf_file in Path(PDF_DIR).rglob("*.pdf"):
    with pdfplumber.open(pdf_file) as pdf:
        total_emails += 1

        ## I assume that the first mail message exists within the first two pages of the pdf
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages[:2])
        email = parse_first_email(full_text)

        if not email:
            failed.append(f"{pdf_file}")
            print(f"Failed to parse {pdf_file}")
            continue

        # Add path to be used in md
        email["Path"] = pdf_file
        email["FileName"] = os.path.basename(pdf_file)

        if email["Content"]:
            email["Content"] = remove_trailing_text(email["Content"])

            # For transparancy, add a disclaimer that there are removed pages here:
            if len(pdf.pages) > 2:
                email["Content"] += (
                    "\n\n ** Pages have been removed, see source for all pages **"
                )

        print(f"Successfully parsed {pdf_file} ")
        emails.append(email)

    ## Sort newest first:
    sorted_emails = sorted(emails, key=lambda email: email["Sent"], reverse=True)

# Save CSV
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["Path", "FileName", "From", "To", "Sent", "Subject", "Content"],
        quoting=csv.QUOTE_ALL,
    )
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
