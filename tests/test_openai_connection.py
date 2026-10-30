from openai import OpenAI
from app.config import settings


def main():
    if not settings.openai_api_key:
        raise RuntimeError(
            "Set OPENAI_API_KEY in your .env file first."
        )

    client = OpenAI(api_key=settings.openai_api_key)

    response = client.responses.create(
        model=settings.openai_model,
        input="Reply with exactly: OpenAI connection successful."
    )

    print(response.output_text)

if __name__ == "__main__":
    main()