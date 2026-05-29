from langchain.chat_models import init_chat_model


def get_llm():
    return init_chat_model(
        base_url="http://127.0.0.1:1234/v1",
        model="google/gemma-4-26b-a4b",
        model_provider="openai",
        api_key="lm-studio",
    )