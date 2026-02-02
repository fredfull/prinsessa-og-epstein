export PDF_DIR="./test/pdf/"
export CSV_FILE=./test/csv/messages.csv
export STATS_FILE=./test/stats.json

## Purge csv folder
rm -rf ./test/csv/*

./scripts/pdf_to_csv.py
./scripts/split_csv.py

# Purge md folder
rm -rf ./test/md/*

for path in ./test/csv/*; do
  if [ -f "$path" ]; then
    filename="${path##*/}"
    filename="${filename%.*}"
    echo filename
    # Create new folder per csv
    export CSV_FILE="$path"
    mkdir "./test/md/$filename"
    export MD_FILE="./test/md/$filename/README.md"
    ./scripts/csv_to_md.py
  fi
done
