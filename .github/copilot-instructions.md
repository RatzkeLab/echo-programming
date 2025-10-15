# Echo Programming Assistant Instructions

This repository generates automation files for Echo liquid handling systems and downstream sequencing data processing in molecular biology workflows.

## Architecture Overview

**Core Workflow**: Jupyter notebooks generate Echo transfer CSVs for barcoded PCR primer distribution → Python scripts process barcode mappings → Output files for sequencing demultiplexing and visualization.

**Data Flow**:
1. Notebooks calculate primer well assignments and generate transfer volumes  
2. `echo_transfer.py` creates Echo-compatible CSVs for liquid handling robots
3. `generate_minimap_tsv.py` converts barcode mappings to minimap2 format for demultiplexing
4. `generate_heatmap_mapping.py` creates coordinate files for result visualization

## Critical Patterns

### Well Notation Standards
- Use format `A1`, `B12`, `P24` (letter+number, case-insensitive)  
- Helper functions: `well_to_row_col()` and `row_col_to_well()` in scripts
- Support both 96-well (A-H, 1-12) and 384-well (A-P, 1-24) formats

### Random Seed Convention
All notebooks use date-based seeds (`randseed = DDMMYY`) for reproducible primer assignments. This ensures identical outputs for the same date.

### File Naming Patterns
- Echo transfers: `helloPrimersRand{randseed}.csv` or `echo_primer_transfer.csv`
- Barcode outputs: `barcodes{randseed}.tsv`
- Always include seed/date in generated filenames for traceability

### DataFrame Structure Standards
**Transfer CSVs**: `Source Well`, `Destination Well`, `Volume` (in nL)
**Barcode CSVs**: `Well`, `Barcode_Name`, `Sequence`
**Minimap TSV**: Tab-separated `Barcode_Name\tSequence`

## Development Workflows

### Testing Scripts
```bash
# Test with example data
python echo_transfer.py -n 16 -s 96 -d 384 -v 100 -o test_transfer.csv
python generate_minimap_tsv.py example_barcodes.csv -o test.tsv
```

### Notebook Execution
Always run cells sequentially - later cells depend on variables from earlier ones. Google Colab compatibility maintained with drive mounting cells.

### Volume Constraints  
Echo systems typically use 25nL-2.5μL ranges. Default to 100nL unless specified otherwise. Source plate capacity limits primer count (96 max for 96-well source).

## Integration Points

**External Dependencies**:
- Excel files from `/content/drive/MyDrive/` (Google Colab paths)
- Plate specification files with `Well Position`, `Sequence Name`, `Sequence` columns
- Minimap2 compatibility for downstream demultiplexing

**Key Libraries**: numpy (well grid generation), pandas (data manipulation), string (well naming)

## Conventions

- Primer direction extraction: Use `.str.extract(r'([^\d])\d*$')` to get F/R from sequence names
- Sequence cleaning: Always `.str.replace(' ', '')` to remove whitespace  
- Index slicing: Barcode sequences typically trimmed with `.str.slice(15,39)`
- Duplicate checking: Track `covered_list` to prevent primer pair reuse

When modifying scripts, maintain Echo CSV format compatibility and preserve the random seed reproducibility for laboratory traceability.