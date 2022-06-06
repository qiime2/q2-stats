# ----------------------------------------------------------------------------
# Copyright (c) 2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from qiime2.plugin import Plugin

import q2_stats

plugin = Plugin(name='stats',
                version=q2_stats.__version__,
                website='https://github.com/qiime2/q2-stats',
                package='q2_stats',
                description='This QIIME 2 plugin supports statistical analyses.',
                short_description='Plugin for statistical analyses.')

importlib.import_module('q2_stats._transformer')
