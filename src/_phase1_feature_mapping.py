"""Private, non-runtime scaffold for grounded phase-1 feature surfaces.

This module intentionally exposes only the current phase-1 feature surface
shape plus a parallel per-field provenance structure. It is not wired into
any runtime path.
"""

from __future__ import annotations


_PHASE1_FEATURE_TEMPLATE = {
    "host_receptor_surface": {
        "receptor_type": None,
        "receptor_variant": None,
    },
    "host_resource_profile": {
        "transcription_capacity": None,
        "translation_capacity": None,
        "energy_state": None,
        "growth_rate": None,
    },
    "host_defense_profile": {
        "host_defense_stage": None,
        "host_defense_strength": None,
    },
    "phage_target_profile": {
        "receptor_target_type": None,
        "target_variant_preference": None,
    },
    "phage_binding_profile": {
        "binding_specificity_strength": None,
    },
}

_PHASE1_PROVENANCE_TEMPLATE = {
    surface_name: {
        field_name: None
        for field_name in surface_fields
    }
    for surface_name, surface_fields in _PHASE1_FEATURE_TEMPLATE.items()
}


def create_phase1_feature_mapping_scaffold() -> dict[str, dict[str, object]]:
    """Return a fresh phase-1 feature/provenance scaffold."""

    scaffold = {
        surface_name: dict(surface_fields)
        for surface_name, surface_fields in _PHASE1_FEATURE_TEMPLATE.items()
    }
    scaffold["provenance"] = {
        surface_name: dict(surface_fields)
        for surface_name, surface_fields in _PHASE1_PROVENANCE_TEMPLATE.items()
    }
    return scaffold
