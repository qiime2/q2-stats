# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import ValidationError, model

import frictionless
import json
import jsonschema


class NDJSONFileFormat(model.TextFileFormat):
    """Format for JSON file.

    first line is headers


    More to be added on this later.

    """
    def _validate_(self, level):
        pass


class DataResourceSchemaFileFormat(model.TextFileFormat):
    """
    Format for data resource schema.

    More on this later.
    """
    def _validate_(self, level):
        pass


class TabularDataResourceDirFmt(model.DirectoryFormat):
    data = model.File('data.ndjson', format=NDJSONFileFormat)
    metadata = model.File('dataresource.json',
                          format=DataResourceSchemaFileFormat)

    def _validate_(self, level='min'):
        try:
            frictionless.validate(str(self.path/'dataresource.json'))
        except ValidationError:
            raise model.ValidationError(
                'The dataresource does not completely describe'
                ' the data.ndjson file')


# WIP - JSON Formats
class _JSONFileFormat(model.TextFileFormat):

    def _validate_(self, level):
        try:
            # I don't think this is the right way to access this
            json.load(self)
        except ValidationError:
            raise model.ValidationError('The input file is not valid JSON.')


class _JSONSchemaFileFormat(model.TextFileFormat):

    def _validate_(self, level):
        with open('_schema.json', 'r') as fh:
            schema = json.load(fh)

        try:
            jsonschema.validate(instance=self, schema=schema)
        except ValidationError:
            raise model.ValidationError('The data schema provided does not'
                                        ' validate against the metaschema.')


class _JSONSchemaDirFmt(model.DirectoryFormat):
    data = model.File('data.json', format=_JSONFileFormat)
    schema = model.File('schema.json', format=_JSONSchemaFileFormat)

    def _validate_(self, level):
        try:
            # not sure if this is the right way to access these objects yet
            jsonschema.validate(instance=self.data, schema=self.schema)
        except ValidationError:
            raise model.ValidationError('The data provided does not match'
                                        ' the schema requirements.')
