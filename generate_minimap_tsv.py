#!/usr/bin/env python3
"""
Minimap Demultiplexing TSV Generator

This script takes a CSV listing barcode positions and sequences in a destination
plate and creates a TSV file compatible with minimap2 for demultiplexing.

Input CSV format:
    Well,Barcode_Name,Sequence
    A1,BC01,ACGTACGTACGT
    A2,BC02,TGCATGCATGCA
    ...

Output TSV format (minimap2-friendly):
    Barcode_Name\tSequence
    BC01\tACGTACGTACGT
    BC02\tTGCATGCATGCA
    ...
"""

import csv
import argparse
from typing import Dict, List, Tuple


def parse_barcode_csv(input_file: str) -> List[Tuple[str, str, str]]:
    """
    Parse the input CSV containing barcode positions and sequences.
    
    Args:
        input_file: Path to input CSV file
    
    Returns:
        List of tuples (well, barcode_name, sequence)
    """
    barcodes = []
    
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        
        # Try to detect column names (case-insensitive)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row")
        
        # Normalize column names
        fieldnames_lower = [fn.lower() if fn else '' for fn in reader.fieldnames]
        
        # Find the relevant columns
        well_col = None
        barcode_col = None
        sequence_col = None
        
        for i, fn in enumerate(fieldnames_lower):
            if 'well' in fn:
                well_col = reader.fieldnames[i]
            elif 'barcode' in fn or 'name' in fn or 'id' in fn:
                barcode_col = reader.fieldnames[i]
            elif 'sequence' in fn or 'seq' in fn:
                sequence_col = reader.fieldnames[i]
        
        if not all([well_col, barcode_col, sequence_col]):
            raise ValueError(
                f"Could not find required columns. Found: {reader.fieldnames}. "
                "Expected columns containing 'well', 'barcode'/'name', and 'sequence'"
            )
        
        for row in reader:
            well = row[well_col].strip()
            barcode_name = row[barcode_col].strip()
            sequence = row[sequence_col].strip().upper()
            
            if well and barcode_name and sequence:
                barcodes.append((well, barcode_name, sequence))
    
    return barcodes


def generate_minimap_tsv(
    input_csv: str,
    output_tsv: str,
    include_well: bool = False
) -> None:
    """
    Generate a minimap2-compatible TSV file from barcode CSV.
    
    Args:
        input_csv: Input CSV file with barcode positions and sequences
        output_tsv: Output TSV filename
        include_well: If True, include well position in barcode name
    """
    barcodes = parse_barcode_csv(input_csv)
    
    with open(output_tsv, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        
        for well, barcode_name, sequence in barcodes:
            if include_well:
                name = f"{barcode_name}_{well}"
            else:
                name = barcode_name
            
            writer.writerow([name, sequence])
    
    print(f"Generated minimap TSV: {output_tsv}")
    print(f"  Barcodes: {len(barcodes)}")


def generate_fasta(
    input_csv: str,
    output_fasta: str,
    include_well: bool = False
) -> None:
    """
    Generate a FASTA file from barcode CSV (alternative format).
    
    Args:
        input_csv: Input CSV file with barcode positions and sequences
        output_fasta: Output FASTA filename
        include_well: If True, include well position in barcode name
    """
    barcodes = parse_barcode_csv(input_csv)
    
    with open(output_fasta, 'w') as f:
        for well, barcode_name, sequence in barcodes:
            if include_well:
                name = f"{barcode_name}_{well}"
            else:
                name = barcode_name
            
            f.write(f">{name}\n{sequence}\n")
    
    print(f"Generated FASTA file: {output_fasta}")
    print(f"  Barcodes: {len(barcodes)}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate minimap2-compatible TSV from barcode CSV'
    )
    parser.add_argument(
        'input_csv',
        help='Input CSV file with columns: Well, Barcode_Name, Sequence'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='barcodes_minimap.tsv',
        help='Output TSV filename (default: barcodes_minimap.tsv)'
    )
    parser.add_argument(
        '--include-well', '-w',
        action='store_true',
        help='Include well position in barcode name (e.g., BC01_A1)'
    )
    parser.add_argument(
        '--fasta', '-f',
        type=str,
        help='Also generate a FASTA file with the given filename'
    )
    
    args = parser.parse_args()
    
    # Generate TSV
    generate_minimap_tsv(args.input_csv, args.output, args.include_well)
    
    # Optionally generate FASTA
    if args.fasta:
        generate_fasta(args.input_csv, args.fasta, args.include_well)


if __name__ == '__main__':
    main()
