import re
import tiktoken
from typing import List

ENCODER = tiktoken.encoding_for_model("gpt-4o")


def split_sentences(text: str) -> List[str]:
    return re.split(r'(?<=[.!?])\s+', text)


def chunk_text(text: str, chunk_tokens: int = 256, overlap_tokens: int = 64) -> List[str]:
    sentences = split_sentences(text)
    chunks = []
    current_tokens = []
    current_count = 0

    for sent in sentences:
        sent_tokens = ENCODER.encode(sent)
        sent_len = len(sent_tokens)

        if current_count + sent_len > chunk_tokens and current_tokens:
            chunks.append(ENCODER.decode(current_tokens))
            # Keep overlap
            overlap_start = max(0, len(current_tokens) - overlap_tokens)
            current_tokens = current_tokens[overlap_start:]
            current_count = len(current_tokens)

        current_tokens.extend(sent_tokens)
        current_count += sent_len

    if current_tokens:
        chunks.append(ENCODER.decode(current_tokens))

    return chunks
