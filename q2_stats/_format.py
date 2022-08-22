# ----------------------------------------------------------------------------
# Copyright (c) 2022-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import ValidationError, model

from frictionless import validate
import numpy as np
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
    data_slices = model.FileCollection(r'.+\.csv', format=NDJSONFileFormat)
    nutrition_facts = model.File('datapackage.json',
                                 format=DataPackageSchemaFileFormat)

    def _check_nutrition_facts(self):
        for slice in self.data_slices.iter_views(pd.DataFrame):
            if self.nutrition_facts.columns != slice.columns:
                raise ValidationError('The datapackage does not completely'
                                      ' describe the .csv files.')

    def _check_matching_data_slices(self):
        slice_lengths = []
        slice_widths = []

        for slice in self.data_slices.iter_views(pd.DataFrame):
            slice_lengths.append(len(slice.index))
            slice_widths.append(len(slice.columns))

        if (len(np.unique(slice_lengths)) > 1
                or len(np.unique(slice_widths)) > 1):
            raise ValidationError('.csv files are not all the same size.')

    def _validate_(self, level):
        # self._check_matching_data_slices()
        # self._check_nutrition_facts()
        pass

    @data_slices.set_path_maker
    def _data_slices_path_maker(self, slice_name):
        return slice_name + '.csv'
