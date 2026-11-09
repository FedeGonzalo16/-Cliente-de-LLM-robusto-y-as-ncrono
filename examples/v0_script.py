import time

""" Este script llama a un "OpenAI" simulado, de forma síncrona y secuencial. """

def fake_openai_call(prompt):  # simula una llamada de red a OpenAI
    time.sleep(2.0)  # bloquea todo el programa mientras "espera"
    return {"choices": [{"message": {"content": f"[openai/gpt-mock] respuesta a: {prompt}"}}]}

def ask(prompt):  # deuda 3: no hay contrato, solo una función suelta
    resp = fake_openai_call(prompt)  # deuda 1: atado a OpenAI
    return resp["choices"][0]["message"]["content"]  # deuda 1: formato de OpenAI en la lógic

if __name__ == "__main__":
    prompts = [
        "¿Qué es la entropía?",
        "Explicá qué es un event loop.",
        "¿Qué es un rate limit?",
        "Dame una analogía para una API.",
        "¿Qué es el TTFT?",
    ]
    start = time.perf_counter()
    for p in prompts:  # deuda 2: secuencial, cada llamada espera a la anterior
        print("-", ask(p)[:80])
    print(f"Total: {time.perf_counter() - start:.2f}s")
    
#Corrélo al inicio y anotá el tiempo total (unos 10 segundos: 5 llamadas de 2 segundos, una detrás de otra). Es tu línea base para comparar al final.
#Total first try: 10.01s