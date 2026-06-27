"""Extension registry for Kira — the primary extensibility mechanism.

Third-party Django apps can register hooks by defining a ``kira_extensions``
dict on their AppConfig and calling ``registry.register()`` in ``ready()``.

Example::

    class MyPluginConfig(AppConfig):
        name = "my_plugin"

        def ready(self):
            from apps.core.extensions import registry
            registry.register("nav_items", {
                "label": "Reports",
                "url_name": "my_plugin:reports",
                "icon": "chart",
            })
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtensionHook:
    """A single registered extension entry."""

    key: str
    group: str
    data: dict[str, Any] = field(default_factory=dict)
    handler: Callable[..., Any] | None = None
    priority: int = 100


class ExtensionRegistry:
    """Central registry for all Kira extension points."""

    def __init__(self):
        self._hooks: dict[str, list[ExtensionHook]] = defaultdict(list)

    def register(
        self,
        group: str,
        data: dict[str, Any] | None = None,
        *,
        key: str | None = None,
        handler: Callable[..., Any] | None = None,
        priority: int = 100,
    ) -> None:
        hook_key = key or data.get("key", "") if data else ""
        hook = ExtensionHook(
            key=hook_key,
            group=group,
            data=data or {},
            handler=handler,
            priority=priority,
        )
        self._hooks[group].append(hook)
        self._hooks[group].sort(key=lambda h: h.priority)

    def get(self, group: str) -> list[ExtensionHook]:
        return list(self._hooks.get(group, []))

    def get_data(self, group: str) -> list[dict[str, Any]]:
        return [hook.data for hook in self.get(group)]

    def call_handlers(self, group: str, *args, **kwargs) -> list[Any]:
        results = []
        for hook in self.get(group):
            if hook.handler:
                results.append(hook.handler(*args, **kwargs))
        return results

    def load_builtin_extensions(self) -> None:
        """Register built-in extension defaults."""
        self.register(
            "nav_items",
            {"label": "Dashboard", "url_name": "projects:dashboard", "icon": "home"},
            key="dashboard",
            priority=10,
        )
        self.register(
            "nav_items",
            {"label": "Projects", "url_name": "projects:list", "icon": "folder"},
            key="projects",
            priority=20,
        )


registry = ExtensionRegistry()
