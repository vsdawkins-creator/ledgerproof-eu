"""LedgerProofGenerativeModel — Vertex AI GenerativeModel wrapper.

Wraps `vertexai.generative_models.GenerativeModel` so that every
`generate_content` call emits a side-channel LedgerProof receipt that
captures Vertex AI's project + location (EU data residency).

C7: response payload is returned unchanged. Receipts are out-of-band.
C6: streaming is supported — the receipt is emitted after the stream
    finalizes, with the concatenated output digest. Intermediate chunks
    are yielded immediately and unmodified.
"""
from __future__ import annotations

from typing import Any, Iterable, Iterator

from .emitter import emit_receipt
from .chat_wrapper import LedgerProofChatSession


def _resolve_vertex_init() -> tuple[str | None, str | None]:
    """Best-effort lookup of the current vertexai.init(project, location).

    Vertex AI does not expose a stable public accessor; we read the
    private module attribute when available, falling back to None.
    """
    try:
        import vertexai  # type: ignore

        init_mod = getattr(vertexai, "init", None)
        # Newer SDKs expose `vertexai._project` / `vertexai._location` via
        # the global config singleton. Use defensive getattr.
        proj = getattr(vertexai, "_project", None) or getattr(
            getattr(vertexai, "_config", object()), "project", None
        )
        loc = getattr(vertexai, "_location", None) or getattr(
            getattr(vertexai, "_config", object()), "location", None
        )
        return proj, loc
    except Exception:
        return None, None


class LedgerProofGenerativeModel:
    """Drop-in wrapper around `vertexai.generative_models.GenerativeModel`."""

    def __init__(
        self,
        model_name: str,
        *,
        lpr_schema: str = "generated_content/v1",
        lpr_project: str | None = None,
        lpr_location: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Late import so the package is import-safe without vertexai
        # installed (e.g. doc builds).
        from vertexai.generative_models import GenerativeModel  # type: ignore

        self._model = GenerativeModel(model_name, **kwargs)
        self._model_name = model_name
        self._lpr_schema = lpr_schema

        proj, loc = _resolve_vertex_init()
        self._project = lpr_project or proj
        self._location = lpr_location or loc

    # -- attribute fall-through ------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        return getattr(self._model, name)

    # -- core API --------------------------------------------------------------

    def generate_content(
        self,
        contents: Any,
        *,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        input_text = _to_text(contents)

        if stream:
            iterator = self._model.generate_content(
                contents, stream=True, **kwargs
            )
            return self._wrap_stream(iterator, input_text)

        resp = self._model.generate_content(contents, stream=False, **kwargs)
        output_text = _response_text(resp)
        try:
            emit_receipt(
                self._lpr_schema,
                model=self._model_name,
                project=self._project,
                location=self._location,
                input_text=input_text,
                output_text=output_text,
            )
        except Exception:
            # C7: never let receipt emission impact caller.
            pass
        return resp

    def _wrap_stream(
        self, iterator: Iterable[Any], input_text: str
    ) -> Iterator[Any]:
        chunks: list[str] = []
        for chunk in iterator:
            try:
                text = _response_text(chunk)
                if text:
                    chunks.append(text)
            except Exception:
                pass
            yield chunk  # C7: never mutate or delay payload
        try:
            emit_receipt(
                self._lpr_schema,
                model=self._model_name,
                project=self._project,
                location=self._location,
                input_text=input_text,
                output_text="".join(chunks),
            )
        except Exception:
            pass

    def start_chat(self, **kwargs: Any) -> "LedgerProofChatSession":
        session = self._model.start_chat(**kwargs)
        return LedgerProofChatSession(
            session,
            model_name=self._model_name,
            project=self._project,
            location=self._location,
            lpr_schema="chatbot_session/v1",
        )


# -- helpers -------------------------------------------------------------------


def _to_text(contents: Any) -> str:
    """Best-effort conversion of Vertex AI prompt content to a flat string."""
    if isinstance(contents, str):
        return contents
    if isinstance(contents, (list, tuple)):
        return "\n".join(_to_text(c) for c in contents)
    # vertexai Part / Content objects expose .text
    txt = getattr(contents, "text", None)
    if isinstance(txt, str):
        return txt
    return repr(contents)


def _response_text(resp: Any) -> str:
    txt = getattr(resp, "text", None)
    if isinstance(txt, str):
        return txt
    # GenerationResponse: candidates[0].content.parts[*].text
    try:
        parts = resp.candidates[0].content.parts
        return "".join(getattr(p, "text", "") for p in parts)
    except Exception:
        return ""
