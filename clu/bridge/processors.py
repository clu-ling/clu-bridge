from __future__ import annotations
from clu.bridge.typing import Tokens, Indices
from enum import Enum
from typing import Dict, ForwardRef, List, Optional, Text, Tuple
from pydantic import BaseModel, Extra, Field, PrivateAttr, validate_arguments

__all__ = ["Document", "Sentence", "DirectedGraph", "Graphs", "Edge"]

GraphMap = Dict[ForwardRef("Graphs"), ForwardRef("DirectedGraph")]

# see https://github.com/clulab/processors/blob/master/main/src/main/scala/org/clulab/struct/GraphMap.scala
class Graphs(Text, Enum):
  UNIVERSAL_BASIC = "universal-basic" # basic Universal dependencies
  UNIVERSAL_ENHANCED = "universal-enhanced" # collapsed (or enhanced) Universal dependencies
  STANFORD_BASIC = "stanford-basic" # basic Stanford dependencies
  STANFORD_COLLAPSED = "stanford-collapsed" # collapsed Stanford dependencies
  SEMANTIC_ROLES = "semantic-roles" # semantic roles from CoNLL 2008-09, which includes PropBank and NomBank
  ENHANCED_SEMANTIC_ROLES = "enhanced-semantic-roles" # enhanced semantic roles
  HYBRID_DEPENDENCIES = "hybrid" # graph that merges ENHANCED_SEMANTIC_ROLES and UNIVERSAL_ENHANCED

class Edge(BaseModel):
  source: int
  destination: int
  relation: Text

class DirectedGraph(BaseModel):
  edges: List[Edge]
  roots: List[int]

class Sentence(BaseModel):
  raw: Tokens
  words: Tokens
  tags: Optional[Tokens] = None
  lemmas: Optional[Tokens] = None
  entities: Optional[Tokens] = None
  chunks: Optional[Tokens] = None
  norms: Optional[Tokens] = None
  startOffsets: Optional[Indices] = None
  endOffsets: Optional[Indices] = None
  graphs: Optional[Dict[Graphs, DirectedGraph]] = None
  # tell pydantic to use enum *values*
  class Config:
      use_enum_values = True
      underscore_attrs_are_private = True
      validate_assignment = True
      extra = Extra.allow  # "ignore" # vs. "allow"

class Document(BaseModel):
  """clu.processors.Document"""
  id: Optional[Text] = None
  text: Optional[Text] = None
  sentences: List[Sentence]
  class Config:
      use_enum_values = True
      underscore_attrs_are_private = True
      validate_assignment = True
      extra = Extra.allow  # "ignore" # vs. "allow"