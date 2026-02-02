# Scripts

- `pdf_to_csv.py` takes a folder with pdfs and creates a csv with the first message of each pdf. It is sorted by oldest message first. Expects env variables 
PDF_DIR (directory of pdf files to use)
CSV_FILE (output csv file path)

- `split_csv.py` takes a master csv /csv/messages.csv and splits it into multiple csvs based upon sender-receiver pairs. expects env variables:
- CSV_FILE (input file path)

- `csv_to_md.py` creates a markdown file `README.md` from the csv. Expects env variables 
- CSV_FILE (input file path)
- MD_FILE (output file path).

Run from project root:
`export PDF_DIR="./pdf/" && export CSV_FILE=./csv/messages.csv && export MD_FILE=md/README.md && export STATS_FILE=stats.json && ./scripts/pdf_to_csv.py && ./scripts/csv_to_md.py`
