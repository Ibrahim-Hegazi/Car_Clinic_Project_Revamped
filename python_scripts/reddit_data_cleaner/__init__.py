"""
reddit_data_cleaner - A modular package for cleaning and structuring Reddit data using LLMs.

This package contains:
- cleaner.py: Core logic for processing raw Reddit CSVs using a local LLM (Ollama).
- flow.py: Prefect flow that orchestrates the cleaning process.
- llm_runner.py: Encapsulates the subprocess logic for calling the LLM.
- preprocessor.py: Handles content validation and pre-cleaning filters.
- postprocessor.py: Handles post-cleaning transformations and output writing.
- utils.py: Shared utility functions.
"""

from .cleaner import run_llm_cleaning_logic
from .flow import reddit_llm_flow
from . import cleaner, flow#, llm_runner, preprocessor, postprocessor, utils

__version__ = "1.0.0"

__all__ = [
    "run_llm_cleaning_logic",
    "reddit_llm_flow",
    "cleaner",
    "flow",
]
""""
    "llm_runner",
    "preprocessor",
    "postprocessor",
    "utils"
]
"""