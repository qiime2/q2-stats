# ----------------------------------------------------------------------------
# Copyright (c) 2022-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import numpy as np

from qiime2.plugin.testing import TestPluginBase

from q2_stats.hypotheses.pairwise import (
    wilcoxon_srt, mann_whitney_u, _compare_wilcoxon)
from q2_stats.examples import (faithpd_timedist_factory,
                               faithpd_refdist_factory)


class TestBase(TestPluginBase):
    package = 'q2_stats.tests'

    def setUp(self):
        super().setUp()

        self.faithpd_timedist = faithpd_timedist_factory().view(pd.DataFrame)
        self.faithpd_refdist = faithpd_refdist_factory().view(pd.DataFrame)


class TestStats(TestBase):
    # Wilcoxon SRT test cases

    # Data in the exp_stats_data dataframes were pulled from Greg Caporaso's
    # Autism study repo on github, which can be found here:
    # https://github.com/caporaso-lab/autism-fmt1/
    # blob/18-month-followup/16S/engraftment.ipynb
    def test_wilcoxon_with_faith_pd_baseline0_asymptotic(self):
        exp_stats_data = pd.DataFrame({
            'A:group': [0.0, 0.0, 0.0, 0.0],
            'A:n': [18, 18, 18, 18],
            'A:measure': [9.54973486, 9.54973486, 9.54973486, 9.54973486],
            'B:group': [3, 10, 18, 100],
            'B:n': [17, 18, 18, 16],
            'B:measure': [9.592979726, 10.9817719, 11.39392352, 12.97286672],
            'n': [17, 18, 18, 16],
            'test-statistic': [70.0, 20.0, 4.0, 5.0],
            'p-value': [0.758312374, 0.004337022, 0.000386178, 0.001123379],
            'q-value': [0.758312374, 0.005782696, 0.00154471, 0.002246758]
        })

        stats_data = wilcoxon_srt(distribution=self.faithpd_timedist,
                                  compare='baseline',
                                  baseline_group='0',
                                  p_val_approx='asymptotic')

        pd.testing.assert_frame_equal(stats_data, exp_stats_data)

    def test_wilcoxon_pairwise_against_each_alternative_hypothesis(self):
        stats_data_greater = wilcoxon_srt(distribution=self.faithpd_timedist,
                                          compare='consecutive',
                                          alternative='greater',
                                          p_val_approx='asymptotic')
        p_vals_greater = stats_data_greater['p-value']

        stats_data_less = wilcoxon_srt(distribution=self.faithpd_timedist,
                                       compare='consecutive',
                                       alternative='less',
                                       p_val_approx='asymptotic')
        p_vals_less = stats_data_less['p-value']

        p_val_total = np.add(p_vals_greater, p_vals_less)
        for p_val in p_val_total:
            self.assertAlmostEqual(p_val, 1, places=1)

    def test_wilcoxon_with_faith_pd_consecutive_asymptotic(self):
        exp_stats_data = pd.DataFrame({
            'A:group': [0, 3, 10, 18],
            'A:n': [18, 17, 18, 18],
            'A:measure': [9.54973486, 9.592979726, 10.9817719, 11.393923515],
            'B:group': [3, 10, 18, 100],
            'B:n': [17, 18, 18, 16],
            'B:measure': [9.592980, 10.981772, 11.393924, 12.972867],
            'n': [17, 17, 18, 16],
            'test-statistic': [70.0, 26.0, 83.0, 24.0],
            'p-value': [0.758312, 0.016822, 0.913301, 0.022895],
            'q-value': [0.913301, 0.0457895, 0.913301, 0.0457895]
        })

        stats_data = wilcoxon_srt(distribution=self.faithpd_timedist,
                                  compare='consecutive',
                                  p_val_approx='asymptotic')

        pd.testing.assert_frame_equal(stats_data, exp_stats_data)

    def test_wilcoxon_consecutive_comparison_with_baseline_group(self):
        with self.assertRaisesRegex(ValueError, "`consecutive` was selected as"
                                    " the comparison, but a `baseline_group`"
                                    " was added."):
            wilcoxon_srt(distribution=self.faithpd_timedist,
                         compare='consecutive', baseline_group='reference')

    def test_wilcoxon_invalid_comparison(self):
        with self.assertRaisesRegex(ValueError, "Invalid comparison. Please"
                                    " either choose `baseline` or"
                                    " `consecutive` as your comparison."):
            wilcoxon_srt(distribution=self.faithpd_timedist,
                         compare='foo')

    def test_wilcoxon_invalid_baseline_group(self):
        with self.assertRaisesRegex(ValueError, "'foo' was not found as a"
                                    " group within the distribution."):
            wilcoxon_srt(distribution=self.faithpd_timedist,
                         compare='baseline', baseline_group='foo')

    def test_wilcoxon_invalid_alternative_hypothesis(self):
        with self.assertRaisesRegex(ValueError, "Invalid `alternative`"
                                    " hypothesis selected."):
            wilcoxon_srt(distribution=self.faithpd_timedist,
                         compare='consecutive', alternative='foo')

    # Mann-Whitney U test cases

    # Data in the exp_stats_data dataframes were calculated 'by hand' in a
    # jupyter notebook using the same data, manually organized into groups
    # and subsequently compared using scipy.stats.mannwhitneyu to calculate
    # the test-statistic and p-values. Notebook can be found here:
    # https://gist.github.com/lizgehret/c9add7b451e5e91b1017a2a963276bff
    def test_mann_whitney_pairwise_against_each(self):
        exp_stats_data = pd.DataFrame({
            'A:group': ['control', 'control', 'control', 'control',
                        'control', 'reference', 'reference', 'reference',
                        'reference', 'reference'],
            'A:n': [23, 23, 23, 23, 23, 5, 5, 5, 5, 5],
            'A:measure': [11.64962736, 11.64962736, 11.64962736, 11.64962736,
                          11.64962736, 10.24883918, 10.24883918, 10.24883918,
                          10.24883918, 10.24883918],
            'B:group': [0, 3, 10, 18, 100, 0, 3, 10, 18, 100],
            'B:n': [18, 17, 18, 18, 16, 18, 17, 18, 18, 16],
            'B:measure': [9.54973486, 9.592979726, 10.9817719, 11.39392352,
                          12.97286672, 9.54973486, 9.592979726, 10.9817719,
                          11.39392352, 12.97286672],
            'n': [41, 40, 41, 41, 39, 23, 22, 23, 23, 21],
            'test-statistic': [282.0, 260.0, 194.0, 190.0, 104.0,
                               49.0, 43.0, 20.0, 14.0, 6.0],
            'p-value': [0.050330911733538534, 0.07994303215567311,
                        0.7426248650660427, 0.6646800940267454,
                        0.02321456407322841, 0.7941892150565809,
                        1.0, 0.06783185968744732, 0.023005953105134484,
                        0.0056718704407604376],
            'q-value': [0.12582728, 0.13323839, 0.88243246, 0.88243246,
                        0.07738188, 0.88243246, 1.0, 0.13323838,
                        0.07738188, 0.0567187],
        })

        stats_data = mann_whitney_u(distribution=self.faithpd_refdist,
                                    against_each=self.faithpd_timedist,
                                    compare='all-pairwise',
                                    p_val_approx='asymptotic')

        pd.testing.assert_frame_equal(stats_data, exp_stats_data)

    def test_mann_whitney_pairwise_against_each_alternative_hypothesis(self):
        stats_data_greater = mann_whitney_u(distribution=self.faithpd_refdist,
                                            against_each=self.faithpd_timedist,
                                            compare='all-pairwise',
                                            alternative='greater',
                                            p_val_approx='asymptotic')
        p_vals_greater = stats_data_greater['p-value']

        stats_data_less = mann_whitney_u(distribution=self.faithpd_refdist,
                                         against_each=self.faithpd_timedist,
                                         compare='all-pairwise',
                                         alternative='less',
                                         p_val_approx='asymptotic')
        p_vals_less = stats_data_less['p-value']

        p_val_total = np.add(p_vals_greater, p_vals_less)
        for p_val in p_val_total:
            self.assertAlmostEqual(p_val, 1, places=1)

    def test_mann_whitney_reference(self):
        exp_stats_data = pd.DataFrame({
            'A:group': ['reference'],
            'A:n': [5],
            'A:measure': [10.2488392],
            'B:group': ['control'],
            'B:n': [23],
            'B:measure': [11.6496274],
            'n': [28],
            'test-statistic': [37.0],
            'p-value': [0.23025583],
            'q-value': [0.23025583],
        })

        stats_data = mann_whitney_u(distribution=self.faithpd_refdist,
                                    compare='reference',
                                    reference_group='reference',
                                    p_val_approx='asymptotic')

        pd.testing.assert_frame_equal(stats_data, exp_stats_data)

    def test_mann_whitney_all_pairwise_comparisons_with_reference_group(self):
        with self.assertRaisesRegex(ValueError, "`all-pairwise` was selected"
                                    " as the comparison, but a"
                                    " `reference_group` was added."):
            mann_whitney_u(distribution=self.faithpd_refdist,
                           compare='all-pairwise',
                           reference_group='reference')

    def test_mann_whitney_invalid_comparison(self):
        with self.assertRaisesRegex(ValueError, "Invalid comparison. Please"
                                    " either choose `reference` or"
                                    " `all-pairwise` as your comparison."):
            mann_whitney_u(distribution=self.faithpd_refdist,
                           compare='foo')

    def test_mann_whitney_invalid_reference_group(self):
        with self.assertRaisesRegex(ValueError, "'foo' was not found as a"
                                    " group within the distribution."):
            mann_whitney_u(distribution=self.faithpd_refdist,
                           compare='reference', reference_group='foo')

    def test_mann_whitney_invalid_alternative_hypothesis(self):
        with self.assertRaisesRegex(ValueError, "Invalid `alternative`"
                                    " hypothesis selected."):
            mann_whitney_u(distribution=self.faithpd_refdist,
                           compare='all-pairwise', alternative='foo')

    def test_examples(self):
        self.execute_examples()

    def test_ignore_comparator_false(self):
        groupa_dict = {"subject1": 0.8091,
                       "subject2": 0.09271, "subject3": 0.9290}
        groupa = pd.Series(data=groupa_dict, index=['subject1', 'subject2',
                                                    'subject3'])
        groupa.index.name = 1
        groupb = {"subject4": 0.1809, "subject5": 0.9271, "subject6": 0.0290}
        groupb = pd.Series(data=groupb, index=['subject4', 'subject5',
                                               'subject6'])
        groupb.index.name = 2

        with self.assertRaisesRegex(ValueError, ".*no subject overlap between"
                                    " Group 1 and Group 2.*['subject1',"
                                    " 'subject2', 'subject3'].*['subject4',"
                                    " 'subject5', 'subject6']"):
            _compare_wilcoxon(group_a=groupa, group_b=groupb,
                              alternative='two-sided',
                              p_val_approx='auto',
                              ignore_empty_comparator=False)

    def test_ignore_comparator_true(self):
        wil_stats_data = pd.DataFrame({
            'id': ["sample1", "sample2", "sample3", "sample4"],
            'measure': [0.9002, 0.8221, 0.0981, 0.0100],
            'group': [1, 1, 2, 2],
            'subject': ["subject1", "subject2", "subject3", "subject4"]
        })

        wil_stats_data['id'].attrs.update({
            'title': 'Pairwise Comparison'})
        wil_stats_data['measure'].attrs.update({
            'title': 'Pairwise Comparison'})
        stats_data = wilcoxon_srt(wil_stats_data, compare='baseline',
                                  baseline_group=1,
                                  ignore_empty_comparator=True)
        exp_stats_data = pd.DataFrame({
            'A:group': [1],
            'A:n': [2],
            'A:measure':  [0.8611500000000001],
            'B:group': [2],
            'B:n': [2],
            'B:measure': [0.05405],
            'n': [0],
            'test-statistic': [float("Nan")],
            'p-value': [float("Nan")],
            'q-value': [float("Nan")]})

        pd.testing.assert_frame_equal(stats_data, exp_stats_data)
