import importlib

from q2_stats.plugin_setup import plugin
from q2_stats.types import (NDJSONFileFormat,
                            DataResourceSchemaFileFormat,
                            TabularDataResourceDirFmt)
from q2_stats.types import (StatsTable, Pairwise, Dist1D,
                            Matched, Independent, Ordered, Unordered, Multi,
                            NestedOrdered, NestedUnordered)

plugin.register_formats(NDJSONFileFormat, DataResourceSchemaFileFormat,
                        TabularDataResourceDirFmt)


plugin.register_semantic_types(StatsTable, Pairwise, Dist1D,
                               NestedOrdered, NestedUnordered, Matched,
                               Independent, Ordered, Unordered, Multi)

plugin.register_semantic_type_to_format(
    Dist1D[Ordered | Unordered | NestedOrdered | NestedUnordered | Multi,
           Matched | Independent] |
    StatsTable[Pairwise],
    TabularDataResourceDirFmt)

importlib.import_module('q2_stats.types.setup.transformers')
importlib.import_module('q2_stats.types.setup.validators')
