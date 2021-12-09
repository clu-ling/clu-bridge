from clu.bridge.conversion import ConversionUtils
from clu.bridge import odinson, processors
import json
import os
import unittest

# see https://docs.python.org/3/library/unittest.html#basic-example
class TestConversionUtils(unittest.TestCase):
    proc_doc_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "processors-doc.json")
    odinson_doc_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "odinson-doc.json")

    def test_to_processors(self):
        """clu.bridge.conversion.ConversionUtils.to_processors() should convert an Odinson Document to a Processors Document."""
        #pdoc = processors.Document.parse_file(TestConversionUtils.proc_doc_path)
        odinson_doc = odinson.Document.parse_file(TestConversionUtils.odinson_doc_path)
        res = ConversionUtils.to_processors(odinson_doc)
        self.assertTrue(isinstance(res, processors.Document), f"{type(res)} was not a processors.Document")
        expected = "tp-pies"
        self.assertEqual(res.id, expected, f"{res.id} != '{expected}'")
        
