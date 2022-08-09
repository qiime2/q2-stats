# ----------------------------------------------------------------------------
# Copyright (c) 2022-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import ValidationError, model

from frictionless import validate


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
            validate(str(self.path/'dataresource.json'))
        except ValidationError:
            raise model.ValidationError(
                'The dataresource does not completely describe'
                ' the data.ndjson file')


class DataPackageSchemaFileFormat(model.TextFileFormat):
    """Format for the associated metadata for each file in the DataLoaf.

    More on this later.
    """
    def _validate_(self, level):
        pass


class DataLoafPackageDirFmt(model.DirectoryFormat):
    data_slices = model.FileCollection(r'.+\.ndjson', format=NDJSONFileFormat)
    nutrition_facts = model.File('dataresource.json',
                                 format=DataPackageSchemaFileFormat)

    def _check_nutrition_facts(self):
        pass

    def _check_matching_data_slices(self):
        pass

    def _validate_(self, level):
        pass
