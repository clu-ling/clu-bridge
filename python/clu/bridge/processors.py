from __future__ import annotations

from lum.clu.processors.directed_graph import DirectedGraph as CluDirectedGraph, Edge as CluEdge
from lum.clu.processors.document import Document as CluDocument
from lum.clu.processors.sentence import Sentence as CluSentence
from lum.odinson.doc import Document as OdinsonDocument, Sentence as OdinsonSentence, TokensField, GraphField, Field
from clu.bridge.typing import Tokens, Indices
from enum import Enum
from typing import Dict, ForwardRef, List, Optional, Text, Tuple
from pydantic import BaseModel, Extra, Field, PrivateAttr, validate_arguments
import typing


PartialGraph = typing.Dict[int, typing.List[Tuple[int, typing.Text]]]
HYBRID = "hybrid"

class ConversionUtils:

    """Conversion utilities for processors to Odinson"""

    @staticmethod
    def _make_collapsed_deps(words: typing.List[typing.Text], edges: typing.List[CluEdge]) -> typing.Set[CluEdge]:
        """Converts prep -> pobj to prep_pobj edge"""
        incoming: PartialGraph = {}
        outgoing: PartialGraph = {}
        for edge in edges:
            outgoing[edge.source] = outgoing.get(edge.source, []) + [
                (edge.destination, edge.relation)
            ]
            incoming[edge.destination] = incoming.get(edge.destination, []) + [
                (edge.source, edge.relation)
            ]
        res = set()
        for edge in edges:
            if edge.relation == "prep":
                adpos_idx = edge.destination
                for (dest, rel) in outgoing[edge.destination]:
                    if rel == "pobj":
                        collapsed = CluEdge(
                            source=edge.source,
                            destination=dest,
                            relation=f"prep_{words[adpos_idx].lower()}",
                        )
                        res.add(collapsed)
        return res

    # - create processors.HYBRID
    @staticmethod
    def _make_hybrid_graph(
        tokens: typing.List[typing.Text], 
        graph_map: typing.Dict[typing.Text, CluDirectedGraph]
    ) -> CluDirectedGraph:
        """Combine all roots and edges of graphs, as well as collapsed edges"""
        if HYBRID in graph_map:
            return graph_map[HYBRID]

        edges: typing.Set[CluEdge] = {}
        roots: typing.Set[int] = {}
        for (k, dg) in graph_map.values():
            for root in dg.roots:
                roots.add(root)
            for edge in dg.edges:
                edges.add(edge)
        collapsed = ConversionUtils._make_collapsed_deps(
            words=tokens, edges=list(edges)
        )
        return CluDirectedGraph(roots=list(roots), edges=list(collapsed.union(edges)))

    @staticmethod
    def to_odinson_document(doc: CluDocument, metadata: typing.List[Field] = []) -> OdinsonDocument:
        """Create an OdinsonDocument from a processors.Document"""
        odinson_ss = [ConversionUtils.to_odinson_sentence(s) for s in doc.sentences]
        return OdinsonDocument(
            id=doc.id or str(doc.__hash__()), metadata=metadata, sentences=odinson_ss
        )

    @staticmethod
    def _none_or_all_empty(elements: typing.Optional[typing.List[typing.Text]]) -> bool:
        return True if elements == None else all(len(e) == 0 for e in elements)
    
    @staticmethod
    def to_odinson_sentence(s: CluSentence) -> OdinsonSentence:
        """Create an OdinsonSentence from a processors.Sentence"""
        graph = ConversionUtils._make_hybrid_graph(tokens=s.words, graph_map=s.graphs)
        return OdinsonSentence(
            numTokens=len(s.raw),
            # List[Type[Field]]
            fields=[
                f
                for f in [
                    # raw
                    TokensField(tokens=s.raw, name="raw"),
                    # dependencies (hybrid graph)
                    None
                    if s.graphs is None
                    else GraphField(
                        name="dependencies",
                        roots=graph.roots,
                        edges=[
                            (edge.source, edge.destination, edge.relation)
                            for edge in graph.edges
                        ],
                    ),
                    # words
                    None
                    if ConversionUtils._none_or_all_empty(s.words)
                    else TokensField(tokens=s.words, name="word"),
                    # lemmas
                    None
                    if ConversionUtils._none_or_all_empty(s.lemmas)
                    else TokensField(tokens=s.lemmas, name="lemma"),
                    # tags
                    None
                    if ConversionUtils._none_or_all_empty(s.tags)
                    else TokensField(tokens=s.tags, name="tag"),
                    # entities
                    None
                    if ConversionUtils._none_or_all_empty(s.entities)
                    else TokensField(tokens=s.entities, name="entity"),
                    # chunks
                    None
                    if ConversionUtils._none_or_all_empty(s.chunks)
                    else TokensField(tokens=s.chunks, name="chunk"),
                    # norms
                    None
                    if ConversionUtils._none_or_all_empty(s.norms)
                    else TokensField(tokens=s.norms, name="norm"),
                ]
                if f is not None
            ],
        )

    @staticmethod
    def to_processors_document(doc: OdinsonDocument) -> CluDocument:
        return CluDocument(
            id=doc.id,
            sentences=[
                ConversionUtils.to_processors_sentence(s) for s in doc.sentences
            ],
        )

    @staticmethod
    def create_character_offsets(toks: Tokens) -> Tuple[Indices, Indices]:
        """Create start and end char offsets for tokens by treating them as whitespace-delimited"""
        current_start = -1
        current_end = 0
        start_offsets = []
        end_offsets = []
        for tok in toks:
            current_start += 1
            start_offsets.append(current_start)
            current_start += len(tok)
            current_end += len(tok)
            end_offsets.append(current_end)
            current_end += 1
        return start_offsets, end_offsets

    @staticmethod
    def to_processors_sentence(s: OdinsonSentence) -> CluSentence:

        graphs: typing.Optional[typing.Dict[typing.Text, CluDirectedGraph]] = None
        # NOTE: by convention, these are non-plural
        fields_dict: typing.Dict[typing.Text, typing.Optional[Tokens]] = {
            "raw": None,
            "word": None,
            "tag": None,
            "lemma": None,
            "entity": None,
            "chunk": None,
            "norm": None,
        }

        def is_token_field(
            field: Field, name: str = None
        ) -> bool:
            _is_token_field = isinstance(field, TokensField)
            if name is not None:
                return True if _is_token_field and field.name == name else False
            return _is_token_field

        for field in s.fields:
            if is_token_field(field) and field.name in fields_dict:
                fields_dict[field.name] = field.tokens
            elif isinstance(field, GraphField):
                # assume graph is hybrid
                graphs = graphs or dict()
                graphs[HYBRID] = CluDirectedGraph(
                    edges=[
                        CluEdge(source=e[0], destination=e[1], relation=e[2])
                        for e in field.edges
                    ],
                    roots=list(field.roots),
                )

        PLACEHOLDER = [""] * s.numTokens
        raw = (
            fields_dict.get("raw", PLACEHOLDER)
            or fields_dict.get("word", PLACEHOLDER)
            or PLACEHOLDER
        )
        start_offsets, end_offsets = ConversionUtils.create_character_offsets(raw)
        return Sentence(
            raw=raw,
            startOffsets=start_offsets,
            endOffsets=end_offsets,
            words=fields_dict.get("word", PLACEHOLDER) or PLACEHOLDER,
            tags=fields_dict.get("tag", None),
            lemmas=fields_dict.get("lemma", None),
            entities=fields_dict.get("entity", None),
            chunks=fields_dict.get("chunk", None),
            norms=fields_dict.get("norm", None),
            graphs=graphs,
        )
