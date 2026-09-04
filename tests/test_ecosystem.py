import pytest
from orchestrator.ecosystem import default_ecosystem_manager, EcosystemCatalogEntry

def test_capability_submission_and_validation():
    entry_ok = EcosystemCatalogEntry(
        capability_id="eco_weather_plugin",
        name="Global Weather Plugin",
        description="Provides real-time weather forecasts.",
        capability_type="plugin",
        version="1.0.0",
        required_permissions=["network_access"],
    )
    assert default_ecosystem_manager.submit_capability(entry_ok) is True

    # Dangerous permission fails validation
    entry_bad = EcosystemCatalogEntry(
        capability_id="eco_bad_plugin",
        name="Malicious Plugin",
        description="Attempts shell access.",
        capability_type="plugin",
        version="1.0.0",
        required_permissions=["unrestricted_shell"],
    )
    assert default_ecosystem_manager.submit_capability(entry_bad) is False

def test_catalog_search_install_and_uninstall():
    user_id = "user_eco_1"
    matches = default_ecosystem_manager.search_catalog("Weather")
    assert len(matches) >= 1

    cap_id = matches[0].capability_id
    assert default_ecosystem_manager.install_capability(user_id, cap_id) is True

    assert default_ecosystem_manager.uninstall_capability(user_id, cap_id) is True
