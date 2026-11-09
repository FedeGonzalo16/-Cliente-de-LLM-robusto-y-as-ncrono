class LLMClientError(Exception):
    """Error controlado para los proveedores de LLM."""
    
class LLMAuthenticationError(LLMClientError):
    """Credenciales inválidas o rechazadas."""

class LLMRateLimitError(LLMClientError):
    """Se alcanzó un límite de solicitudes o de cuota."""

class LLMNetworkError(LLMClientError):
    """Falló la conexión o se agotó el tiempo de espera."""