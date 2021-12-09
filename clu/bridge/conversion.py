from __future__ import annotations
from clu.bridge import processors
from clu.bridge import odinson
from clu.bridge.typing import Tokens, Indices

from enum import Enum
from typing import Dict, List, Literal, Optional, Set, Text, Tuple, Type
import abc


__all__ = ["ConversionUtils"]
class ConversionUtils:
  """Conversion utilities for greater CLU family docs"""
  
  @staticmethod
  def to_odinson(doc: processors.Document) -> odinson.Document:
    pass

  @staticmethod
  def to_odinson_sentence(s: processors.Sentence) -> odinson.Sentence:
    pass

  @staticmethod
  def to_processors(doc: odinson.Document) -> processors.Document:
    return processors.Document(
      id = doc.id,
      sentences = [ConversionUtils.to_processors_sentence(s) for s in doc.sentences]
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
  def to_processors_sentence(s: odinson.Sentence) -> processors.Sentence:

    graphs: Optional[processors.GraphMap] = None
    # NOTE: by convention, these are non-plural
    fields_dict: Dict[Text, Optional[Tokens]] = {
      "raw" : None,
      "word" : None,
      "tag" : None,
      "lemma" : None,
      "entity" : None,
      "chunk" : None,
      "norm" : None
    }

    def is_token_field(field: odinson.Field, name: Optional[odinson.Fields] = None) -> bool:
      _is_token_field = isinstance(field, odinson.TokensField)
      if name is not None:
        return True if _is_token_field and field.name == name else False
      return _is_token_field
    

    for field in s.fields:
      if is_token_field(field) and field.name in fields_dict:
        fields_dict[field.name] = field.tokens
      elif isinstance(field, odinson.GraphField):
        # assume graph is hybrid
        graphs = graphs or dict()
        graphs[processors.Graphs.HYBRID_DEPENDENCIES] = processors.DirectedGraph(
          edges = [processors.Edge(source=e[0], destination=e[1], relation=e[2]) for e in field.edges],
          roots = list(field.roots)
        )

    PLACEHOLDER = [""] * s.numTokens
    raw = fields_dict.get("raw", PLACEHOLDER) or fields_dict.get("word", PLACEHOLDER) or PLACEHOLDER
    start_offsets, end_offsets = ConversionUtils.create_character_offsets(raw)
    return processors.Sentence(
      raw = raw,
      startOffsets = start_offsets,
      endOffsets = end_offsets,
      words = fields_dict.get("word", PLACEHOLDER) or PLACEHOLDER,
      tags = fields_dict.get("tag", None),
      lemmas = fields_dict.get("lemma", None),
      entities = fields_dict.get("entity", None),
      chunks= fields_dict.get("chunk", None),
      norms = fields_dict.get("norm", None),
      graphs = graphs
    )


#   /** Start character offsets for the raw tokens; start at 0 */
#   val startOffsets: Array[Int],
#   /** End character offsets for the raw tokens; start at 0 */
#   val endOffsets: Array[Int],
# exclude_none=True