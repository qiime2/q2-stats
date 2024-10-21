import pandas as pd
from statsmodels.stats.multitest import multipletests


def fdr_benjamini_hochberg(stats: pd.DataFrame) -> pd.DataFrame:
    stats['q-value'] = multipletests(stats['p-value'], method='fdr_bh')[1]
    stats['q-value'].attrs.update({
        'title': 'Benjamini-Hochberg',
        'description': 'Adjusted p-values to control false-discovery rate.'
    })

    return stats
