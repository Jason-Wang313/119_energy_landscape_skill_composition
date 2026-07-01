#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

PYTHON_BIN="${PYTHON:-python3}"
CONFIRM_OFFICIAL_COLLECTION=0
BACKEND_MODULE="external_validation/runner/maniskill_reference_backend.py"
TASK_CONFIG_DIR="external_validation/configs"
ACCEPTED_BACKEND="<accepted_backend>"
SHADER_PACK="<accepted_shader_pack>"
RUN_ID="<accepted_run_id>"
OPERATOR_NAME_OR_LAB="<independent_operator_or_lab>"
OPERATOR_ID="<independent_operator_or_lab>"
COLLECTION_MACHINE="<machine_or_robot_platform>"
CONTACT_SOLVER_AND_FRICTION_MODEL="<solver_friction_contact_model>"
TIMESTEP_AND_SUBSTEPS_PER_CONTROL_STEP="<sim_dt_control_dt_substeps>"
PAIRED_RESET_REPLAY_TEST="<paired_reset_replay_result>"
CALIBRATION_BASIS="<calibration_basis>"
TASK_BINDING_DECISION="<accepted_or_replaced_task_bindings>"
ACCEPTANCE_GATE_SIGNOFF="<gate_signoff_summary>"
KNOWN_LIMITATIONS="<known_limitations>"
DATE_LOCKED="<YYYY-MM-DD>"
DATE_SEALED="<YYYY-MM-DD>"
CODE_COMMIT="<commit_sha>"
SKILL_LIBRARY_HASH="<sha256>"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --confirm-official-collection)
            CONFIRM_OFFICIAL_COLLECTION=1
            shift
            ;;
        --backend-module)
            BACKEND_MODULE="${2:-}"
            shift 2
            ;;
        --task-config-dir)
            TASK_CONFIG_DIR="${2:-}"
            shift 2
            ;;
        --accepted-backend)
            ACCEPTED_BACKEND="${2:-}"
            shift 2
            ;;
        --shader-pack)
            SHADER_PACK="${2:-}"
            shift 2
            ;;
        --run-id)
            RUN_ID="${2:-}"
            shift 2
            ;;
        --operator-name-or-lab)
            OPERATOR_NAME_OR_LAB="${2:-}"
            shift 2
            ;;
        --operator-id)
            OPERATOR_ID="${2:-}"
            shift 2
            ;;
        --collection-machine)
            COLLECTION_MACHINE="${2:-}"
            shift 2
            ;;
        --contact-solver-and-friction-model)
            CONTACT_SOLVER_AND_FRICTION_MODEL="${2:-}"
            shift 2
            ;;
        --timestep-and-substeps-per-control-step)
            TIMESTEP_AND_SUBSTEPS_PER_CONTROL_STEP="${2:-}"
            shift 2
            ;;
        --paired-reset-replay-test)
            PAIRED_RESET_REPLAY_TEST="${2:-}"
            shift 2
            ;;
        --real-or-benchmark-calibration-basis)
            CALIBRATION_BASIS="${2:-}"
            shift 2
            ;;
        --task-binding-decision)
            TASK_BINDING_DECISION="${2:-}"
            shift 2
            ;;
        --acceptance-gate-signoff)
            ACCEPTANCE_GATE_SIGNOFF="${2:-}"
            shift 2
            ;;
        --known-limitations)
            KNOWN_LIMITATIONS="${2:-}"
            shift 2
            ;;
        --date-locked)
            DATE_LOCKED="${2:-}"
            shift 2
            ;;
        --date-sealed)
            DATE_SEALED="${2:-}"
            shift 2
            ;;
        --code-commit)
            CODE_COMMIT="${2:-}"
            shift 2
            ;;
        --skill-library-hash)
            SKILL_LIBRARY_HASH="${2:-}"
            shift 2
            ;;
        --python)
            PYTHON_BIN="${2:-}"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

if [[ "${PAPER119_CONFIRM_OFFICIAL_COLLECTION:-0}" == "1" ]]; then
    CONFIRM_OFFICIAL_COLLECTION=1
fi

run_python() {
    "${PYTHON_BIN}" "$@"
}

require_real_value() {
    local name="$1"
    local value="$2"
    if [[ -z "${value//[[:space:]]/}" || "$value" == *"<"* || "$value" == *">"* ]]; then
        echo "${name} still has placeholder value: ${value}" >&2
        exit 2
    fi
}

if [[ "${CONFIRM_OFFICIAL_COLLECTION}" != "1" ]]; then
    echo "Refusing official collection. Re-run with --confirm-official-collection only after render-machine qualification, fidelity acceptance, strict collection readiness, and operator fields are real." >&2
    exit 2
fi

require_real_value "BackendModule" "${BACKEND_MODULE}"
require_real_value "TaskConfigDir" "${TASK_CONFIG_DIR}"
require_real_value "AcceptedBackend" "${ACCEPTED_BACKEND}"
require_real_value "ShaderPack" "${SHADER_PACK}"
require_real_value "RunId" "${RUN_ID}"
require_real_value "OperatorNameOrLab" "${OPERATOR_NAME_OR_LAB}"
require_real_value "OperatorId" "${OPERATOR_ID}"
require_real_value "CollectionMachine" "${COLLECTION_MACHINE}"
require_real_value "ContactSolverAndFrictionModel" "${CONTACT_SOLVER_AND_FRICTION_MODEL}"
require_real_value "TimestepAndSubstepsPerControlStep" "${TIMESTEP_AND_SUBSTEPS_PER_CONTROL_STEP}"
require_real_value "PairedResetReplayTest" "${PAIRED_RESET_REPLAY_TEST}"
require_real_value "CalibrationBasis" "${CALIBRATION_BASIS}"
require_real_value "TaskBindingDecision" "${TASK_BINDING_DECISION}"
require_real_value "AcceptanceGateSignoff" "${ACCEPTANCE_GATE_SIGNOFF}"
require_real_value "KnownLimitations" "${KNOWN_LIMITATIONS}"
require_real_value "DateLocked" "${DATE_LOCKED}"
require_real_value "DateSealed" "${DATE_SEALED}"
require_real_value "CodeCommit" "${CODE_COMMIT}"
require_real_value "SkillLibraryHash" "${SKILL_LIBRARY_HASH}"

run_python scripts/probe_external_platform.py
run_python scripts/audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend "${ACCEPTED_BACKEND}" --shader-pack "${SHADER_PACK}" --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
run_python scripts/audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180
run_python scripts/audit_external_backend_contract.py --strict --backend-module "${BACKEND_MODULE}" --task-config-dir "${TASK_CONFIG_DIR}" --alias-map external_validation/method_alias_map.json
run_python scripts/materialize_fidelity_acceptance.py --operator-name-or-lab "${OPERATOR_NAME_OR_LAB}" --accepted-collection-machine "${COLLECTION_MACHINE}" --contact-solver-and-friction-model "${CONTACT_SOLVER_AND_FRICTION_MODEL}" --timestep-and-substeps-per-control-step "${TIMESTEP_AND_SUBSTEPS_PER_CONTROL_STEP}" --paired-reset-replay-test "${PAIRED_RESET_REPLAY_TEST}" --real-or-benchmark-calibration-basis "${CALIBRATION_BASIS}" --task-binding-decision "${TASK_BINDING_DECISION}" --acceptance-gate-signoff "${ACCEPTANCE_GATE_SIGNOFF}" --known-limitations "${KNOWN_LIMITATIONS}" --date-locked "${DATE_LOCKED}" --code-commit "${CODE_COMMIT}" --skill-library-hash "${SKILL_LIBRARY_HASH}" --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write
run_python scripts/audit_external_collection_readiness.py --strict --backend-module "${BACKEND_MODULE}" --task-config-dir "${TASK_CONFIG_DIR}" --run-id "${RUN_ID}" --unsealed-alias-map
run_python scripts/build_external_precollection_freeze_receipt.py --backend-module "${BACKEND_MODULE}" --run-id "${RUN_ID}" --operator-id "${OPERATOR_ID}" --collection-machine "${COLLECTION_MACHINE}" --date-locked "${DATE_LOCKED}" --unsealed-alias-map
run_python external_validation/runner/real_collection_runner.py --backend-module "${BACKEND_MODULE}" --task-config-dir "${TASK_CONFIG_DIR}" --output-log-dir external_validation/logs --video-dir external_validation/videos --run-id "${RUN_ID}" --unsealed-alias-map
run_python scripts/build_external_postcollection_evidence_seal.py --backend-module "${BACKEND_MODULE}" --run-id "${RUN_ID}" --operator-id "${OPERATOR_ID}" --collection-machine "${COLLECTION_MACHINE}" --date-sealed "${DATE_SEALED}"
run_python scripts/audit_external_postcollection_seal_consistency.py
run_python scripts/build_external_manifest.py --write --check-video-paths
run_python scripts/validate_external_rollouts.py --write-results --check-video-paths --strict
run_python scripts/validate_external_configs.py --strict
run_python scripts/validate_external_adapters.py --strict
run_python scripts/audit_external_pairing_integrity.py --strict
run_python scripts/audit_external_release_package.py --strict
run_python scripts/audit_external_evidence.py --strict
