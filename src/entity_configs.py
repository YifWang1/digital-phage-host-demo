"""Minimal entity configuration layer for host and phage presets.

The goal of this file is to keep early-stage host/phage definitions in one
place so future model expansion can add new entities without rewriting the
simulation logic. Each entry is intentionally lightweight and only stores
the coarse-grained fields needed by the current scaffold.
"""

host_configs = {
    "ecoli_LPS_host": {
        "receptor_type": "LPS",
        "receptor_variant": "LPS_core_A",
        "receptor_availability": 1.0,
        "receptor_accessibility": 1.0,
        "surface_shielding_factor": 0.0,
        "growth_rate": 1.0,
        "translation_capacity": 1.0,
        "energy_state": 1.0,
        "cell_volume": 1.0,
        "nutrient_state": 1.0,
        "transcription_capacity": 1.0,
        "host_defense_stage": "none",
        "host_defense_strength": 0.0,
    },
    "ecoli_LPS_low_resource_host": {
        "receptor_type": "LPS",
        "receptor_variant": "LPS_core_A",
        "receptor_availability": 1.0,
        "receptor_accessibility": 1.0,
        "surface_shielding_factor": 0.0,
        "growth_rate": 0.5,
        "translation_capacity": 0.35,
        "energy_state": 0.3,
        "cell_volume": 1.0,
        "nutrient_state": 0.4,
        "transcription_capacity": 0.4,
        "host_defense_stage": "none",
        "host_defense_strength": 0.0,
    },
    "ecoli_LPS_low_transcription_host": {
        "receptor_type": "LPS",
        "receptor_variant": "LPS_core_A",
        "receptor_availability": 1.0,
        "receptor_accessibility": 1.0,
        "surface_shielding_factor": 0.0,
        "growth_rate": 1.0,
        "translation_capacity": 1.0,
        "energy_state": 1.0,
        "cell_volume": 1.0,
        "nutrient_state": 1.0,
        "transcription_capacity": 0.3,
        "host_defense_stage": "none",
        "host_defense_strength": 0.0,
    },
    "ecoli_LPS_low_translation_host": {
        "receptor_type": "LPS",
        "receptor_variant": "LPS_core_A",
        "receptor_availability": 1.0,
        "receptor_accessibility": 1.0,
        "surface_shielding_factor": 0.0,
        "growth_rate": 1.0,
        "translation_capacity": 0.3,
        "energy_state": 1.0,
        "cell_volume": 1.0,
        "nutrient_state": 1.0,
        "transcription_capacity": 1.0,
        "host_defense_stage": "none",
        "host_defense_strength": 0.0,
    },
    "ecoli_LPS_low_energy_host": {
        "receptor_type": "LPS",
        "receptor_variant": "LPS_core_A",
        "receptor_availability": 1.0,
        "receptor_accessibility": 1.0,
        "surface_shielding_factor": 0.0,
        "growth_rate": 1.0,
        "translation_capacity": 1.0,
        "energy_state": 0.3,
        "cell_volume": 1.0,
        "nutrient_state": 1.0,
        "transcription_capacity": 1.0,
        "host_defense_stage": "none",
        "host_defense_strength": 0.0,
    },
    "ecoli_LPS_replication_defense_host": {
        "receptor_type": "LPS",
        "receptor_variant": "LPS_core_A",
        "receptor_availability": 1.0,
        "receptor_accessibility": 1.0,
        "surface_shielding_factor": 0.0,
        "growth_rate": 1.0,
        "translation_capacity": 1.0,
        "energy_state": 1.0,
        "cell_volume": 1.0,
        "nutrient_state": 1.0,
        "transcription_capacity": 1.0,
        "host_defense_stage": "replication",
        "host_defense_strength": 0.8,
    },
    "ecoli_LPS_variant_B_host": {
        "receptor_type": "LPS",
        "receptor_variant": "LPS_core_B",
        "receptor_availability": 1.0,
        "receptor_accessibility": 1.0,
        "surface_shielding_factor": 0.0,
        "growth_rate": 1.0,
        "translation_capacity": 1.0,
        "energy_state": 1.0,
        "cell_volume": 1.0,
        "nutrient_state": 1.0,
        "transcription_capacity": 1.0,
        "host_defense_stage": "none",
        "host_defense_strength": 0.0,
    },
    "ecoli_OmpC_host": {
        "receptor_type": "OmpC",
        "receptor_variant": "OmpC_variant_A",
        "receptor_availability": 1.0,
        "receptor_accessibility": 1.0,
        "surface_shielding_factor": 0.0,
        "growth_rate": 1.0,
        "translation_capacity": 1.0,
        "energy_state": 1.0,
        "cell_volume": 1.0,
        "nutrient_state": 1.0,
        "transcription_capacity": 1.0,
        "host_defense_stage": "none",
        "host_defense_strength": 0.0,
    },
}


phage_configs = {
    "T7_like_LPS_phage": {
        "receptor_target_type": "LPS",
        "target_variant_preference": "LPS_core_A",
        "binding_specificity_strength": 1.0,
        "tail_fiber_protein_type": "LPS_binding_tail_fiber",
        "tail_spike_protein_type": "unknown_tail_spike",
        "host_range_index": 0.0,
    },
}


def _normalize_annotation_stub(
    annotation_stub: dict,
    alias_field_map: dict[str, list[str]],
) -> tuple[dict, list[str]]:
    """Fill canonical annotation fields from supported aliases when needed."""

    normalized_stub = dict(annotation_stub)
    used_alias_fields: list[str] = []

    for canonical_field, alias_fields in alias_field_map.items():
        if canonical_field in normalized_stub:
            continue

        for alias_field in alias_fields:
            if alias_field in annotation_stub:
                normalized_stub[canonical_field] = annotation_stub[alias_field]
                used_alias_fields.append(alias_field)
                break

    return normalized_stub, used_alias_fields


def normalize_annotation_stubs(
    host_annotation_stub: dict,
    phage_annotation_stub: dict,
) -> dict[str, dict | list[str]]:
    """Return canonicalized host/phage stubs plus the aliases used."""

    schema = get_minimal_annotation_schema()
    normalized_host_annotation_stub, used_host_alias_fields = (
        _normalize_annotation_stub(
            host_annotation_stub,
            dict(schema["host_annotation_stub"]["alias_field_map"]),
        )
    )
    normalized_phage_annotation_stub, used_phage_alias_fields = (
        _normalize_annotation_stub(
            phage_annotation_stub,
            dict(schema["phage_annotation_stub"]["alias_field_map"]),
        )
    )

    return {
        "host_annotation_stub": normalized_host_annotation_stub,
        "phage_annotation_stub": normalized_phage_annotation_stub,
        "used_host_alias_fields": used_host_alias_fields,
        "used_phage_alias_fields": used_phage_alias_fields,
    }


def prepare_normalized_annotation_inputs(
    host_annotation_stub: dict,
    phage_annotation_stub: dict,
) -> dict[str, dict | list[str] | bool | None]:
    """Prepare a normalized phase-1 input bundle from annotation-style stubs.

    This is a schema/input-layer public helper only. It normalizes supported
    aliases, reports minimal required-field validation, and returns the current
    combined config only when the normalized inputs are minimally valid.
    """

    normalized_inputs = normalize_annotation_stubs(
        host_annotation_stub,
        phage_annotation_stub,
    )
    normalized_host_annotation_stub = dict(normalized_inputs["host_annotation_stub"])
    normalized_phage_annotation_stub = dict(normalized_inputs["phage_annotation_stub"])
    validation_result = validate_annotation_stubs(
        host_annotation_stub,
        phage_annotation_stub,
    )

    combined_config = None
    if bool(validation_result["is_minimally_valid"]):
        combined_config = build_combined_config_from_annotation_stubs(
            host_annotation_stub,
            phage_annotation_stub,
        )

    return {
        "host_annotation_stub": normalized_host_annotation_stub,
        "phage_annotation_stub": normalized_phage_annotation_stub,
        "used_host_alias_fields": list(normalized_inputs["used_host_alias_fields"]),
        "used_phage_alias_fields": list(normalized_inputs["used_phage_alias_fields"]),
        "validation_result": validation_result,
        "combined_config": combined_config,
    }


def build_recognition_config_from_annotation_stub(
    annotation_stub: dict,
) -> dict[str, str | float]:
    """Map a minimal annotation-style stub into recognition-layer config fields."""

    binding_specificity_strength = annotation_stub.get("phage_binding_specificity")
    if binding_specificity_strength is None:
        specificity_class = annotation_stub.get("phage_tail_fiber_specificity_class")
        if specificity_class is None:
            specificity_class = annotation_stub.get("phage_tail_spike_specificity_class")
        binding_specificity_strength = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4,
        }.get(str(specificity_class).lower(), 1.0)

    return {
        "receptor_type": str(
            annotation_stub.get(
                "host_receptor_type",
                annotation_stub.get("host_receptor_family", "unknown"),
            )
        ),
        "receptor_variant": str(
            annotation_stub.get(
                "host_receptor_variant",
                annotation_stub.get("host_receptor_subtype", "unknown_variant"),
            )
        ),
        "receptor_target_type": str(
            annotation_stub.get(
                "phage_receptor_target_type",
                annotation_stub.get("phage_rbp_target_family", "unknown"),
            )
        ),
        "target_variant_preference": str(
            annotation_stub.get(
                "phage_target_variant_preference",
                annotation_stub.get(
                    "phage_rbp_target_subtype",
                    "unknown_variant",
                ),
            )
        ),
        "binding_specificity_strength": float(binding_specificity_strength),
    }


def build_host_resource_config_from_annotation_stub(
    annotation_stub: dict,
) -> dict[str, float]:
    """Map a minimal annotation-style stub into host resource config fields."""

    class_to_value = {
        "high": 1.0,
        "medium": 0.8,
        "low": 0.4,
    }
    transcription_class = annotation_stub.get(
        "host_transcription_class",
        annotation_stub.get("host_transcription_capacity_class", "medium"),
    )
    translation_class = annotation_stub.get(
        "host_translation_class",
        annotation_stub.get(
            "host_translation_capacity_class",
            annotation_stub.get("host_expression_capacity_class", "medium"),
        ),
    )
    energy_class = annotation_stub.get(
        "host_energy_class",
        annotation_stub.get("host_cellular_energy_class", "medium"),
    )
    growth_class = annotation_stub.get(
        "host_growth_class",
        annotation_stub.get("host_growth_capacity_class", "medium"),
    )

    return {
        "transcription_capacity": float(
            class_to_value.get(
                str(transcription_class).lower(),
                1.0,
            )
        ),
        "translation_capacity": float(
            class_to_value.get(
                str(translation_class).lower(),
                1.0,
            )
        ),
        "energy_state": float(
            class_to_value.get(
                str(energy_class).lower(),
                1.0,
            )
        ),
        "growth_rate": float(
            class_to_value.get(
                str(growth_class).lower(),
                1.0,
            )
        ),
    }


def build_host_defense_config_from_annotation_stub(
    annotation_stub: dict,
) -> dict[str, str | float]:
    """Map a minimal annotation-style stub into host defense config fields."""

    defense_strength = {
        "none": 0.0,
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8,
    }.get(str(annotation_stub.get("host_defense_strength_class", "none")).lower(), 0.0)
    defense_stage = str(annotation_stub.get("host_defense_stage_stub", "none"))
    if defense_stage not in {"none", "injection", "early_expression", "replication"}:
        defense_stage = "none"

    return {
        "host_defense_stage": defense_stage,
        "host_defense_strength": float(defense_strength),
    }


def build_combined_config_from_annotation_stubs(
    host_annotation_stub: dict,
    phage_annotation_stub: dict,
) -> dict[str, str | float | list[str]]:
    """Build a minimal combined config from host and phage annotation stubs."""

    fallback_fields: list[str] = []
    if (
        "host_receptor_type" not in host_annotation_stub
        and "host_receptor_family" not in host_annotation_stub
    ):
        fallback_fields.append("host_receptor_type")
    if (
        "host_receptor_variant" not in host_annotation_stub
        and "host_receptor_subtype" not in host_annotation_stub
    ):
        fallback_fields.append("host_receptor_variant")
    if (
        "phage_receptor_target_type" not in phage_annotation_stub
        and "phage_rbp_target_family" not in phage_annotation_stub
    ):
        fallback_fields.append("phage_receptor_target_type")
    if (
        "phage_target_variant_preference" not in phage_annotation_stub
        and "phage_rbp_target_subtype" not in phage_annotation_stub
    ):
        fallback_fields.append("phage_target_variant_preference")
    if (
        "phage_binding_specificity" not in phage_annotation_stub
        and "phage_tail_fiber_specificity_class" not in phage_annotation_stub
        and "phage_tail_spike_specificity_class" not in phage_annotation_stub
    ):
        fallback_fields.append("phage_binding_specificity")
    if (
        "host_transcription_class" not in host_annotation_stub
        and "host_transcription_capacity_class" not in host_annotation_stub
    ):
        fallback_fields.append("host_transcription_class")
    if (
        "host_translation_class" not in host_annotation_stub
        and "host_translation_capacity_class" not in host_annotation_stub
        and "host_expression_capacity_class" not in host_annotation_stub
    ):
        fallback_fields.append("host_translation_class")
    if (
        "host_energy_class" not in host_annotation_stub
        and "host_cellular_energy_class" not in host_annotation_stub
    ):
        fallback_fields.append("host_energy_class")
    if (
        "host_growth_class" not in host_annotation_stub
        and "host_growth_capacity_class" not in host_annotation_stub
    ):
        fallback_fields.append("host_growth_class")

    recognition_config = build_recognition_config_from_annotation_stub(
        {
            **host_annotation_stub,
            **phage_annotation_stub,
        }
    )
    host_resource_config = build_host_resource_config_from_annotation_stub(
        host_annotation_stub
    )

    return {
        "receptor_type": str(recognition_config["receptor_type"]),
        "receptor_variant": str(recognition_config["receptor_variant"]),
        "transcription_capacity": float(
            host_resource_config["transcription_capacity"]
        ),
        "translation_capacity": float(host_resource_config["translation_capacity"]),
        "energy_state": float(host_resource_config["energy_state"]),
        "growth_rate": float(host_resource_config["growth_rate"]),
        "receptor_target_type": str(recognition_config["receptor_target_type"]),
        "target_variant_preference": str(
            recognition_config["target_variant_preference"]
        ),
        "binding_specificity_strength": float(
            recognition_config["binding_specificity_strength"]
        ),
        "fallback_fields": fallback_fields,
    }


def get_minimal_annotation_schema() -> dict[str, dict[str, list[str] | dict[str, str]]]:
    """Return the minimal recommended annotation-stub schema."""

    return {
        "host_annotation_stub": {
            "direct_fields": [
                "host_receptor_type",
                "host_receptor_variant",
                "host_transcription_class",
                "host_translation_class",
                "host_energy_class",
                "host_growth_class",
            ],
            "required_fields": [
                "host_receptor_type",
                "host_receptor_variant",
            ],
            "optional_fields": [
                "host_transcription_class",
                "host_translation_class",
                "host_energy_class",
                "host_growth_class",
            ],
            "alias_fields": [
                "host_receptor_family",
                "host_receptor_subtype",
                "host_transcription_capacity_class",
                "host_translation_capacity_class",
                "host_expression_capacity_class",
                "host_cellular_energy_class",
                "host_growth_capacity_class",
            ],
            "alias_field_map": {
                "host_receptor_type": ["host_receptor_family"],
                "host_receptor_variant": ["host_receptor_subtype"],
                "host_transcription_class": ["host_transcription_capacity_class"],
                "host_translation_class": [
                    "host_translation_capacity_class",
                    "host_expression_capacity_class",
                ],
                "host_energy_class": ["host_cellular_energy_class"],
                "host_growth_class": ["host_growth_capacity_class"],
            },
            "field_notes": {
                "host_receptor_type": "Recognition layer: host receptor family used for receptor-type matching.",
                "host_receptor_variant": "Recognition layer: host receptor subtype used for variant-level matching.",
                "host_transcription_class": "Resource layer: host transcription support that affects early expression and replication.",
                "host_translation_class": "Resource layer: host translation support that affects expression and assembly progression.",
                "host_energy_class": "Resource layer: host energy support that affects replication, assembly, and lysis progression.",
                "host_growth_class": "Resource layer: coarse host growth/resource state used as a minimal physiological input.",
            },
            "field_mapping_targets": {
                "host_receptor_type": "receptor_type",
                "host_receptor_variant": "receptor_variant",
                "host_transcription_class": "transcription_capacity",
                "host_translation_class": "translation_capacity",
                "host_energy_class": "energy_state",
                "host_growth_class": "growth_rate",
            },
        },
        "phage_annotation_stub": {
            "direct_fields": [
                "phage_receptor_target_type",
                "phage_target_variant_preference",
                "phage_binding_specificity",
            ],
            "required_fields": [
                "phage_receptor_target_type",
                "phage_target_variant_preference",
            ],
            "optional_fields": [
                "phage_binding_specificity",
            ],
            "alias_fields": [
                "phage_rbp_target_family",
                "phage_rbp_target_subtype",
                "phage_tail_fiber_specificity_class",
                "phage_tail_spike_specificity_class",
            ],
            "alias_field_map": {
                "phage_receptor_target_type": ["phage_rbp_target_family"],
                "phage_target_variant_preference": ["phage_rbp_target_subtype"],
                "phage_binding_specificity": [
                    "phage_tail_fiber_specificity_class",
                    "phage_tail_spike_specificity_class",
                ],
            },
            "field_notes": {
                "phage_receptor_target_type": "Recognition layer: phage target receptor family used for receptor-type matching.",
                "phage_target_variant_preference": "Recognition layer: phage preferred receptor subtype used for variant-level matching.",
                "phage_binding_specificity": "Recognition layer: coarse binding specificity strength that scales downstream recognition efficiency.",
            },
            "field_mapping_targets": {
                "phage_receptor_target_type": "receptor_target_type",
                "phage_target_variant_preference": "target_variant_preference",
                "phage_binding_specificity": "binding_specificity_strength",
            },
        },
    }


def validate_annotation_stubs(
    host_annotation_stub: dict,
    phage_annotation_stub: dict,
) -> dict[str, list[str] | bool]:
    """Perform a minimal required-field check for annotation stubs."""

    normalized_stubs = normalize_annotation_stubs(
        host_annotation_stub,
        phage_annotation_stub,
    )
    normalized_host_annotation_stub = dict(normalized_stubs["host_annotation_stub"])
    normalized_phage_annotation_stub = dict(normalized_stubs["phage_annotation_stub"])
    schema = get_minimal_annotation_schema()
    host_required_fields = list(schema["host_annotation_stub"]["required_fields"])
    phage_required_fields = list(schema["phage_annotation_stub"]["required_fields"])

    missing_host_required_fields = [
        field
        for field in host_required_fields
        if field not in normalized_host_annotation_stub
    ]
    missing_phage_required_fields = [
        field
        for field in phage_required_fields
        if field not in normalized_phage_annotation_stub
    ]

    return {
        "missing_host_required_fields": missing_host_required_fields,
        "missing_phage_required_fields": missing_phage_required_fields,
        "is_minimally_valid": (
            not missing_host_required_fields and not missing_phage_required_fields
        ),
    }


def get_minimal_pipeline_schema() -> dict[str, object]:
    """Return the minimal in-program schema for the current input pipeline."""

    return {
        "annotation_schema": get_minimal_annotation_schema(),
        "validation_outputs": {
            "missing_host_required_fields": "List of missing required host input fields.",
            "missing_phage_required_fields": "List of missing required phage input fields.",
            "is_minimally_valid": "True when all required host and phage fields are present.",
        },
        "builder_outputs": {
            "fallback_fields": "List of fields that used default-value fallback during combined config building.",
        },
        "pipeline_outputs": {
            "validation_status": "High-level validation state for the current input set.",
            "pipeline_decision": "Whether the pipeline runs directly or runs with fallback.",
            "pipeline_summary_label": "High-level summary of the overall pipeline result.",
            "infection_outcome": "Coarse infection outcome returned by the infection model.",
            "failure_cause": "Primary failure cause label from the infection model.",
            "failure_stage": "Stage at which failure is assigned in the infection model.",
            "trajectory_label": "High-level trajectory classification label.",
        },
    }
