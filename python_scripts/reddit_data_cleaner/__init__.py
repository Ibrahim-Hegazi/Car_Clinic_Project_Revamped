"""
reddit_data_cleaner - A modular package for cleaning and structuring Reddit data using LLMs.

This package contains:
- cleaner.py: Core logic for processing raw Reddit CSVs using a local LLM (Ollama).
- flow.py: Prefect flow that orchestrates the cleaning process.
- llm_runner.py: Builds prompts and manages LLM interaction (via Ollama).
- preprocessor.py: (Optional) Handles content validation and pre-cleaning filters.
- postprocessor.py: Handles post-cleaning transformations and formatting.
- utils.py: Shared file I/O and logging utilities.
"""

from . import cleaner, flow, llm_runner, preprocessor, postprocessor, utils
from .cleaner import run_llm_cleaning_logic
from .flow import reddit_llm_flow

__version__ = "1.0.0"

__all__ = [
    "run_llm_cleaning_logic",
    "reddit_llm_flow",
    "cleaner",
    "flow",
    "llm_runner",
    "preprocessor",
    "postprocessor",
    "utils"
]
