# ----------------------------------------------------------------------------
# Copyright (c) 2022-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import ValidationError, model

from frictionless import validate
import pandas as pd


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

    def _check_dataresource_filepath(self):
        try:
            validate(str(self.path/'dataresource.json'))
        except ValidationError:
            raise model.ValidationError(
                'The dataresource does not completely describe'
                ' the data.ndjson file')

    def _check_matching_metadata(self):
        # TODO: use fls framework to handle the data structures here
        if (self.data.view(pd.DataFrame).columns
                != self.metadata.view(pd.DataFrame).columns):
            raise ValidationError('The dataresource columns do not match the'
                                  ' data.ndjson file columns.')

    def _validate_(self, level='min'):
        self._check_dataresource_filepath()
        # self._check_matching_metadata()
