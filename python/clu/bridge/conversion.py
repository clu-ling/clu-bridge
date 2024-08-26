from __future__ import annotations
from clu.bridge import processors
from clu.bridge import spacy
#from clu.bridge.typing import Tokens, Indices

#from lum.clu.processors.directed_graph import DirectedGraph as CluDirectedGraph, Edge as CluEdge
from lum.clu.processors.document import Document as CluDocument
#from lum.clu.processors.sentence import Sentence as CluSentence
from lum.odinson.doc import Document as OdinsonDocument, Field
#from lum.odinson.doc import Document as OdinsonDocument, Sentence as OdinsonSentence, TokensField, GraphField, Field
from spacy.tokens import Doc as SpacyDocument

import typing


__all__ = ["ConversionUtils"]


class ConversionUtils:
    UNKNOWN: str = "???"

    @staticmethod
    def to_clu_document(doc: typing.Union[SpacyDocument, OdinsonDocument]) -> CluDocument:
        if isinstance(doc, SpacyDocument):
            return spacy.ConversionUtils.to_clu_document(doc)
        elif isinstance(doc, OdinsonDocument):
            raise NotImplementedError("OdinsonDocument -> CluDocument not yet supported")
        raise NotImplementedError(f"doc of type '{type(doc)}' not supported")

    @staticmethod
    def to_odinson_document(doc: typing.Union[SpacyDocument, CluDocument], metadata: typing.List[Field]) -> CluDocument:
        clu_doc = doc
        if isinstance(doc, SpacyDocument):
            clu_doc = spacy.ConversionUtils.to_clu_document(doc)
        elif isinstance(clu_doc, CluDocument):
            if doc.id == None:
                doc.id = ConversionUtils.UNKNOWN
            return processors.ConversionUtils.to_odinson_document(doc=clu_doc, metadata=metadata)
        raise NotImplementedError(f"doc of type '{type(doc)}' not supported")
