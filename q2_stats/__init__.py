# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._version import get_versions
from ._format import (NDJSONFileFormat, DataResourceSchemaFileFormat,
                      TabularDataResourceDirFmt)
from ._type import (StatsTable, Pairwise, Dist1D, Ordered, Unordered,
                    NestedOrdered, NestedUnordered, Multi,
                    Matched, Independent)

__version__ = get_versions()['version']
del get_versions

__all__ = ['NDJSONFileFormat', 'DataResourceSchemaFileFormat',
           'TabularDataResourceDirFmt', 'StatsTable', 'Pairwise',
           'Dist1D', 'Ordered', 'Unordered', 'Nested_Ordered',
           'Nested_Unordered', 'Multi', 'Matched', 'Independent']
