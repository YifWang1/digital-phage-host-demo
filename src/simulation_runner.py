"""Minimal simulation runner for the digital host-phage project.

This file provides a single-step demonstration of how the stage-1 modules
fit together. The current version is intentionally simple: it initializes
host and phage states, runs one placeholder update step, and returns a
compact result dictionary.

Future versions can expand this runner to support:
- multi-step time integration
- multiple hosts or phages
- parameter loading from configuration files
- batch simulation and result export
"""

from entity_configs import (
    build_combined_config_from_annotation_stubs,
    build_host_defense_config_from_annotation_stub,
    build_host_resource_config_from_annotation_stub,
    build_recognition_config_from_annotation_stub,
    get_minimal_annotation_schema,
    get_minimal_pipeline_schema,
    validate_annotation_stubs,
)
from host_growth_model import (
    create_host_state_from_config,
    create_initial_host_state,
    update_host_growth_state,
)
from phage_infection_model import (
    create_phage_state_from_config,
    create_initial_phage_state,
    simulate_adsorption_and_recognition,
    simulate_infection_cycle,
)


def extract_infection_summary(phage_state) -> dict[str, float | str]:
    """Extract a compact, unified infection summary from the phage state."""

    return {
        "receptor_type": getattr(phage_state, "receptor_type", ""),
        "receptor_variant": getattr(phage_state, "receptor_variant", ""),
        "transcription_capacity": getattr(phage_state, "transcription_capacity", 0.0),
        "translation_capacity": getattr(phage_state, "translation_capacity", 0.0),
        "energy_state": getattr(phage_state, "energy_state", 0.0),
        "host_defense_stage": getattr(phage_state, "host_defense_stage", "none"),
        "host_defense_strength": getattr(phage_state, "host_defense_strength", 0.0),
        "host_takeover_level": getattr(phage_state, "host_takeover_level", 0.0),
        "phage_resource_allocation": getattr(
            phage_state,
            "phage_resource_allocation",
            0.0,
        ),
        "receptor_target_type": phage_state.receptor_target_type,
        "target_variant_preference": phage_state.target_variant_preference,
        "recognition_match_score": phage_state.recognition_match_score,
        "adsorption_probability": phage_state.adsorption_probability,
        "injection_success_probability": phage_state.injection_success_probability,
        "adsorption_state": phage_state.adsorption_state,
        "injection_state": phage_state.injection_state,
        "infection_outcome": phage_state.infection_outcome,
        "failure_cause": phage_state.failure_cause,
        "failure_stage": phage_state.failure_stage,
        "trajectory_label": phage_state.trajectory_label,
        "early_expression_state": phage_state.early_expression_state,
        "replication_state": phage_state.replication_state,
        "late_assembly_state": phage_state.late_assembly_state,
        "lysis_state": phage_state.lysis_state,
        "progeny_potential": phage_state.progeny_potential,
        "release_readiness": phage_state.release_readiness,
        "latent_period_proxy": phage_state.latent_period_proxy,
    }


def extract_stage_progression_summary(phage_state) -> dict[str, float | str]:
    """Extract a compact stage-progression summary from the phage state."""

    infection_summary = extract_infection_summary(phage_state)
    early_expression_state = float(infection_summary["early_expression_state"])
    replication_state = float(infection_summary["replication_state"])
    late_assembly_state = float(infection_summary["late_assembly_state"])
    lysis_state = float(infection_summary["lysis_state"])

    if lysis_state > 0.0:
        stage_reach_label = "reached_lysis"
    elif late_assembly_state > 0.0:
        stage_reach_label = "reached_assembly"
    elif replication_state > 0.0:
        stage_reach_label = "reached_replication"
    elif early_expression_state > 0.0:
        stage_reach_label = "reached_early_expression"
    else:
        stage_reach_label = "reached_adsorption_only"

    return {
        "recognition_match_score": infection_summary["recognition_match_score"],
        "adsorption_probability": infection_summary["adsorption_probability"],
        "injection_success_probability": infection_summary[
            "injection_success_probability"
        ],
        "early_expression_state": early_expression_state,
        "replication_state": replication_state,
        "late_assembly_state": late_assembly_state,
        "lysis_state": lysis_state,
        "infection_outcome": infection_summary["infection_outcome"],
        "failure_cause": infection_summary["failure_cause"],
        "failure_stage": infection_summary["failure_stage"],
        "trajectory_label": infection_summary["trajectory_label"],
        "stage_reach_label": stage_reach_label,
    }


def extract_host_remodeling_summary(
    host_state,
    phage_state,
    initial_host_state=None,
) -> dict[str, float | str]:
    """Extract a compact host-remodeling summary after infection progression."""

    infection_summary = extract_infection_summary(phage_state)
    if initial_host_state is None:
        initial_host_state = host_state

    delta_transcription_capacity = (
        host_state.transcription_capacity - initial_host_state.transcription_capacity
    )
    delta_translation_capacity = (
        host_state.translation_capacity - initial_host_state.translation_capacity
    )
    delta_energy_state = host_state.energy_state - initial_host_state.energy_state
    remodeling_magnitude = (
        abs(delta_transcription_capacity)
        + abs(delta_translation_capacity)
        + abs(delta_energy_state)
    )
    host_remodeling_label = "limited_remodeling"
    if (
        float(host_state.host_takeover_level) <= 0.05
        and float(host_state.phage_resource_allocation) <= 0.05
        and remodeling_magnitude < 0.02
    ):
        host_remodeling_label = "minimal_remodeling"
    elif (
        infection_summary["failure_cause"] == "host_defense"
        and remodeling_magnitude < 0.04
    ):
        host_remodeling_label = "defense_preserved_host_state"
    elif (
        float(host_state.host_takeover_level) >= 0.3
        and float(host_state.phage_resource_allocation) >= 0.15
        and remodeling_magnitude >= 0.06
    ):
        host_remodeling_label = "deep_remodeling"

    return {
        "initial_transcription_capacity": initial_host_state.transcription_capacity,
        "final_transcription_capacity": host_state.transcription_capacity,
        "delta_transcription_capacity": delta_transcription_capacity,
        "initial_translation_capacity": initial_host_state.translation_capacity,
        "final_translation_capacity": host_state.translation_capacity,
        "delta_translation_capacity": delta_translation_capacity,
        "initial_energy_state": initial_host_state.energy_state,
        "final_energy_state": host_state.energy_state,
        "delta_energy_state": delta_energy_state,
        "host_takeover_level": host_state.host_takeover_level,
        "phage_resource_allocation": host_state.phage_resource_allocation,
        "infection_outcome": infection_summary["infection_outcome"],
        "failure_cause": infection_summary["failure_cause"],
        "failure_stage": infection_summary["failure_stage"],
        "trajectory_label": infection_summary["trajectory_label"],
        "host_remodeling_label": host_remodeling_label,
    }


def extract_standard_phase1_summary(
    host_state,
    phage_state,
    initial_host_state=None,
) -> dict[str, float | str]:
    """Extract the standard phase-1 summary from host and phage states."""

    infection_summary = extract_infection_summary(phage_state)
    stage_progression_summary = extract_stage_progression_summary(phage_state)
    host_remodeling_summary = extract_host_remodeling_summary(
        host_state,
        phage_state,
        initial_host_state=initial_host_state,
    )

    return {
        "recognition_match_score": stage_progression_summary[
            "recognition_match_score"
        ],
        "adsorption_probability": stage_progression_summary["adsorption_probability"],
        "injection_success_probability": stage_progression_summary[
            "injection_success_probability"
        ],
        "early_expression_state": stage_progression_summary["early_expression_state"],
        "replication_state": stage_progression_summary["replication_state"],
        "late_assembly_state": stage_progression_summary["late_assembly_state"],
        "lysis_state": stage_progression_summary["lysis_state"],
        "stage_reach_label": stage_progression_summary["stage_reach_label"],
        "infection_outcome": infection_summary["infection_outcome"],
        "failure_cause": infection_summary["failure_cause"],
        "failure_stage": infection_summary["failure_stage"],
        "trajectory_label": infection_summary["trajectory_label"],
        "host_takeover_level": host_remodeling_summary["host_takeover_level"],
        "phage_resource_allocation": host_remodeling_summary[
            "phage_resource_allocation"
        ],
        "host_remodeling_label": host_remodeling_summary["host_remodeling_label"],
    }


def run_single_case(
    host_config_name: str,
    phage_config_name: str,
    dt: float = 0.1,
    return_full_states: bool = False,
) -> dict[str, float | str] | dict[str, object]:
    """Run one named phase-1 case through the current standard pipeline.

    By default this returns the standard phase-1 summary. When
    ``return_full_states`` is True, it returns the host/phage states, the
    saved initial host state, and the standard summary together.
    """

    if dt < 0:
        raise ValueError("dt must be non-negative")

    host_state = create_host_state_from_config(host_config_name)
    initial_host_state = create_host_state_from_config(host_config_name)
    phage_state = create_phage_state_from_config(phage_config_name)

    host_state = update_host_growth_state(host_state, dt)
    phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
    phage_state = simulate_infection_cycle(host_state, phage_state, dt)
    phage_state.receptor_type = host_state.receptor_type
    phage_state.receptor_variant = host_state.receptor_variant
    phage_state.transcription_capacity = host_state.transcription_capacity
    phage_state.translation_capacity = host_state.translation_capacity
    phage_state.energy_state = host_state.energy_state
    phage_state.host_defense_stage = host_state.host_defense_stage
    phage_state.host_defense_strength = host_state.host_defense_strength
    phage_state.host_takeover_level = host_state.host_takeover_level
    phage_state.phage_resource_allocation = host_state.phage_resource_allocation

    standard_summary = extract_standard_phase1_summary(
        host_state,
        phage_state,
        initial_host_state=initial_host_state,
    )

    if return_full_states:
        return {
            "host_state": host_state,
            "phage_state": phage_state,
            "initial_host_state": initial_host_state,
            "standard_summary": standard_summary,
        }

    return standard_summary


def run_minimal_simulation() -> dict[str, float | str]:
    """Run a one-step placeholder simulation.

    The goal is not numerical realism yet. This function only demonstrates
    the basic data flow between the host-growth module and the phage-
    infection module, which gives us a stable starting point for later
    extensions.
    """

    # Single-step placeholder time increment. Later versions can replace
    # this with a loop over many time steps or an event-driven controller.
    dt = 0.1

    # Initialize the host and phage states with their default stage-1 values.
    host_state = create_initial_host_state()
    phage_state = create_initial_phage_state()

    # Update the host first so downstream infection logic can depend on the
    # current physiological state of the host.
    host_state = update_host_growth_state(host_state, dt)

    # Keep adsorption/recognition as an explicit independent module.
    phage_state = simulate_adsorption_and_recognition(host_state, phage_state)

    # Then advance the simplified infection-cycle state by one step.
    phage_state = simulate_infection_cycle(host_state, phage_state, dt)
    phage_state.receptor_type = host_state.receptor_type
    phage_state.receptor_variant = host_state.receptor_variant
    phage_state.transcription_capacity = host_state.transcription_capacity
    phage_state.translation_capacity = host_state.translation_capacity
    phage_state.energy_state = host_state.energy_state
    phage_state.host_defense_stage = host_state.host_defense_stage
    phage_state.host_defense_strength = host_state.host_defense_strength
    phage_state.host_takeover_level = host_state.host_takeover_level
    phage_state.phage_resource_allocation = host_state.phage_resource_allocation

    return {
        "host_growth_rate": host_state.growth_rate,
        "receptor_availability": host_state.receptor_availability,
        **extract_infection_summary(phage_state),
    }


def run_receptor_matching_comparison() -> dict[str, dict[str, float | str]]:
    """Compare matched and mismatched receptor cases in one minimal step.

    This is a simple control check for the current rule layer. Later
    versions can expand this pattern into multi-step, multi-host, or
    multi-phage comparison experiments without changing the module order.
    """

    return {
        "matched_case": run_single_case(
            host_config_name="ecoli_LPS_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "mismatched_case": run_single_case(
            host_config_name="ecoli_OmpC_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "variant_mismatched_case": run_single_case(
            host_config_name="ecoli_LPS_variant_B_host",
            phage_config_name="T7_like_LPS_phage",
        ),
    }


def run_host_resource_comparison() -> dict[str, dict[str, float | str]]:
    """Compare matched infections under different host resource states."""

    return {
        "high_resource_matched_case": run_single_case(
            host_config_name="ecoli_LPS_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "low_resource_matched_case": run_single_case(
            host_config_name="ecoli_LPS_low_resource_host",
            phage_config_name="T7_like_LPS_phage",
        ),
    }


def run_host_defense_comparison() -> dict[str, dict[str, float | str]]:
    """Compare matched infections with and without a host defense placeholder."""

    return {
        "high_resource_no_defense_case": run_single_case(
            host_config_name="ecoli_LPS_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "replication_defense_case": run_single_case(
            host_config_name="ecoli_LPS_replication_defense_host",
            phage_config_name="T7_like_LPS_phage",
        ),
    }


def run_resource_dimension_sensitivity_comparison() -> dict[str, dict[str, float | str]]:
    """Compare matched infections under isolated resource-dimension reductions."""

    return {
        "high_resource_matched_case": run_single_case(
            host_config_name="ecoli_LPS_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "low_transcription_case": run_single_case(
            host_config_name="ecoli_LPS_low_transcription_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "low_translation_case": run_single_case(
            host_config_name="ecoli_LPS_low_translation_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "low_energy_case": run_single_case(
            host_config_name="ecoli_LPS_low_energy_host",
            phage_config_name="T7_like_LPS_phage",
        ),
    }


def run_host_takeover_comparison() -> dict[str, dict[str, float | str]]:
    """Run the minimal host-takeover visibility check for one matched case."""

    return {
        "ecoli_LPS_host__T7_like_LPS_phage": run_single_case(
            host_config_name="ecoli_LPS_host",
            phage_config_name="T7_like_LPS_phage",
        ),
    }


def run_host_takeover_trajectory_comparison() -> dict[str, dict[str, float | str]]:
    """Compare host takeover trajectories across three infection outcomes."""

    return {
        "high_resource_matched_case": run_single_case(
            host_config_name="ecoli_LPS_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "low_energy_case": run_single_case(
            host_config_name="ecoli_LPS_low_energy_host",
            phage_config_name="T7_like_LPS_phage",
        ),
        "replication_defense_case": run_single_case(
            host_config_name="ecoli_LPS_replication_defense_host",
            phage_config_name="T7_like_LPS_phage",
        ),
    }


def run_host_remodeling_comparison() -> dict[str, dict[str, float | str]]:
    """Compare host remodeling summaries across three representative cases."""

    case_definitions = {
        "high_resource_matched_case": "ecoli_LPS_host",
        "low_energy_case": "ecoli_LPS_low_energy_host",
        "replication_defense_case": "ecoli_LPS_replication_defense_host",
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, host_config_name in case_definitions.items():
        case_result = run_single_case(
            host_config_name=host_config_name,
            phage_config_name="T7_like_LPS_phage",
            return_full_states=True,
        )
        results[case_name] = extract_host_remodeling_summary(
            case_result["host_state"],
            case_result["phage_state"],
            initial_host_state=case_result["initial_host_state"],
        )

    return results


def run_host_remodeling_delta_comparison() -> dict[str, dict[str, float | str]]:
    """Compare host remodeling deltas across three representative cases."""

    comparison_results = run_host_remodeling_comparison()
    labeled_results: dict[str, dict[str, float | str]] = {}

    for case_name, case_result in comparison_results.items():
        remodeling_magnitude = (
            abs(float(case_result["delta_transcription_capacity"]))
            + abs(float(case_result["delta_translation_capacity"]))
            + abs(float(case_result["delta_energy_state"]))
        )
        host_remodeling_label = "limited_remodeling"
        if (
            float(case_result["host_takeover_level"]) <= 0.05
            and float(case_result["phage_resource_allocation"]) <= 0.05
            and remodeling_magnitude < 0.02
        ):
            host_remodeling_label = "minimal_remodeling"
        elif (
            case_result["failure_cause"] == "host_defense"
            and remodeling_magnitude < 0.04
        ):
            host_remodeling_label = "defense_preserved_host_state"
        elif (
            float(case_result["host_takeover_level"]) >= 0.3
            and float(case_result["phage_resource_allocation"]) >= 0.15
            and remodeling_magnitude >= 0.06
        ):
            host_remodeling_label = "deep_remodeling"

        labeled_results[case_name] = {
            **case_result,
            "host_remodeling_label": host_remodeling_label,
        }

    return labeled_results


def run_trajectory_remodeling_matrix() -> dict[str, dict[str, float | str]]:
    """Compare trajectory labels and host remodeling labels side by side."""

    matrix_results: dict[str, dict[str, float | str]] = {}
    case_definitions = {
        "high_resource_matched_case": "ecoli_LPS_host",
        "low_energy_case": "ecoli_LPS_low_energy_host",
        "replication_defense_case": "ecoli_LPS_replication_defense_host",
    }

    for case_name, host_config_name in case_definitions.items():
        case_result = run_single_case(
            host_config_name=host_config_name,
            phage_config_name="T7_like_LPS_phage",
            return_full_states=True,
        )
        standard_summary = case_result["standard_summary"]
        host_remodeling_summary = extract_host_remodeling_summary(
            case_result["host_state"],
            case_result["phage_state"],
            initial_host_state=case_result["initial_host_state"],
        )
        matrix_results[case_name] = {
            "infection_outcome": standard_summary["infection_outcome"],
            "failure_cause": standard_summary["failure_cause"],
            "failure_stage": standard_summary["failure_stage"],
            "trajectory_label": standard_summary["trajectory_label"],
            "host_remodeling_label": standard_summary["host_remodeling_label"],
            "host_takeover_level": standard_summary["host_takeover_level"],
            "phage_resource_allocation": standard_summary[
                "phage_resource_allocation"
            ],
            "delta_transcription_capacity": host_remodeling_summary[
                "delta_transcription_capacity"
            ],
            "delta_translation_capacity": host_remodeling_summary[
                "delta_translation_capacity"
            ],
            "delta_energy_state": host_remodeling_summary["delta_energy_state"],
        }

    return matrix_results


def run_takeover_allocation_interpretation() -> dict[str, dict[str, float | str]]:
    """Compare takeover establishment and downstream allocation across cases."""

    case_names = {
        "high_resource_matched_case": "ecoli_LPS_host",
        "low_energy_case": "ecoli_LPS_low_energy_host",
        "replication_defense_case": "ecoli_LPS_replication_defense_host",
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, host_config_name in case_names.items():
        case_result = run_single_case(
            host_config_name=host_config_name,
            phage_config_name="T7_like_LPS_phage",
            return_full_states=True,
        )
        infection_summary = extract_infection_summary(case_result["phage_state"])
        results[case_name] = {
            "host_takeover_level": infection_summary["host_takeover_level"],
            "phage_resource_allocation": infection_summary[
                "phage_resource_allocation"
            ],
            "takeover_to_allocation_gap": (
                float(infection_summary["host_takeover_level"])
                - float(infection_summary["phage_resource_allocation"])
            ),
            "downstream_progress_indicator": (
                float(infection_summary["replication_state"])
                + float(infection_summary["late_assembly_state"])
                + float(infection_summary["lysis_state"])
            ),
            "progeny_potential": infection_summary["progeny_potential"],
            "early_expression_state": infection_summary["early_expression_state"],
            "replication_state": infection_summary["replication_state"],
            "late_assembly_state": infection_summary["late_assembly_state"],
            "lysis_state": infection_summary["lysis_state"],
            "infection_outcome": infection_summary["infection_outcome"],
            "failure_cause": infection_summary["failure_cause"],
        }

    return results


def run_late_stage_progression_comparison() -> dict[str, dict[str, float | str]]:
    """Compare coarse-grained late-stage progression across three cases."""

    case_names = {
        "high_resource_matched_case": "ecoli_LPS_host",
        "low_energy_case": "ecoli_LPS_low_energy_host",
        "replication_defense_case": "ecoli_LPS_replication_defense_host",
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, host_config_name in case_names.items():
        case_result = _run_single_receptor_case(
            host_config_name=host_config_name,
            phage_config_name="T7_like_LPS_phage",
        )
        results[case_name] = {
            "host_takeover_level": case_result["host_takeover_level"],
            "phage_resource_allocation": case_result["phage_resource_allocation"],
            "replication_state": case_result["replication_state"],
            "late_assembly_state": case_result["late_assembly_state"],
            "progeny_potential": case_result["progeny_potential"],
            "release_readiness": case_result["release_readiness"],
            "latent_period_proxy": case_result["latent_period_proxy"],
            "lysis_state": case_result["lysis_state"],
            "infection_outcome": case_result["infection_outcome"],
            "failure_cause": case_result["failure_cause"],
            "failure_stage": case_result["failure_stage"],
        }

    return results


def run_progeny_release_interpretation() -> dict[str, dict[str, float | str]]:
    """Compare progeny buildup and release-readiness across three cases."""

    case_names = {
        "high_resource_matched_case": "ecoli_LPS_host",
        "low_energy_case": "ecoli_LPS_low_energy_host",
        "replication_defense_case": "ecoli_LPS_replication_defense_host",
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, host_config_name in case_names.items():
        case_result = _run_single_receptor_case(
            host_config_name=host_config_name,
            phage_config_name="T7_like_LPS_phage",
        )
        results[case_name] = {
            "host_takeover_level": case_result["host_takeover_level"],
            "phage_resource_allocation": case_result["phage_resource_allocation"],
            "replication_state": case_result["replication_state"],
            "late_assembly_state": case_result["late_assembly_state"],
            "progeny_potential": case_result["progeny_potential"],
            "release_readiness": case_result["release_readiness"],
            "latent_period_proxy": case_result["latent_period_proxy"],
            "lysis_state": case_result["lysis_state"],
            "infection_outcome": case_result["infection_outcome"],
            "failure_cause": case_result["failure_cause"],
        }

    return results


def run_failure_trajectory_summary() -> dict[str, dict[str, float | str]]:
    """Summarize four representative success and failure trajectories."""

    case_definitions = {
        "high_resource_matched_case": "ecoli_LPS_host",
        "low_energy_case": "ecoli_LPS_low_energy_host",
        "replication_defense_case": "ecoli_LPS_replication_defense_host",
        "receptor_mismatch_case": "ecoli_OmpC_host",
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, host_config_name in case_definitions.items():
        case_result = _run_single_receptor_case(
            host_config_name=host_config_name,
            phage_config_name="T7_like_LPS_phage",
        )
        results[case_name] = {
            "recognition_match_score": case_result["recognition_match_score"],
            "host_takeover_level": case_result["host_takeover_level"],
            "phage_resource_allocation": case_result["phage_resource_allocation"],
            "replication_state": case_result["replication_state"],
            "late_assembly_state": case_result["late_assembly_state"],
            "progeny_potential": case_result["progeny_potential"],
            "release_readiness": case_result["release_readiness"],
            "latent_period_proxy": case_result["latent_period_proxy"],
            "lysis_state": case_result["lysis_state"],
            "infection_outcome": case_result["infection_outcome"],
            "failure_cause": case_result["failure_cause"],
            "failure_stage": case_result["failure_stage"],
            "trajectory_label": case_result["trajectory_label"],
        }

    return results


def run_energy_transition_scan() -> dict[str, dict[str, float | str]]:
    """Scan matched infections across a small range of host energy states."""

    energy_levels = [1.0, 0.8, 0.6, 0.4, 0.2]
    results: dict[str, dict[str, float | str]] = {}

    for energy_level in energy_levels:
        dt = 0.1
        host_state = create_host_state_from_config("ecoli_LPS_host")
        initial_host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.energy_state = energy_level
        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        phage_state.host_takeover_level = host_state.host_takeover_level
        phage_state.phage_resource_allocation = host_state.phage_resource_allocation

        summary = extract_infection_summary(phage_state)
        results[f"energy_{energy_level:.1f}"] = {
            "recognition_match_score": summary["recognition_match_score"],
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "progeny_potential": summary["progeny_potential"],
            "release_readiness": summary["release_readiness"],
            "latent_period_proxy": summary["latent_period_proxy"],
            "lysis_state": summary["lysis_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_defense_transition_scan() -> dict[str, dict[str, float | str]]:
    """Scan matched infections across a small range of defense strengths."""

    defense_levels = [0.0, 0.2, 0.4, 0.6, 0.8]
    results: dict[str, dict[str, float | str]] = {}

    for defense_level in defense_levels:
        dt = 0.1
        host_state = create_host_state_from_config("ecoli_LPS_replication_defense_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.host_defense_strength = defense_level
        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)

        summary = extract_infection_summary(phage_state)
        results[f"defense_{defense_level:.1f}"] = {
            "recognition_match_score": summary["recognition_match_score"],
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "progeny_potential": summary["progeny_potential"],
            "release_readiness": summary["release_readiness"],
            "latent_period_proxy": summary["latent_period_proxy"],
            "lysis_state": summary["lysis_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_energy_defense_grid_scan() -> dict[str, dict[str, dict[str, float | str]]]:
    """Scan matched infections across a small energy-defense grid."""

    energy_levels = [1.0, 0.8, 0.6]
    defense_levels = [0.0, 0.2, 0.4]
    results: dict[str, dict[str, dict[str, float | str]]] = {}

    for energy_level in energy_levels:
        energy_key = f"energy_{energy_level:.1f}"
        results[energy_key] = {}

        for defense_level in defense_levels:
            dt = 0.1
            host_state = create_host_state_from_config("ecoli_LPS_replication_defense_host")
            phage_state = create_phage_state_from_config("T7_like_LPS_phage")

            host_state.energy_state = energy_level
            host_state.host_defense_strength = defense_level
            if defense_level == 0.0:
                host_state.host_defense_stage = "none"
            else:
                host_state.host_defense_stage = "replication"
            host_state = update_host_growth_state(host_state, dt)
            phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
            phage_state = simulate_infection_cycle(host_state, phage_state, dt)

            summary = extract_infection_summary(phage_state)
            results[energy_key][f"defense_{defense_level:.1f}"] = {
                "infection_outcome": summary["infection_outcome"],
                "failure_cause": summary["failure_cause"],
                "failure_stage": summary["failure_stage"],
                "trajectory_label": summary["trajectory_label"],
            }

    return results


def run_defense_annotation_stub_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate host defense-layer mapping from annotation stubs."""

    annotation_stubs = {
        "no_defense_annotation_stub": {
            "host_defense_stage_stub": "none",
            "host_defense_strength_class": "none",
        },
        "low_replication_defense_stub": {
            "host_defense_stage_stub": "replication",
            "host_defense_strength_class": "low",
        },
        "high_replication_defense_stub": {
            "host_defense_stage_stub": "replication",
            "host_defense_strength_class": "high",
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, annotation_stub in annotation_stubs.items():
        dt = 0.1
        defense_config = build_host_defense_config_from_annotation_stub(
            annotation_stub
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        initial_host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.host_defense_stage = str(defense_config["host_defense_stage"])
        host_state.host_defense_strength = float(defense_config["host_defense_strength"])

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        phage_state.host_takeover_level = host_state.host_takeover_level
        phage_state.phage_resource_allocation = host_state.phage_resource_allocation

        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
            "host_takeover_level": summary["host_takeover_level"],
            "phage_resource_allocation": summary["phage_resource_allocation"],
        }

    return results


def run_resource_annotation_stub_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate host resource-layer mapping from annotation stubs."""

    annotation_stubs = {
        "high_resource_annotation_stub": {
            "host_transcription_class": "high",
            "host_translation_class": "high",
            "host_energy_class": "high",
            "host_growth_class": "high",
        },
        "medium_resource_annotation_stub": {
            "host_transcription_class": "medium",
            "host_translation_class": "medium",
            "host_energy_class": "medium",
            "host_growth_class": "medium",
        },
        "low_resource_annotation_stub": {
            "host_transcription_class": "low",
            "host_translation_class": "low",
            "host_energy_class": "low",
            "host_growth_class": "low",
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, annotation_stub in annotation_stubs.items():
        dt = 0.1
        resource_config = build_host_resource_config_from_annotation_stub(
            annotation_stub
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        initial_host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.transcription_capacity = float(
            resource_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(resource_config["translation_capacity"])
        host_state.energy_state = float(resource_config["energy_state"])
        host_state.growth_rate = float(resource_config["growth_rate"])

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "progeny_potential": summary["progeny_potential"],
            "release_readiness": summary["release_readiness"],
            "lysis_state": summary["lysis_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_resource_annotation_alias_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate host resource-layer mapping from alias-style annotation stubs."""

    annotation_stubs = {
        "alias_high_resource_stub": {
            "host_transcription_capacity_class": "high",
            "host_translation_capacity_class": "high",
            "host_cellular_energy_class": "high",
            "host_growth_capacity_class": "high",
        },
        "alias_medium_resource_stub": {
            "host_transcription_capacity_class": "medium",
            "host_expression_capacity_class": "medium",
            "host_cellular_energy_class": "medium",
            "host_growth_capacity_class": "medium",
        },
        "alias_low_resource_stub": {
            "host_transcription_capacity_class": "low",
            "host_translation_capacity_class": "low",
            "host_cellular_energy_class": "low",
            "host_growth_capacity_class": "low",
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, annotation_stub in annotation_stubs.items():
        dt = 0.1
        resource_config = build_host_resource_config_from_annotation_stub(
            annotation_stub
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.transcription_capacity = float(
            resource_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(resource_config["translation_capacity"])
        host_state.energy_state = float(resource_config["energy_state"])
        host_state.growth_rate = float(resource_config["growth_rate"])

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "progeny_potential": summary["progeny_potential"],
            "release_readiness": summary["release_readiness"],
            "lysis_state": summary["lysis_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_resource_class_transition_scan() -> dict[str, dict[str, float | str]]:
    """Scan infection trajectories across a small host-resource class ladder."""

    annotation_stubs = {
        "all_high": {
            "host_transcription_class": "high",
            "host_translation_class": "high",
            "host_energy_class": "high",
            "host_growth_class": "high",
        },
        "high_medium_mix": {
            "host_transcription_class": "high",
            "host_translation_class": "medium",
            "host_energy_class": "medium",
            "host_growth_class": "high",
        },
        "all_medium": {
            "host_transcription_class": "medium",
            "host_translation_class": "medium",
            "host_energy_class": "medium",
            "host_growth_class": "medium",
        },
        "medium_low_mix": {
            "host_transcription_class": "medium",
            "host_translation_class": "low",
            "host_energy_class": "low",
            "host_growth_class": "medium",
        },
        "all_low": {
            "host_transcription_class": "low",
            "host_translation_class": "low",
            "host_energy_class": "low",
            "host_growth_class": "low",
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, annotation_stub in annotation_stubs.items():
        dt = 0.1
        resource_config = build_host_resource_config_from_annotation_stub(
            annotation_stub
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.transcription_capacity = float(
            resource_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(resource_config["translation_capacity"])
        host_state.energy_state = float(resource_config["energy_state"])
        host_state.growth_rate = float(resource_config["growth_rate"])

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "progeny_potential": summary["progeny_potential"],
            "release_readiness": summary["release_readiness"],
            "lysis_state": summary["lysis_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_combined_annotation_stub_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate combined recognition and resource annotation-stub mapping."""

    case_definitions = {
        "matched_high_resource_stub": {
            "recognition_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "resource_stub": {
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
        },
        "matched_medium_resource_stub": {
            "recognition_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "resource_stub": {
                "host_transcription_class": "medium",
                "host_translation_class": "medium",
                "host_energy_class": "medium",
                "host_growth_class": "medium",
            },
        },
        "receptor_mismatch_high_resource_stub": {
            "recognition_stub": {
                "host_receptor_type": "OmpC",
                "host_receptor_variant": "OmpC_variant_A",
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "resource_stub": {
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        recognition_config = build_recognition_config_from_annotation_stub(
            case_definition["recognition_stub"]
        )
        resource_config = build_host_resource_config_from_annotation_stub(
            case_definition["resource_stub"]
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(recognition_config["receptor_type"])
        host_state.receptor_variant = str(recognition_config["receptor_variant"])
        phage_state.receptor_target_type = str(
            recognition_config["receptor_target_type"]
        )
        phage_state.target_variant_preference = str(
            recognition_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            recognition_config["binding_specificity_strength"]
        )
        host_state.transcription_capacity = float(
            resource_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(resource_config["translation_capacity"])
        host_state.energy_state = float(resource_config["energy_state"])
        host_state.growth_rate = float(resource_config["growth_rate"])

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "progeny_potential": summary["progeny_potential"],
            "release_readiness": summary["release_readiness"],
            "lysis_state": summary["lysis_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_combined_annotation_pipeline_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate combined recognition, resource, and defense annotation stubs."""

    from entity_configs import prepare_normalized_annotation_inputs

    case_definitions = {
        "matched_high_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
        "matched_high_resource_high_replication_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "replication",
                "host_defense_strength_class": "high",
            },
        },
        "receptor_mismatch_high_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "OmpC",
                "host_receptor_variant": "OmpC_variant_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        prepared_inputs = prepare_normalized_annotation_inputs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        combined_config = prepared_inputs["combined_config"]
        if combined_config is None:
            raise ValueError(
                "run_combined_annotation_pipeline_demo requires minimally valid "
                "annotation stubs"
            )
        defense_config = build_host_defense_config_from_annotation_stub(
            case_definition["defense_annotation_stub"]
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        initial_host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        host_state.host_defense_stage = str(defense_config["host_defense_stage"])
        host_state.host_defense_strength = float(defense_config["host_defense_strength"])
        initial_host_state.receptor_type = host_state.receptor_type
        initial_host_state.receptor_variant = host_state.receptor_variant
        initial_host_state.transcription_capacity = host_state.transcription_capacity
        initial_host_state.translation_capacity = host_state.translation_capacity
        initial_host_state.energy_state = host_state.energy_state
        initial_host_state.growth_rate = host_state.growth_rate
        initial_host_state.host_defense_stage = host_state.host_defense_stage
        initial_host_state.host_defense_strength = host_state.host_defense_strength
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        standard_summary = extract_standard_phase1_summary(
            host_state,
            phage_state,
            initial_host_state=initial_host_state,
        )
        results[case_name] = {
            "recognition_match_score": standard_summary["recognition_match_score"],
            "replication_state": standard_summary["replication_state"],
            "late_assembly_state": standard_summary["late_assembly_state"],
            "infection_outcome": standard_summary["infection_outcome"],
            "failure_cause": standard_summary["failure_cause"],
            "failure_stage": standard_summary["failure_stage"],
            "trajectory_label": standard_summary["trajectory_label"],
            "host_takeover_level": standard_summary["host_takeover_level"],
            "phage_resource_allocation": standard_summary[
                "phage_resource_allocation"
            ],
        }

    return results


def run_stage_progression_comparison() -> dict[str, dict[str, float | str]]:
    """Compare stage-progression summaries across three minimal trajectories."""

    from entity_configs import prepare_normalized_annotation_inputs

    case_definitions = {
        "matched_high_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
        "matched_high_resource_high_replication_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "replication",
                "host_defense_strength_class": "high",
            },
        },
        "receptor_mismatch_high_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "OmpC",
                "host_receptor_variant": "OmpC_variant_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        prepared_inputs = prepare_normalized_annotation_inputs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        combined_config = prepared_inputs["combined_config"]
        if combined_config is None:
            raise ValueError(
                "run_stage_progression_comparison requires minimally valid "
                "annotation stubs"
            )
        defense_config = build_host_defense_config_from_annotation_stub(
            case_definition["defense_annotation_stub"]
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        initial_host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        host_state.host_defense_stage = str(defense_config["host_defense_stage"])
        host_state.host_defense_strength = float(defense_config["host_defense_strength"])
        initial_host_state.receptor_type = host_state.receptor_type
        initial_host_state.receptor_variant = host_state.receptor_variant
        initial_host_state.transcription_capacity = host_state.transcription_capacity
        initial_host_state.translation_capacity = host_state.translation_capacity
        initial_host_state.energy_state = host_state.energy_state
        initial_host_state.growth_rate = host_state.growth_rate
        initial_host_state.host_defense_stage = host_state.host_defense_stage
        initial_host_state.host_defense_strength = host_state.host_defense_strength
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        standard_summary = extract_standard_phase1_summary(
            host_state,
            phage_state,
            initial_host_state=initial_host_state,
        )
        results[case_name] = {
            "recognition_match_score": standard_summary["recognition_match_score"],
            "adsorption_probability": standard_summary["adsorption_probability"],
            "injection_success_probability": standard_summary[
                "injection_success_probability"
            ],
            "early_expression_state": standard_summary["early_expression_state"],
            "replication_state": standard_summary["replication_state"],
            "late_assembly_state": standard_summary["late_assembly_state"],
            "lysis_state": standard_summary["lysis_state"],
            "infection_outcome": standard_summary["infection_outcome"],
            "failure_cause": standard_summary["failure_cause"],
            "failure_stage": standard_summary["failure_stage"],
            "trajectory_label": standard_summary["trajectory_label"],
            "stage_reach_label": standard_summary["stage_reach_label"],
        }

    return results


def run_skewed_resource_stage_comparison() -> dict[str, dict[str, float | str]]:
    """Compare stage progression across matched hosts with skewed resource states."""

    case_definitions = {
        "high_resource_matched_case": "ecoli_LPS_host",
        "low_transcription_case": "ecoli_LPS_low_transcription_host",
        "low_translation_case": "ecoli_LPS_low_translation_host",
        "low_energy_case": "ecoli_LPS_low_energy_host",
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, host_config_name in case_definitions.items():
        dt = 0.1
        host_state = create_host_state_from_config(host_config_name)
        initial_host_state = create_host_state_from_config(host_config_name)
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        standard_summary = extract_standard_phase1_summary(
            host_state,
            phage_state,
            initial_host_state=initial_host_state,
        )
        results[case_name] = {
            "early_expression_state": standard_summary["early_expression_state"],
            "replication_state": standard_summary["replication_state"],
            "late_assembly_state": standard_summary["late_assembly_state"],
            "lysis_state": standard_summary["lysis_state"],
            "infection_outcome": standard_summary["infection_outcome"],
            "failure_cause": standard_summary["failure_cause"],
            "failure_stage": standard_summary["failure_stage"],
            "trajectory_label": standard_summary["trajectory_label"],
            "stage_reach_label": standard_summary["stage_reach_label"],
        }

    return results


def run_resource_axis_sensitivity_summary() -> dict[str, dict[str, float | str]]:
    """Summarize stage sensitivity across skewed host-resource axes."""

    comparison_results = run_skewed_resource_stage_comparison()
    summary_results: dict[str, dict[str, float | str]] = {}

    for case_name, case_result in comparison_results.items():
        summary_results[case_name] = {
            "early_expression_state": case_result["early_expression_state"],
            "replication_state": case_result["replication_state"],
            "late_assembly_state": case_result["late_assembly_state"],
            "stage_reach_label": case_result["stage_reach_label"],
            "infection_outcome": case_result["infection_outcome"],
            "failure_cause": case_result["failure_cause"],
            "failure_stage": case_result["failure_stage"],
            "trajectory_label": case_result["trajectory_label"],
        }

    return summary_results


def run_resource_axis_takeover_probe() -> dict[str, dict[str, float | str]]:
    """Probe takeover/allocation and stage reach across skewed resource axes."""

    case_definitions = {
        "high_resource_matched_case": "ecoli_LPS_host",
        "low_transcription_case": "ecoli_LPS_low_transcription_host",
        "low_translation_case": "ecoli_LPS_low_translation_host",
        "low_energy_case": "ecoli_LPS_low_energy_host",
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, host_config_name in case_definitions.items():
        dt = 0.1
        host_state = create_host_state_from_config(host_config_name)
        initial_host_state = create_host_state_from_config(host_config_name)
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        standard_summary = extract_standard_phase1_summary(
            host_state,
            phage_state,
            initial_host_state=initial_host_state,
        )
        results[case_name] = {
            "host_takeover_level": standard_summary["host_takeover_level"],
            "phage_resource_allocation": standard_summary[
                "phage_resource_allocation"
            ],
            "host_remodeling_label": standard_summary["host_remodeling_label"],
            "stage_reach_label": standard_summary["stage_reach_label"],
            "infection_outcome": standard_summary["infection_outcome"],
            "early_expression_state": standard_summary["early_expression_state"],
            "replication_state": standard_summary["replication_state"],
            "late_assembly_state": standard_summary["late_assembly_state"],
        }

    return results


def run_phase2_resource_remodeling_comparison() -> dict[str, dict[str, float | str]]:
    """Return the current phase-2 resource-axis remodeling comparison."""

    return run_resource_axis_takeover_probe()


def run_standard_phase1_summary_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate the standard phase-1 summary across three minimal cases."""

    from entity_configs import prepare_normalized_annotation_inputs

    case_definitions = {
        "matched_high_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
        "matched_high_resource_high_replication_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "replication",
                "host_defense_strength_class": "high",
            },
        },
        "receptor_mismatch_high_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "OmpC",
                "host_receptor_variant": "OmpC_variant_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        prepared_inputs = prepare_normalized_annotation_inputs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        combined_config = prepared_inputs["combined_config"]
        if combined_config is None:
            raise ValueError(
                "run_standard_phase1_summary_demo requires minimally valid "
                "annotation stubs"
            )
        defense_config = build_host_defense_config_from_annotation_stub(
            case_definition["defense_annotation_stub"]
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        initial_host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        host_state.host_defense_stage = str(defense_config["host_defense_stage"])
        host_state.host_defense_strength = float(defense_config["host_defense_strength"])
        initial_host_state.receptor_type = host_state.receptor_type
        initial_host_state.receptor_variant = host_state.receptor_variant
        initial_host_state.transcription_capacity = host_state.transcription_capacity
        initial_host_state.translation_capacity = host_state.translation_capacity
        initial_host_state.energy_state = host_state.energy_state
        initial_host_state.growth_rate = host_state.growth_rate
        initial_host_state.host_defense_stage = host_state.host_defense_stage
        initial_host_state.host_defense_strength = host_state.host_defense_strength
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        results[case_name] = extract_standard_phase1_summary(
            host_state,
            phage_state,
            initial_host_state=initial_host_state,
        )

    return results


def run_phase2_consistency_check() -> dict[str, dict[str, float | str]]:
    """Compare whether core phase-1 labels remain aligned across four cases."""

    from entity_configs import prepare_normalized_annotation_inputs

    case_definitions = {
        "matched_high_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
        "matched_high_resource_high_replication_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "replication",
                "host_defense_strength_class": "high",
            },
        },
        "matched_medium_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "medium",
                "host_translation_class": "medium",
                "host_energy_class": "medium",
                "host_growth_class": "medium",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
        "receptor_mismatch_high_resource_no_defense": {
            "host_annotation_stub": {
                "host_receptor_type": "OmpC",
                "host_receptor_variant": "OmpC_variant_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
            "defense_annotation_stub": {
                "host_defense_stage_stub": "none",
                "host_defense_strength_class": "none",
            },
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        prepared_inputs = prepare_normalized_annotation_inputs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        combined_config = prepared_inputs["combined_config"]
        if combined_config is None:
            raise ValueError(
                "run_phase2_consistency_check requires minimally valid "
                "annotation stubs"
            )
        defense_config = build_host_defense_config_from_annotation_stub(
            case_definition["defense_annotation_stub"]
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        initial_host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        host_state.host_defense_stage = str(defense_config["host_defense_stage"])
        host_state.host_defense_strength = float(defense_config["host_defense_strength"])
        initial_host_state.receptor_type = host_state.receptor_type
        initial_host_state.receptor_variant = host_state.receptor_variant
        initial_host_state.transcription_capacity = host_state.transcription_capacity
        initial_host_state.translation_capacity = host_state.translation_capacity
        initial_host_state.energy_state = host_state.energy_state
        initial_host_state.growth_rate = host_state.growth_rate
        initial_host_state.host_defense_stage = host_state.host_defense_stage
        initial_host_state.host_defense_strength = host_state.host_defense_strength
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        standard_summary = extract_standard_phase1_summary(
            host_state,
            phage_state,
            initial_host_state=initial_host_state,
        )
        results[case_name] = {
            "stage_reach_label": standard_summary["stage_reach_label"],
            "trajectory_label": standard_summary["trajectory_label"],
            "host_remodeling_label": standard_summary["host_remodeling_label"],
            "infection_outcome": standard_summary["infection_outcome"],
            "failure_cause": standard_summary["failure_cause"],
            "failure_stage": standard_summary["failure_stage"],
            "host_takeover_level": standard_summary["host_takeover_level"],
            "phage_resource_allocation": standard_summary[
                "phage_resource_allocation"
            ],
        }

    return results


def run_three_factor_minigrid_scan() -> (
    dict[str, dict[str, dict[str, dict[str, float | str]]]]
):
    """Scan a minimal 2x2x2 recognition-resource-defense trajectory grid."""

    from entity_configs import prepare_normalized_annotation_inputs

    recognition_stubs = {
        "matched": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "receptor_mismatch": {
            "host_annotation_stub": {
                "host_receptor_type": "OmpC",
                "host_receptor_variant": "OmpC_variant_A",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
    }
    resource_stubs = {
        "high_resource": {
            "host_transcription_class": "high",
            "host_translation_class": "high",
            "host_energy_class": "high",
            "host_growth_class": "high",
        },
        "medium_resource": {
            "host_transcription_class": "medium",
            "host_translation_class": "medium",
            "host_energy_class": "medium",
            "host_growth_class": "medium",
        },
    }
    defense_stubs = {
        "no_defense": {
            "host_defense_stage_stub": "none",
            "host_defense_strength_class": "none",
        },
        "high_replication_defense": {
            "host_defense_stage_stub": "replication",
            "host_defense_strength_class": "high",
        },
    }
    results: dict[str, dict[str, dict[str, dict[str, float | str]]]] = {}

    for recognition_name, recognition_definition in recognition_stubs.items():
        results[recognition_name] = {}

        for resource_name, resource_stub in resource_stubs.items():
            results[recognition_name][resource_name] = {}

            for defense_name, defense_stub in defense_stubs.items():
                dt = 0.1
                host_annotation_stub = {
                    **recognition_definition["host_annotation_stub"],
                    **resource_stub,
                }
                prepared_inputs = prepare_normalized_annotation_inputs(
                    host_annotation_stub,
                    recognition_definition["phage_annotation_stub"],
                )
                combined_config = prepared_inputs["combined_config"]
                if combined_config is None:
                    raise ValueError(
                        "run_three_factor_minigrid_scan requires minimally valid "
                        "annotation stubs"
                    )
                defense_config = build_host_defense_config_from_annotation_stub(
                    defense_stub
                )
                host_state = create_host_state_from_config("ecoli_LPS_host")
                phage_state = create_phage_state_from_config("T7_like_LPS_phage")

                host_state.receptor_type = str(combined_config["receptor_type"])
                host_state.receptor_variant = str(combined_config["receptor_variant"])
                host_state.transcription_capacity = float(
                    combined_config["transcription_capacity"]
                )
                host_state.translation_capacity = float(
                    combined_config["translation_capacity"]
                )
                host_state.energy_state = float(combined_config["energy_state"])
                host_state.growth_rate = float(combined_config["growth_rate"])
                host_state.host_defense_stage = str(
                    defense_config["host_defense_stage"]
                )
                host_state.host_defense_strength = float(
                    defense_config["host_defense_strength"]
                )
                phage_state.receptor_target_type = str(
                    combined_config["receptor_target_type"]
                )
                phage_state.target_variant_preference = str(
                    combined_config["target_variant_preference"]
                )
                phage_state.binding_specificity_strength = float(
                    combined_config["binding_specificity_strength"]
                )

                host_state = update_host_growth_state(host_state, dt)
                phage_state = simulate_adsorption_and_recognition(
                    host_state,
                    phage_state,
                )
                phage_state = simulate_infection_cycle(host_state, phage_state, dt)
                phage_state.host_takeover_level = host_state.host_takeover_level
                phage_state.phage_resource_allocation = (
                    host_state.phage_resource_allocation
                )

                summary = extract_infection_summary(phage_state)
                results[recognition_name][resource_name][defense_name] = {
                    "recognition_match_score": summary["recognition_match_score"],
                    "infection_outcome": summary["infection_outcome"],
                    "failure_cause": summary["failure_cause"],
                    "failure_stage": summary["failure_stage"],
                    "trajectory_label": summary["trajectory_label"],
                }

    return results


def run_combined_config_builder_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate the unified combined-config builder on three minimal cases."""

    from entity_configs import prepare_normalized_annotation_inputs

    case_definitions = {
        "combined_matched_high_resource": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "combined_matched_medium_resource": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "medium",
                "host_translation_class": "medium",
                "host_energy_class": "medium",
                "host_growth_class": "medium",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "combined_receptor_mismatch_high_resource": {
            "host_annotation_stub": {
                "host_receptor_type": "OmpC",
                "host_receptor_variant": "OmpC_variant_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        prepared_inputs = prepare_normalized_annotation_inputs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        combined_config = prepared_inputs["combined_config"]
        if combined_config is None:
            raise ValueError(
                "run_combined_config_builder_demo requires minimally valid "
                "annotation stubs"
            )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_combined_builder_missing_field_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate exploratory direct-builder fallback behavior on missing fields."""

    case_definitions = {
        "complete_matched_high_resource": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_resource_fields_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_energy_class": "medium",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_recognition_fields_stub": {
            "host_annotation_stub": {
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_binding_specificity": 1.0,
            },
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        # This deferred demo intentionally exercises direct-builder fallback on
        # missing fields rather than the valid-gated normalized-input helper.
        combined_config = build_combined_config_from_annotation_stubs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_builder_missing_component_scan() -> dict[str, dict[str, float | str]]:
    """Compare exploratory direct-builder outcomes when builder inputs are missing."""

    case_definitions = {
        "complete_reference_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_energy_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_translation_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_receptor_target_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        # This deferred demo intentionally stays on the direct builder so that
        # missing-component fallback behavior remains observable at demo scope.
        combined_config = build_combined_config_from_annotation_stubs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "replication_state": summary["replication_state"],
            "late_assembly_state": summary["late_assembly_state"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_builder_fallback_trace_demo() -> dict[str, dict[str, float | str | list[str]]]:
    """Demonstrate fallback-field tracing from the unified combined builder."""

    case_definitions = {
        "complete_reference_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_energy_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_receptor_target_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
    }
    results: dict[str, dict[str, float | str | list[str]]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        combined_config = build_combined_config_from_annotation_stubs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
            "fallback_fields": list(combined_config.get("fallback_fields", [])),
        }

    return results


def run_builder_multi_fallback_demo() -> dict[str, dict[str, float | str | list[str]]]:
    """Demonstrate fallback tracing when multiple builder inputs are missing."""

    case_definitions = {
        "complete_reference_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_resource_pair_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_recognition_pair_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_binding_specificity": 1.0,
            },
        },
    }
    results: dict[str, dict[str, float | str | list[str]]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        combined_config = build_combined_config_from_annotation_stubs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
            "fallback_fields": list(combined_config.get("fallback_fields", [])),
        }

    return results


def run_annotation_schema_demo() -> dict[str, dict[str, list[str]]]:
    """Return the current minimal annotation schema description."""

    return get_minimal_annotation_schema()


def run_annotation_schema_notes_demo() -> dict[str, dict[str, list[str] | dict[str, str]]]:
    """Return the current minimal annotation schema description with notes."""

    return get_minimal_annotation_schema()


def run_annotation_schema_mapping_demo() -> dict[str, dict[str, list[str] | dict[str, str]]]:
    """Return the current minimal annotation schema description with mappings."""

    return get_minimal_annotation_schema()


def run_annotation_schema_requirement_demo() -> dict[str, dict[str, list[str] | dict[str, str]]]:
    """Return the current minimal annotation schema description with required fields."""

    return get_minimal_annotation_schema()


def run_annotation_validation_demo() -> dict[str, dict[str, list[str] | bool]]:
    """Demonstrate minimal annotation-stub validation against required fields."""

    case_definitions = {
        "complete_reference_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
            },
        },
        "missing_required_host_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
            },
        },
        "missing_required_phage_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
            },
        },
    }
    results: dict[str, dict[str, list[str] | bool]] = {}

    for case_name, case_definition in case_definitions.items():
        results[case_name] = validate_annotation_stubs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )

    return results


def run_pipeline_schema_demo() -> dict[str, object]:
    """Return the current minimal pipeline schema description."""

    return get_minimal_pipeline_schema()


def run_validated_builder_pipeline_demo() -> dict[str, dict[str, list[str] | bool | float | str]]:
    """Demonstrate a minimal validation-builder-simulation pipeline."""

    case_definitions = {
        "complete_reference_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_required_host_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_target_variant_preference": "LPS_core_A",
                "phage_binding_specificity": 1.0,
            },
        },
        "missing_required_phage_field_stub": {
            "host_annotation_stub": {
                "host_receptor_type": "LPS",
                "host_receptor_variant": "LPS_core_A",
                "host_transcription_class": "high",
                "host_translation_class": "high",
                "host_energy_class": "high",
                "host_growth_class": "high",
            },
            "phage_annotation_stub": {
                "phage_receptor_target_type": "LPS",
                "phage_binding_specificity": 1.0,
            },
        },
    }
    results: dict[str, dict[str, list[str] | bool | float | str]] = {}

    for case_name, case_definition in case_definitions.items():
        dt = 0.1
        validation_result = validate_annotation_stubs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        combined_config = build_combined_config_from_annotation_stubs(
            case_definition["host_annotation_stub"],
            case_definition["phage_annotation_stub"],
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(combined_config["receptor_type"])
        host_state.receptor_variant = str(combined_config["receptor_variant"])
        host_state.transcription_capacity = float(
            combined_config["transcription_capacity"]
        )
        host_state.translation_capacity = float(
            combined_config["translation_capacity"]
        )
        host_state.energy_state = float(combined_config["energy_state"])
        host_state.growth_rate = float(combined_config["growth_rate"])
        phage_state.receptor_target_type = str(combined_config["receptor_target_type"])
        phage_state.target_variant_preference = str(
            combined_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            combined_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        validation_status = "invalid_with_fallback"
        if (
            bool(validation_result["is_minimally_valid"])
            and not combined_config.get("fallback_fields", [])
        ):
            validation_status = "valid_complete"
        pipeline_decision = "run_with_fallback"
        if (
            validation_status == "valid_complete"
            and not combined_config.get("fallback_fields", [])
        ):
            pipeline_decision = "run_direct"
        pipeline_summary_label = "fallback_degraded"
        if (
            pipeline_decision == "run_direct"
            and summary["trajectory_label"] == "successful_progression"
        ):
            pipeline_summary_label = "complete_success"
        elif (
            pipeline_decision == "run_with_fallback"
            and summary["trajectory_label"] == "recognition_failure"
        ):
            pipeline_summary_label = "fallback_failure"
        results[case_name] = {
            "is_minimally_valid": bool(validation_result["is_minimally_valid"]),
            "validation_status": validation_status,
            "pipeline_decision": pipeline_decision,
            "pipeline_summary_label": pipeline_summary_label,
            "missing_host_required_fields": list(
                validation_result["missing_host_required_fields"]
            ),
            "missing_phage_required_fields": list(
                validation_result["missing_phage_required_fields"]
            ),
            "recognition_match_score": summary["recognition_match_score"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
            "fallback_fields": list(combined_config.get("fallback_fields", [])),
        }

    return results


def run_recognition_resource_grid_scan() -> dict[str, dict[str, dict[str, float | str]]]:
    """Scan infection trajectories across a minimal recognition-resource grid."""

    recognition_stubs = {
        "matched_high_specificity": {
            "host_receptor_type": "LPS",
            "host_receptor_variant": "LPS_core_A",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 1.0,
        },
        "recognition_limited": {
            "host_receptor_type": "LPS",
            "host_receptor_variant": "LPS_core_A",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 0.7,
        },
        "receptor_mismatch": {
            "host_receptor_type": "OmpC",
            "host_receptor_variant": "OmpC_variant_A",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 1.0,
        },
    }
    resource_stubs = {
        "high_resource": {
            "host_transcription_class": "high",
            "host_translation_class": "high",
            "host_energy_class": "high",
            "host_growth_class": "high",
        },
        "medium_resource": {
            "host_transcription_class": "medium",
            "host_translation_class": "medium",
            "host_energy_class": "medium",
            "host_growth_class": "medium",
        },
        "low_resource": {
            "host_transcription_class": "low",
            "host_translation_class": "low",
            "host_energy_class": "low",
            "host_growth_class": "low",
        },
    }
    results: dict[str, dict[str, dict[str, float | str]]] = {}

    for recognition_name, recognition_stub in recognition_stubs.items():
        results[recognition_name] = {}

        for resource_name, resource_stub in resource_stubs.items():
            dt = 0.1
            recognition_config = build_recognition_config_from_annotation_stub(
                recognition_stub
            )
            resource_config = build_host_resource_config_from_annotation_stub(
                resource_stub
            )
            host_state = create_host_state_from_config("ecoli_LPS_host")
            phage_state = create_phage_state_from_config("T7_like_LPS_phage")

            host_state.receptor_type = str(recognition_config["receptor_type"])
            host_state.receptor_variant = str(recognition_config["receptor_variant"])
            phage_state.receptor_target_type = str(
                recognition_config["receptor_target_type"]
            )
            phage_state.target_variant_preference = str(
                recognition_config["target_variant_preference"]
            )
            phage_state.binding_specificity_strength = float(
                recognition_config["binding_specificity_strength"]
            )
            host_state.transcription_capacity = float(
                resource_config["transcription_capacity"]
            )
            host_state.translation_capacity = float(
                resource_config["translation_capacity"]
            )
            host_state.energy_state = float(resource_config["energy_state"])
            host_state.growth_rate = float(resource_config["growth_rate"])

            host_state = update_host_growth_state(host_state, dt)
            phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
            phage_state = simulate_infection_cycle(host_state, phage_state, dt)
            summary = extract_infection_summary(phage_state)
            results[recognition_name][resource_name] = {
                "recognition_match_score": summary["recognition_match_score"],
                "infection_outcome": summary["infection_outcome"],
                "failure_cause": summary["failure_cause"],
                "failure_stage": summary["failure_stage"],
                "trajectory_label": summary["trajectory_label"],
            }

    return results


def run_annotation_stub_recognition_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate minimal recognition-layer mapping from annotation stubs."""

    annotation_stubs = {
        "matched_annotation_stub": {
            "host_receptor_type": "LPS",
            "host_receptor_variant": "LPS_core_A",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 1.0,
        },
        "variant_mismatch_annotation_stub": {
            "host_receptor_type": "LPS",
            "host_receptor_variant": "LPS_core_B",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 1.0,
        },
        "receptor_mismatch_annotation_stub": {
            "host_receptor_type": "OmpC",
            "host_receptor_variant": "OmpC_variant_A",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 1.0,
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, annotation_stub in annotation_stubs.items():
        dt = 0.1
        recognition_config = build_recognition_config_from_annotation_stub(
            annotation_stub
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(recognition_config["receptor_type"])
        host_state.receptor_variant = str(recognition_config["receptor_variant"])
        phage_state.receptor_target_type = str(
            recognition_config["receptor_target_type"]
        )
        phage_state.target_variant_preference = str(
            recognition_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            recognition_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "adsorption_probability": summary["adsorption_probability"],
            "injection_success_probability": summary["injection_success_probability"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_annotation_alias_recognition_demo() -> dict[str, dict[str, float | str]]:
    """Demonstrate recognition-layer mapping from alias-style annotation stubs."""

    annotation_stubs = {
        "alias_matched_stub": {
            "host_receptor_family": "LPS",
            "host_receptor_subtype": "LPS_core_A",
            "phage_rbp_target_family": "LPS",
            "phage_rbp_target_subtype": "LPS_core_A",
            "phage_tail_fiber_specificity_class": "high",
        },
        "alias_variant_mismatch_stub": {
            "host_receptor_family": "LPS",
            "host_receptor_subtype": "LPS_core_B",
            "phage_rbp_target_family": "LPS",
            "phage_rbp_target_subtype": "LPS_core_A",
            "phage_tail_fiber_specificity_class": "high",
        },
        "alias_receptor_mismatch_stub": {
            "host_receptor_family": "OmpC",
            "host_receptor_subtype": "OmpC_variant_A",
            "phage_rbp_target_family": "LPS",
            "phage_rbp_target_subtype": "LPS_core_A",
            "phage_tail_spike_specificity_class": "high",
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, annotation_stub in annotation_stubs.items():
        dt = 0.1
        recognition_config = build_recognition_config_from_annotation_stub(
            annotation_stub
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(recognition_config["receptor_type"])
        host_state.receptor_variant = str(recognition_config["receptor_variant"])
        phage_state.receptor_target_type = str(
            recognition_config["receptor_target_type"]
        )
        phage_state.target_variant_preference = str(
            recognition_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            recognition_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "adsorption_probability": summary["adsorption_probability"],
            "injection_success_probability": summary["injection_success_probability"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def run_recognition_transition_scan() -> dict[str, dict[str, float | str]]:
    """Scan infection trajectories across a small recognition-strength ladder."""

    scan_definitions = {
        "fully_matched": {
            "host_receptor_type": "LPS",
            "host_receptor_variant": "LPS_core_A",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 1.0,
        },
        "matched_low_specificity": {
            "host_receptor_type": "LPS",
            "host_receptor_variant": "LPS_core_A",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 0.7,
        },
        "variant_mismatch_high_specificity": {
            "host_receptor_type": "LPS",
            "host_receptor_variant": "LPS_core_B",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 1.0,
        },
        "variant_mismatch_low_specificity": {
            "host_receptor_type": "LPS",
            "host_receptor_variant": "LPS_core_B",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 0.5,
        },
        "clear_receptor_mismatch": {
            "host_receptor_type": "OmpC",
            "host_receptor_variant": "OmpC_variant_A",
            "phage_receptor_target_type": "LPS",
            "phage_target_variant_preference": "LPS_core_A",
            "phage_binding_specificity": 1.0,
        },
    }
    results: dict[str, dict[str, float | str]] = {}

    for case_name, annotation_stub in scan_definitions.items():
        dt = 0.1
        recognition_config = build_recognition_config_from_annotation_stub(
            annotation_stub
        )
        host_state = create_host_state_from_config("ecoli_LPS_host")
        phage_state = create_phage_state_from_config("T7_like_LPS_phage")

        host_state.receptor_type = str(recognition_config["receptor_type"])
        host_state.receptor_variant = str(recognition_config["receptor_variant"])
        phage_state.receptor_target_type = str(
            recognition_config["receptor_target_type"]
        )
        phage_state.target_variant_preference = str(
            recognition_config["target_variant_preference"]
        )
        phage_state.binding_specificity_strength = float(
            recognition_config["binding_specificity_strength"]
        )

        host_state = update_host_growth_state(host_state, dt)
        phage_state = simulate_adsorption_and_recognition(host_state, phage_state)
        phage_state = simulate_infection_cycle(host_state, phage_state, dt)
        summary = extract_infection_summary(phage_state)
        results[case_name] = {
            "recognition_match_score": summary["recognition_match_score"],
            "adsorption_probability": summary["adsorption_probability"],
            "injection_success_probability": summary["injection_success_probability"],
            "infection_outcome": summary["infection_outcome"],
            "failure_cause": summary["failure_cause"],
            "failure_stage": summary["failure_stage"],
            "trajectory_label": summary["trajectory_label"],
        }

    return results


def _run_single_receptor_case(
    host_config_name: str,
    phage_config_name: str,
) -> dict[str, float | str]:
    """Thin wrapper that preserves the richer infection-summary view."""

    case_result = run_single_case(
        host_config_name=host_config_name,
        phage_config_name=phage_config_name,
        return_full_states=True,
    )
    return extract_infection_summary(case_result["phage_state"])


if __name__ == "__main__":
    result = run_host_takeover_comparison()
    print(result)
