# ----------------------------------------------------------------------------
# Copyright (c) 2022-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._version import get_versions
from ._format import (NDJSONFileFormat, DataResourceSchemaFileFormat,
                      FrictionlessCSVFileFormat, TabularDataResourceDirFmt,
                      DataPackageSchemaFileFormat, DataLoafPackageDirFmt)
from ._type import (StatsTable, Pairwise, GroupDist,
                    Ordered, Unordered, Matched, Independent,
                    DifferentialAbundance)

__version__ = get_versions()['version']
del get_versions

__all__ = ['NDJSONFileFormat', 'DataResourceSchemaFileFormat',
           'FrictionlessCSVFileFormat', 'TabularDataResourceDirFmt',
           'DataLoafPackageDirFmt', 'DataPackageSchemaFileFormat',
           'StatsTable', 'Pairwise', 'GroupDist', 'Ordered', 'Unordered',
           'Matched', 'Independent', 'DifferentialAbundance']
