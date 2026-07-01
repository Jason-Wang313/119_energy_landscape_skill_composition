#!/usr/bin/env bash
set -euo pipefail

CONFIRM_BOOTSTRAP_ONLY=0
INSTALL_MANISKILL=0
ACCEPTED_BACKEND="${ACCEPTED_BACKEND:-sapien_cuda}"
SHADER_PACK="${SHADER_PACK:-minimal}"
RENDER_PREFLIGHT_TIMEOUT_SECONDS="${RENDER_PREFLIGHT_TIMEOUT_SECONDS:-120}"
PILOT_TIMEOUT_SECONDS="${PILOT_TIMEOUT_SECONDS:-180}"
PYTHON_BIN="${PYTHON:-python3}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --confirm-bootstrap-only)
      CONFIRM_BOOTSTRAP_ONLY=1
      shift
      ;;
    --install-maniskill)
      INSTALL_MANISKILL=1
      shift
      ;;
    --accepted-backend)
      ACCEPTED_BACKEND="$2"
      shift 2
      ;;
    --shader-pack)
      SHADER_PACK="$2"
      shift 2
      ;;
    --render-preflight-timeout-seconds)
      RENDER_PREFLIGHT_TIMEOUT_SECONDS="$2"
      shift 2
      ;;
    --pilot-timeout-seconds)
      PILOT_TIMEOUT_SECONDS="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 --confirm-bootstrap-only [--install-maniskill] [--accepted-backend BACKEND] [--shader-pack PACK]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "${PAPER119_CONFIRM_BOOTSTRAP_ONLY:-0}" == "1" ]]; then
  CONFIRM_BOOTSTRAP_ONLY=1
fi

if [[ "$CONFIRM_BOOTSTRAP_ONLY" != "1" ]]; then
  echo "Refusing to bootstrap silently. Re-run with --confirm-bootstrap-only or PAPER119_CONFIRM_BOOTSTRAP_ONLY=1 on the independent collection machine. This script does not collect official evidence." >&2
  exit 2
fi

run_python() {
  "$PYTHON_BIN" "$@"
}

if [[ "$INSTALL_MANISKILL" == "1" ]]; then
  run_python -m pip install --upgrade pip
  run_python -m pip install numpy matplotlib imageio imageio-ffmpeg
  run_python -m pip install --upgrade mani_skill
  run_python -m pip install torch torchvision torchaudio
fi

run_python scripts/probe_external_platform.py --strict
run_python scripts/probe_maniskill_task_bindings.py --strict
run_python scripts/probe_maniskill_env_smoke.py --strict
run_python scripts/probe_maniskill_fidelity_metadata.py --strict
run_python scripts/audit_maniskill_render_video_preflight.py --timeout-seconds "$RENDER_PREFLIGHT_TIMEOUT_SECONDS" --max-envs 4 --width 128 --height 128 --render-backend "$ACCEPTED_BACKEND" --shader-pack "$SHADER_PACK" --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
run_python scripts/audit_maniskill_pilot_runtime_liveness.py --timeout-seconds "$PILOT_TIMEOUT_SECONDS" --render-backend "$ACCEPTED_BACKEND" --shader-pack "$SHADER_PACK" --render-width 128 --render-height 128
run_python scripts/build_maniskill_render_machine_qualification.py

printf '\nBootstrap probes complete. If render-machine qualification is still DO_NOT_COLLECT_RENDER_MACHINE, do not run official collection.\n'
