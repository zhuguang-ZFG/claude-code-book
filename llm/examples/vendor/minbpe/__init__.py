"""Local entrypoint for the unmodified minbpe BasicTokenizer subset.

Unlike upstream's package entrypoint, this does not import RegexTokenizer
or GPT4Tokenizer, so the basic example needs no regex/tiktoken dependency.
"""

from .base import merge
from .basic import BasicTokenizer

__all__ = ["BasicTokenizer", "merge"]
