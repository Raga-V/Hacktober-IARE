"""OpenAI-compatible inference client, open-weight models only.

DigitalOcean Serverless Inference is the default. Other providers that serve open-weight models are
fallbacks: the first provider whose key is set wins, or force one with LORE_PROVIDER.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

from openai import APIConnectionError, APITimeoutError, BadRequestError, InternalServerError, OpenAI, RateLimitError

PROVIDERS = {  # name: (base url, env var holding the key)
    "digitalocean": (os.environ.get("DO_INFERENCE_URL", "https://inference.do-ai.run/v1/"), "DO_MODEL_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "cerebras": ("https://api.cerebras.ai/v1", "CEREBRAS_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    # Google AI Studio: free key, no billing. Lore uses its open-weight Gemma models only, never Gemini.
    "google": ("https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY"),
    # Vertex AI Model Garden (open models as a service). Authenticates with the gcloud login, not a key.
    "vertex": (None, "VERTEX_PROJECT"),
    "ollama": (os.environ.get("OLLAMA_URL", "http://localhost:11434/v1"), None),
}

# Vertex has no model listing on its OpenAI endpoint; these open-weight MaaS models are tried in order.
# Each must be enabled once in the Model Garden console for the project.
VERTEX_MODELS = ["qwen/qwen3-235b-a22b-instruct-2507-maas", "deepseek-ai/deepseek-v3.1-maas",
                 "openai/gpt-oss-120b-maas"]

# Closed models that Lore must never use for its core steps.
CLOSED = re.compile(r"(claude|anthropic|gpt-[345]|chatgpt|(^|[/-])o[134]($|-)|gemini|grok)", re.I)
# Speech, guard and embedding models are not chat models.
NOT_CHAT = re.compile(r"(whisper|tts|guard|embed|compound|vision|rerank|moderation|^llamacpp:)", re.I)
# Open-weight families, in order of preference (matched with punctuation stripped).
PREFERRED = ["glm", "qwen3", "deepseekv3", "gptoss120b", "kimi", "llama3370b", "llama", "mistral", "qwen",
             "deepseek", "gptoss", "gemma", "phi"]

_client = None
_client_born = 0.0
_model = None
_provider = None


def provider():
    global _provider
    if _provider is None:
        forced = os.environ.get("LORE_PROVIDER", "").lower()
        if forced:
            if forced not in PROVIDERS:
                sys.exit(f"LORE_PROVIDER must be one of {', '.join(PROVIDERS)}")
            _provider = forced
        else:
            _provider = next((n for n, (_, env) in PROVIDERS.items() if env and os.environ.get(env)), None)
        if _provider is None:
            sys.exit("No model key set. Set DO_MODEL_KEY (DigitalOcean), or GROQ_API_KEY / CEREBRAS_API_KEY / "
                     "OPENROUTER_API_KEY / GEMINI_API_KEY, or LORE_PROVIDER=ollama for a local model.")
    return _provider


def vertex_url():
    region = os.environ.get("VERTEX_REGION", "us-central1")
    host = "aiplatform.googleapis.com" if region == "global" else f"{region}-aiplatform.googleapis.com"
    return f"https://{host}/v1/projects/{os.environ['VERTEX_PROJECT']}/locations/{region}/endpoints/openapi"


def vertex_token():
    gcloud = shutil.which("gcloud") or sys.exit("Vertex AI needs the gcloud CLI.")
    cmd = [gcloud, "auth", "print-access-token"] + ([os.environ["VERTEX_ACCOUNT"]] if os.environ.get("VERTEX_ACCOUNT") else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"gcloud could not print an access token: {r.stderr.strip()} Run: gcloud auth login")
    return r.stdout.strip()


def client():
    global _client, _client_born
    if provider() == "vertex" and _client is not None and time.time() - _client_born > 45 * 60:
        _client = None  # gcloud access tokens last an hour
    if _client is None:
        _client_born = time.time()
        if provider() == "vertex":
            _client = OpenAI(base_url=vertex_url(), api_key=vertex_token(), timeout=120, max_retries=6)
            return _client
        url, env = PROVIDERS[provider()]
        key = os.environ.get(env) if env else "ollama"
        if not key:
            sys.exit(f"{env} is not set for provider {provider()}.")
        if provider() == "ollama":
            # A laptop GPU can take minutes per batch, and a local 500 repeats identically, so don't retry it.
            _client = OpenAI(base_url=url, api_key=key, timeout=900, max_retries=0)
        else:
            # Free tiers answer 429 under parallel load; the client honours Retry-After.
            _client = OpenAI(base_url=url, api_key=key, timeout=120, max_retries=6)
    return _client


def list_models():
    if provider() == "vertex":
        return VERTEX_MODELS
    return sorted(m.id for m in client().models.list().data)


def is_open(model_id):
    return not CLOSED.search(model_id.replace("gpt-oss", ""))


def usable(model_id):
    if not is_open(model_id) or NOT_CHAT.search(model_id):
        return False
    # OpenRouter bills per token; without credits only the ":free" variants answer.
    return provider() != "openrouter" or model_id.endswith(":free")


def model():
    """LORE_MODEL if set (must be open-weight), else the best open-weight model listed by /v1/models."""
    global _model
    if _model:
        return _model
    chosen = os.environ.get("LORE_MODEL")
    if chosen:
        if not is_open(chosen):
            sys.exit(f"LORE_MODEL={chosen} is not an open-weight model; Lore only uses open models.")
        _model = chosen
        return _model
    if provider() == "vertex":
        for m in VERTEX_MODELS:  # first one enabled in this project wins
            try:
                client().chat.completions.create(model=m, max_tokens=1,
                                                 messages=[{"role": "user", "content": "hi"}])
                _model = m
                return _model
            except Exception as e:
                print(f"  {m}: not available ({type(e).__name__})", flush=True)
        sys.exit("No Vertex open model answered. Enable one in Model Garden, or set LORE_MODEL.")
    ids = [m for m in list_models() if usable(m)]
    for family in PREFERRED:
        hits = [m for m in ids if family in re.sub(r"[^a-z0-9]", "", m.lower())]
        if hits:
            _model = sorted(hits, key=lambda m: (-_size(m), len(m)))[0]  # largest, then plainest name
            return _model
    sys.exit(f"No open-weight model found in /v1/models: {ids}")


def _size(model_id):
    """Parameter count in billions parsed from the id ("gemma-3-27b-it" -> 27), 0 if absent."""
    m = re.search(r"(\d+(?:\.\d+)?)b\b", model_id.lower())
    return float(m.group(1)) if m else 0


def _parse(text):
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


_json_mode = True


def chat_json(system, user, max_tokens=4096):
    """One JSON-object completion. temperature=0, retry once on invalid JSON or a failed call (the retry at a
    slightly higher temperature, to escape repetition loops), and return None if both fail so the caller skips
    the batch.

    The system prompt is kept byte-identical across batches so the provider's prompt cache can reuse it.
    """
    global _json_mode
    if provider() == "google":
        # Gemma on AI Studio accepts neither system instructions nor JSON mode; the parser copes without.
        _json_mode = False
        messages = [{"role": "user", "content": f"{system}\n\n---\n\n{user}"}]
    else:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    attempt = 0
    while attempt < 2:
        kwargs = dict(model=model(), messages=messages, temperature=0.3 if attempt else 0, max_tokens=max_tokens)
        if _json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        if provider() == "ollama":  # Ollama's default context window would silently cut long batches
            kwargs["extra_body"] = {"options": {"num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "8192"))}}
        try:
            resp = client().chat.completions.create(**kwargs)
        except BadRequestError as e:
            if _json_mode and "response_format" in str(e):
                _json_mode = False  # model doesn't support JSON mode; rely on prompt + parser
                continue
            raise
        except (InternalServerError, APITimeoutError, APIConnectionError, RateLimitError) as e:
            attempt += 1
            print(f"  model call failed ({type(e).__name__}); " + ("retrying" if attempt < 2 else "skipping batch"),
                  flush=True)
            continue
        attempt += 1
        try:
            return _parse(resp.choices[0].message.content)
        except (json.JSONDecodeError, TypeError):
            if attempt == 1:
                messages = messages + [
                    {"role": "assistant", "content": resp.choices[0].message.content or ""},
                    {"role": "user", "content": "That was not valid JSON. Reply with only the JSON object."},
                ]
    return None
