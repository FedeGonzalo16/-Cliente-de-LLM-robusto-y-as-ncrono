from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
import anthropic
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from contextlib import contextmanager
import os

import openai
from .schemas import ChatMessage, ModelConfig, ModelResponse
from .errors import (
    LLMClientError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMNetworkError,
)

#Errores de los SDK a errores de nuestra app."""
@contextmanager
def handle_api_errors():
    try:
        yield
    except (
        openai.AuthenticationError,
        anthropic.AuthenticationError,
    ) as exc:
        raise LLMAuthenticationError(
            "El proveedor rechazó las credenciales."
        ) from exc
    except (
        openai.RateLimitError,
        anthropic.RateLimitError,
    ) as exc:
        raise LLMRateLimitError(
            "Se alcanzó un límite de solicitudes o de cuota."
        ) from exc
    except (
        openai.APIConnectionError,
        anthropic.APIConnectionError,
    ) as exc:
        raise LLMNetworkError(
            "No se pudo completar la conexión con el proveedor."
        ) from exc
    except (
        openai.APIError,
        anthropic.APIError,
    ) as exc:
        raise LLMClientError(
            "El proveedor devolvió un error al procesar la solicitud."
        ) from exc

#Clase abstracta que heredan clientes de LLM, contrato asíncrono para generar una respuesta a partir de un prompt por medio de X LLM
class BaseLLMClient(ABC):
    
    #Devolver resp completa
    @abstractmethod
    async def generate(
        self,
        messages: list[ChatMessage],
        config: ModelConfig,
        ) -> ModelResponse:
       pass
   
   #Devolver resp en fragmentos
    @abstractmethod
    async def stream(
        self,
        messages: list[ChatMessage],
        config: ModelConfig,
        ) -> AsyncIterator[str]:
        pass
    
    # Cerramos recursos del cliente
    @abstractmethod
    async def aclose(self) -> None:
        pass
        
""" Constructor OpenAIClient """
class OpenAIClient(BaseLLMClient):
    def __init__(self, sdk=None) -> None:
        if sdk is not None:
            self.client = sdk
            return
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada.")
        self.client = AsyncOpenAI(api_key=api_key,
                                  timeout=30.0,
                                  max_retries=2)
        
    """ Función para generar respuesta completa """
    async def generate(self, messages: list[ChatMessage], config: ModelConfig) -> ModelResponse:
        with handle_api_errors():
            response = await self.client.chat.completions.create(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                messages=[{"role": msg.role, "content": msg.content} for msg in messages]
            )
            
            """ Devolvemos un objeto ModelResponse con el texto generado, el proveedor y el modelo utilizado. """
            return ModelResponse(
                text=response.choices[0].message.content or "",
                provider="openai",
                model=config.model
            )

    """ Función para generar respuesta en fragmentos, progrsiva """
    async def stream(
        self,
        messages: list[ChatMessage],
        config: ModelConfig,
        ) -> AsyncIterator[str]:
        with handle_api_errors():
            stream = await self.client.chat.completions.create(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                messages=[{"role": msg.role, "content": msg.content} for msg in messages],
                stream=True
            )
            async with stream:
                async for chunk in stream:
                    if not chunk.choices:
                        continue
                    text = chunk.choices[0].delta.content
                    if text:
                        yield text
                        
    async def aclose(self) -> None:
        await self.client.close()

""" Constructor AnthropicClient """
class AnthropicClient(BaseLLMClient):
    def __init__(self, sdk=None) -> None:
        if sdk is not None:
            self.client = sdk
            return
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Falta configurar ANTHROPIC_API_KEY.")
        self.client = AsyncAnthropic(api_key=api_key,
                                     timeout=30.0,
                                     max_retries=2)
    
    """ Funcion para devolver resp completa """
    def prepare_messages(self, messages: list[ChatMessage]) -> dict:
        system_messages = []
        conversation = []
        for message in messages:
            if message.role == "system":
                system_messages.append(message.content)
            else:
                conversation.append({"role": message.role,
                                 "content": message.content})
        if not conversation:
            raise ValueError("La conversación no puede estar vacía. Porfavor, incluya un mensaje. ")
        
        """ Preparar los mensajes para la llamada a la api """
        payload = {"messages": conversation}
        if system_messages:
            payload["system"] = "\n\n".join(system_messages)
        return payload
            
    """ Función para generar resp completa """
    async def generate(self, messages: list[ChatMessage], config: ModelConfig) -> ModelResponse:
        with handle_api_errors():
            payload = self.prepare_messages(messages)
            response = await self.client.messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                **payload,
            )
            
            """ Devolvemos un objeto ModelResponse con el texto generado, el proveedor y el modelo utilizado. """
            text = "".join(block.text for block in response.content if block.type == "text")
            return ModelResponse(
                text=text,
                provider="anthropic",
                model=config.model
            )
        
    """ Función para generar respuestas en streaming """
    async def stream(
        self,
        messages: list[ChatMessage],
        config: ModelConfig,
        ) -> AsyncIterator[str]:
        payload = self.prepare_messages(messages)
        
        with handle_api_errors():
            async with self.client.messages.stream(
                model=config.model,
                max_tokens=config.max_tokens,
                **payload,
            ) as stream:
                async for text in stream.text_stream:
                    if text:
                        yield text
    
    async def aclose(self) -> None:
        await self.client.close()
    
""" Obtención de cliente según proveedor configurado """
def get_client(provider: str, *, mock: bool = False) -> BaseLLMClient:
    if provider not in {"openai", "anthropic"}:
        raise ValueError(f"Proveedor desconocido: {provider}")
    sdk = None
    if mock:
        from ._mock_sdks import MockSDK

        sdk = MockSDK(provider)
    if provider == "openai":
        return OpenAIClient(sdk=sdk)
    elif provider == "anthropic":
        return AnthropicClient(sdk=sdk)
