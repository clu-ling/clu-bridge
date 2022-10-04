from typing import Dict, Iterable, List, Set, Text, Tuple, Union
from clu.bridge import processors
import spacy

from spacy.tokens import Doc as SpacyDoc
from spacy.tokens import (
  Span as SpacySpan, 
  Token as SpacyToken
)

class ConversionUtils:
  
    @staticmethod
    def _peek(generator: Iterable) -> Union[SpacyToken, None]:
        """peek() will return either the next Spacy Token in the iterable or None."""
        try:
            first = next(generator)
        except StopIteration:
            return None
        return first

    @staticmethod
    def to_clu_document(spacyDoc: SpacyDoc) -> processors.Document:
        """
        Converts a SpacyDoc: Sequence[Token] to a CluDocument: Sequence[processors.Sentence]

        Parameters
        ----------
        spacyDoc: a SpacyDoc object

        Returns
        -------
        A processors.Document object
        """

        return processors.Document(
          # FIXME: what about ID?
          id=None,
          # FIXME: what about text?
          text=None,
          sentences=[ConversionUtils.to_clu_sentence(s) for s in spacyDoc.sents]
        )

    @staticmethod
    def _spaces_to_offsets(sent: SpacySpan) -> Tuple[List[int]]:
        """Converts spaces to char offsets"""
        start_offsets = list()
        end_offsets = list()

        for token in sent:
            offset = token.idx - sent.start_char
            start_offsets.append(offset)
            end_offsets.append(offset + len(token))

        assert start_offsets[0] == 0
        return (start_offsets, end_offsets)



    @staticmethod
    def to_clu_graph(sent: SpacySpan) -> Dict[processors.Graphs, processors.DirectedGraph]:
        """Create a hybrid graph from a SpaCy dependency parse"""
        words = []
        edges: Set[processors.Edge] = set()
        for token in sent:
            words.append(token.text)
            children = token.children
            child = ConversionUtils._peek(children)
            while child is not None:
                edge = processors.Edge(
                  source=token.i - sent.start,
                  destination=child.i - sent.start,
                  relation=child.dep_,
                )
                edges.add(edge)
                child = ConversionUtils._peek(children)
        edges = edges.union(processors.ConversionUtils._make_collapsed_deps(words=words, edges=list(edges)))
        roots =  [sent.root.i - sent.start]

        return { processors.Graphs.HYBRID_DEPENDENCIES: processors.DirectedGraph(edges=list(edges), roots=roots) }

    @staticmethod
    def to_clu_sentence(sent: SpacySpan) -> processors.Sentence:
        """
        Converts a SpaCy Span (Doc slice) object to a processors Sentence object.

        Parameters
        ----------
        sent: a SpaCy Span object

        Returns
        -------
        sentence: a processors Sentence object
        """

        start_offsets, end_offsets = ConversionUtils._spaces_to_offsets(sent)

        sentence = processors.Sentence(
          raw=[token.text for token in sent],
          startOffsets=start_offsets,
          endOffsets=end_offsets,
          words=[token.text for token in sent],
          tags=[token.tag_ for token in sent],
          lemmas=[token.lemma_ for token in sent],
          # FIXME: how to get SpaCy chunks?
          chunks=["O" for token in sent],
          entities=[
            t.ent_iob_ + "-" + t.ent_type_ if t.ent_type_ != "" else "O"
            for t in sent
          ],
          norms=[token.text for token in sent],
          graphs=ConversionUtils.to_clu_graph(sent)
        )
        # FIXME: create hybrid graph
        return sentence