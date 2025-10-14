# echo-programming

Helper Python files and notebooks for generating Echo programming CSVs. Also contains scripts for producing CSVs for downstream data processing.

## Overview

This repository provides tools for:
1. Generating Echo liquid handler transfer CSVs for barcoded PCR primers
2. Creating minimap2-compatible TSV files for demultiplexing
3. Generating heatmap mappings for visualization of demultiplexing results

## Installation

No installation required. Clone the repository and run the Python scripts directly:

```bash
git clone https://github.com/RatzkeLab/echo-programming.git
cd echo-programming
```

Requirements: Python 3.6+

## Scripts

### 1. `echo_transfer.py` - Generate Echo Transfer CSVs

Generate CSV files for Echo liquid handling systems to transfer barcoded PCR primers to well plates.

**Usage:**
```bash
# Generate a 96-well plate transfer from 96-well source
python echo_transfer.py --num-primers 96 --source-format 96 --dest-format 384 --volume 100 --output primer_transfer.csv

# Generate a full 384-well plate transfer (requires 384-well source)
python echo_transfer.py --num-primers 384 --source-format 384 --dest-format 384 --volume 100 --output primer_transfer.csv

# Transfer 96 primers to 96-well destination
python echo_transfer.py -n 96 -s 96 -d 96 -v 50 -o transfer_96.csv
```

**Note:** The number of primers cannot exceed the capacity of the source plate (96 for 96-well, 384 for 384-well).

**Arguments:**
- `--num-primers, -n`: Number of primers to transfer (default: 384)
- `--source-format, -s`: Source plate format, 96 or 384 (default: 96)
- `--dest-format, -d`: Destination plate format, 96 or 384 (default: 384)
- `--volume, -v`: Transfer volume in nanoliters (default: 100.0)
- `--output, -o`: Output CSV filename (default: echo_primer_transfer.csv)

**Output format:**
```csv
Source Well,Destination Well,Transfer Volume
A1,A1,100.0
A2,A2,100.0
...
```

### 2. `generate_minimap_tsv.py` - Create Minimap Demultiplexing TSV

Convert a CSV with barcode positions and sequences to a minimap2-compatible TSV for demultiplexing.

**Usage:**
```bash
# Generate TSV from barcode CSV
python generate_minimap_tsv.py example_barcodes.csv --output barcodes.tsv

# Include well positions in barcode names
python generate_minimap_tsv.py example_barcodes.csv -o barcodes.tsv --include-well

# Also generate FASTA format
python generate_minimap_tsv.py example_barcodes.csv -o barcodes.tsv --fasta barcodes.fasta
```

**Input CSV format:**
```csv
Well,Barcode_Name,Sequence
A1,BC01,ACGTACGTACGT
A2,BC02,TGCATGCATGCA
...
```

**Arguments:**
- `input_csv`: Input CSV file with Well, Barcode_Name, and Sequence columns
- `--output, -o`: Output TSV filename (default: barcodes_minimap.tsv)
- `--include-well, -w`: Include well position in barcode name (e.g., BC01_A1)
- `--fasta, -f`: Also generate a FASTA file

**Output TSV format:**
```tsv
BC01	ACGTACGTACGT
BC02	TGCATGCATGCA
...
```

### 3. `generate_heatmap_mapping.py` - Create Heatmap Mapping

Generate coordinate mappings for plotting demultiplexing results on heatmaps.

**Usage:**
```bash
# Generate coordinate mapping
python generate_heatmap_mapping.py example_barcodes.csv --output heatmap_coords.csv

# Also generate plate layout matrix for direct heatmap plotting
python generate_heatmap_mapping.py example_barcodes.csv -o coords.csv --matrix plate_layout.csv --plate-format 384
```

**Arguments:**
- `input_csv`: Input CSV file with Well and Barcode_Name columns
- `--output, -o`: Output CSV filename for coordinate mapping (default: heatmap_mapping.csv)
- `--matrix, -m`: Generate plate layout matrix CSV
- `--plate-format, -p`: Plate format for matrix, 96 or 384 (default: 384)

**Output coordinate mapping format:**
```csv
Barcode_Name,Well,Row,Column,Row_Index,Column_Index
BC01,A1,A,1,0,0
BC02,A2,A,2,0,1
...
```

**Output plate matrix format (if --matrix specified):**
```csv
Row,1,2,3,4,...
A,BC01,BC02,BC03,BC04,...
B,BC13,BC14,BC15,BC16,...
...
```

## Example Workflow

1. **Generate Echo transfer CSV:**
```bash
# For 96 primers from 96-well source
python echo_transfer.py -n 96 -s 96 -d 384 -v 100 -o primer_transfer.csv

# For full 384-well plate (requires 384-well source)
python echo_transfer.py -n 384 -s 384 -d 384 -v 100 -o primer_transfer.csv
```

2. **Prepare barcode CSV** with well positions and sequences (see `example_barcodes.csv`)

3. **Generate minimap TSV for demultiplexing:**
```bash
python generate_minimap_tsv.py example_barcodes.csv -o barcodes.tsv
```

4. **Generate heatmap mapping:**
```bash
python generate_heatmap_mapping.py example_barcodes.csv -o heatmap_coords.csv --matrix plate_layout.csv
```

5. **Use the outputs:**
   - Load `primer_transfer.csv` into Echo software for liquid handling
   - Use `barcodes.tsv` with minimap2 for demultiplexing sequencing reads
   - Use `heatmap_coords.csv` or `plate_layout.csv` for visualizing results

## Example Data

The repository includes `example_barcodes.csv` with sample barcode sequences for testing.

## License

MIT License - see LICENSE file for details
