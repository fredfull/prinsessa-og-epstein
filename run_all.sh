export PDF_DIR="./pdf/"
export CSV_FILE=./csv/messages.csv
export STATS_FILE=./stats.json

## Purge csv folder
rm -rf ./csv/*

./scripts/pdf_to_csv.py
./scripts/split_csv.py

# Purge md folder
rm -rf ./md/*

for path in ./csv/*; do
  if [ -f "$path" ]; then
    filename="${path##*/}"
    filename="${filename%.*}"
    # Create new folder per csv
    export CSV_FILE="$path"
    mkdir "./md/$filename"
    export MD_FILE="./md/$filename/README.md"
    ./scripts/csv_to_md.py
  fi
done
