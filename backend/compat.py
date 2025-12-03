"""Compatibility helpers for newer Agno versions.

This module backfills the legacy ``agno.sync_layer.SyncLayer`` entrypoint that
older tests expect to patch while still allowing the latest Agno models to run
unchanged when the patch is not in place.  The unit tests monkey patch
``SyncLayer._create_completion``; we detect that hook and route model invocations
through it, otherwise we defer to the original model implementation.
"""

from __future__ import annotations

import types
from typing import Any, Callable, List, Optional

import agno
from agno.models.google import Gemini
from agno.models.message import Message
from agno.models.response import ModelResponse


if not hasattr(agno, "sync_layer"):
    agno.sync_layer = types.SimpleNamespace()  # type: ignore[attr-defined]


class _CompatSyncLayer:
    """Placeholder SyncLayer; tests are expected to monkey patch this."""

    @staticmethod
    def _create_completion(*_args: Any, **_kwargs: Any) -> ModelResponse:
        raise RuntimeError(
            "SyncLayer._create_completion was called without being patched; "
            "tests should provide a MagicMock side effect."
        )


if not hasattr(agno.sync_layer, "SyncLayer"):
    agno.sync_layer.SyncLayer = _CompatSyncLayer  # type: ignore[attr-defined]


_placeholder_method = agno.sync_layer.SyncLayer._create_completion
_original_invoke = Gemini.invoke


def _call_mocked_completion(
    method: Callable[..., Any],
    model: Gemini,
    messages: List[Message],
    assistant_message: Message,
    response_format: Optional[Any] = None,
    tools: Optional[List[Any]] = None,
    tool_choice: Optional[Any] = None,
    run_response: Optional[Any] = None,
) -> ModelResponse:
    completion = method(
        model,
        messages,
        assistant_message=assistant_message,
        response_format=response_format,
        tools=tools,
        tool_choice=tool_choice,
        run_response=run_response,
    )
    if isinstance(completion, ModelResponse):
        return completion
    return ModelResponse(content=completion)


def _compat_invoke(
    self: Gemini,
    messages: List[Message],
    assistant_message: Message,
    response_format: Optional[Any] = None,
    tools: Optional[List[Any]] = None,
    tool_choice: Optional[Any] = None,
    run_response: Optional[Any] = None,
) -> ModelResponse:
    sync_layer = getattr(agno, "sync_layer", None)
    method = getattr(getattr(sync_layer, "SyncLayer", None), "_create_completion", None)
    if method is not None and method is not _placeholder_method:
        return _call_mocked_completion(
            method,
            self,
            messages,
            assistant_message,
            response_format=response_format,
            tools=tools,
            tool_choice=tool_choice,
            run_response=run_response,
        )
    return _original_invoke(
        self,
        messages,
        assistant_message,
        response_format=response_format,
        tools=tools,
        tool_choice=tool_choice,
        run_response=run_response,
    )


Gemini.invoke = _compat_invoke  # type: ignore[assignment]


def get_sync_layer_method() -> Optional[Callable[..., Any]]:
    sync_layer = getattr(agno, "sync_layer", None)
    return getattr(getattr(sync_layer, "SyncLayer", None), "_create_completion", None)


def is_sync_layer_mocked() -> bool:
    method = get_sync_layer_method()
    return method is not None and method is not _placeholder_method
