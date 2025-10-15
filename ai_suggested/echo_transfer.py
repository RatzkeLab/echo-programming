#!/usr/bin/env python3
"""
Echo Transfer CSV Generator

This script generates CSV files for Echo liquid handling systems to transfer
barcoded PCR primers to a 384-well plate.

Echo CSV format typically requires:
- Source Well
- Destination Well
- Transfer Volume (nL)
"""

import csv
import argparse
from typing import List, Dict, Tuple


def well_to_row_col(well: str) -> Tuple[int, int]:
    """
    Convert well notation (e.g., 'A1') to row and column indices.
    
    Args:
        well: Well notation like 'A1', 'B12', 'P24'
    
    Returns:
        Tuple of (row_index, col_index) where row 'A' = 0, col '1' = 0
    """
    row = ord(well[0].upper()) - ord('A')
    col = int(well[1:]) - 1
    return row, col


def row_col_to_well(row: int, col: int, plate_format: int = 384) -> str:
    """
    Convert row and column indices to well notation.
    
    Args:
        row: Row index (0-based)
        col: Column index (0-based)
        plate_format: Plate format (96 or 384)
    
    Returns:
        Well notation like 'A1'
    """
    return f"{chr(ord('A') + row)}{col + 1}"


def generate_384_well_positions() -> List[str]:
    """
    Generate all well positions for a 384-well plate.
    384-well plate: 16 rows (A-P) x 24 columns (1-24)
    
    Returns:
        List of well positions in order
    """
    wells = []
    for row in range(16):  # A-P
        for col in range(24):  # 1-24
            wells.append(row_col_to_well(row, col))
    return wells


def generate_96_well_positions() -> List[str]:
    """
    Generate all well positions for a 96-well plate.
    96-well plate: 8 rows (A-H) x 12 columns (1-12)
    
    Returns:
        List of well positions in order
    """
    wells = []
    for row in range(8):  # A-H
        for col in range(12):  # 1-12
            wells.append(row_col_to_well(row, col, 96))
    return wells


def generate_echo_csv(
    source_wells: List[str],
    destination_wells: List[str],
    transfer_volume_nl: float,
    output_file: str,
    source_plate_name: str = "Source[1]",
    dest_plate_name: str = "Destination[1]"
) -> None:
    """
    Generate an Echo transfer CSV file.
    
    Args:
        source_wells: List of source well positions
        destination_wells: List of destination well positions
        transfer_volume_nl: Transfer volume in nanoliters
        output_file: Output CSV filename
        source_plate_name: Name of source plate
        dest_plate_name: Name of destination plate
    """
    if len(source_wells) != len(destination_wells):
        raise ValueError("Source and destination well lists must be same length")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        # Echo CSV header
        writer.writerow(['Source Well', 'Destination Well', 'Transfer Volume'])
        
        for src, dst in zip(source_wells, destination_wells):
            writer.writerow([src, dst, transfer_volume_nl])
    
    print(f"Generated Echo CSV: {output_file}")
    print(f"  Transfers: {len(source_wells)}")
    print(f"  Volume: {transfer_volume_nl} nL per transfer")


def generate_primer_transfer_csv(
    num_primers: int,
    source_plate_format: int = 96,
    dest_plate_format: int = 384,
    transfer_volume_nl: float = 100.0,
    output_file: str = "echo_primer_transfer.csv"
) -> None:
    """
    Generate an Echo CSV for transferring barcoded primers to a full plate.
    
    Args:
        num_primers: Number of primers to transfer
        source_plate_format: Source plate format (96 or 384)
        dest_plate_format: Destination plate format (96 or 384)
        transfer_volume_nl: Transfer volume in nanoliters
        output_file: Output CSV filename
    """
    # Generate all available wells for each plate format
    if source_plate_format == 96:
        all_source_wells = generate_96_well_positions()
    else:
        all_source_wells = generate_384_well_positions()
    
    if dest_plate_format == 96:
        all_dest_wells = generate_96_well_positions()
    else:
        all_dest_wells = generate_384_well_positions()
    
    # Validate that we have enough wells
    max_source = len(all_source_wells)
    max_dest = len(all_dest_wells)
    
    if num_primers > max_source:
        raise ValueError(
            f"Cannot transfer {num_primers} primers from {source_plate_format}-well "
            f"source plate (max {max_source} wells)"
        )
    
    if num_primers > max_dest:
        raise ValueError(
            f"Cannot transfer {num_primers} primers to {dest_plate_format}-well "
            f"destination plate (max {max_dest} wells)"
        )
    
    # Get the required number of wells
    source_wells = all_source_wells[:num_primers]
    dest_wells = all_dest_wells[:num_primers]
    
    generate_echo_csv(source_wells, dest_wells, transfer_volume_nl, output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Echo transfer CSV for barcoded primers'
    )
    parser.add_argument(
        '--num-primers', '-n',
        type=int,
        default=384,
        help='Number of primers to transfer (default: 384)'
    )
    parser.add_argument(
        '--source-format', '-s',
        type=int,
        choices=[96, 384],
        default=96,
        help='Source plate format (default: 96)'
    )
    parser.add_argument(
        '--dest-format', '-d',
        type=int,
        choices=[96, 384],
        default=384,
        help='Destination plate format (default: 384)'
    )
    parser.add_argument(
        '--volume', '-v',
        type=float,
        default=100.0,
        help='Transfer volume in nL (default: 100.0)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='echo_primer_transfer.csv',
        help='Output CSV filename (default: echo_primer_transfer.csv)'
    )
    
    args = parser.parse_args()
    
    generate_primer_transfer_csv(
        num_primers=args.num_primers,
        source_plate_format=args.source_format,
        dest_plate_format=args.dest_format,
        transfer_volume_nl=args.volume,
        output_file=args.output
    )


if __name__ == '__main__':
    main()
