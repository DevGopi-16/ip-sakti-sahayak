import os

from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


load_dotenv()


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        },
    )


def get_llm_groq():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set."
        )

    return ChatGroq(
        model="qwen/qwen3.6-27b",
        temperature=0.1,
        max_tokens=1200,
        reasoning_effort="none",
        groq_api_key=api_key,
    )


def get_llm_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is not set."
        )

    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        temperature=0.0,
        max_tokens=1200,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def get_llm_gemini():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,
        max_output_tokens=2048,
        google_api_key=api_key,
    )


def get_llm():
    groq_key = os.getenv("GROQ_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    llms = []

    if groq_key:
        llms.append(get_llm_groq())

    if openrouter_key:
        llms.append(get_llm_openrouter())

    if gemini_key:
        llms.append(get_llm_gemini())

    if not llms:
        raise ValueError(
            "No LLM API keys found. Please set at least one of: "
            "GROQ_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY."
        )

    if len(llms) == 1:
        return llms[0]

    return llms[0].with_fallbacks(llms[1:])