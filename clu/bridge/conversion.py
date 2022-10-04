from __future__ import annotations
from clu.bridge import processors
from clu.bridge import spacy
from clu.bridge import odinson
from clu.bridge.typing import Tokens, Indices

from enum import Enum
from typing import Dict, List, Literal, Optional, Set, Text, Tuple, Type
import abc


__all__ = ["ConversionUtils"]
class ConversionUtils:

  processors = processors.ConversionUtils
  spacy = spacy.ConversionUtils

#   /** Start character offsets for the raw tokens; start at 0 */
#   val startOffsets: Array[Int],
#   /** End character offsets for the raw tokens; start at 0 */
#   val endOffsets: Array[Int],
# exclude_none=True