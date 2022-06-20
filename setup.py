# ----------------------------------------------------------------------------
# Copyright (c) 2022-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages

import versioneer

setup(
    name='q2-stats',
    version=versioneer.get_version(),
    packages=find_packages(),
    package_data={
        'q2_stats': ['assets/*'],
        'q2_stats.tests': ['data/*', 'data/faithpd_timedist/*',
                           'data/faithpd_refdist/*', 'data/empty_data_dist/*'],
    },
    author='Liz Gehret',
    author_email='elizabeth.gehret@nau.edu',
    description='QIIME 2 Plugin used for statistical analyses.',
    license='BSD-3-Clause',
    url='https://github.com/qiime2/q2-stats',
    zip_safe=False,
    entry_points={
        'qiime2.plugins': ['q2-stats=q2_stats.plugin_setup:plugin']
    }
)
