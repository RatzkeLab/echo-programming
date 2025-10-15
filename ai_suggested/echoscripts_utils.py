"""Utilities for Echo primer transfer generation and barcode mapping.

This module extracts reusable logic from the notebooks: well grid creation,
primer selection, and transfer CSV generation. It aims to preserve the original
behaviour while making it easier to call from notebooks or scripts.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
import string
from typing import List, Tuple


def wells384_list() -> List[str]:
    """Return a flat list of 384-well names A1..P24 in row-major order."""
    return [r + str(c) for r in string.ascii_uppercase[:16] for c in range(1, 25)]


def wells384_grid() -> np.ndarray:
    """Return a 16x24 numpy array of well names."""
    wells = wells384_list()
    return np.reshape(np.array(wells), (16, 24))


def split_primers_from_grid(grid: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return two 1-D arrays: forward and reverse primer well names.

    The original notebooks used even/odd slicing across rows and cols to
    construct forward/reverse sets. We reproduce that behaviour here.
    """
    fprimers_full = grid[::2, ::2].flatten()
    rprimers_full = grid[1::2, 1::2].flatten()
    return fprimers_full, rprimers_full


@dataclass
class EchoTransferGenerator:
    randseed: int
    grid: np.ndarray = None
    fprimers_full: np.ndarray = None
    rprimers_full: np.ndarray = None

    def __post_init__(self):
        if self.grid is None:
            self.grid = wells384_grid()
        if self.fprimers_full is None or self.rprimers_full is None:
            self.fprimers_full, self.rprimers_full = split_primers_from_grid(self.grid)

    def sample_primers(self, offset: int = 12) -> Tuple[np.ndarray, np.ndarray]:
        """Return the active forward and reverse primer pools.

        The notebooks slice off the first `offset` primers from each pool; keep
        the same default to maintain behaviour.
        """
        fprimers = self.fprimers_full[offset:]
        rprimers = self.rprimers_full[offset:]
        return fprimers, rprimers

    def generate_transfer_df(self, volume_nl: int = 500, use_seed: bool = True) -> pd.DataFrame:
        """Generate a transfer dataframe with columns Source Well, Destination Well, Volume.

        Behaviour mirrors the notebooks: for each destination well in a 16x24
        plate (A1..P24), pick a unique pair (forward, reverse) from the
        available pools, avoiding duplicates in the same order. Each pair
        contributes two transfer lines (fwd and rev) to the destination well.
        """
        fprimers, rprimers = self.sample_primers()

        if use_seed:
            np.random.seed(self.randseed)

        sourcewells = []
        destwells = []
        vols = []
        covered_list = []

        # start with a random pair
        iforward = np.random.randint(0, len(fprimers))
        ireverse = iforward
        while ireverse == iforward:
            ireverse = np.random.randint(0, len(rprimers))
        currtup = (iforward, ireverse)

        for row in range(16):
            for col in range(24):
                while currtup in covered_list:
                    iforward = np.random.randint(0, len(fprimers))
                    ireverse = iforward
                    while ireverse == iforward:
                        ireverse = np.random.randint(0, len(rprimers))
                    currtup = (iforward, ireverse)
                covered_list.append(currtup)

                dest = string.ascii_uppercase[row] + str(col + 1)

                sourcewells.append(fprimers[iforward])
                destwells.append(dest)
                vols.append(volume_nl)

                sourcewells.append(rprimers[ireverse])
                destwells.append(dest)
                vols.append(volume_nl)

        df = pd.DataFrame({"Source Well": sourcewells, "Destination Well": destwells, "Volume": vols})
        return df


def join_transfer_with_barcodes(df_transfer: pd.DataFrame, df_barcodes: pd.DataFrame) -> pd.DataFrame:
    """Join transfer dataframe with barcode mapping, return cleaned joined frame.

    Matches df_transfer.Source Well with df_barcodes.Storage and returns a
    dataframe with Destination Well, Direction (F/R) and Sequence (spaces removed).
    """
    df_joined = pd.merge(df_transfer, df_barcodes, left_on='Source Well', right_on='Storage')
    df_joined['Direction'] = df_joined['Sequence Name'].str.extract(r'([^\d])\d*$')
    df_joined = df_joined.drop(columns=['Source Well', 'Volume', 'Well Position', 'Sequence Name', 'Storage'])
    df_joined['Sequence'] = df_joined['Sequence'].str.replace(' ', '')
    return df_joined


def pivot_barcodes(df_joined: pd.DataFrame) -> pd.DataFrame:
    """Pivot joined barcodes into table indexed by Destination Well with columns F and R.

    Returned frame has columns SampleID (Destination Well), FwIndex, RvIndex.
    """
    df_pivoted = df_joined.pivot(index='Destination Well', columns='Direction', values='Sequence').reset_index().reset_index(drop=True)
    df_pivoted.columns = ['SampleID', 'FwIndex', 'RvIndex']
    df_pivoted.set_index('SampleID', inplace=True)
    return df_pivoted
