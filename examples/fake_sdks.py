import asyncio
from types import SimpleNamespace

OPENAI_LATENCY_S = 2.0
ANTHROPIC_LATENCY_S = 1.5

class FakeAsyncOpenAI:
    "Imitar forma de AsyncOpenAi: client.chat.comletions.create(...)"
    
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
        
    async def create(self,*,model: str, messages: list[dict]):
        await asyncio.sleep(OPENAI_LATENCY_S)
        prompt = messages[-1]["content"]
        message = SimpleNamespace(content=f"[openai/{model}] respuesta a: {prompt}")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])
    
class FakeAsyncAnthropic:
    "Imitar forma de AsyncAnthropic: client.messages.create(...)"

    def __init__(self) -> None:
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, *, model: str, max_tokens: int, messages: list[dict]):
        await asyncio.sleep(ANTHROPIC_LATENCY_S)
        prompt = messages[-1]["content"]
        text = f"[anthropic/{model}] respuesta a: {prompt}"
        return SimpleNamespace(content=[SimpleNamespace(text=text)])
