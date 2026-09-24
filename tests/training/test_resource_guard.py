from training.resource_guard import (
    ResourceAction,
    ResourceLimits,
    ResourcePolicy,
    ResourceSnapshot,
    ResourceState,
)


def make_snapshot(
    process_ram=1.0,
    system_used=6.0,
    available=6.0,
    gpu_used=None,
    gpu_total=None,
    disk_free=100.0,
):
    return ResourceSnapshot(
        process_ram_gb=process_ram,
        system_ram_used_gb=system_used,
        system_ram_available_gb=available,
        gpu_memory_used_gb=gpu_used,
        gpu_memory_total_gb=gpu_total,
        disk_free_gb=disk_free,
    )


def test_safe_resource_state():
    policy = ResourcePolicy(
        ResourceLimits()
    )

    state, action = policy.evaluate(
        make_snapshot()
    )

    assert state == ResourceState.SAFE
    assert action == ResourceAction.CONTINUE


def test_ram_warning():
    policy = ResourcePolicy(
        ResourceLimits(
            max_training_ram_gb=5.5
        )
    )

    state, action = policy.evaluate(
        make_snapshot(
            process_ram=4.6
        )
    )

    assert state == ResourceState.WARNING
    assert action == ResourceAction.WARNING


def test_ram_critical():
    policy = ResourcePolicy(
        ResourceLimits(
            max_training_ram_gb=5.5
        )
    )

    state, action = policy.evaluate(
        make_snapshot(
            process_ram=5.6
        )
    )

    assert state == ResourceState.CRITICAL
    assert action == ResourceAction.CHECKPOINT


def test_system_ram_critical():
    policy = ResourcePolicy(
        ResourceLimits(
            max_system_ram_gb=12.5
        )
    )

    state, action = policy.evaluate(
        make_snapshot(
            system_used=12.6
        )
    )

    assert state == ResourceState.CRITICAL
    assert action == ResourceAction.CHECKPOINT


def test_available_ram_critical():
    policy = ResourcePolicy(
        ResourceLimits(
            min_available_ram_gb=2.0
        )
    )

    state, action = policy.evaluate(
        make_snapshot(
            available=1.9
        )
    )

    assert state == ResourceState.CRITICAL
    assert action == ResourceAction.CHECKPOINT


def test_gpu_warning():
    policy = ResourcePolicy(
        ResourceLimits(
            max_gpu_memory_percent=90.0
        )
    )

    state, action = policy.evaluate(
        make_snapshot(
            gpu_used=3.2,
            gpu_total=4.0,
        )
    )

    assert state == ResourceState.WARNING
    assert action == ResourceAction.WARNING


def test_gpu_critical():
    policy = ResourcePolicy(
        ResourceLimits(
            max_gpu_memory_percent=90.0
        )
    )

    state, action = policy.evaluate(
        make_snapshot(
            gpu_used=3.7,
            gpu_total=4.0,
        )
    )

    assert state == ResourceState.CRITICAL
    assert action == ResourceAction.CHECKPOINT


def test_disk_critical():
    policy = ResourcePolicy(
        ResourceLimits(
            min_free_disk_gb=10.0
        )
    )

    state, action = policy.evaluate(
        make_snapshot(
            disk_free=9.0
        )
    )

    assert state == ResourceState.CRITICAL
    assert action == ResourceAction.CHECKPOINT