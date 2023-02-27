# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import frictionless as fls
import json

from q2_stats.plugin_setup import plugin
from q2_stats._format import (NDJSONFileFormat,
                              DataResourceSchemaFileFormat,
                              TabularDataResourceDirFmt)


@plugin.register_transformer
def _1(obj: pd.DataFrame) -> NDJSONFileFormat:
    ff = NDJSONFileFormat()
    obj.to_json(str(ff), lines=True, orient='records')
    return ff


@plugin.register_transformer
def _2(obj: DataResourceSchemaFileFormat) -> fls.Resource:
    return fls.Resource(str(obj))


@plugin.register_transformer
def _3(df: TabularDataResourceDirFmt) -> pd.DataFrame:
    path = df.data.view(NDJSONFileFormat)
    data = pd.read_json(str(path), lines=True)
    resource = df.metadata.view(fls.Resource)

    if data.empty:
        data = pd.DataFrame(
            columns=[c.name for c in resource.schema.fields])

    for field in resource.schema.fields:
        data[field.name].attrs = field.to_dict()

    return data


@plugin.register_transformer
def _4(obj: pd.DataFrame) -> TabularDataResourceDirFmt:
    metadata_obj = []

    for col in obj.columns:
        series = obj[col]
        dtype = series.convert_dtypes().dtype
        metadata = series.attrs.copy()

        if pd.api.types.is_float_dtype(dtype):
            schema_dtype = 'number'
        elif pd.api.types.is_integer_dtype(dtype):
            schema_dtype = 'integer'
        else:
            schema_dtype = 'string'

        metadata['name'] = col
        metadata['type'] = schema_dtype

        metadata_obj.append(metadata)

    metadata_dict = {'schema': {'fields': metadata_obj}}
    metadata_dict['format'] = 'ndjson'
    metadata_dict['path'] = 'data.ndjson'

    dir_fmt = TabularDataResourceDirFmt()

    dir_fmt.data.write_data(obj, pd.DataFrame)
    with open(dir_fmt.path / 'dataresource.json', 'w') as fh:
        fh.write(json.dumps(metadata_dict, indent=4))

    return dir_fmt
