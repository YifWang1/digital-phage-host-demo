"""Minimal phage infection model skeleton for the digital host-phage project.

This module keeps the first-stage implementation intentionally lightweight.
The main goal is to preserve a clear adsorption/recognition module and a
separate infection-cycle module, so future work can extend the biology
without changing the high-level interface.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from entity_configs import phage_configs
from host_growth_model import HostGrowthState


@dataclass
class PhageInfectionState:
    """Container for the minimal phage infection state.

    The current state tracks coarse-grained infection progress plus a few
    explicit fields for future host-range and receptor-recognition work.
    This allows us to keep the model modular from the beginning instead of
    treating adsorption as an opaque black box.
    """

    adsorption_state: str
    recognition_match_score: float
    adsorption_probability: float
    injection_success_probability: float
    injection_state: str
    infection_outcome: str
    failure_cause: str
    failure_stage: str
    trajectory_label: str
    early_expression_state: float
    replication_state: float
    late_assembly_state: float
    lysis_state: float
    progeny_potential: float
    release_readiness: float
    latent_period_proxy: float
    tail_fiber_protein_type: str
    tail_spike_protein_type: str
    receptor_target_type: str
    target_variant_preference: str
    binding_specificity_strength: float
    host_range_index: float


def create_initial_phage_state() -> PhageInfectionState:
    """Create a default phage infection state for stage-1 scaffolding.

    These values are placeholders chosen for code integration rather than
    biological calibration. Future versions can replace them with
    phage-specific defaults loaded from curated parameter sets.
    """

    return create_phage_state_from_config("T7_like_LPS_phage")


def create_phage_state_from_config(config_name: str) -> PhageInfectionState:
    """Create a phage state from a named configuration preset.

    This keeps receptor-target definitions and structural descriptors in a
    shared configuration layer so new phages can be added without editing
    the infection-state logic.
    """

    if config_name not in phage_configs:
        raise ValueError(f"Unknown phage config: {config_name}")

    config = phage_configs[config_name]

    return PhageInfectionState(
        adsorption_state="unbound",
        recognition_match_score=0.0,
        adsorption_probability=0.0,
        injection_success_probability=0.0,
        injection_state="not_injected",
        infection_outcome="unresolved",
        failure_cause="none",
        failure_stage="none",
        trajectory_label="successful_progression",
        early_expression_state=0.0,
        replication_state=0.0,
        late_assembly_state=0.0,
        lysis_state=0.0,
        progeny_potential=0.0,
        release_readiness=0.0,
        latent_period_proxy=0.0,
        tail_fiber_protein_type=str(config["tail_fiber_protein_type"]),
        tail_spike_protein_type=str(config["tail_spike_protein_type"]),
        receptor_target_type=str(config["receptor_target_type"]),
        target_variant_preference=str(
            config.get("target_variant_preference", "unknown_variant")
        ),
        binding_specificity_strength=float(
            config.get("binding_specificity_strength", 1.0)
        ),
        host_range_index=float(config["host_range_index"]),
    )


def calculate_receptor_match(
    phage_state: PhageInfectionState,
    host_state: HostGrowthState,
) -> float:
    """Calculate a minimal receptor-recognition match score.

    This function keeps the adsorption/recognition module explicit and
    separates a few biologically meaningful checks:
    - whether the host presents the target receptor type
    - whether receptor availability is high enough to support binding
    - whether the phage tail fiber or tail spike appears compatible with
      the target receptor class

    The current implementation is intentionally simple. Future versions can
    replace the string-based rules with genome-informed annotations,
    structure-aware matching, or curated receptor-binding specificity maps.
    """

    receptor_availability = _clamp(host_state.receptor_availability, 0.0, 1.0)
    receptor_accessibility = _clamp(host_state.receptor_accessibility, 0.0, 1.0)
    shielding_penalty = 1.0 - _clamp(host_state.surface_shielding_factor, 0.0, 1.0)
    specificity_strength = _clamp(phage_state.binding_specificity_strength, 0.0, 1.0)
    receptor_type_match = phage_state.receptor_target_type == host_state.receptor_type
    receptor_variant_match = (
        phage_state.target_variant_preference == host_state.receptor_variant
    )

    # Keep the rule intentionally simple but explicitly tiered:
    # type mismatch -> very low score
    # type match + variant mismatch -> intermediate score
    # type match + variant match -> highest score
    if not receptor_type_match:
        base_match_score = 0.1
    elif receptor_variant_match:
        base_match_score = 1.0
    else:
        base_match_score = 0.45

    tail_structure_factor = _calculate_tail_structure_match(phage_state)

    return _clamp(
        base_match_score
        * receptor_availability
        * receptor_accessibility
        * shielding_penalty
        * specificity_strength
        * tail_structure_factor,
        0.0,
        1.0,
    )


def simulate_adsorption_and_recognition(
    host_state: HostGrowthState,
    phage_state: PhageInfectionState,
) -> PhageInfectionState:
    """Run a minimal adsorption/recognition placeholder step.

    This function is intentionally simple, but it preserves the future
    extension point where we will connect:
    - tail fiber / tail spike specificity
    - host receptor matching
    - adsorption probability
    - DNA injection success
    - host range expansion across multiple hosts and phages

    In later versions, the recognition score can be computed from explicit
    phage structural proteins and host receptor annotations, potentially
    informed by genome-derived features. The current version already keeps
    this as an independent rule layer through ``calculate_receptor_match``.
    """

    recognition_match_score = calculate_receptor_match(phage_state, host_state)
    adsorption_probability = _clamp(0.8 * recognition_match_score, 0.0, 1.0)

    # Injection success must be strongly constrained by receptor matching.
    # Even with a physiologically healthy host, poor receptor recognition
    # should keep successful DNA injection unlikely.
    energy_support = _clamp(host_state.energy_state, 0.0, 1.0)
    translation_support = _clamp(host_state.translation_capacity, 0.0, 1.0)
    injection_success_probability = _clamp(
        recognition_match_score
        * ((energy_support + translation_support) / 2.0),
        0.0,
        1.0,
    )

    if adsorption_probability <= 0.0:
        adsorption_state = "unbound"
    elif injection_success_probability <= 0.2:
        adsorption_state = "adsorbed"
    else:
        adsorption_state = "post_injection"

    host_range_index = recognition_match_score

    injection_state = "pending" if adsorption_state == "post_injection" else "not_injected"

    return replace(
        phage_state,
        adsorption_state=adsorption_state,
        recognition_match_score=recognition_match_score,
        adsorption_probability=adsorption_probability,
        injection_success_probability=injection_success_probability,
        injection_state=injection_state,
        host_range_index=host_range_index,
    )


def simulate_infection_cycle(
    host_state: HostGrowthState,
    phage_state: PhageInfectionState,
    dt: float,
) -> PhageInfectionState:
    """Advance the infection state by calling ordered stage functions.

    The current implementation intentionally keeps each stage lightweight.
    The main goal is to expose clear phase boundaries so later work can
    replace each placeholder with more realistic biology. This function is
    intentionally only an orchestrator and should not collapse back into a
    single monolithic state-update block.
    """

    if dt < 0:
        raise ValueError("dt must be non-negative")

    # ``dt`` is reserved for future finer-grained updates. The current
    # scaffold keeps the ordered phase architecture explicit:
    # injection -> early expression -> replication -> late assembly -> lysis.
    updated_state = simulate_injection(host_state, phage_state)
    updated_state = simulate_early_expression(host_state, updated_state)
    updated_state = simulate_replication(host_state, updated_state)
    updated_state = simulate_late_assembly(host_state, updated_state)
    updated_state = simulate_lysis_release(host_state, updated_state)

    infection_outcome = "unresolved"
    if (
        updated_state.lysis_state >= 0.01
        and updated_state.late_assembly_state >= 0.15
        and updated_state.progeny_potential >= 0.15
        and updated_state.release_readiness >= 0.08
    ):
        infection_outcome = "successful_lysis"
    elif updated_state.lysis_state > 0:
        infection_outcome = "partial_lysis"
    elif updated_state.adsorption_state != "post_injection":
        infection_outcome = "blocked_at_adsorption"
    elif updated_state.injection_state != "successful":
        infection_outcome = "blocked_at_injection"
    elif updated_state.early_expression_state == 0:
        infection_outcome = "blocked_at_early_expression"
    elif updated_state.replication_state == 0:
        infection_outcome = "blocked_at_replication"
    elif updated_state.late_assembly_state == 0:
        infection_outcome = "blocked_at_assembly"
    else:
        infection_outcome = "partial_lysis"

    failure_cause = "none"
    if infection_outcome == "successful_lysis":
        failure_cause = "none"
    elif updated_state.adsorption_state != "post_injection":
        failure_cause = "recognition_mismatch"
    elif host_state.host_defense_stage != "none":
        failure_cause = "host_defense"
    elif infection_outcome != "successful_lysis":
        failure_cause = "resource_limitation"

    failure_stage = "none"
    if infection_outcome == "successful_lysis":
        failure_stage = "none"
    elif updated_state.adsorption_state != "post_injection":
        failure_stage = "adsorption"
    elif updated_state.injection_state != "successful":
        failure_stage = "injection"
    elif updated_state.early_expression_state == 0:
        failure_stage = "early_expression"
    elif updated_state.replication_state == 0:
        failure_stage = "replication"
    elif updated_state.late_assembly_state == 0:
        failure_stage = "assembly"
    else:
        failure_stage = "lysis"

    trajectory_label = "successful_progression"
    if failure_cause == "recognition_mismatch":
        trajectory_label = "recognition_failure"
    elif failure_cause == "host_defense":
        trajectory_label = "defense_blocked_failure"
    elif (
        infection_outcome != "successful_lysis"
        and updated_state.recognition_match_score < 0.8
    ):
        trajectory_label = "recognition_limited_failure"
    elif infection_outcome != "successful_lysis":
        trajectory_label = "resource_limited_failure"

    return replace(
        updated_state,
        infection_outcome=infection_outcome,
        failure_cause=failure_cause,
        failure_stage=failure_stage,
        trajectory_label=trajectory_label,
    )


def simulate_injection(
    host_state: HostGrowthState,
    phage_state: PhageInfectionState,
) -> PhageInfectionState:
    """Resolve whether the phage successfully enters an injected state."""

    if phage_state.adsorption_state != "post_injection":
        injection_state = "not_injected"
    elif phage_state.injection_success_probability > 0.2:
        injection_state = "successful"
    else:
        injection_state = "blocked"

    if injection_state == "successful":
        host_state.host_takeover_level = _clamp(
            host_state.host_takeover_level + 0.2 * phage_state.injection_success_probability,
            0.0,
            1.0,
        )

    return replace(phage_state, injection_state=injection_state)


def simulate_early_expression(
    host_state: HostGrowthState,
    phage_state: PhageInfectionState,
) -> PhageInfectionState:
    """Advance early expression after successful injection.

    This stage currently depends primarily on host transcription and
    translation capacity, modulated by infection efficiency.
    """

    if phage_state.injection_state != "successful":
        return replace(phage_state, early_expression_state=0.0)

    infection_efficiency_factor = _calculate_infection_efficiency_factor(phage_state)
    early_expression_resource_factor = _calculate_early_expression_resource_factor(
        host_state
    )
    progress = 0.25 * infection_efficiency_factor * early_expression_resource_factor

    # Minimal resource consumption: early expression lightly draws on host
    # transcription and translation capacity.
    host_state.transcription_capacity = _clamp(
        host_state.transcription_capacity
        - 0.05
        * progress
        * (
            1.0
            + 0.18 * _clamp(host_state.host_takeover_level, 0.0, 1.0)
            + 0.01 * _clamp(host_state.phage_resource_allocation, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    host_state.translation_capacity = _clamp(
        host_state.translation_capacity
        - 0.04
        * progress
        * (
            1.0
            + 0.04 * _clamp(host_state.host_takeover_level, 0.0, 1.0)
            + 0.1 * _clamp(host_state.phage_resource_allocation, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    host_state.host_takeover_level = _clamp(
        host_state.host_takeover_level + 0.4 * progress,
        0.0,
        1.0,
    )
    host_state.phage_resource_allocation = _clamp(
        host_state.phage_resource_allocation + 0.1 * progress,
        0.0,
        1.0,
    )

    return replace(
        phage_state,
        early_expression_state=_clamp(
            phage_state.early_expression_state + progress,
            0.0,
            1.0,
        ),
    )


def simulate_replication(
    host_state: HostGrowthState,
    phage_state: PhageInfectionState,
) -> PhageInfectionState:
    """Advance replication after early expression reaches a minimal threshold.

    This stage currently depends primarily on host transcription capacity
    and energy state, modulated by infection efficiency.
    """

    if phage_state.early_expression_state < 0.2:
        return replace(phage_state, replication_state=0.0)

    infection_efficiency_factor = _calculate_infection_efficiency_factor(phage_state)
    replication_resource_factor = _calculate_replication_resource_factor(host_state)
    takeover_factor = _clamp(
        1.0 + 0.28 * _clamp(host_state.host_takeover_level, 0.0, 1.0),
        1.0,
        1.28,
    )
    defense_factor = 1.0
    if host_state.host_defense_stage == "replication":
        defense_factor = 1.0 - _clamp(host_state.host_defense_strength, 0.0, 1.0)
    progress = (
        0.2
        * infection_efficiency_factor
        * replication_resource_factor
        * takeover_factor
        * defense_factor
    )

    # Minimal resource consumption: replication is modeled as energetically
    # expensive, with a smaller transcriptional burden.
    host_state.energy_state = _clamp(
        host_state.energy_state
        - 0.12
        * progress
        * (
            1.0
            + 0.05 * _clamp(host_state.host_takeover_level, 0.0, 1.0)
            + 0.18 * _clamp(host_state.phage_resource_allocation, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    host_state.transcription_capacity = _clamp(
        host_state.transcription_capacity
        - 0.03
        * progress
        * (
            1.0
            + 0.22 * _clamp(host_state.host_takeover_level, 0.0, 1.0)
            + 0.03 * _clamp(host_state.phage_resource_allocation, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    host_state.host_takeover_level = _clamp(
        host_state.host_takeover_level + 0.48 * progress,
        0.0,
        1.0,
    )
    host_state.phage_resource_allocation = _clamp(
        host_state.phage_resource_allocation + 0.44 * progress,
        0.0,
        1.0,
    )

    return replace(
        phage_state,
        replication_state=_clamp(
            phage_state.replication_state + progress,
            0.0,
            1.0,
        ),
        progeny_potential=_clamp(
            phage_state.progeny_potential + 0.22 * progress,
            0.0,
            1.0,
        ),
        release_readiness=_clamp(
            phage_state.release_readiness + 0.02 * progress,
            0.0,
            1.0,
        ),
        latent_period_proxy=_clamp(
            phage_state.latent_period_proxy + 0.005 * progress,
            0.0,
            1.0,
        ),
    )


def simulate_late_assembly(
    host_state: HostGrowthState,
    phage_state: PhageInfectionState,
) -> PhageInfectionState:
    """Advance late assembly only after replication is underway.

    This stage currently depends primarily on host translation capacity
    and energy state, modulated by infection efficiency.
    """

    if phage_state.replication_state < 0.17:
        return replace(phage_state, late_assembly_state=0.0)

    infection_efficiency_factor = _calculate_infection_efficiency_factor(phage_state)
    late_assembly_resource_factor = _calculate_late_assembly_resource_factor(
        host_state
    )
    takeover_factor = _clamp(
        1.0 + 0.2 * _clamp(host_state.host_takeover_level, 0.0, 1.0),
        1.0,
        1.2,
    )
    progress = (
        0.16
        * infection_efficiency_factor
        * late_assembly_resource_factor
        * takeover_factor
    )

    # Minimal resource consumption: late assembly draws on translation and
    # still consumes some energy.
    host_state.translation_capacity = _clamp(
        host_state.translation_capacity
        - 0.06
        * progress
        * (
            1.0
            + 0.04 * _clamp(host_state.host_takeover_level, 0.0, 1.0)
            + 0.3 * _clamp(host_state.phage_resource_allocation, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    host_state.energy_state = _clamp(
        host_state.energy_state
        - 0.05
        * progress
        * (
            1.0
            + 0.03 * _clamp(host_state.host_takeover_level, 0.0, 1.0)
            + 0.24 * _clamp(host_state.phage_resource_allocation, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    host_state.host_takeover_level = _clamp(
        host_state.host_takeover_level + 0.06 * progress,
        0.0,
        1.0,
    )
    host_state.phage_resource_allocation = _clamp(
        host_state.phage_resource_allocation + 0.72 * progress,
        0.0,
        1.0,
    )
    updated_late_assembly = _clamp(phage_state.late_assembly_state + progress, 0.0, 1.0)
    updated_progeny_potential = _clamp(
        phage_state.progeny_potential + 0.78 * progress,
        0.0,
        1.0,
    )
    energy_support = _clamp(host_state.energy_state, 0.0, 1.0)
    allocation_support = _clamp(host_state.phage_resource_allocation, 0.0, 1.0)
    readiness_support = _clamp(
        updated_late_assembly * (0.65 + 0.25 * updated_progeny_potential),
        0.0,
        1.0,
    )
    auxiliary_support = _clamp(
        0.92 + 0.05 * energy_support + 0.03 * allocation_support,
        0.0,
        1.0,
    )

    return replace(
        phage_state,
        late_assembly_state=updated_late_assembly,
        progeny_potential=updated_progeny_potential,
        release_readiness=_clamp(
            phage_state.release_readiness + 0.55 * readiness_support * auxiliary_support,
            0.0,
            1.0,
        ),
        latent_period_proxy=_clamp(
            phage_state.latent_period_proxy + 0.3 * readiness_support * auxiliary_support,
            0.0,
            1.0,
        ),
    )


def simulate_lysis_release(
    host_state: HostGrowthState,
    phage_state: PhageInfectionState,
) -> PhageInfectionState:
    """Advance lysis/release only after late assembly reaches a threshold.

    This stage depends mainly on late assembly progress, with progeny
    accumulation acting as a second major requirement. Host energy and
    resource allocation only provide lighter support.
    """

    if (
        phage_state.late_assembly_state < 0.13
        or phage_state.progeny_potential < 0.06
    ):
        return replace(phage_state, lysis_state=0.0)

    infection_efficiency_factor = _calculate_infection_efficiency_factor(phage_state)
    progress = (
        0.16
        * infection_efficiency_factor
        * _calculate_lysis_resource_factor(host_state, phage_state)
    )
    host_state.energy_state = _clamp(
        host_state.energy_state
        - 0.018
        * progress
        * (
            1.0
            + 0.22 * _clamp(host_state.phage_resource_allocation, 0.0, 1.0)
        ),
        0.0,
        1.0,
    )
    return replace(
        phage_state,
        lysis_state=_clamp(phage_state.lysis_state + progress, 0.0, 1.0),
        release_readiness=_clamp(
            phage_state.release_readiness
            + 0.12 * _calculate_lysis_resource_factor(host_state, phage_state),
            0.0,
            1.0,
        ),
        latent_period_proxy=_clamp(
            phage_state.latent_period_proxy
            + 0.06
            * (
                _clamp(phage_state.release_readiness, 0.0, 1.0)
                + _clamp(phage_state.lysis_state + progress, 0.0, 1.0)
            )
            / 2.0,
            0.0,
            1.0,
        ),
    )


def _clamp(value: float, lower: float, upper: float) -> float:
    """Clamp a scalar value into a closed interval."""

    return max(lower, min(value, upper))


def _calculate_infection_efficiency_factor(phage_state: PhageInfectionState) -> float:
    """Compute a minimal downstream infection-efficiency factor.

    This keeps downstream progression coupled to the quality of recognition
    and injection. Matched cases therefore advance further, variant-mismatch
    cases advance more weakly, and poor-recognition cases remain low.
    """

    return _clamp(
        (
            phage_state.recognition_match_score
            + phage_state.injection_success_probability
        ) / 2.0,
        0.0,
        1.0,
    )


def _calculate_early_expression_resource_factor(host_state: HostGrowthState) -> float:
    """Resource support for early expression.

    Early expression is currently modeled as depending primarily on host
    transcription and translation capacity. This stage intentionally does
    not receive a strong boost from phage resource allocation yet.
    """

    return _clamp(
        _clamp(
            (
                _clamp(host_state.transcription_capacity, 0.0, 1.0)
                + _clamp(host_state.translation_capacity, 0.0, 1.0)
            ) / 2.0,
            0.0,
            1.0,
        )
        * _clamp(
            1.0 + 0.12 * _clamp(host_state.host_takeover_level, 0.0, 1.0),
            1.0,
            1.12,
        ),
        0.0,
        1.0,
    )


def _calculate_replication_resource_factor(host_state: HostGrowthState) -> float:
    """Resource support for genome replication.

    Replication is currently modeled as depending primarily on host
    transcription capacity and energy availability, with a mild boost once
    host resources have started to reallocate toward the phage program.
    """

    base_factor = _clamp(
        (
            _clamp(host_state.transcription_capacity, 0.0, 1.0)
            + _clamp(host_state.energy_state, 0.0, 1.0)
        ) / 2.0,
        0.0,
        1.0,
    )
    takeover_gain = 1.0 + 0.04 * _clamp(host_state.host_takeover_level, 0.0, 1.0)
    allocation_gain = 1.0 + 0.45 * _clamp(
        host_state.phage_resource_allocation,
        0.0,
        1.0,
    )
    return _clamp(base_factor * takeover_gain * allocation_gain, 0.0, 1.0)


def _calculate_late_assembly_resource_factor(host_state: HostGrowthState) -> float:
    """Resource support for late assembly.

    Late assembly is currently modeled as depending primarily on host
    translation capacity and energy availability, with a mild boost from
    prior phage-directed resource reallocation.
    """

    base_factor = _clamp(
        (
            _clamp(host_state.translation_capacity, 0.0, 1.0)
            + _clamp(host_state.energy_state, 0.0, 1.0)
        ) / 2.0,
        0.0,
        1.0,
    )
    allocation_gain = 1.0 + 0.5 * _clamp(
        host_state.phage_resource_allocation,
        0.0,
        1.0,
    )
    return _clamp(base_factor * allocation_gain, 0.0, 1.0)


def _calculate_lysis_resource_factor(
    host_state: HostGrowthState,
    phage_state: PhageInfectionState,
) -> float:
    """Resource support for lysis and release.

    Lysis is driven primarily by late assembly completion, with progeny
    buildup as a clear secondary dependency. Host energy and prior
    allocation bias only provide light support.
    """

    energy_support = _clamp(host_state.energy_state, 0.0, 1.0)
    assembly_support = _clamp(phage_state.late_assembly_state, 0.0, 1.0)
    progeny_support = _clamp(phage_state.progeny_potential, 0.0, 1.0)
    base_factor = _clamp(
        assembly_support * (0.5 + 0.5 * progeny_support),
        0.0,
        1.0,
    )
    energy_gain = 0.94 + 0.06 * energy_support
    allocation_gain = 1.0 + 0.14 * _clamp(
        host_state.phage_resource_allocation,
        0.0,
        1.0,
    )
    return _clamp(base_factor * energy_gain * allocation_gain, 0.0, 1.0)


def _calculate_tail_structure_match(phage_state: PhageInfectionState) -> float:
    """Estimate whether the phage tail structures fit the target receptor.

    This is a deliberately small placeholder for future work on:
    - tail fiber / tail spike specificity
    - receptor-binding motifs inferred from annotations
    - host range expansion across multiple receptor classes
    """

    target = phage_state.receptor_target_type.lower()
    tail_fiber = phage_state.tail_fiber_protein_type.lower()
    tail_spike = phage_state.tail_spike_protein_type.lower()

    if target and (target in tail_fiber or target in tail_spike):
        return 1.0
    if "unknown" in tail_fiber and "unknown" in tail_spike:
        return 0.5
    return 0.2
