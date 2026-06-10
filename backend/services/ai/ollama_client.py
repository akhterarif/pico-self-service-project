import os
import requests


class OllamaClient:
    """Minimal Ollama client using the local Ollama HTTP API.

    Expects an Ollama server reachable at `OLLAMA_URL` env var (default http://ollama:11434).
    Uses model `qwen-2.5-7b` by default.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen-2.5-7b")

    def chat(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt}
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # Ollama's response shape can vary; prefer `text` or `response` fields
        return data.get("text") or data.get("response") or str(data)
