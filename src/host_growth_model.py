"""Minimal host growth model skeleton for the digital host-phage project.

This module intentionally keeps the first-stage implementation simple.
It defines a host state container plus lightweight helper functions so
future work can plug in richer physiology, regulation, and genome-aware
host modules without rewriting the calling interface.
"""

from __future__ import annotations

from dataclasses import dataclass

from entity_configs import host_configs


@dataclass
class HostGrowthState:
    """Container for the minimal host growth state.

    The current version tracks only a small set of coarse-grained host
    properties needed by the stage-1 infection framework. Each field is
    represented as a simple scalar so later versions can replace the
    placeholder logic with calibrated update rules.
    """

    growth_rate: float
    cell_volume: float
    nutrient_state: float
    transcription_capacity: float
    translation_capacity: float
    energy_state: float
    receptor_type: str
    receptor_variant: str
    receptor_accessibility: float
    surface_shielding_factor: float
    receptor_availability: float
    host_defense_stage: str
    host_defense_strength: float
    host_takeover_level: float
    phage_resource_allocation: float


def create_initial_host_state() -> HostGrowthState:
    """Create a default host state for early-stage simulations.

    These values are placeholders rather than fitted biological constants.
    They provide a stable, minimal starting point for wiring the rest of
    the project together before detailed parameterization is introduced.
    """

    return create_host_state_from_config("ecoli_LPS_host")


def create_host_state_from_config(config_name: str) -> HostGrowthState:
    """Create a host state from a named configuration preset.

    This keeps entity-specific properties outside the simulation logic so
    additional hosts can be introduced by adding new config entries.
    """

    if config_name not in host_configs:
        raise ValueError(f"Unknown host config: {config_name}")

    config = host_configs[config_name]
    base_growth_rate = float(config["growth_rate"])
    base_transcription_capacity = float(config.get("transcription_capacity", 1.0))
    base_translation_capacity = float(config["translation_capacity"])
    base_energy_state = float(config["energy_state"])

    growth_rate = _clamp(
        base_growth_rate
        * (
            0.85
            + 0.1 * _clamp(base_energy_state, 0.0, 1.0)
            + 0.05 * _clamp(base_transcription_capacity, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    transcription_capacity = _clamp(
        base_transcription_capacity
        * (
            0.88
            + 0.08 * _clamp(base_growth_rate, 0.0, 1.0)
            + 0.04 * _clamp(base_energy_state, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    translation_capacity = _clamp(
        base_translation_capacity
        * (
            0.9
            + 0.07 * _clamp(base_growth_rate, 0.0, 1.0)
            + 0.03 * _clamp(base_transcription_capacity, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    energy_state = _clamp(
        base_energy_state
        * (
            0.9
            + 0.06 * _clamp(base_growth_rate, 0.0, 1.0)
            + 0.04 * _clamp(base_translation_capacity, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )

    return HostGrowthState(
        growth_rate=growth_rate,
        cell_volume=float(config.get("cell_volume", 1.0)),
        nutrient_state=float(config.get("nutrient_state", 1.0)),
        transcription_capacity=transcription_capacity,
        translation_capacity=translation_capacity,
        energy_state=energy_state,
        receptor_type=str(config["receptor_type"]),
        receptor_variant=str(config.get("receptor_variant", "unknown_variant")),
        receptor_accessibility=float(config.get("receptor_accessibility", 1.0)),
        surface_shielding_factor=float(config.get("surface_shielding_factor", 0.0)),
        receptor_availability=float(config["receptor_availability"]),
        host_defense_stage=str(config.get("host_defense_stage", "none")),
        host_defense_strength=float(config.get("host_defense_strength", 0.0)),
        host_takeover_level=0.0,
        phage_resource_allocation=0.0,
    )


def update_host_growth_state(
    state: HostGrowthState,
    dt: float,
) -> HostGrowthState:
    """Update the host state over a small time step.

    This is intentionally a placeholder implementation. For now, it applies
    a tiny amount of conservative bookkeeping so the function is usable by
    a simulation runner, while keeping the model simple and easy to extend.

    Future extensions may replace this logic with:
    - nutrient-dependent growth equations
    - transcription and translation resource allocation
    - energy limitation or stress coupling
    - receptor exposure dynamics linked to host physiology
    - host-specific parameter sets inferred from experiments or genomes
    """

    if dt < 0:
        raise ValueError("dt must be non-negative")

    # Minimal placeholder behavior:
    # keep most state variables stable while gently coupling receptor
    # availability to nutrient and energy status. This preserves a valid
    # interface without pretending to be a detailed biological model.
    nutrient_factor = _clamp(state.nutrient_state, 0.0, 1.0)
    energy_factor = _clamp(state.energy_state, 0.0, 1.0)
    receptor_baseline = state.receptor_availability
    receptor_adjustment = 0.05 * dt * (nutrient_factor + energy_factor - 1.0)

    return HostGrowthState(
        growth_rate=max(state.growth_rate, 0.0),
        cell_volume=max(state.cell_volume, 0.0),
        nutrient_state=nutrient_factor,
        transcription_capacity=max(state.transcription_capacity, 0.0),
        translation_capacity=max(state.translation_capacity, 0.0),
        energy_state=energy_factor,
        receptor_type=state.receptor_type,
        receptor_variant=state.receptor_variant,
        receptor_accessibility=_clamp(state.receptor_accessibility, 0.0, 1.0),
        surface_shielding_factor=_clamp(state.surface_shielding_factor, 0.0, 1.0),
        receptor_availability=_clamp(
            receptor_baseline + receptor_adjustment,
            0.0,
            1.0,
        ),
        host_defense_stage=state.host_defense_stage,
        host_defense_strength=_clamp(state.host_defense_strength, 0.0, 1.0),
        host_takeover_level=_clamp(state.host_takeover_level, 0.0, 1.0),
        phage_resource_allocation=_clamp(
            state.phage_resource_allocation,
            0.0,
            1.0,
        ),
    )


def _clamp(value: float, lower: float, upper: float) -> float:
    """Clamp a scalar value into a closed interval."""

    return max(lower, min(value, upper))
