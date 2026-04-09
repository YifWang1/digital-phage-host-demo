"""Minimal Streamlit demo for the digital host-phage phase-1 project."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from entity_configs import host_configs, phage_configs
from simulation_runner import run_single_case


SUMMARY_FIELDS = [
    "recognition_match_score",
    "adsorption_probability",
    "injection_success_probability",
    "early_expression_state",
    "replication_state",
    "late_assembly_state",
    "lysis_state",
    "infection_outcome",
    "trajectory_label",
    "stage_reach_label",
]

FIELD_LABELS = {
    "recognition_match_score": "Recognition Match",
    "adsorption_probability": "Adsorption Prob.",
    "injection_success_probability": "Injection Success",
    "early_expression_state": "Early Expression",
    "replication_state": "Replication",
    "late_assembly_state": "Late Assembly",
    "lysis_state": "Lysis",
    "infection_outcome": "Infection Outcome",
    "trajectory_label": "Trajectory Label",
    "stage_reach_label": "Stage Reach Label",
}

DEMO_CASES = [
    {
        "label": "successful_match",
        "button_label": "Successful Match",
        "host": "ecoli_LPS_host",
        "phage": "T7_like_LPS_phage",
    },
    {
        "label": "recognition_mismatch",
        "button_label": "Recognition Mismatch",
        "host": "ecoli_OmpC_host",
        "phage": "T7_like_LPS_phage",
    },
    {
        "label": "resource_limited",
        "button_label": "Resource Limited",
        "host": "ecoli_LPS_low_resource_host",
        "phage": "T7_like_LPS_phage",
    },
    {
        "label": "defense_blocked",
        "button_label": "Defense Blocked",
        "host": "ecoli_LPS_replication_defense_host",
        "phage": "T7_like_LPS_phage",
    },
]

STAGE_ORDER = [
    ("adsorption", "adsorption"),
    ("injection", "injection"),
    ("early_expression", "early expression"),
    ("replication", "replication"),
    ("assembly", "assembly"),
    ("lysis", "lysis"),
]

HOST_FEATURE_SECTIONS = [
    (
        "Receptor Surface",
        [
            ("receptor_type", "Receptor type"),
            ("receptor_variant", "Receptor variant"),
            ("receptor_availability", "Receptor availability"),
            ("receptor_accessibility", "Receptor accessibility"),
            ("surface_shielding_factor", "Surface shielding"),
        ],
    ),
    (
        "Resource Profile",
        [
            ("growth_rate", "Growth rate"),
            ("transcription_capacity", "Transcription capacity"),
            ("translation_capacity", "Translation capacity"),
            ("energy_state", "Energy state"),
            ("nutrient_state", "Nutrient state"),
        ],
    ),
    (
        "Defense Profile",
        [
            ("host_defense_stage", "Defense stage"),
            ("host_defense_strength", "Defense strength"),
        ],
    ),
]

PHAGE_FEATURE_SECTIONS = [
    (
        "Target Profile",
        [
            ("receptor_target_type", "Target receptor type"),
            ("target_variant_preference", "Target variant preference"),
        ],
    ),
    (
        "Binding Profile",
        [
            ("binding_specificity_strength", "Binding specificity"),
            ("tail_fiber_protein_type", "Tail fiber protein"),
            ("tail_spike_protein_type", "Tail spike protein"),
            ("host_range_index", "Host range index"),
        ],
    ),
]

PROJECT_VISION_TEXT = (
    "The long-term goal of this project is to build a digital phage–host "
    "interaction system that leverages phage/host genomic sequences and "
    "related annotations to infer, simulate, and predict infection success, "
    "host defense effects, and other key infection-associated interaction "
    "behaviors."
)

AUTHOR_TEXT = "Developed by Yinfeng Wang, Ocean University of China"

FOOTER_LINES = [
    "© 2026 Yinfeng Wang (王崟沣). All rights reserved.",
    "This demo is a phase-1 research prototype for academic presentation and research communication only.",
    "It is not a validated quantitative prediction platform.",
    "For collaboration or further development of this project, please contact: yif_wang1@163.com",
]


def _default_index(options: list[str], preferred: str) -> int:
    """Return the preferred option index when present."""

    if preferred in options:
        return options.index(preferred)
    return 0


def _coerce_valid_option(
    options: list[str],
    candidate: object,
    preferred: str,
) -> str:
    """Return a safe option value for selectors and persisted UI state."""

    if isinstance(candidate, str) and candidate in options:
        return candidate
    return options[_default_index(options, preferred)]


def _format_summary_value(value: object) -> str:
    """Format summary values for card display."""

    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, int):
        return str(value)
    return str(value)


def _format_feature_value(value: object) -> str:
    """Format feature-layer values with graceful fallback."""

    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.3f}"
    if value == "":
        return "N/A"
    return str(value)


def _infer_case_label(host_name: str, phage_name: str) -> str:
    """Return a known label for supported demo pairs."""

    for demo_case in DEMO_CASES:
        if demo_case["host"] == host_name and demo_case["phage"] == phage_name:
            return str(demo_case["label"])
    return "custom_case"


def _run_case(host_name: str, phage_name: str, case_label: str) -> None:
    """Run a selected case and persist the active result/header state."""

    if host_name not in host_configs:
        st.session_state["simulation_result"] = None
        st.session_state["simulation_error"] = f"Unknown host config: {host_name}"
        return
    if phage_name not in phage_configs:
        st.session_state["simulation_result"] = None
        st.session_state["simulation_error"] = f"Unknown phage config: {phage_name}"
        return

    st.session_state["active_host"] = host_name
    st.session_state["active_phage"] = phage_name
    st.session_state["active_case_label"] = case_label

    try:
        st.session_state["simulation_result"] = run_single_case(
            host_name,
            phage_name,
        )
        st.session_state["simulation_error"] = None
    except Exception as exc:  # pragma: no cover - UI safety path
        st.session_state["simulation_result"] = None
        st.session_state["simulation_error"] = str(exc)


def _render_summary_cards(result: dict[str, object]) -> None:
    """Render summary metrics in a compact card-like grid."""

    st.subheader("Summary Cards")
    for start_index in range(0, len(SUMMARY_FIELDS), 5):
        row_fields = SUMMARY_FIELDS[start_index : start_index + 5]
        columns = st.columns(len(row_fields))
        for column, field_name in zip(columns, row_fields):
            with column:
                st.metric(
                    FIELD_LABELS[field_name],
                    _format_summary_value(result.get(field_name)),
                )


def _infer_stage_statuses(result: dict[str, object]) -> list[dict[str, str]]:
    """Infer stage progression status from the current phase-1 summary."""

    failure_stage = str(result.get("failure_stage", "none"))
    stage_reach_label = str(result.get("stage_reach_label", ""))
    trajectory_label = str(result.get("trajectory_label", ""))
    infection_outcome = str(result.get("infection_outcome", ""))

    reach_index_by_label = {
        "reached_adsorption_only": 0,
        "reached_early_expression": 2,
        "reached_replication": 3,
        "reached_assembly": 4,
        "reached_lysis": 5,
    }
    failure_index_by_stage = {
        "adsorption": 0,
        "injection": 1,
        "early_expression": 2,
        "replication": 3,
        "assembly": 4,
        "lysis": 5,
    }

    if (
        infection_outcome == "successful_lysis"
        or stage_reach_label == "reached_lysis"
        or trajectory_label == "successful_progression"
    ):
        return [
            {"stage": stage_name, "label": stage_label, "status": "completed"}
            for stage_name, stage_label in STAGE_ORDER
        ]

    failure_index = failure_index_by_stage.get(failure_stage)
    reached_index = reach_index_by_label.get(stage_reach_label)

    # Fallback to summary states when labels are absent. These values are already
    # produced by the existing canonical phase-1 summary and stay in the UI layer.
    if reached_index is None:
        if float(result.get("lysis_state", 0.0) or 0.0) > 0.0:
            reached_index = 5
        elif float(result.get("late_assembly_state", 0.0) or 0.0) > 0.0:
            reached_index = 4
        elif float(result.get("replication_state", 0.0) or 0.0) > 0.0:
            reached_index = 3
        elif float(result.get("early_expression_state", 0.0) or 0.0) > 0.0:
            reached_index = 2
        elif float(result.get("adsorption_probability", 0.0) or 0.0) > 0.0:
            reached_index = 0
        else:
            reached_index = -1

    stage_statuses: list[dict[str, str]] = []
    for stage_index, (stage_name, stage_label) in enumerate(STAGE_ORDER):
        status = "not_reached"
        if failure_index is not None:
            if stage_index < failure_index:
                status = "completed"
            elif stage_index == failure_index:
                status = "failed_here"
        elif stage_index <= reached_index:
            status = "completed"

        stage_statuses.append(
            {"stage": stage_name, "label": stage_label, "status": status}
        )

    return stage_statuses


def _render_stage_progression_bar(result: dict[str, object]) -> None:
    """Render a horizontal phase-1 stage progression view."""

    status_styles = {
        "completed": {
            "background": "#e8f5e9",
            "border": "#2e7d32",
            "text": "#1b5e20",
            "badge": "completed",
        },
        "failed_here": {
            "background": "#fff3e0",
            "border": "#ef6c00",
            "text": "#b53d00",
            "badge": "failed here",
        },
        "not_reached": {
            "background": "#f5f5f5",
            "border": "#bdbdbd",
            "text": "#616161",
            "badge": "not reached",
        },
    }

    st.subheader("Stage Progression Bar")
    stage_statuses = _infer_stage_statuses(result)
    stage_columns = st.columns(len(stage_statuses))

    for column, stage_info in zip(stage_columns, stage_statuses):
        style = status_styles[stage_info["status"]]
        with column:
            st.markdown(
                f"""
                <div style="
                    border: 2px solid {style["border"]};
                    border-radius: 10px;
                    background: {style["background"]};
                    color: {style["text"]};
                    padding: 0.85rem 0.65rem;
                    min-height: 110px;
                    text-align: center;
                ">
                    <div style="
                        font-size: 0.76rem;
                        text-transform: uppercase;
                        letter-spacing: 0.04em;
                        margin-bottom: 0.4rem;
                    ">
                        {style["badge"]}
                    </div>
                    <div style="
                        font-size: 1rem;
                        font-weight: 600;
                        line-height: 1.25;
                    ">
                        {stage_info["label"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_feature_section(
    title: str,
    config: dict[str, object],
    fields: list[tuple[str, str]],
) -> None:
    """Render one structured feature section from preset-backed config fields."""

    st.markdown(f"**{title}**")
    for field_name, field_label in fields:
        st.write(f"{field_label}: {_format_feature_value(config.get(field_name))}")


def _render_feature_layer_panels(host_name: str, phage_name: str) -> None:
    """Render host/phage feature panels from the current preset configs."""

    st.subheader("Feature Layer Panels")
    host_config = dict(host_configs.get(host_name, {}))
    phage_config = dict(phage_configs.get(phage_name, {}))

    host_column, phage_column = st.columns(2)

    with host_column:
        st.markdown("### Host")
        for section_title, section_fields in HOST_FEATURE_SECTIONS:
            with st.container(border=True):
                _render_feature_section(section_title, host_config, section_fields)

    with phage_column:
        st.markdown("### Phage")
        for section_title, section_fields in PHAGE_FEATURE_SECTIONS:
            with st.container(border=True):
                _render_feature_section(section_title, phage_config, section_fields)


def _render_footer() -> None:
    """Render a simple footer for public demo attribution and contact."""

    st.markdown("---")
    for line in FOOTER_LINES:
        st.caption(line)


def main() -> None:
    """Render the enhanced single-page Streamlit wrapper."""

    st.set_page_config(
        page_title="Digital Host-Phage Phase 1 Demo",
        layout="wide",
    )
    st.title("Digital Host–Phage Phase 1 Demo")
    st.caption(PROJECT_VISION_TEXT)
    st.caption(AUTHOR_TEXT)

    host_options = sorted(host_configs.keys())
    phage_options = sorted(phage_configs.keys())

    if not host_options or not phage_options:
        st.error("No host or phage configs are available in the current project.")
        return

    st.session_state["host_selector"] = _coerce_valid_option(
        host_options,
        st.session_state.get("host_selector"),
        "ecoli_LPS_host",
    )
    st.session_state["phage_selector"] = _coerce_valid_option(
        phage_options,
        st.session_state.get("phage_selector"),
        "T7_like_LPS_phage",
    )
    st.session_state["active_host"] = _coerce_valid_option(
        host_options,
        st.session_state.get("active_host"),
        st.session_state["host_selector"],
    )
    st.session_state["active_phage"] = _coerce_valid_option(
        phage_options,
        st.session_state.get("active_phage"),
        st.session_state["phage_selector"],
    )
    if "active_case_label" not in st.session_state:
        st.session_state["active_case_label"] = _infer_case_label(
            st.session_state["active_host"],
            st.session_state["active_phage"],
        )
    if "simulation_result" not in st.session_state:
        st.session_state["simulation_result"] = None
    if "simulation_error" not in st.session_state:
        st.session_state["simulation_error"] = None

    available_demo_cases = [
        demo_case
        for demo_case in DEMO_CASES
        if demo_case["host"] in host_options and demo_case["phage"] in phage_options
    ]
    if available_demo_cases:
        st.subheader("Quick Demo Cases")
        demo_columns = st.columns(len(available_demo_cases))
        for column, demo_case in zip(demo_columns, available_demo_cases):
            with column:
                if st.button(demo_case["button_label"], use_container_width=True):
                    # Safe here because the selectboxes have not been instantiated yet
                    # in the current rerun, so the widget state can still be updated.
                    st.session_state["host_selector"] = str(demo_case["host"])
                    st.session_state["phage_selector"] = str(demo_case["phage"])
                    _run_case(
                        str(demo_case["host"]),
                        str(demo_case["phage"]),
                        str(demo_case["label"]),
                    )

    selected_host = st.selectbox(
        "Host config",
        host_options,
        index=_default_index(host_options, st.session_state["host_selector"]),
        key="host_selector",
    )
    selected_phage = st.selectbox(
        "Phage config",
        phage_options,
        index=_default_index(phage_options, st.session_state["phage_selector"]),
        key="phage_selector",
    )

    if st.button("Run simulation", type="primary"):
        _run_case(
            selected_host,
            selected_phage,
            _infer_case_label(selected_host, selected_phage),
        )

    if st.session_state["simulation_error"]:
        st.error(st.session_state["simulation_error"])

    result = st.session_state["simulation_result"]
    if result is None:
        st.info("Select a host/phage pair or click a demo case, then run simulation.")
    else:
        st.subheader("Case Header")
        header_columns = st.columns(3)
        header_columns[0].metric("Host name", st.session_state["active_host"])
        header_columns[1].metric("Phage name", st.session_state["active_phage"])
        header_columns[2].metric("Case label", st.session_state["active_case_label"])

        _render_summary_cards(result)
        _render_stage_progression_bar(result)
        _render_feature_layer_panels(
            st.session_state["active_host"],
            st.session_state["active_phage"],
        )

        st.subheader("Full JSON")
        st.json(result)

    _render_footer()


if __name__ == "__main__":
    main()
