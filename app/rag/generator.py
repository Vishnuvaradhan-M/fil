from __future__ import annotations
from typing import List
import logging
from .config import settings

logger = logging.getLogger("app.rag.generator")


class Generator:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        api_key = api_key or settings.GROQ_API_KEY
        model = model or settings.GROQ_MODEL
        logger.info("Initializing Groq generator model=%s", model)
        self.model = model
        self.client = None
        self.available = False
        if not api_key:
            logger.warning("GROQ_API_KEY not set; generator will be unavailable")
            return
        try:
            from groq import Groq  # lazy import

            self.client = Groq(api_key=api_key)
            self.available = True
        except Exception as exc:
            logger.warning("groq client unavailable: %s", exc)
            self.client = None
            self.available = False

    def _build_prompt(self, context: str, query: str) -> str:
        prompt = (
            "You are a hospital knowledge assistant.\n\n"
            "Guidelines:\n"
            "- Use ONLY the provided context. Do not invent facts or add information not present in the documents.\n"
            "- Do not copy large blocks verbatim from the source. Paraphrase and synthesize concise answers.\n"
            "- If the documents do not contain sufficient information to answer, respond exactly: \"The provided documents do not contain sufficient information.\"\n"
            "- Provide output in the following structured format:\n\n"
            "Answer Summary:\n"
            "<A concise 1-3 sentence summary that directly answers the question>\n\n"
            "Key Points:\n"
            "- Bullet point 1 (short)\n"
            "- Bullet point 2 (short)\n\n"
            "Sources:\n"
            "- filename1\n"
            "- filename2\n\n"
            "Context:\n"
            f"{context}\n\n"
            "Question:\n"
            f"{query}\n\n"
            "Respond concisely and follow the structure exactly."
        )
        return prompt

    def generate(self, context: str, query: str, max_tokens: int | None = None) -> str:
        prompt = self._build_prompt(context, query)
        if not self.available or self.client is None:
            logger.info("Generator unavailable; returning fallback message")
            return "RAG generation unavailable: generator dependency not installed or GROQ_API_KEY unset."
        try:
            # Call the underlying client using the correct method depending on the Groq SDK version.
            resp = None
            # Try common method names and call signatures.
            tried = []
            def try_call(fn, *args, **kwargs):
                try:
                    return fn(*args, **kwargs)
                except TypeError:
                    # signature mismatch, bubble up to try next
                    raise

            client = self.client
            # preferred order
            for method_name in ("generate", "create", "run", "predict", "complete"):
                if hasattr(client, method_name):
                    method = getattr(client, method_name)
                    tried.append(method_name)
                    # try common signatures
                    for call_args in (
                        {"model": self.model, "prompt": prompt, "max_tokens": max_tokens or 512},
                        (self.model, prompt, max_tokens or 512),
                        {"prompt": prompt, "max_tokens": max_tokens or 512},
                        (prompt,),
                    ):
                        try:
                            if isinstance(call_args, dict):
                                resp = method(**call_args)
                            else:
                                resp = method(*call_args)
                            break
                        except TypeError:
                            resp = None
                            continue
                    if resp is not None:
                        break
            if resp is None:
                logger.error("Unable to call Groq client; tried methods: %s", tried)
                return "RAG generation failed due to an internal error."

            # Extract text from common response shapes
            text = None
            # object-like with .data and .text
            try:
                if hasattr(resp, "data") and resp.data:
                    first = resp.data[0]
                    text = getattr(first, "text", None) or (first[0] if isinstance(first, (list, tuple)) and first else None)
            except Exception:
                text = None
            # dict-like responses
            if text is None and isinstance(resp, dict):
                # common keys
                for path in ("text", "output", "result", "outputs", "choices", "data"):
                    if path in resp and resp[path]:
                        candidate = resp[path]
                        # choices -> [{text:...}] or [{message:{content:...}}]
                        if isinstance(candidate, list):
                            c0 = candidate[0]
                            if isinstance(c0, dict):
                                text = c0.get("text") or (c0.get("message") and c0["message"].get("content")) or None
                                if text:
                                    break
                            elif isinstance(c0, str):
                                text = c0
                                break
                        elif isinstance(candidate, str):
                            text = candidate
                            break
            # fallback to str(resp)
            if text is None:
                text = str(resp)
            if "I do not have enough information" in text:
                return "I do not have enough information from the provided documents."
            return text.strip()
        except Exception as exc:
            logger.exception("Groq generation error: %s", exc)
            return "RAG generation failed due to an internal error."

