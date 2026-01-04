# ----------------------------------------------------------------------------
# Copyright (c) 2022-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import (
    Str, Plugin, Choices, Bool, Metadata, List, TypeMap, TypeMatch,
    Collection, Visualization, Citations)

from q2_types.sample_data import SampleData, AlphaDiversity
from q2_types.tabular import (
    StatsTable, Pairwise, Dist1D, Multi, Matched, Independent, Ordered,
    NestedOrdered, Unordered, NestedUnordered
)

import q2_stats
from q2_stats.hypotheses import mann_whitney_u, wilcoxon_srt
from q2_stats.hypotheses.pairwise_facet import (
    mann_whitney_u_facet, wilcoxon_srt_facet)
from q2_stats.deprecated.alpha_group_significance import (
    alpha_group_significance, prep_alpha_distribution)
from q2_stats.meta.facet import collate_stats, facet_across, facet_within
from q2_stats.plots import plot_rainclouds
import q2_stats.examples as ex


citations = Citations.load('citations.bib', package='q2_stats')
plugin = Plugin(name='stats',
                version=q2_stats.__version__,
                website='https://github.com/qiime2/q2-stats',
                package='q2_stats',
                description='This QIIME 2 plugin supports'
                            ' statistical analyses.',
                short_description='Plugin for statistical analyses.')


plugin.methods.register_function(
    function=mann_whitney_u,
    inputs={'distribution': Dist1D[Unordered | Ordered, Independent],
            'against_each': Dist1D[Unordered | Ordered,
                                   Matched | Independent]},
    parameters={'compare': Str % Choices('reference', 'all-pairwise'),
                'reference_group': Str,
                'alternative': Str % Choices('two-sided', 'greater', 'less'),
                'p_val_approx': Str % Choices('auto', 'exact', 'asymptotic')},
    outputs=[('stats', StatsTable[Pairwise])],
    parameter_descriptions={
        'compare': 'The comparison that will be used to analyze the input'
                   ' `distribution`. Either "reference" or "all-pairwise"'
                   ' must be selected. The "reference" comparison defines'
                   ' Group A as the reference/control provided to'
                   ' `reference_group` (sourced from either `reference_column`'
                   ' or `control_column`), and Group B as all other groups.'
                   ' The "all-pairwise" comparison compares all groups to'
                   ' all other groups. If `against_each` is used, this will'
                   ' define Group B.',
        'reference_group': 'If "reference" is the selected comparison, this'
                           ' is the column that will be used to compare all'
                           ' other groups against.',
        'alternative': 'The "two-sided" alternative hypothesis is that the'
                       ' median of Group A does not equal the median of Group'
                       ' B. The "greater" alternative hypothesis is that the'
                       ' median of group A is greater than the median of Group'
                       ' B. The "less" alternative hypothesis is that the'
                       ' median of group A is less than the median of Group'
                       ' B.',
        'p_val_approx': '"exact" will calculate an exact p-value for'
                        ' distributions, "asymptotic" will use a normal'
                        ' distribution, and "auto" will use either "exact"'
                        ' when one of the groups has less than 8 observations'
                        ' and there are no ties, otherwise "asymptotic".'
    },
    output_descriptions={
        'stats': 'The Mann-Whitney U table for either the "reference"'
                 ' or "all-pairwise" comparison.',
    },
    citations=[citations['MannWhitney1947']],
    name='Mann-Whitney U Test',
    description='',
    examples={
        'mann_whitney_pairwise': ex.mann_whitney_pairwise
    }
)

plugin.methods.register_function(
    function=wilcoxon_srt,
    inputs={'distribution': Dist1D[Ordered, Matched]},
    parameters={'compare': Str % Choices('baseline', 'consecutive'),
                'baseline_group': Str,
                'alternative': Str % Choices('two-sided', 'greater', 'less'),
                'p_val_approx': Str % Choices('auto', 'exact', 'asymptotic'),
                'ignore_empty_comparator': Bool},
    outputs=[('stats', StatsTable[Pairwise])],
    parameter_descriptions={
        'compare': 'The type of comparison that will be used to analyze the'
                   ' input `distribution`.'
                   ' The "baseline" comparison defines Group A as the'
                   ' timepoint provided to `baseline_group` (sourced from'
                   ' `time_column`), and Group B as all other timepoints'
                   ' contained in `time_column`. The "consecutive" comparison'
                   ' defines Group A as "timepoint n", and Group B as'
                   ' "timepoint n+1" (both sourced from `time_column`).',
        'baseline_group': 'If "baseline" is the selected comparison, this is'
                          ' the column that will be used to compare all'
                          ' other groups against.',
        'alternative': 'The "two-sided" alternative hypothesis is that the'
                       ' median of Group A does not equal the median of Group'
                       ' B. The "greater" alternative hypothesis is that the'
                       ' median of group A is greater than the median of Group'
                       ' B. The "less" alternative hypothesis is that the'
                       ' median of group A is less than the median of Group'
                       ' B.',
        'p_val_approx': '"exact" will calculate an exact p-value for'
                        ' distributions of up to 25 (inclusive) measurements,'
                        ' "asymptotic" will use a normal distribution,'
                        ' and "auto" will use either "exact" or "approx"'
                        ' depending on size.',
        'ignore_empty_comparator': 'Ignore any group that does not have any'
                                   ' overlapping subjects with comparison'
                                   ' group. These groups will have NaNs'
                                   ' in the stats table output'
    },
    output_descriptions={
        'stats': 'The Wilcoxon SRT table for either the "baseline"'
                 ' or "consecutive" comparison.',
    },
    citations=[citations['Wilcoxon1945']],
    name='Wilcoxon Signed Rank Test',
    description='',
    examples={
        'wilcoxon_baseline0': ex.wilcoxon_baseline0
    }
)

plugin.visualizers.register_function(
    function=plot_rainclouds,
    inputs={
        'data': Dist1D[
            Multi | Ordered | Unordered | NestedOrdered | NestedUnordered,
            Matched | Independent
        ],
        'stats': StatsTable[Pairwise]
    },
    parameters={},
    input_descriptions={
        'data': 'The group distributions to plot.',
        'stats': 'Statistical tests to display.'
    },
    parameter_descriptions={},
    name='Raincloud plots',
    description='Plot raincloud distributions for each group.',
    examples={
        'plot_rainclouds': ex.plot_rainclouds
    }
)

plugin.methods.register_function(
    function=facet_within,
    inputs={
        'distribution': Dist1D[Multi | NestedOrdered | NestedUnordered,
                               Matched | Independent]
    },
    parameters={},
    outputs={
        'distributions': Collection[Dist1D[Unordered, Independent]]
    },
    input_descriptions={
        'distribution': 'A nested or multi Dist1D which will be partitioned'
                        ' into undordered and independent subgroups.'
    },
    output_descriptions={
        'distributions': 'A collection of unordered and independent Dist1Ds.'
    },
    name='Facet within outer group',
    description='Facets a distribution into independent distributions where'
                ' each facet is an inner slice from the outer group.'
)

T_dep = TypeMatch([Independent, Matched])
T_nested, T_simple = TypeMap({
    NestedOrdered: Ordered,
    NestedUnordered: Unordered
})
plugin.methods.register_function(
    function=facet_across,
    inputs={
        'distribution': Dist1D[T_nested, T_dep]
    },
    parameters={},
    outputs={
        'distributions': Collection[Dist1D[T_simple, T_dep]]
    },
    input_descriptions={
        'distribution': 'A nested Dist1D which will be partitioned'
                        ' into non-nested Dist1D'
    },
    output_descriptions={
        'distributions': 'A collection of non-nested Dist1Ds'
    },
    name='Facet across outer group',
    description='Facet a distribution into per-class/level distributions where'
                ' each facet preserves the outer group structure.'
)

plugin.methods.register_function(
    function=collate_stats,
    inputs={
        'tables': Collection[StatsTable[Pairwise]]
    },
    parameters={},
    outputs={
        'table': StatsTable[Pairwise]
    },
    name='Combine and FDR correct multiple stats',
    description='Converts a collection of stats tables into a single table'
)

T_dist, T_facet, _ = TypeMap({
    (Dist1D[Multi, Independent],
     Str % Choices('within')): Visualization,
    (Dist1D[NestedOrdered | NestedUnordered, Matched],
     Str % Choices('within')): Visualization,
    (Dist1D[NestedOrdered | NestedUnordered, Independent],
     Str % Choices('within', 'across')): Visualization,
})

plugin.pipelines.register_function(
    function=mann_whitney_u_facet,
    inputs={
        'distribution': T_dist
    },
    parameters={
        'facet': T_facet
    },
    outputs={
        'stats': StatsTable[Pairwise]
    },
    parameter_descriptions={
        'facet': 'Whether to facet within or across the outer group.'
    },
    citations=[citations['MannWhitney1947']],
    name='Per-facet Mann-Whitney U Test',
    description='',
    examples={
        'mann_whitney_u_facet_across': ex.mann_whitney_facet_across,
        'mann_whitney_u_facet_within': ex.mann_whitney_facet_within
    }
)

plugin.pipelines.register_function(
    function=wilcoxon_srt_facet,
    inputs={
        'distribution': Dist1D[Multi | NestedOrdered | NestedUnordered,
                               Matched]
    },
    parameters={
        'ignore_empty_comparator': Bool,
    },
    parameter_descriptions={
        'ignore_empty_comparator': 'Ignore any group that does not have any'
                                   ' overlapping subjects with comparison'
                                   ' group. These groups will have NaNs'
                                   ' in the stats table output'
    },
    outputs={
        'stats': StatsTable[Pairwise]
    },
    citations=[citations['Wilcoxon1945']],
    name='Per-facet Wilcoxon Signed Rank Test',
    description='',
    examples={
        'wilcoxon_srt_facet': ex.wilcoxon_srt_facet
    }
)

T_time, T_subj, T_dist = TypeMap({
    (Str % Choices(''), Str % Choices('')): Dist1D[Multi, Independent],
    (Str % Choices(''), Str): Dist1D[Multi, Matched],
    (Str, Str % Choices('')): Dist1D[NestedOrdered, Independent],
    (Str, Str): Dist1D[NestedOrdered, Matched]
})
plugin.methods.register_function(
    deprecated=True,
    function=prep_alpha_distribution,
    inputs={
        'alpha_diversity': SampleData[AlphaDiversity]
    },
    parameters={
        'metadata': Metadata,
        'columns': List[Str],
        'subject': T_subj,
        'timepoint': T_time,
    },
    outputs={
        'distribution': T_dist
    },
    input_descriptions={
        'alpha_diversity': 'Alpha diversity which will become the "measure"'
    },
    parameter_descriptions={
        'metadata': 'Sample metadata to use',
        'columns': 'Columns to include as group information',
        'subject': 'If provided, will cause the Dist1D to be matched for'
                   ' repeated measures.',
        'timepoint': 'If provided, will cause the Dist1D to be stratified by'
                     ' timepoint. Required if using ``subject``.'
    },
    output_descriptions={
        'distribution': 'The resulting Dist1D.'
    },
    name='Alpha diversity to Dist1D',
    description='Alpha diversity to Dist1D'
)

plugin.pipelines.register_function(
    deprecated=True,
    function=alpha_group_significance,
    inputs={
        'alpha_diversity': SampleData[AlphaDiversity]
    },
    parameters={
        'metadata': Metadata,
        'columns': List[Str],
        'subject': T_subj,
        'timepoint': T_time,
    },
    outputs={
        'distribution': T_dist,
        'stats': StatsTable[Pairwise],
        'raincloud': Visualization
    },
    input_descriptions={
        'alpha_diversity': 'Alpha diversity which will become the "measure"'
    },
    parameter_descriptions={
        'metadata': 'Sample metadata to use',
        'columns': 'Columns to include as group information',
        'subject': 'If provided, will cause the results to be matched for'
                   ' repeated measures.',
        'timepoint': 'If provided, will cause the results to be stratified by'
                     ' timepoint. Required if using ``subject``.'
    },
    output_descriptions={
        'distribution': 'Dist1D generated by metadata and alpha diversity.',
        'stats': 'A stats table of the per-group/timepoint results',
        'raincloud': 'A visualization of the distribution and statistics'
    },
    name='Alpha group significance test and plot',
    description='Will select between Wilcoxon SRT and Mann-Whitney U depending'
                ' on the presence of repeated measures.',
    examples={
        'alpha_group_significance_faith_pd':
            ex.alpha_group_significance_faith_pd
    }
)
