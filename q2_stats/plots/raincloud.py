# ----------------------------------------------------------------------------
# Copyright (c) 2022-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import importlib
import jinja2
import json
import pandas as pd

from q2_stats.util import json_replace


def plot_rainclouds(output_dir: str, data: pd.DataFrame,
                    stats: pd.DataFrame = None):
    table1 = None
    if stats is not None:
        table1, stats = _make_stats(stats)

    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_stats.plots', 'specs')
    )

    extras = {}
    is_multi = False

    x_label = data['measure'].attrs.get('title', 'measure')
    if 'group' in data.columns:
        y_label = data['group'].attrs.get('title', 'group')
    else:
        is_multi = True
        y_label = 'group'
        data = data.copy()
        data['group'] = data['class']
    if 'subject' in data.columns:
        subject_unit = data['subject'].get('title', 'subject')
        extras.update({
            'lightning': {"name": "$show_lightning",
                          "value": True,
                          "bind": {"input": "checkbox"}},
        })
    else:
        subject_unit = data['id'].get('title', 'sample')
        extras.update({
            'lightning': {"name": "$show_lightning",
                          "value": False},
        })
    title = f'{x_label} of {subject_unit} across {y_label}'
    figure1 = (
        f'Raincloud plots showing the distribution of subjects\''
        f' measure of {x_label} across {y_label}. Kernel density estimation'
        f' performed using a bandwidth calculated by Scott\'s method. Boxplots'
        f' show the min and max of the data (whiskers) as well as the first,'
        f' second (median), and third quartiles (box). '
        f' Points and connecting lines represent individual subjects'
        f' with a consistent jitter added across groups such that slopes'
        f' across adjacent groups are visually comparable between subjects.')

    index = J_ENV.get_template('index.html')
    records = json.loads(data.to_json(orient='records'))

    if 'class' in data.columns:
        spec = importlib.resources.open_text('q2_stats.plots.specs',
                                             'raincloud_multi.json')
        selection_opts = []
        selection_labels = []
        for cls in data['class'].unique():
            selection_opts.append([cls, ''])
            selection_labels.append(cls)
            if not is_multi:
                for lvl in data[data['class'] == cls]['level'].unique():
                    selection_opts.append([cls, lvl])
                    selection_labels.append(f'{cls} > {lvl}')

        extras.update({
            'class': selection_labels[0],
            'selection_labels': selection_labels,
            'selection_opts': selection_opts
        })
    else:
        spec = importlib.resources.open_text('q2_stats.plots.specs',
                                             'raincloud_single.json')
    with spec as fh:
        json_obj = json.load(fh)

    full_spec = json_replace(json_obj,
                             data=records, x_label=x_label, y_label=y_label,
                             title=title, **extras)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string, stats=stats,
                              figure1=figure1, table1=table1))


def _make_stats(stats):
    method = stats['test-statistic'].attrs['title']
    group_unit = (stats['A:group'].attrs['title']
                  + ' vs ' + stats['B:group'].attrs['title'])
    pval_method = stats['p-value'].attrs['title']
    qval_method = stats['q-value'].attrs['title']
    table1 = (f'{method} tests between groups ({group_unit}), with'
              f' {pval_method} p-value calculations and {qval_method}'
              f' correction for multiple comparisons (q-value).')
    df = pd.DataFrame(index=stats.index)
    group_a = _make_group_col('A', stats)
    df[group_a.name] = group_a
    group_b = _make_group_col('B', stats)
    df[group_b.name] = group_b
    df['A'] = stats['A:measure']
    df['B'] = stats['B:measure']
    if 'facet' in stats:
        df = df.merge(stats.iloc[:, 7:], left_index=True, right_index=True)
        df.insert(0, 'facet', stats['facet'])
        facet = [('Facet', stats['facet'].attrs['title'])]
    else:
        df = df.merge(stats.iloc[:, 6:], left_index=True, right_index=True)
        facet = []
    df.columns = pd.MultiIndex.from_tuples([
        *facet,
        ('Group A', stats['A:group'].attrs['title']),
        ('Group B', stats['B:group'].attrs['title']),
        ('A', stats['A:measure'].attrs['title']),
        ('B', stats['B:measure'].attrs['title']),
        ('', 'n'),
        ('', 'test-statistic'),
        ('', 'p-value'),
        ('', 'q-value'),
    ])
    html = df.to_html(index=False)

    return table1, html


def _make_group_col(prefix, df):
    group_series = df[prefix + ':group']
    group_n = df[prefix + ':n']

    if (group_series.dtype == float
            and group_series.apply(float.is_integer).all()):
        group_series = group_series.astype(int)

    group_series = group_series.apply(str)
    group_n = " (n=" + group_n.apply(str) + ")"

    series = group_series + group_n
    series.name = f'{"Group "}' + prefix
    return series
