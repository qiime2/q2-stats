# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

StatsTable = SemanticType('StatsTable', field_names=['kind'])

Pairwise = SemanticType('Pairwise', variant_of=StatsTable.field['kind'])

GroupDist = SemanticType('GroupDist', field_names=['order', 'dependence'])

NestedGroupDist = SemanticType('NestedGroupDist', field_names=['order',
                                                               'dependence'])

Ordered = SemanticType('Ordered', variant_of=(GroupDist.field['order'],
                                              NestedGroupDist.field['order']))
Unordered = SemanticType('Unordered',
                         variant_of=(GroupDist.field['order'],
                                     NestedGroupDist.field['order']))
Multi = SemanticType('Multi', variant_of=GroupDist.field['order'])

Matched = SemanticType('Matched',
                       variant_of=(GroupDist.field['dependence'],
                                   NestedGroupDist.field['dependence']))
Independent = SemanticType('Independent',
                           variant_of=(GroupDist.field['dependence'],
                                       NestedGroupDist.field['dependence']))

# WIP - GroupDist refactoring
_Dist1D = SemanticType('_Dist1D', field_names=['_order', '_dependence'])

_Ordered = SemanticType('_Ordered', variant_of=(_Dist1D.field['_order']))

_Unordered = SemanticType('_Unordered', variant_of=(_Dist1D.field['_order']))

_Multi = SemanticType('_Multi', variant_of=_Dist1D.field['_order'])

_Matched = SemanticType('_Matched', variant_of=(_Dist1D.field['_dependence']))

_Independent = SemanticType('_Independent',
                            variant_of=(_Dist1D.field['_dependence']))
