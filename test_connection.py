import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OLLAMA_API_KEY") or os.getenv("OPENAI_API_KEY")
api_base = os.getenv("API_BASE", "https://ollama.com/v1")

print(f"Testing with API Key: {api_key[:10]}...{api_key[-4:]}")
print(f"Testing with API Base: {api_base}")

def test_llm():
    print("\n--- Testing LLM (Chat) ---")
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-oss:120b-cloud",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5
    }
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30)
        print(f"LLM Status: {response.status_code}")
        print(f"LLM Response: {response.text[:200]}")
    except Exception as e:
        print(f"LLM Error: {e}")

def test_embeddings_v1():
    print("\n--- Testing Embeddings (/v1/embeddings) ---")
    url = f"{api_base}/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "nomic-embed-text:latest",
        "input": "Hello world"
    }
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30)
        print(f"Embeddings (/v1) Status: {response.status_code}")
        print(f"Embeddings (/v1) Response: {response.text[:200]}")
    except Exception as e:
        print(f"Embeddings (/v1) Error: {e}")

def test_embeddings_api():
    print("\n--- Testing Embeddings (/api/embed) ---")
    # Base should be https://ollama.com for /api endpoints
    host = api_base.replace("/v1", "")
    url = f"{host}/api/embed"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "nomic-embed-text:latest",
        "input": "Hello world"
    }
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30)
        print(f"Embeddings (/api/embed) Status: {response.status_code}")
        print(f"Embeddings (/api/embed) Response: {response.text[:200]}")
    except Exception as e:
        print(f"Embeddings (/api/embed) Error: {e}")

def test_models():
    print("\n--- Listing All Models ---")
    url = f"{api_base}/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = httpx.get(url, headers=headers, timeout=30)
        print(f"Models Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            ids = [m['id'] for m in data.get('data', [])]
            print(f"Available Models ({len(ids)}):")
            for i in ids:
                print(f"  - {i}")
            
            embed_models = [i for i in ids if "embed" in i.lower()]
            print(f"\nPotential Embedding Models: {embed_models}")
        else:
            print(f"Models Response: {response.text}")
    except Exception as e:
        print(f"Models Error: {e}")

def test_embeddings_extra():
    # Try /api/embeddings and /v1/embeddings with model in path if applicable
    host = api_base.replace("/v1", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "nomic-embed-text:latest",
        "input": "Hello world"
    }
    
    paths = ["/api/embeddings", "/v1/embedding"]
    for p in paths:
        print(f"\n--- Testing Embeddings ({p}) ---")
        try:
            response = httpx.post(f"{host}{p}", headers=headers, json=payload, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

def test_api_tags():
    print("\n--- Listing Models (/api/tags) ---")
    host = api_base.replace("/v1", "")
    url = f"{host}/api/tags"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = httpx.get(url, headers=headers, timeout=30)
        print(f"Tags Status: {response.status_code}")
        print(f"Tags Response: {response.text[:500]}")
    except Exception as e:
        print(f"Tags Error: {e}")

def test_models():
    print("\n--- Listing All Models ---")
    url = f"{api_base}/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = httpx.get(url, headers=headers, timeout=30)
        print(f"Models Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Full Model Data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Models Response: {response.text}")
    except Exception as e:
        print(f"Models Error: {e}")

def test_embeddings_exhaustive():
    print("\n--- Exhaustive Embedding & Auth Tests ---")
    host = api_base.replace("/v1", "")
    
    # Auth variants
    auth_variants = [
        {"Authorization": f"Bearer {api_key}"},
    ]
    
    # Paths to try
    paths_to_try = [
        "/api/embed",
        "/api/embeddings",
        "/v1/embeddings",
        "/v1/embed",
    ]
    
    # Models from the actual list + common ones
    models_to_try = [
        "nomic-embed-text:latest",
        "nomic-embed-text",
        "gpt-oss:20b",
        "gpt-oss:120b",
        "gemma3:4b",
        "text-embedding-004"
    ]
    
    for h_var in auth_variants:
        headers = {"Content-Type": "application/json", **h_var}
        print(f"\n--- Testing Auth: Authorization (Bearer) ---")
        
        for m in models_to_try:
            print(f"\n>> Testing Model: {m}")
            for p in paths_to_try:
                url = f"{host}{p}"
                payload = {"model": m, "input": "test"}
                try:
                    response = httpx.post(url, headers=headers, json=payload, timeout=5)
                    if response.status_code != 404:
                        print(f"Path: {p:18} | Status: {response.status_code} | {response.text[:100]}")
                except Exception as e:
                    pass

from ollama import Client as OllamaClient

def test_ollama_library():
    print("\n--- Testing with Ollama Library ---")
    host = api_base.replace("/v1", "")
    client = OllamaClient(host=host, headers={"Authorization": f"Bearer {api_key}"})
    try:
        print("Listing models via library...")
        client.list()
        print(f"Library List Status: SUCCESS")
        print("Testing embed via library...")
        resp = client.embed(model="gemma3:4b", input="test")
        print(f"Library Embed Status: SUCCESS")
    except Exception as e:
        print(f"Library Error: {e}")

def test_embeddings_exhaustive():
    print("\n--- Exhaustive Embedding & Auth Tests ---")
    host = api_base.replace("/v1", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    paths_to_try = ["/api/embed", "/api/embeddings", "/v1/embeddings", "/v1/embed"]
    models_to_try = ["nomic-embed-text:latest", "nomic-embed-text", "gemma3:4b", "gpt-oss:20b"]
    
    for m in models_to_try:
        print(f"\n>> Testing Model: {m}")
        for p in paths_to_try:
            url = f"{host}{p}"
            try:
                response = httpx.post(url, headers=headers, json={"model": m, "input": "test"}, timeout=5)
                if response.status_code != 404:
                    print(f"Path: {p:18} | Status: {response.status_code} | {response.text[:100]}")
            except Exception as e:
                pass

if __name__ == "__main__":
    test_api_tags()
    test_models()
    test_llm()
    test_ollama_library()
    test_embeddings_exhaustive()
