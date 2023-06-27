# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._version import get_versions
from ._format import (NDJSONFileFormat, DataResourceSchemaFileFormat,
                      TabularDataResourceDirFmt,
                      _JSONFileFormat, _JSONSchemaFileFormat,
                      _JSONSchemaDirFmt)
from ._type import (StatsTable, Pairwise, GroupDist, NestedGroupDist, Ordered,
                    Unordered, Multi, Matched, Independent,
                    _Dist1D, _Independent, _Matched,
                    _Multi, _Ordered, _Unordered)

__version__ = get_versions()['version']
del get_versions

__all__ = ['NDJSONFileFormat', 'DataResourceSchemaFileFormat',
           'TabularDataResourceDirFmt',
           '_JSONFileFormat', '_JSONSchemaFileFormat', '_JSONSchemaDirFmt',
           'StatsTable', 'Pairwise',
           'GroupDist', 'NestedGroupDist', 'Ordered', 'Unordered',
           'Multi', 'Matched', 'Independent',
           '_Dist1D', '_Independent', '_Matched',
           '_Multi', '_Ordered', '_Unordered']
