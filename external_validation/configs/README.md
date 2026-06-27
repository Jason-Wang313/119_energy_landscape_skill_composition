# External Task Config Intake

Not external evidence: `true`.

This directory is the intake location for real, manifest-declared task configs used by the external collection runner. It is intentionally tracked before real evidence exists so the collection preflight can distinguish a missing intake directory from missing real configs.

Do not copy files from `external_validation/config_templates/` here unchanged. A config in this directory is admissible only after the operator has selected a real robot or accepted high-fidelity simulator and filled:

- `version: "paper119_external_config_v1"`
- `platform_name`
- `skill_i`
- `skill_j`
- `compute_budget.wall_clock_seconds`
- `compute_budget.simulator_query_budget`
- task-specific fidelity checks and reset protocol details

Expected real config files:

- `peg_place_regrasp.json`
- `drawer_to_pick_transfer.json`
- `door_open_navigation.json`
- `cable_route_insert.json`

Strict validation command after real configs exist:

```powershell
python scripts\validate_external_configs.py --strict
```

