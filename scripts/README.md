# Scripts

- `pdf_to_csv.py` takes a folder with pdfs and creates a csv with the first message of each pdf. It is sorted by oldest message first. Expects env variables PDF_DIR (directory of pdf files to use) and CSV_FILE (output csv file path)


Example output:
```
"File","From","To","Sent","Subject","Content"
"kronprinsessen/EFTA00646552.pdf","H.K.H. Kronprinsessen","Jeffrey Epstein <jeevacation®gmail.com>","Mon, 10 Dec 2012 17:1 1 :03 +0000","Re:"," Called u today"
"kronprinsessen/EFTA01754699.pdf","H.K.H. Kronprinsessen","Jeffrey Epstein","2026-11-22T00:00:00+00:00","Re: Thank you"," Yes there are. Where are you?"
```

- `split_csv.py` takes a master csv /csv/messages.csv and splits it into multiple csvs based upon sender-receiver pairs.

- `csv_to_md.py` creates a markdown file `README.md` from the csv. Expects env variables CSV_FILE (input file) and MD_FILE (output file).

Run from project root:
`export PDF_DIR="./pdfs/" && export CSV_FILE=messages.csv && export MD_FILE=README.md && export STATS_FILE=stats.json && ./scripts/pdf_to_csv.py && ./scripts/csv_to_md.py`
