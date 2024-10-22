# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
from statsmodels.stats.multitest import multipletests


def fdr_benjamini_hochberg(stats: pd.DataFrame) -> pd.DataFrame:
    stats['q-value'] = multipletests(stats['p-value'], method='fdr_bh')[1]
    stats['q-value'].attrs.update({
        'title': 'Benjamini-Hochberg',
        'description': 'Adjusted p-values to control false-discovery rate.'
    })

    return stats
