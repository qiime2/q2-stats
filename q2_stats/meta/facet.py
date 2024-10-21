import re
import pandas as pd

from .correction import fdr_benjamini_hochberg


def _clean_keys(keys):
    return re.sub(r'[^a-zA-Z0-9_\.\-\+]', '.', '__'.join(map(str, keys)))


def facet_within(distribution: pd.DataFrame) -> pd.DataFrame:
    if 'group' in distribution.columns:
        groupby = ['group', 'class']
        facet_title = distribution['group'].attrs.get('title', 'group')
    else:
        groupby = ['class']
        facet_title = distribution['class'].attrs.get('title', 'class')

    facets = {}
    for keys, df in distribution.groupby(groupby):
        df['group'] = df['level']
        df = df.drop(['class', 'level'], axis='columns')
        df['group'].attrs.update({
            'title': keys[-1]
        })

        df.attrs.update({
            'title': facet_title
        })
        facets[_clean_keys(keys)] = df

    return facets


def facet_across(distribution: pd.DataFrame) -> pd.DataFrame:
    facets = {}
    for keys, df in distribution.groupby(['class', 'level']):
        df = df.drop(['class', 'level'], axis='columns')

        for col in df.columns:
            df[col].attrs = distribution[col].attrs

        facets[_clean_keys(keys)] = df

    return facets


def collate_stats(tables: pd.DataFrame) -> pd.DataFrame:
    stats = []
    last = None
    for key, df in tables.items():
        df.insert(0, 'facet', key)
        df['facet'].attrs.update({
            'title': df.attrs.get('title', 'facet')
        })
        stats.append(df)

        last = df

    stats = pd.concat(stats)
    stats = fdr_benjamini_hochberg(stats)

    for col in last.columns:
        stats[col].attrs.update(last[col].attrs)

    return stats
