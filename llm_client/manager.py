import os
import asyncio
from collections.abc import AsyncIterator
from contextlib import aclosing
from .clients import BaseLLMClient, get_client
from .schemas import ChatMessage, ModelConfig, ModelResponse

class AsyncLLMManager:
    def __init__(self, 
                 provider: str | None = None,
                 max_concurrency: int = 3,
                 *, mock: bool = False) -> None:
        if (isinstance(max_concurrency, bool) or not isinstance(max_concurrency, int)) or max_concurrency < 1:
            raise ValueError("max_concurrency debe ser mayor a cero.")
        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "openai")
        self.provider = provider.strip().lower()
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self.client: BaseLLMClient = get_client(self.provider, mock=mock)
     
    """ Función para generar respuesta completa """   
    async def generate(
        self,
        messages: list[ChatMessage],
        config: ModelConfig,
    ) -> ModelResponse:
        async with self._semaphore:
            return await self.client.generate(messages, config)
    
    """ Función para generar respuesta en fragmentos """
    async def stream(
        self,
        messages: list[ChatMessage],
        config: ModelConfig,
    ) -> AsyncIterator[str]:
        async with self._semaphore:
            async with aclosing(
                self.client.stream(messages, config)
            ) as stream:
                async for text in stream:
                    yield text
            
    """ Cerramos recursos del cliente """
    async def aclose(self) -> None:
        await self.client.aclose()
        
    """ Context manager para usar con `async with` """
    
    #Devolvemos el manager al entrar al contexto
    async def __aenter__(self) -> "AsyncLLMManager":
        return self

    #Cerramos el cliente al salir
    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        await self.aclose()
