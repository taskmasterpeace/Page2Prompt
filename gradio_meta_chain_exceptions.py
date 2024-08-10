class MetaChainException(Exception):
    """Base exception for MetaChain errors"""
    pass

class PromptGenerationError(MetaChainException):
    """Raised when there's an error in prompt generation"""
    pass

class ScriptAnalysisError(MetaChainException):
    """Raised when there's an error in script analysis"""
    pass

class ModelInvocationError(MetaChainException):
    """Raised when there's an error invoking the language model"""
    pass
