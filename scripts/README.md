# Scripts

There are two script here.

- `pdf_to_csv.py` takes a folder with pdfs and creates a csv with the first message of each pdf. It is sorted by oldest message first. 

Expects env variables 
- PDF_DIR (directory of pdf files to use)
- CSV_FILE (output csv file path)
- STATS_FILE (output stats for successfull and failed pdfs)

Example output:
```
"File","From","To","Sent","Subject","Content"
"kronprinsessen/EFTA00646552.pdf","H.K.H. Kronprinsessen","Jeffrey Epstein <jeevacation®gmail.com>","Mon, 10 Dec 2012 17:1 1 :03 +0000","Re:"," Called u today"
"kronprinsessen/EFTA01754699.pdf","H.K.H. Kronprinsessen","Jeffrey Epstein","2026-11-22T00:00:00+00:00","Re: Thank you"," Yes there are. Where are you?"
```

- `csv_to_md.py` creates a markdown file `README.md` from the csv. 

Expects env variables 
- CSV_FILE (input file)
- MD_FILE (output file).

Run from project root:

`export PDF_DIR="./pdf/" && export CSV_FILE=./csv/messages.csv && export MD_FILE=./md/README.md && export STATS_FILE=./stats.json && ./scripts/pdf_to_csv.py && ./scripts/csv_to_md.py`
