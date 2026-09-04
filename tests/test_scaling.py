"""
Unit Tests for Phase 64: Global Scale & High Availability.
"""

import pytest
from orchestrator.platform.scaling import DistributedScalingManager

def test_distributed_leader_election_lock():
    mgr = DistributedScalingManager()

    # Node 1 acquires lock
    assert mgr.acquire_leader_lock("instance_node_1") is True
    assert mgr.get_ha_health_status()["leader_instance"] == "instance_node_1"

    # Node 2 attempts lock -> DENIED
    assert mgr.acquire_leader_lock("instance_node_2") is False

    # Node 1 releases lock
    assert mgr.release_leader_lock("instance_node_1") is True

    # Node 2 acquires lock
    assert mgr.acquire_leader_lock("instance_node_2") is True
    assert mgr.get_ha_health_status()["leader_instance"] == "instance_node_2"
