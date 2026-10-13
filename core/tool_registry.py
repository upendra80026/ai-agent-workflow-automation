import inspect
import time
from typing import Callable, Dict, Any, Optional, List
from pydantic import BaseModel


class ToolMetadata(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str = "general"


class ToolRegistry:
    """
    Centralized, extensible registry for all tools and simulated APIs.
    Allows dynamic registration, discovery, parameter validation, and execution.
    """
    _instance: Optional['ToolRegistry'] = None

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, ToolMetadata] = {}

    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, description: str, category: str = "general"):
        """Decorator to register a tool function into the registry."""
        def decorator(func: Callable):
            sig = inspect.signature(func)
            params = {}
            for param_name, param in sig.parameters.items():
                params[param_name] = {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": None if param.default == inspect.Parameter.empty else param.default,
                    "required": param.default == inspect.Parameter.empty
                }

            meta = ToolMetadata(
                name=name,
                description=description,
                parameters=params,
                category=category
            )
            self._tools[name] = func
            self._metadata[name] = meta
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Executes a registered tool with timing and error handling.
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered. Available tools: {list(self._tools.keys())}")

        func = self._tools[name]
        start_time = time.perf_counter()
        try:
            result = func(**kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "tool": name,
                "status": "SUCCESS",
                "result": result,
                "duration_ms": round(duration_ms, 2)
            }
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "tool": name,
                "status": "FAILED",
                "error": str(e),
                "duration_ms": round(duration_ms, 2)
            }

    def list_tools(self) -> List[ToolMetadata]:
        return list(self._metadata.values())


# Global registry helper
registry = ToolRegistry.get_instance()
register_tool = registry.register
