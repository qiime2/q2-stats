# ----------------------------------------------------------------------------
# Copyright (c) 2022-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import itertools
from functools import cache
import importlib

import numpy as np
import pandas as pd

import qiime2


def _make_it_up(dist, prefix):
    n, cols = dist.shape
    columns = [f'{prefix}_g{d}' for d in range(1, cols+1)]
    df = pd.DataFrame(dist, columns=columns
                      ).melt(var_name='level', value_name='measure')
    df['class'] = prefix
    df['group'] = list(range(1, 6)) * (n // 5 * cols)
    df['subject'] = list(itertools.chain.from_iterable(
        [[f'{prefix}_s{d}'] * 5 for d in range(1, n // 5 * cols + 1)]))
    df['id'] = [f'{prefix}{d}' for d in range(1, n * cols + 1)]
    df = df[['id', 'measure', 'subject', 'group', 'class', 'level']]
    return df


@cache
def _random_df():
    rng = np.random.default_rng(12345)

    uniform = rng.uniform(size=(100, 2))
    unif_df = _make_it_up(uniform, 'unif')

    poisson = rng.poisson([20, 24, 50], (100, 3)) / 100
    pois_df = _make_it_up(poisson, 'pois')

    normal = rng.normal([0.2, 0.2, 0.5, 0.55], scale=[.5, .6, 1, 2],
                        size=(100, 4))
    norm_df = _make_it_up(normal, 'norm')

    return pd.concat([unif_df, pois_df, norm_df])


def _synthetic_data(type):
    to_drop = {
        'Dist1D[NestedOrdered, Matched]': [],
        'Dist1D[NestedOrdered, Independent]': ['subject'],
        'Dist1D[NestedUnordered, Matched]': [],
        'Dist1D[NestedUnordered, Independent]': ['subject'],
        'Dist1D[Ordered, Matched]': ['class', 'level'],
        'Dist1D[Ordered, Independent]': ['class', 'level', 'subject'],
        'Dist1D[Unordered, Matched]': ['class', 'level'],
        'Dist1D[Unordered, Independent]': ['class', 'level', 'subject'],
        'Dist1D[Multi, Matched]': ['group'],
        'Dist1D[Multi, Independent]': ['group', 'subject'],
    }

    full_df = _random_df().copy()
    sub_df = full_df.drop(columns=to_drop[type])
    return qiime2.Artifact.import_data(type, sub_df)


def synth_o_m_factory():
    return _synthetic_data('Dist1D[Ordered, Matched]')


def _get_data_from_tests(path):
    return importlib.resources.files('q2_stats.tests.data') / path


def faithpd_timedist_factory():
    return qiime2.Artifact.import_data(
        'Dist1D[Ordered, Matched]',
        _get_data_from_tests('faithpd_timedist.table.jsonl')
    )


def faithpd_refdist_factory():
    return qiime2.Artifact.import_data(
        'Dist1D[Unordered, Independent]',
        _get_data_from_tests('faithpd_refdist.table.jsonl')
    )


def stats_table_factory():
    return qiime2.Artifact.import_data(
        'StatsTable[Pairwise]', _get_data_from_tests('stats_table')
    )


def wilcoxon_baseline0(use):
    timedist = use.init_artifact('timedist', faithpd_timedist_factory)

    stats_table, = use.action(
        use.UsageAction('stats', 'wilcoxon_srt'),
        use.UsageInputs(
            distribution=timedist,
            compare='baseline',
            baseline_group='0',
            p_val_approx='asymptotic',
        ),
        use.UsageOutputNames(
            stats='stats'
        )
    )

    stats_table.assert_output_type('StatsTable[Pairwise]')


def mann_whitney_pairwise(use):
    timedist = use.init_artifact('timedist', faithpd_timedist_factory)
    refdist = use.init_artifact('refdist', faithpd_refdist_factory)

    stats_table, = use.action(
        use.UsageAction('stats', 'mann_whitney_u'),
        use.UsageInputs(
            distribution=refdist,
            compare='all-pairwise',
            against_each=timedist,
            p_val_approx='asymptotic',
        ),
        use.UsageOutputNames(
            stats='stats'
        )
    )

    stats_table.assert_output_type('StatsTable[Pairwise]')


def plot_rainclouds(use):
    dist = use.init_artifact('dist', synth_o_m_factory)

    raincloud, = use.action(
        use.UsageAction('stats', 'plot_rainclouds'),
        use.UsageInputs(
            data=dist,
        ),
        use.UsageOutputNames(
            visualization='raincloud_plot'
        )
    )

    raincloud.assert_output_type('Visualization')


def synth_no_i_factory():
    return _synthetic_data('Dist1D[NestedOrdered, Independent]')


def mann_whitney_facet_across(use):
    dist = use.init_artifact('dist', synth_no_i_factory)

    use.action(
        use.UsageAction('stats', 'mann_whitney_u_facet'),
        use.UsageInputs(
            distribution=dist,
            facet='across'
        ),
        use.UsageOutputNames(
            stats='stats'
        )
    )


def mann_whitney_facet_within(use):
    dist = use.init_artifact('dist', synth_no_i_factory)

    use.action(
        use.UsageAction('stats', 'mann_whitney_u_facet'),
        use.UsageInputs(
            distribution=dist,
            facet='within'
        ),
        use.UsageOutputNames(
            stats='stats'
        )
    )


def synth_no_m_factory():
    return _synthetic_data('Dist1D[NestedOrdered, Matched]')


def wilcoxon_srt_facet(use):
    dist = use.init_artifact('dist', synth_no_m_factory)

    use.action(
        use.UsageAction('stats', 'wilcoxon_srt_facet'),
        use.UsageInputs(
            distribution=dist,
        ),
        use.UsageOutputNames(
            stats='stats'
        )
    )


# PD Mice Data
pd_alpha_div_faith_pd_url = ('https://data.qiime2.org/usage-examples/pd-mice/'
                             'core-metrics-results/faith_pd_vector.qza')

pd_metadata_url = ('https://data.qiime2.org/usage-examples/'
                   'pd-mice/sample-metadata.tsv')


def alpha_group_significance_faith_pd(use):
    alpha_div_faith_pd = use.init_artifact_from_url('alpha_div_faith_pd',
                                                    pd_alpha_div_faith_pd_url)

    metadata = use.init_metadata_from_url('metadata', pd_metadata_url)

    dist, stats, raincloud = use.action(
        use.UsageAction('stats', 'alpha_group_significance'),
        use.UsageInputs(
            alpha_diversity=alpha_div_faith_pd,
            metadata=metadata,
            columns=['genotype', 'donor_status'],
            subject='mouse_id',
            timepoint='days_post_transplant'
        ),
        use.UsageOutputNames(
            distribution='dist',
            stats='stats',
            raincloud='raincloud'
        )
    )

    dist.assert_output_type('Dist1D[NestedOrdered, Matched]')

    dist2, stats2, raincloud2 = use.action(
        use.UsageAction('stats', 'alpha_group_significance'),
        use.UsageInputs(
            alpha_diversity=alpha_div_faith_pd,
            metadata=metadata,
            columns=['genotype', 'donor_status'],
        ),
        use.UsageOutputNames(
            distribution='dist2',
            stats='stats2',
            raincloud='raincloud2'
        )
    )

    dist2.assert_output_type('Dist1D[Multi, Independent]')
