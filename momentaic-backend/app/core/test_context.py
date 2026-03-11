from contextvars import ContextVar

# Global context variable to track if the current request/execution is part of an E2E Playwright test
# This allows deep layers (like BaseAgent.structured_llm_call) to safely mock paid APIs
e2e_test_mode: ContextVar[bool] = ContextVar('e2e_test_mode', default=False)

def is_e2e_test_mode() -> bool:
    """Check if the current execution context is in Zero-Cost E2E Test Mode."""
    return e2e_test_mode.get()
