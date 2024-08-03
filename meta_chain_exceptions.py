class MetaChainException(Exception):
    """Base exception class for MetaChain errors."""
    pass

class PromptGenerationError(MetaChainException):
    """Raised when there's an error generating a prompt."""
    pass

class ScriptAnalysisError(MetaChainException):
    """Raised when there's an error analyzing a script."""
    pass

class ModelInvocationError(MetaChainException):
    """Raised when there's an error invoking the language model."""
    pass
