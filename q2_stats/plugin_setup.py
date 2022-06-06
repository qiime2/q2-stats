# ----------------------------------------------------------------------------
# Copyright (c) 2022-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from qiime2.plugin import Str, Plugin, Choices

import q2_stats
from q2_stats._stats import mann_whitney_u, wilcoxon_srt
from q2_stats._format import (NDJSONFileFormat, DataResourceSchemaFileFormat,
                              TabularDataResourceDirFmt)
from q2_stats._visualizer import plot_rainclouds
from q2_stats._type import (StatsTable, Pairwise, GroupDist, Matched,
                            Independent, Ordered, Unordered)
import q2_stats._examples as ex

plugin = Plugin(name='stats',
                version=q2_stats.__version__,
                website='https://github.com/qiime2/q2-stats',
                package='q2_stats',
                description='This QIIME 2 plugin supports'
                            ' statistical analyses.',
                short_description='Plugin for statistical analyses.')

plugin.register_formats(NDJSONFileFormat, DataResourceSchemaFileFormat,
                        TabularDataResourceDirFmt)
plugin.register_semantic_types(StatsTable, Pairwise, GroupDist, Matched,
                               Independent, Ordered, Unordered)

plugin.register_semantic_type_to_format(
    GroupDist[Ordered | Unordered,
              Matched | Independent] | StatsTable[Pairwise],
    TabularDataResourceDirFmt)

plugin.methods.register_function(
    function=mann_whitney_u,
    inputs={'distribution': GroupDist[Unordered | Ordered, Independent],
            'against_each': GroupDist[Unordered | Ordered,
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
    name='Mann-Whitney U Test',
    description='',
    examples={
        'mann_whitney_pairwise': ex.mann_whitney_pairwise
    }
)

plugin.methods.register_function(
    function=wilcoxon_srt,
    inputs={'distribution': GroupDist[Ordered, Matched]},
    parameters={'compare': Str % Choices('baseline', 'consecutive'),
                'baseline_group': Str,
                'alternative': Str % Choices('two-sided', 'greater', 'less'),
                'p_val_approx': Str % Choices('auto', 'exact', 'asymptotic')},
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
                        ' depending on size.'
    },
    output_descriptions={
        'stats': 'The Wilcoxon SRT table for either the "baseline"'
                 ' or "consecutive" comparison.',
    },
    name='Wilcoxon Signed Rank Test',
    description='',
    examples={
        'wilcoxon_baseline0': ex.wilcoxon_baseline0
    }
)

plugin.visualizers.register_function(
    function=plot_rainclouds,
    inputs={
        'data': GroupDist[Ordered, Matched],
        'stats': StatsTable[Pairwise]
    },
    parameters={},
    input_descriptions={
        'data': 'The group distributions to plot.',
        'stats': 'Statistical tests to display.'
    },
    parameter_descriptions={},
    name='Raincloud plots',
    description='Plot raincloud distributions for each group.'
)

importlib.import_module('q2_stats._transformer')
