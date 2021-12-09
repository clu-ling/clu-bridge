from clu.bridge import processors
import json
import os
import unittest

# see https://docs.python.org/3/library/unittest.html#basic-example
class TestProcessorsDocument(unittest.TestCase):
    doc_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "processors-doc.json")
    with open(doc_path, "r") as infile:
      odinson_json = json.load(infile)

    def test_load_from(self):
        """processors.Document.parse_file() should load an processors.Document from a path to a Processors Document JSON file."""
        doc = processors.Document.parse_file(TestProcessorsDocument.doc_path)
        self.assertTrue(isinstance(doc, processors.Document), f"{type(doc)} was not a processors.Document")
