"""Code generation utilities for mazure.

Provides tools for:
- Schema generation from discovery samples
- Response synthesis based on patterns
- Service validation against live Azure
"""

from .response_synthesizer import ResponseSynthesizer

__all__ = ['ResponseSynthesizer']
