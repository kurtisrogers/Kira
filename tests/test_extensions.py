from apps.core.extensions import ExtensionRegistry


def test_register_and_get_sorted_by_priority():
    registry = ExtensionRegistry()
    registry.register("nav_items", {"label": "Low"}, key="low", priority=50)
    registry.register("nav_items", {"label": "High"}, key="high", priority=10)

    labels = [hook.data["label"] for hook in registry.get("nav_items")]
    assert labels == ["High", "Low"]


def test_get_data_returns_dicts():
    registry = ExtensionRegistry()
    registry.register("widgets", {"label": "Stats"}, key="stats")

    assert registry.get_data("widgets") == [{"label": "Stats"}]


def test_call_handlers_invokes_registered_callables():
    registry = ExtensionRegistry()
    registry.register("hooks", handler=lambda x: x * 2, key="double")

    assert registry.call_handlers("hooks", 3) == [6]


def test_builtin_extensions_load():
    registry = ExtensionRegistry()
    registry.load_builtin_extensions()

    labels = [item["label"] for item in registry.get_data("nav_items")]
    assert "Dashboard" in labels
    assert "Projects" in labels
