#!/usr/bin/env python3
"""
Local LLM inference wrapper using CTransformers (GGUF models on CPU).
Provides a drop-in replacement for _llm_generate when API keys are unavailable
or when the user explicitly enables Local Mode.
"""

import os
import sys
from pathlib import Path

LOCAL_LLM_ENABLED = False
LOCAL_MODEL = None
LOCAL_MODEL_PATH = None

# Default model: Qwen2.5-3B-Instruct Q4_K_M (~1.9 GB)
# Fast enough on CPU for short answers, capable enough for construction queries
DEFAULT_MODEL_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
DEFAULT_MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


def get_local_model_path() -> Path:
    """Return path to downloaded GGUF model, or None if not downloaded."""
    path = MODELS_DIR / DEFAULT_MODEL_FILE
    return path if path.exists() else None


def download_model():
    """Download the default GGUF model from HuggingFace Hub."""
    global LOCAL_MODEL_PATH
    path = get_local_model_path()
    if path:
        LOCAL_MODEL_PATH = path
        return path
    
    try:
        from huggingface_hub import hf_hub_download
        print(f"Downloading {DEFAULT_MODEL_FILE}... This may take a few minutes.")
        downloaded = hf_hub_download(
            repo_id=DEFAULT_MODEL_REPO,
            filename=DEFAULT_MODEL_FILE,
            local_dir=str(MODELS_DIR),
            local_dir_use_symlinks=False,
        )
        LOCAL_MODEL_PATH = Path(downloaded)
        print(f"Model downloaded to {LOCAL_MODEL_PATH}")
        return LOCAL_MODEL_PATH
    except Exception as e:
        print(f"Failed to download model: {e}")
        return None


def init_local_llm(model_path: Path = None) -> bool:
    """Initialize the local LLM. Returns True if successful."""
    global LOCAL_LLM_ENABLED, LOCAL_MODEL, LOCAL_MODEL_PATH
    
    try:
        from ctransformers import AutoModelForCausalLM
    except ImportError:
        print("ctransformers not installed. Local LLM unavailable.")
        return False
    
    path = model_path or get_local_model_path()
    if not path:
        path = download_model()
    if not path:
        return False
    
    try:
        print(f"Loading local LLM from {path}...")
        LOCAL_MODEL = AutoModelForCausalLM.from_pretrained(
            str(path),
            model_type="qwen",  # qwen, llama, mistral, etc.
            context_length=4096,
            threads=os.cpu_count() or 4,
            gpu_layers=0,  # CPU only
        )
        LOCAL_LLM_ENABLED = True
        print("Local LLM loaded successfully.")
        return True
    except Exception as e:
        print(f"Failed to load local LLM: {e}")
        return False


def local_generate(prompt: str, max_new_tokens: int = 300) -> str:
    """Generate text using the local CPU model."""
    if not LOCAL_LLM_ENABLED or LOCAL_MODEL is None:
        return "[Error: Local LLM not initialized. Set USE_LOCAL_LLM=true or download a model.]"
    
    try:
        # Qwen uses chat template
        formatted = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        result = LOCAL_MODEL(
            formatted,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            stop=["<|im_end|>", "<|im_start|>"],
        )
        return result.strip()
    except Exception as e:
        return f"[Error: Local LLM generation failed: {e}]"


def is_local_llm_ready() -> bool:
    return LOCAL_LLM_ENABLED and LOCAL_MODEL is not None


if __name__ == "__main__":
    if init_local_llm():
        test_prompt = "What is the concrete strength required for structural columns in a typical office building?"
        print("\nTest prompt:", test_prompt)
        print("\nResponse:")
        print(local_generate(test_prompt, max_new_tokens=150))
    else:
        print("Could not initialize local LLM.")
