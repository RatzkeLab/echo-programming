#!/usr/bin/env python3
"""
Heatmap Mapping Generator

This script creates a mapping file for plotting demultiplexing results on a heatmap.
It takes barcode positions and creates a coordinate mapping suitable for visualization.

Input CSV format:
    Well,Barcode_Name,Sequence
    A1,BC01,ACGTACGTACGT
    A2,BC02,TGCATGCATGCA
    ...

Output CSV format for heatmap:
    Barcode_Name,Well,Row,Column,Row_Index,Column_Index
    BC01,A1,A,1,0,0
    BC02,A2,A,2,0,1
    ...
"""

import csv
import argparse
from typing import List, Tuple, Dict
import sys


def well_to_row_col(well: str) -> Tuple[str, int, int, int]:
    """
    Convert well notation to row, column, and indices.
    
    Args:
        well: Well notation like 'A1', 'B12', 'P24'
    
    Returns:
        Tuple of (row_letter, col_number, row_index, col_index)
    """
    row_letter = well[0].upper()
    col_number = int(well[1:])
    row_index = ord(row_letter) - ord('A')
    col_index = col_number - 1
    return row_letter, col_number, row_index, col_index


def parse_barcode_csv(input_file: str) -> List[Tuple[str, str]]:
    """
    Parse the input CSV containing barcode positions.
    
    Args:
        input_file: Path to input CSV file
    
    Returns:
        List of tuples (well, barcode_name)
    """
    barcodes = []
    
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row")
        
        # Normalize column names
        fieldnames_lower = [fn.lower() if fn else '' for fn in reader.fieldnames]
        
        # Find the relevant columns
        well_col = None
        barcode_col = None
        
        for i, fn in enumerate(fieldnames_lower):
            if 'well' in fn:
                well_col = reader.fieldnames[i]
            elif 'barcode' in fn or 'name' in fn or 'id' in fn:
                barcode_col = reader.fieldnames[i]
        
        if not all([well_col, barcode_col]):
            raise ValueError(
                f"Could not find required columns. Found: {reader.fieldnames}. "
                "Expected columns containing 'well' and 'barcode'/'name'"
            )
        
        for row in reader:
            well = row[well_col].strip()
            barcode_name = row[barcode_col].strip()
            
            if well and barcode_name:
                barcodes.append((well, barcode_name))
    
    return barcodes


def generate_heatmap_mapping(
    input_csv: str,
    output_csv: str
) -> None:
    """
    Generate a heatmap mapping CSV from barcode positions.
    
    Args:
        input_csv: Input CSV file with barcode positions
        output_csv: Output CSV filename for heatmap mapping
    """
    barcodes = parse_barcode_csv(input_csv)
    
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Barcode_Name', 'Well', 'Row', 'Column', 'Row_Index', 'Column_Index'])
        
        for well, barcode_name in barcodes:
            row_letter, col_number, row_index, col_index = well_to_row_col(well)
            writer.writerow([
                barcode_name,
                well,
                row_letter,
                col_number,
                row_index,
                col_index
            ])
    
    print(f"Generated heatmap mapping: {output_csv}")
    print(f"  Barcodes: {len(barcodes)}")


def generate_plate_layout_matrix(
    input_csv: str,
    output_csv: str,
    plate_format: int = 384
) -> None:
    """
    Generate a plate layout matrix suitable for direct heatmap plotting.
    
    Args:
        input_csv: Input CSV file with barcode positions
        output_csv: Output CSV filename for plate matrix
        plate_format: Plate format (96 or 384)
    """
    barcodes = parse_barcode_csv(input_csv)
    
    # Determine plate dimensions
    if plate_format == 96:
        num_rows, num_cols = 8, 12
    elif plate_format == 384:
        num_rows, num_cols = 16, 24
    else:
        raise ValueError(f"Unsupported plate format: {plate_format}")
    
    # Create empty matrix
    matrix = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    
    # Fill matrix with barcode names
    for well, barcode_name in barcodes:
        row_letter, col_number, row_index, col_index = well_to_row_col(well)
        
        if row_index < num_rows and col_index < num_cols:
            matrix[row_index][col_index] = barcode_name
    
    # Write matrix to CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header row with column numbers
        header = ['Row'] + [str(i+1) for i in range(num_cols)]
        writer.writerow(header)
        
        # Data rows
        for i, row in enumerate(matrix):
            row_letter = chr(ord('A') + i)
            writer.writerow([row_letter] + row)
    
    print(f"Generated plate layout matrix: {output_csv}")
    print(f"  Format: {plate_format}-well plate ({num_rows}x{num_cols})")


def main():
    parser = argparse.ArgumentParser(
        description='Generate heatmap mapping from barcode positions'
    )
    parser.add_argument(
        'input_csv',
        help='Input CSV file with columns: Well, Barcode_Name, ...'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='heatmap_mapping.csv',
        help='Output CSV filename for coordinate mapping (default: heatmap_mapping.csv)'
    )
    parser.add_argument(
        '--matrix', '-m',
        type=str,
        help='Generate plate layout matrix CSV with the given filename'
    )
    parser.add_argument(
        '--plate-format', '-p',
        type=int,
        choices=[96, 384],
        default=384,
        help='Plate format for matrix generation (default: 384)'
    )
    
    args = parser.parse_args()
    
    # Generate coordinate mapping
    generate_heatmap_mapping(args.input_csv, args.output)
    
    # Optionally generate plate matrix
    if args.matrix:
        generate_plate_layout_matrix(
            args.input_csv,
            args.matrix,
            args.plate_format
        )


if __name__ == '__main__':
    main()
