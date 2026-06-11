import os
from typing import List

import requests


class OllamaClient:
    """Robust Ollama client with fallback hosts and mock mode.

    It will try the configured `OLLAMA_URL`, then localhost and 127.0.0.1 on the same port.
    This helps when running the backend on-host (where `ollama` DNS is not resolvable)
    or inside Docker Compose (where `ollama` service name should resolve).
    
    Set OLLAMA_MOCK_MODE=1 to enable mock responses for testing when Ollama is unavailable.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.mock_mode = os.getenv("OLLAMA_MOCK_MODE", "").lower() in ("1", "true", "yes")
        configured = base_url or os.getenv("OLLAMA_URL")
        default = "http://ollama:11434"
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma")
        # Build a list of candidate base URLs to try, in order
        candidates: List[str] = []
        if configured:
            candidates.extend([u.strip() for u in configured.split(",") if u.strip()])
        # always try the default service name first
        if default not in candidates:
            candidates.append(default)
        # try localhost variants using the same port as the last candidate
        try:
            port = int(candidates[0].rsplit(":", 1)[-1]) if ":" in candidates[0] else 11434
        except Exception:
            port = 11434
        localhosts = [f"http://localhost:{port}", f"http://127.0.0.1:{port}"]
        for h in localhosts:
            if h not in candidates:
                candidates.append(h)

        self.candidates = candidates

    def _try_post(self, url: str, payload: dict, timeout: int = 60) -> dict:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def _parse_error_message(self, response: requests.Response) -> str:
        try:
            body = response.json()
            if isinstance(body, dict):
                error = body.get("error")
                if isinstance(error, dict):
                    return error.get("message") or str(error)
                if isinstance(error, str):
                    return error
            return response.text
        except ValueError:
            return response.text

    def _flatten_response(self, data: dict) -> str:
        if not isinstance(data, dict):
            return str(data)

        if "text" in data and isinstance(data["text"], str):
            return data["text"]

        if "response" in data and isinstance(data["response"], str):
            return data["response"]

        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                if "message" in first and isinstance(first["message"], dict):
                    return first["message"].get("content", "")
                if "text" in first:
                    return first.get("text", "")
            return str(first)

        if "error" in data:
            return str(data["error"])

        return str(data)

    def chat(self, prompt: str) -> str:
        # If mock mode is enabled, return mock responses
        if self.mock_mode:
            return self._generate_mock_response(prompt)
        
        errors = []
        # Try several plausible Ollama endpoints to support different versions
        endpoints = [
            ("/v1/chat/completions", {"model": self.model, "messages": [{"role": "user", "content": prompt}]}),
            ("/api/chat", {"model": self.model, "prompt": prompt}),
            ("/api/generate", {"model": self.model, "prompt": prompt}),
            ("/api/chat/completions", {"model": self.model, "messages": [{"role": "user", "content": prompt}]}),
            ("/api/completions", {"model": self.model, "messages": [{"role": "user", "content": prompt}]}),
            ("/completions", {"model": self.model, "messages": [{"role": "user", "content": prompt}]}),
            ("/v1/completions", {"model": self.model, "prompt": prompt}),
        ]

        for base in self.candidates:
            for ep, payload in endpoints:
                url = f"{base.rstrip('/')}{ep}"
                try:
                    data = self._try_post(url, payload)
                    return self._flatten_response(data)
                except requests.exceptions.HTTPError as http_err:
                    status = http_err.response.status_code
                    msg = self._parse_error_message(http_err.response)
                    if status == 404 and self.model in msg and "not found" in msg.lower():
                        raise RuntimeError(
                            f"Ollama model not found: {self.model}. "
                            f"Pull or install the model in Ollama. Server response: {msg}"
                        )
                    errors.append(f"{url}: HTTP {status} ({msg})")
                    continue
                except requests.exceptions.RequestException as exc:
                    errors.append(f"{url}: {exc}")
                    continue

        raise RuntimeError("Ollama API unreachable. Tried: " + "; ".join(errors))

    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock responses for testing when Ollama is unavailable."""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["hello", "hi", "hey", "greetings"]):
            return f"Hello! I'm {self.model} running in mock mode. How can I assist you today?"
        
        if any(word in prompt_lower for word in ["how are you", "how do you feel", "you doing"]):
            return f"I'm functioning well, thank you for asking! I'm {self.model} in test mode."
        
        if any(word in prompt_lower for word in ["what", "which", "who", "when", "where", "why"]):
            return f"That's an interesting question! As {self.model} in mock mode, I'd normally process this with the full model, but for now I can tell you this is a test response."
        
        if "math" in prompt_lower or "calculate" in prompt_lower:
            return "I can help with math! In production mode with Ollama, I would calculate this for you. Currently in mock mode."
        
        # Default response
        return f"Thank you for your message. I'm {self.model} running in mock/test mode. This is a demonstration response."
