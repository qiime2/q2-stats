import pandas as pd

from qiime2.plugin.testing import TestPluginBase

from .. import TabularDataResourceDirFmt

class TestTransformers(TestPluginBase):
    package = 'q2_stats.tests'

    def test_empty_tabular_data_resource_to_dataframe(self):
        _, obs = self.transform_format(TabularDataResourceDirFmt,
                                       pd.DataFrame,
                                       filename='empty_data_dist')

        exp = pd.DataFrame(columns=['id', 'measure', 'group', 'subject'])

        pd.testing.assert_frame_equal(obs, exp)