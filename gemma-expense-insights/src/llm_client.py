"""Thin wrapper around the local Ollama HTTP API.

Ollama exposes /api/generate on http://localhost:11434 by default. We use
JSON-mode (`format: "json"`) when we want structured output, and a low
temperature for repeatable answers.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import requests


class OllamaError(RuntimeError):
    pass


@dataclass
class OllamaClient:
    model: str = "gemma3:4b"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.1
    max_tokens: int = 256
    timeout_s: int = 120

    def ping(self) -> None:
        """Raise if the Ollama server isn't reachable or model isn't pulled."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
        except requests.RequestException as e:
            raise OllamaError(
                f"Cannot reach Ollama at {self.base_url}. "
                "Is the service running? Try `ollama serve` or restart the app."
            ) from e

        names = [m.get("name", "") for m in r.json().get("models", [])]
        if not any(self.model in n for n in names):
            raise OllamaError(
                f"Model '{self.model}' not found locally. "
                f"Pull it first:  ollama pull {self.model}"
            )

    def generate(self, prompt: str, *, json_mode: bool = False, retries: int = 2) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }
        if json_mode:
            payload["format"] = "json"

        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                r = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout_s,
                )
                r.raise_for_status()
                return r.json().get("response", "").strip()
            except requests.RequestException as e:
                last_err = e
                time.sleep(1 + attempt)
        raise OllamaError(f"Ollama generate failed after retries: {last_err}")

    def generate_json(self, prompt: str, schema_hint: str = "") -> dict:
        """Returns parsed JSON. Raises OllamaError on parse failure."""
        full_prompt = prompt
        if schema_hint:
            full_prompt += f"\n\nReturn ONLY valid JSON matching this shape:\n{schema_hint}"
        raw = self.generate(full_prompt, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise OllamaError(f"Model returned non-JSON: {raw[:200]!r}") from e
