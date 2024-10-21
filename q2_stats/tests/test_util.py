# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_stats.util import json_replace


class TestJSONReplace(unittest.TestCase):
    def test_root(self):
        input = {"{{REPLACE_PARAM}}": "key1"}
        result = json_replace(input, key1='success')
        self.assertEqual(result, 'success')

    def test_value(self):
        input = {
            "foo": {"{{REPLACE_PARAM}}": "key1"}
        }
        result = json_replace(input, key1="bar")
        self.assertEqual(result, {"foo": "bar"})

    def test_list(self):
        input = {
            "foo": [1, {"{{REPLACE_PARAM}}": "key1"}, 3]
        }
        result = json_replace(input, key1=2)
        self.assertEqual(result, {"foo": [1, 2, 3]})

    def test_no_replace(self):
        input = 'a'
        result = json_replace(input, key1='asd')
        self.assertEqual(result, input)

    def test_many(self):
        input = {
            "foo": {
                "bar": [{"{{REPLACE_PARAM}}": "key1"}],
                "baz": {
                    "foo": {"{{REPLACE_PARAM}}": "key2"},
                    "bar": {"{{REPLACE_PARAM}}": "key3"}
                },
            },
            "bar": [{"baz": {"{{REPLACE_PARAM}}": "key1"}}]
        }

        result = json_replace(input, key1=1, key2={"baz": 2}, key3=None)
        self.assertEqual(result, {
            "foo": {
                "bar": [1],
                "baz": {
                    "foo": {"baz": 2},
                    "bar": None
                }
            },
            "bar": [{"baz": 1}]
        })


if __name__ == '__main__':
    unittest.main()
