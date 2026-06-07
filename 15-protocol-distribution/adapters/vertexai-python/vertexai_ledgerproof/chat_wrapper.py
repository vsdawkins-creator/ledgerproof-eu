"""ChatSession wrapper for multi-turn conversations.

Emits one `chatbot_session/v1` receipt per send_message turn.
"""
from __future__ import annotations

import uuid
from typing import Any

from .emitter import emit_receipt


class LedgerProofChatSession:
    """Wraps `vertexai.generative_models.ChatSession`."""

    def __init__(
        self,
        session: Any,
        *,
        model_name: str,
        project: str | None,
        location: str | None,
        lpr_schema: str = "chatbot_session/v1",
        session_id: str | None = None,
    ) -> None:
        self._session = session
        self._model_name = model_name
        self._project = project
        self._location = location
        self._lpr_schema = lpr_schema
        self._session_id = session_id or f"urn:lpr:session:{uuid.uuid4()}"
        self._turn = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self._session, name)

    @property
    def session_id(self) -> str:
        return self._session_id

    def send_message(
        self,
        content: Any,
        *,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        input_text = _to_text(content)
        turn_index = self._turn
        self._turn += 1

        if stream:
            iterator = self._session.send_message(
                content, stream=True, **kwargs
            )
            return self._wrap_stream(iterator, input_text, turn_index)

        resp = self._session.send_message(content, stream=False, **kwargs)
        try:
            emit_receipt(
                self._lpr_schema,
                model=self._model_name,
                project=self._project,
                location=self._location,
                input_text=input_text,
                output_text=_response_text(resp),
                extra={
                    "session_id": self._session_id,
                    "turn_index": turn_index,
                },
            )
        except Exception:
            pass
        return resp

    def _wrap_stream(self, iterator: Any, input_text: str, turn_index: int) -> Any:
        chunks: list[str] = []
        for chunk in iterator:
            try:
                t = _response_text(chunk)
                if t:
                    chunks.append(t)
            except Exception:
                pass
            yield chunk
        try:
            emit_receipt(
                self._lpr_schema,
                model=self._model_name,
                project=self._project,
                location=self._location,
                input_text=input_text,
                output_text="".join(chunks),
                extra={
                    "session_id": self._session_id,
                    "turn_index": turn_index,
                },
            )
        except Exception:
            pass


def _to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, (list, tuple)):
        return "\n".join(_to_text(c) for c in content)
    txt = getattr(content, "text", None)
    if isinstance(txt, str):
        return txt
    return repr(content)


def _response_text(resp: Any) -> str:
    txt = getattr(resp, "text", None)
    if isinstance(txt, str):
        return txt
    try:
        parts = resp.candidates[0].content.parts
        return "".join(getattr(p, "text", "") for p in parts)
    except Exception:
        return ""
