# Pre-entrega 1: organización de la implementación

El proyecto utiliza **Python 3.14**. Las instrucciones de instalación, configuración y ejecución se encuentran en [README.md](../README.md).

## Implementación

- [x] Esquemas Pydantic para mensajes, configuración y respuestas.
- [x] Validación de temperatura entre 0 y 2 y máximo de tokens positivo.
- [x] Contrato común `BaseLLMClient`.
- [x] Adaptadores para `AsyncOpenAI` y `AsyncAnthropic`.
- [x] Generación normal y streaming mediante generadores asíncronos.
- [x] Selección del proveedor mediante `AsyncLLMManager`.
- [x] Manejo controlado de errores de API, red y rate limit.
- [x] Cierre de recursos mediante contextos asíncronos.
- [x] Semáforo compartido para limitar solicitudes simultáneas.
- [x] Timeouts y reintentos configurados en los SDK.
- [x] Script de demostración y ejemplo de variables de entorno.
- [x] README con requisitos y comandos de ejecución.

## Ubicación de los archivos

| Ubicación | Contenido |
|---|---|
| `llm_client/` | Paquete con adaptadores, manager, esquemas y excepciones. |
| `main.py` | Demostración de generación normal y streaming. |
| `requirements.txt` | Dependencias del proyecto. |
| `.env.example` | Ejemplo de configuración sin credenciales. |
| `config/.env` | Configuración local excluida de Git. |
| `examples/` | Simuladores iniciales y versión síncrona de práctica. |
| `docs/` | Notas del proyecto. |

Los módulos internos utilizan imports relativos. El punto de entrada importa desde `llm_client` y se ejecuta desde la raíz con `python main.py`.

La carpeta `.env/` de la raíz contiene el entorno virtual existente. Se conserva y es distinta del archivo `config/.env`.
