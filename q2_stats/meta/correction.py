import pandas as pd
import scipy.stats


def fdr_benjamini_hochberg(stats: pd.DataFrame) -> pd.DataFrame:
    ps = stats['p-value']

    ranked_p_values = scipy.stats.rankdata(ps)
    fdr = ps * len(ps) / ranked_p_values
    fdr[fdr > 1] = 1

    # qs = scipy.stats.false_discovery_control(ps, method='bh')

    stats['q-value'] = fdr
    stats['q-value'].attrs.update({
        'title': 'Benjamini-Hochberg',
        'description': 'Adjusted p-values to control false-discovery rate.'
    })

    return stats


def fwer_holm_bonferroni(stats):
    return stats
