"""SDK simulados para ejecutar la demostración sin credenciales ni red."""

import asyncio
from types import SimpleNamespace


class MockStream:
    def __init__(self, text: str) -> None:
        self.text = text
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args) -> None:
        self.closed = True

    async def _chunks(self):
        for start in range(0, len(self.text), 8):
            if self.closed:
                break
            await asyncio.sleep(0.01)
            yield self.text[start : start + 8]

    @property
    def text_stream(self):
        return self._chunks()

    async def __aiter__(self):
        async for text in self._chunks():
            yield SimpleNamespace(
                choices=[SimpleNamespace(delta=SimpleNamespace(content=text))]
            )


class MockSDK:
    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.closed = False
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self.create)
        )
        self.messages = SimpleNamespace(create=self.create, stream=self.stream)

    def _text(self) -> str:
        if self.closed:
            raise RuntimeError("El cliente simulado está cerrado.")
        return (
            f"[MOCK {self.provider}] La entropía es una medida de la "
            "incertidumbre o del número de configuraciones posibles de un sistema."
        )

    async def create(self, **kwargs):
        text = self._text()
        await asyncio.sleep(0.01)
        if kwargs.get("stream"):
            return MockStream(text)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=text))],
            content=[SimpleNamespace(type="text", text=text)],
        )

    def stream(self, **kwargs) -> MockStream:
        return MockStream(self._text())

    async def close(self) -> None:
        self.closed = True
