import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import ValidationError
from llm_client.errors import LLMClientError
from llm_client.manager import AsyncLLMManager
from llm_client.schemas import ChatMessage, ModelConfig

async def main():
    env_path = Path(__file__).resolve().parent / "config" / ".env"
    load_dotenv(dotenv_path=env_path)
    
    """ Obtener proveedor """
    mock = "--mock" in sys.argv[1:]
    arguments = [argument for argument in sys.argv[1:] if argument != "--mock"]
    if len(arguments) > 1:
        raise ValueError("Uso: python main.py [openai|anthropic] [--mock]")
    provider = arguments[0] if arguments else os.getenv("LLM_PROVIDER", "openai")
    provider = provider.strip().lower()
    
    model_variables = {
        "openai": "OPENAI_MODEL",
        "anthropic": "ANTHROPIC_MODEL",
    }
    
    if provider not in model_variables:
        raise ValueError(f"Proveedor no soportado: {provider}")
        
    model_variable = model_variables[provider]
    model = os.getenv(model_variable,"").strip()
    if mock and not model:
        model = f"mock-{provider}"
    if not model:
        raise ValueError(
            f"Falta configurar {model_variable} en el entorno."
        )

    config = ModelConfig(
        model=model,
        temperature=0.7,
        max_tokens=512,
    )
    
    messages = [
    ChatMessage(
        role="user",
        content="¿Qué es la entropía?",
    )]
    
    """ Llamamos al Manager """
    async with AsyncLLMManager(provider=provider,
                               max_concurrency=3,
                               mock=mock) as manager:
        print(f"Modo: {'mock (sin API)' if mock else 'API real'}")
        print(f"Proveedor: {provider}")
        print(f"Modelo: {config.model}")

        print("\nRespuesta completa:")
        response = await manager.generate(messages, config)
        print(response.text)

        print("\nRespuesta en streaming:")
        async for text in manager.stream(messages, config):
            print(text, end="", flush=True)

        print()

def run() -> int:
    try:
        asyncio.run(main())
        return 0
    except LLMClientError as exc:
        print(f"\nError del proveedor: {exc}", file=sys.stderr)
        return 1
    except ValidationError:
        print(
            "\nConfiguración o mensajes inválidos. "
            "Revisá los valores de entrada.",
            file=sys.stderr,
        )
        return 1
    except ValueError as exc:
        print(f"\nError de configuración: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(run())
