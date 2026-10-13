"""Typed exceptions for truedemo."""

from __future__ import annotations


class TruedemoError(Exception):
    """Base class for all truedemo errors."""


class SpecError(TruedemoError):
    """The video spec is malformed or references something that does not exist."""


class ToolError(TruedemoError):
    """An external tool (ffmpeg, rsvg-convert, a browser, a TTS engine) failed."""


class ProviderError(TruedemoError):
    """The data provider could not supply the values the spec asked for."""
