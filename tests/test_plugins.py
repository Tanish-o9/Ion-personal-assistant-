import pytest
from orchestrator.plugins import PluginRegistry, PluginManifest

def test_plugin_registration_and_duplicate_prevention():
    reg = PluginRegistry()
    manifest = PluginManifest(
        id="calc_ext_plugin",
        name="Advanced Calculator Plugin",
        version="1.0.0",
        description="Extends standard calculator with matrix operations.",
        capabilities=["matrix_math"],
        permissions=["read_only"],
    )

    plugin = reg.register_plugin(manifest)
    assert plugin.manifest.id == "calc_ext_plugin"
    assert plugin.enabled is True

    # Duplicate registration should fail
    with pytest.raises(ValueError):
        reg.register_plugin(manifest)

def test_plugin_enable_disable_and_capability_search():
    reg = PluginRegistry()
    manifest = PluginManifest(
        id="search_plugin",
        name="Custom Web Searcher",
        description="Searches custom enterprise index.",
        capabilities=["enterprise_search"],
    )
    reg.register_plugin(manifest)

    matches = reg.search_capabilities("enterprise_search")
    assert len(matches) == 1

    # Disable plugin
    assert reg.disable_plugin("search_plugin") is True
    matches_disabled = reg.search_capabilities("enterprise_search")
    assert len(matches_disabled) == 0

    # Enable plugin
    assert reg.enable_plugin("search_plugin") is True
    matches_enabled = reg.search_capabilities("enterprise_search")
    assert len(matches_enabled) == 1
