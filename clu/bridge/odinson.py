from __future__ import annotations
from enum import Enum
from typing import List, Literal, Set, Text, Tuple, Type
import abc
from pydantic import BaseModel
import pydantic

__all__ = ["Document"]

Tokens = List[Text]

class Fields(Text, Enum):
  # $type      ai.lum.odinson.*
  TOKENS_FIELD = "ai.lum.odinson.TokensField"
  GRAPH_FIELD = "ai.lum.odinson.GraphField"
  STRING_FIELD = "ai.lum.odinson.StringField"
  DATE_FIELD = "ai.lum.odinson.DateField"
  NUMBER_FIELD = "ai.lum.odinson.NumberField"
  NESTED_FIELD = "ai.lum.odinson.NestedField"
  #$type": "ai.lum.odinson.TokensField",

class Field(BaseModel, abc.ABC):
  name: Text
  type: Fields = pydantic.Field(alias="$type", default="ai.lum.odinson.Field")
  # def toJson: String = write(this)
  # def toPrettyJson: String = write(this, indent = 4)
  class Config:
      use_enum_values = True

class TokensField(Field):
  name: Text
  tokens: Tokens
  type: Literal[Fields.TOKENS_FIELD]

class GraphField(Field):
  name: Text
  edges: List[Tuple[int, int, Text]]
  roots: Set[int]
  type: Literal[Fields.GRAPH_FIELD]

class StringField(Field):
  name: Text
  string: Text
  type: Literal[Fields.STRING_FIELD]

class DateField(Field):
  name: Text
  date: Text
  type: Literal[Fields.DATE_FIELD]

class NumberField(Field):
  name: Text
  value: float
  type: Literal[Fields.NUMBER_FIELD]

class NestedField(Field):
  name: Text
  fields: List[Field]
  type: Literal[Fields.NESTED_FIELD]

class Sentence(BaseModel):
  numTokens: int
  fields: List[Field]

class Document(BaseModel):
  """clu.processors.Document"""
  id: Text
  metadata: List[Field]
  sentences: List[Sentence]
