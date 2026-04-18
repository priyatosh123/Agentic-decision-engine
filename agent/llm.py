import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def _call(model, prompt, temperature=0.3, max_tokens=900):
    start = time.time()

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    response = requests.post(BASE_URL, headers=HEADERS, json=payload)

    end = time.time()

    if response.status_code != 200:
        return {
            "content": f"ERROR: {response.text}",
            "latency": 0,
            "model": model
        }

    data = response.json()

    return {
        "content": data["choices"][0]["message"]["content"],
        "latency": round(end - start, 3),
        "model": model
    }


MODEL_REASONING = "openai/gpt-oss-120b"
MODEL_ROUTER = "mistralai/mistral-7b-instruct"
MODEL_CRITIC = "google/gemma-4-31b"


def router_llm(prompt):
    return _call(MODEL_ROUTER, prompt, temperature=0.0, max_tokens=10)


def planner_llm(prompt):
    return _call(MODEL_REASONING, prompt)


def analyst_llm(prompt):
    return _call(MODEL_REASONING, prompt)


def critic_llm(prompt):
    return _call(MODEL_CRITIC, prompt)


def final_llm(prompt):
    return _call(MODEL_REASONING, prompt)


def safe_call(func, prompt):
    try:
        return func(prompt)
    except Exception as e:
        return {
            "content": f"ERROR: {str(e)}",
            "latency": 0,
            "model": "fallback"
        }