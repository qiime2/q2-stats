# ----------------------------------------------------------------------------
# Copyright (c) 2022-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import itertools
import pandas as pd
import scipy.stats

from q2_stats.hypotheses._util import set_pairwise_attrs
from q2_stats.meta import fdr_benjamini_hochberg


def mann_whitney_u(distribution: pd.DataFrame, compare: str,
                   reference_group: str = None,
                   against_each: pd.DataFrame = None,
                   alternative: str = 'two-sided',
                   p_val_approx: str = 'auto') -> pd.DataFrame:

    dists = [distribution]

    if against_each is not None:
        dists.append(against_each)

    if compare == 'reference':
        comparisons = _comp_reference(distribution, reference_group,
                                      against_each=against_each)
    elif compare == 'all-pairwise':
        if reference_group is not None:
            raise ValueError("`all-pairwise` was selected as the comparison,"
                             " but a `reference_group` was added."
                             " Please either select `reference` as the"
                             " comparison, or remove the `reference_group`"
                             " parameter from your command.")
        comparisons = _comp_all_pairwise(distribution,
                                         against_each=against_each)
    else:
        raise ValueError("Invalid comparison. Please either choose `reference`"
                         " or `all-pairwise` as your comparison.")

    _alternative_comps(alternative=alternative)

    table = []
    for (idx_a, comp_a), (idx_b, comp_b) in comparisons:
        a_dist = dists[idx_a]
        b_dist = dists[idx_b]

        group_a = a_dist[a_dist['group'] == comp_a]['measure']
        group_b = b_dist[b_dist['group'] == comp_b]['measure']

        row = _compare_mannwhitneyu(group_a, group_b,
                                    alternative, p_val_approx)
        row['A:group'] = comp_a
        row['B:group'] = comp_b
        table.append(row)

    if not table:
        raise ValueError('Not enough groups to compare.')

    df = pd.DataFrame(table)
    df = fdr_benjamini_hochberg(df)
    df = _set_attrs_mannwhitneyu(df, dists[idx_a], dists[idx_b],
                                 alternative, p_val_approx)

    return df


def _comp_reference(distribution, reference_group, against_each=None):
    group = distribution['group']
    reference_group = _get_reference_from_column(group, reference_group,
                                                 'reference_group')

    if against_each is None:
        for other in sorted(group[group != reference_group].unique()):
            yield ((0, reference_group), (0, other))
    else:
        for other in sorted(against_each['group'].unique()):
            yield ((0, reference_group), (1, other))


def _comp_all_pairwise(distribution, against_each=None):
    if against_each is None:
        for (comp_a, comp_b) in itertools.combinations(
                sorted(distribution['group'].unique()), 2):
            yield ((0, comp_a), (0, comp_b))
    else:
        for (comp_a, comp_b) in itertools.product(
                sorted(distribution['group'].unique()),
                sorted(against_each['group'].unique())):
            yield ((0, comp_a), (1, comp_b))


def _compare_mannwhitneyu(group_a, group_b, alternative, p_val_approx):
    stat, p_val = scipy.stats.mannwhitneyu(
        group_a, group_b, method=p_val_approx,
        alternative=alternative, nan_policy='raise')

    return {
        'A:n': len(group_a),
        'B:n': len(group_b),
        'A:measure': group_a.median(),
        'B:measure': group_b.median(),
        'n': len(group_a) + len(group_b),
        'test-statistic': stat,
        'p-value': p_val
    }


def _set_attrs_mannwhitneyu(df, group_a, group_b, alternative, p_val_approx):
    if p_val_approx == 'auto':
        null_desc = (
            'considered either asymptotically normal,'
            ' or, if there are no ties and few observations, the exact'
            ' Mann-Whitney U distribution.')
    elif p_val_approx == 'asymptotic':
        null_desc = ' asymptotically normal'
    else:
        null_desc = ' the exact Mann-Whitney U distribution'

    df = set_pairwise_attrs(
        df, group_a, group_b,
        group_measure='Median',
        test_stat='Mann-Whitney U',
        test_desc='The Mann-Whitney U test statistic of group A.',
        p_val=f'{alternative}, {p_val_approx}', null_desc=null_desc)

    return df


def wilcoxon_srt(distribution: pd.DataFrame, compare: str,
                 baseline_group: str = None,
                 alternative: str = 'two-sided',
                 p_val_approx: str = 'auto',
                 ignore_empty_comparator: bool = False) -> pd.DataFrame:

    if compare == 'baseline':
        comparisons = _comp_baseline(distribution, baseline_group)
    elif compare == 'consecutive':
        if baseline_group is not None:
            raise ValueError("`consecutive` was selected as the comparison,"
                             " but a `baseline_group` was added. Please"
                             " either select `baseline` as the comparison,"
                             " or remove the `baseline_group` parameter"
                             " from your command.")
        comparisons = _comp_consecutive(distribution)
    else:
        raise ValueError("Invalid comparison. Please either choose `baseline`"
                         " or `consecutive` as your comparison.")

    _alternative_comps(alternative=alternative)

    table = []
    for comp_a, comp_b in comparisons:
        group_a = distribution[distribution['group'] == comp_a]
        group_b = distribution[distribution['group'] == comp_b]

        group_a = group_a.set_index('subject')['measure']
        group_a.index.name = comp_a
        group_b = group_b.set_index('subject')['measure']
        group_b.index.name = comp_b

        row = _compare_wilcoxon(group_a, group_b, alternative, p_val_approx,
                                ignore_empty_comparator)

        row['A:group'] = comp_a
        row['B:group'] = comp_b
        table.append(row)

    if not table:
        raise ValueError('Not enough groups to compare.')

    df = pd.DataFrame(table)
    df = fdr_benjamini_hochberg(df)
    df = _set_attrs_wilcoxon(
        df, distribution, alternative, p_val_approx)

    return df


def _comp_baseline(distribution, baseline_group):
    group = distribution['group']
    baseline_group = _get_reference_from_column(group, baseline_group,
                                                'baseline_group')

    for comp_b in sorted(group[group != baseline_group].unique()):
        yield (baseline_group, comp_b)


def _comp_consecutive(distribution):
    group = distribution['group']
    timepoints = list(sorted(group.unique()))
    yield from zip(timepoints, timepoints[1:])


def _compare_wilcoxon(group_a, group_b, alternative, p_val_approx,
                      ignore_empty_comparator) -> dict:
    if p_val_approx == 'asymptotic':
        # wilcoxon differs from mannwhitneyu in arg value, but does the same
        # test using a normal dist instead of the permutational dist so
        # normalize the naming in Q2
        p_val_approx = 'approx'
    comp = pd.merge(group_a.to_frame(), group_b.to_frame(), how='outer',
                    left_index=True, right_index=True)
    filtered = comp.dropna()

    results = {
        'A:n': len(group_a),
        'B:n': len(group_b),
        'A:measure': group_a.median(),
        'B:measure': group_b.median(),
        'n': len(filtered.index),
    }

    if filtered.empty:
        if ignore_empty_comparator:
            stat = float('nan')
            p_val = float('nan')
        else:
            raise ValueError("There is no subject overlap between Group %s and"
                             " Group %s. There has to be at least 1 subject"
                             " overlap between the groups. Group %s contains"
                             " these subjects: %s and Group %s contains these"
                             " subjects: %s" % (group_a.index.name,
                                                group_b.index.name,
                                                group_a.index.name,
                                                list(group_a.index),
                                                group_b.index.name,
                                                list(group_b.index)))
    else:
        stat, p_val = scipy.stats.wilcoxon(
            filtered.iloc[:, 0], filtered.iloc[:, 1],
            nan_policy='raise', mode=p_val_approx, alternative=alternative)

    results['test-statistic'] = stat
    results['p-value'] = p_val

    return results


def _set_attrs_wilcoxon(df, group, alternative, p_val_approx):
    if p_val_approx == 'auto':
        null_desc = (
            'considered either asymptotically normal,'
            ' or, if there are no ties and few observations, the exact'
            ' Wilcoxon T distribution.')
    elif p_val_approx == 'asymptotic':
        null_desc = ' asymptotically normal'
    else:
        null_desc = ' the exact Wilcoxon T distribution'

    df = set_pairwise_attrs(
        df, group, group,
        group_measure='Median',
        test_stat='Wilcoxon T',
        test_desc='The sum of rank differences.',
        p_val=f'{alternative}, {p_val_approx}', null_desc=null_desc)

    return df


def _alternative_comps(alternative):
    if not (alternative == 'two-sided' or alternative == 'greater'
            or alternative == 'less'):
        raise ValueError("Invalid `alternative` hypothesis selected."
                         " Please either choose `two-sided`, `greater`"
                         " or `less` as your alternative hypothesis.")


def _get_reference_from_column(series, reference_value, param_name):
    if reference_value is None:
        raise ValueError("%s must be provided." % param_name)

    if (series == reference_value).any():
        return reference_value

    try:
        reference_value = float(reference_value)
    except Exception:
        pass
    else:
        if (series == reference_value).any():
            return reference_value

    raise ValueError("%r was not found as a group within the distribution."
                     % reference_value)
