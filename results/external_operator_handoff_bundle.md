# External Operator Handoff Bundle

Passed: `true`.
Not evidence: `true`.
Strict evidence ready: `false`.
Start state: `DO_NOT_COLLECT_YET`.
Included files: `392`.

This is a hash-listed handoff manifest for an independent validation operator. It intentionally does not package rollout logs, videos, checkpoints, local dry-run artifacts, placeholder media, or `external_validation/manifest.json`. It is a non-evidence checklist for what to send before a real robot or accepted high-fidelity simulator run.

## Commands

Strict backend qualification:

```powershell
python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
```

Strict pre-collection gate:

```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
```

Precollection freeze receipt:

```powershell
python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
```

Actual collection command after the strict gate passes:

```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```

Postcollection evidence seal before manifest promotion:

```powershell
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
```

Postcollection seal consistency gate before manifest promotion:

```powershell
python scripts\audit_external_postcollection_seal_consistency.py
```

Post-collection strict gates:

- `python scripts\build_external_postcollection_evidence_seal.py`
- `python scripts\audit_external_postcollection_seal_consistency.py`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_evidence.py --strict`

## Category Counts

- `baseline_spec`: `12`
- `config_template`: `4`
- `generated_non_evidence_report`: `136`
- `method_config_candidate`: `11`
- `operator_command_source`: `63`
- `operator_facing_input`: `93`
- `prepared_config_input`: `4`
- `reference_adapter`: `60`
- `runner_backend_template`: `5`
- `task_card`: `4`

## Excluded Evidence Paths

- `external_validation/checkpoints/`
- `external_validation/local_dry_run/`
- `external_validation/logs/`
- `external_validation/manifest.json`
- `external_validation/videos/`
- `placeholder_not_external_evidence`

## Included Files

- `README.md` (operator_facing_input, 36234 bytes, sha256 `2C653B0E71DD498371482BC3557295C3340942D45D8CEDB1185F665A9455FFCE`)
- `docs/external_evidence_closure_brief.md` (operator_facing_input, 11318 bytes, sha256 `7A284EC84C024910358918C31EFBF71D21B42FBF5C8E572CF35634802304CFAA`)
- `docs/haonan_yilun_outreach_package.md` (operator_facing_input, 15332 bytes, sha256 `A442CD743D708F1792AD8E15AE9682513415608259AD4E6A0B5462254C559569`)
- `docs/independent_validation_launch_ticket.md` (operator_facing_input, 8219 bytes, sha256 `ABE7F32CBFEB5D4C48C1838008BB51C74F4F7C6349AC09B6108C47AB1EE1C7D1`)
- `docs/independent_validation_protocol.md` (operator_facing_input, 21796 bytes, sha256 `7EDFEE348BE624FC1BA8818A88D526CC53B3632F3D31A1500A19F9C5A868FC2E`)
- `docs/maniskill_render_host_qualification_brief.md` (operator_facing_input, 6332 bytes, sha256 `5F3317883345DE601B48E0B729077EF1EF4F74D73082200AB83E18EA1BAC38D5`)
- `docs/reproducibility_checklist.md` (operator_facing_input, 26263 bytes, sha256 `4817F0A77C9F93E63BCF2191A85EA11994AB35186535F164448888753F3CA5B3`)
- `docs/submission_readiness_decision.md` (operator_facing_input, 27488 bytes, sha256 `399E97C325DF8D679DCFD8B4BB13B5FBC141F41CB582ED8A2376C42C18F33780`)
- `external_validation/README.md` (operator_facing_input, 34698 bytes, sha256 `5E0E6D9D7D06DC4AB8F664ACC65BEEAEE65799B48D82753722812C08BBFB261B`)
- `external_validation/ablation_collection_packet.json` (operator_facing_input, 15553 bytes, sha256 `5B7814EF0C0555B0148B40B2D5E2B9DB1069C9BC1E1686C96E1411B1FA36D94E`)
- `external_validation/ablation_collection_packet.md` (operator_facing_input, 4221 bytes, sha256 `CE3703F13541AAFB56EA072107D224E585DBFCB3025B97C9940A6DCEA536D545`)
- `external_validation/ablation_collection_work_orders.csv` (operator_facing_input, 8153 bytes, sha256 `B441B51BAA4DA00DEC488C05E11EF8D381DF1B2D742024936691A12B16CBB1B7`)
- `external_validation/adapter_acceptance_fixtures.csv` (operator_facing_input, 6081 bytes, sha256 `D03B5D89EE71FEA723CCC37A7092CD725574382CCC88C229784D7D5CE0CA8F54`)
- `external_validation/adapter_acceptance_fixtures.json` (operator_facing_input, 41085 bytes, sha256 `9EE0526CF98600195B1E5257F9177C69346D2F3593ED582D67D3CB5797984D08`)
- `external_validation/adapter_acceptance_fixtures.md` (operator_facing_input, 18169 bytes, sha256 `EE98FFB8E3767687273702ABAD34E29AF5ECDCF5A67C17A545657CCB11AB2EF0`)
- `external_validation/backend_integration_packet.json` (operator_facing_input, 9078 bytes, sha256 `8581FAD2CF3865FBCB78A8F796FC70195830DA8771053556F9C5BB147718E303`)
- `external_validation/backend_integration_packet.md` (operator_facing_input, 5517 bytes, sha256 `4253E6578CD2C0EE2C3906484A6ABFB8DEE168F54A5C4F7441867C80E33201A0`)
- `external_validation/backend_integration_work_orders.csv` (operator_facing_input, 3496 bytes, sha256 `A7A4D24FE4AB850B63AFD1719C2642A30E2D029BD8260C298A0BFC43F18E346D`)
- `external_validation/baseline_adapter_scaffold.md` (operator_facing_input, 2583 bytes, sha256 `60574D9F61C86A680A760F066FB23E800EA4AA119660D829DB93107D86B48F31`)
- `external_validation/baseline_implementation_contract.md` (operator_facing_input, 5322 bytes, sha256 `6A9D35C0AF017DF3D40DFA4606F6D25D77D5A6394D800FC123E26E3CA9899DAD`)
- `external_validation/baseline_implementation_matrix.csv` (operator_facing_input, 2715 bytes, sha256 `BD52E82CD3323352ECF291BAEF9CFBBAAFC382A8902A9505A817B156F45CD01D`)
- `external_validation/baseline_specs/barrier_certified_energy_composer_v5.json` (baseline_spec, 2147 bytes, sha256 `C9F658C69E506D4D6041BA15AFDD6B3D7CCA59C66215C59AAEB18846E552F812`)
- `external_validation/baseline_specs/behavior_cloned_skill_chain.json` (baseline_spec, 2151 bytes, sha256 `6C6F97BA41C0E43FA1BE3547AA25A7F0FB92EB5B1D04C5D75058734A2B6A79E6`)
- `external_validation/baseline_specs/cem_trajectory_composer.json` (baseline_spec, 2123 bytes, sha256 `47A2E1400A54A14AD03C29BA3A557EF2A3C0F36D55C8B03E9C88ED32E34F626D`)
- `external_validation/baseline_specs/diffusion_skill_stitcher.json` (baseline_spec, 2141 bytes, sha256 `635E07B25AA4DD9CBAF18DB439C58971CA99AEE86482EDE3FCD4C1FDD3BA7611`)
- `external_validation/baseline_specs/energy_compatibility_heuristic.json` (baseline_spec, 2131 bytes, sha256 `585EE36283EBCC0780C5C6B79BFCAB0F8DDB562DBCCC6E98379E6AE99F9EFF18`)
- `external_validation/baseline_specs/greedy_module_sequence.json` (baseline_spec, 2132 bytes, sha256 `6C4327B7F5B0719D0DAC4E12B4B507A8744AA6C68E54EE48CA16B52E81D90336`)
- `external_validation/baseline_specs/option_graph_planner.json` (baseline_spec, 2118 bytes, sha256 `D0DE4635206512731388A74FACD5BB1FF87F1DA236C5F3559F676A0B88E99F4E`)
- `external_validation/baseline_specs/oracle_basin_composer.json` (baseline_spec, 2107 bytes, sha256 `32979EF2B3C53C14F53301F308B51033A823593BAE0628BCA9C7A0D785052881`)
- `external_validation/baseline_specs/proposed_energy_landscape_composer_v4_1.json` (baseline_spec, 2121 bytes, sha256 `2A5C0BCA5465CC83977CA434C807074BD71F71B3DA6BFAE5BE57A8EE9351069F`)
- `external_validation/baseline_specs/residual_rl_composer.json` (baseline_spec, 2109 bytes, sha256 `03B3E3134A6564F6FC4E991B7F5ED2A772032238D79CC744E0B179A7D3EEE0BB`)
- `external_validation/baseline_specs/stable_dmp_handoff.json` (baseline_spec, 2101 bytes, sha256 `9D6536D923635D4BE87B26F0A984303BF751331A8917F9CF52F4A7E7F42E7A70`)
- `external_validation/baseline_specs/tamp_feasibility_screen.json` (baseline_spec, 2109 bytes, sha256 `84C3DDFB27AB3207B9AD378F40A299051C94A43BBD73C17EF90055A2BF5A49CB`)
- `external_validation/baselines/README.md` (operator_facing_input, 2296 bytes, sha256 `A4AD8488DCAE6276DBDBD3041DCA1720ED1DFC6003D046DACEB954DB2081D3D6`)
- `external_validation/baselines/barrier_certified_energy_composer_v5/README.md` (reference_adapter, 564 bytes, sha256 `8A56F3BEA2DDD6993AE3D1B4C3300E53304B8F06702739D2953D8C003DD30150`)
- `external_validation/baselines/barrier_certified_energy_composer_v5/adapter.py` (reference_adapter, 839 bytes, sha256 `DFECC8475DFE638A5F23B7941CEB00C1F8094EF2256BE60F20CA6F817341859B`)
- `external_validation/baselines/barrier_certified_energy_composer_v5/adapter_metadata.json` (reference_adapter, 913 bytes, sha256 `A25FF99BAEA881AF4B679244DB781C153A6565F0221C69C5AF410571DAD6EDB4`)
- `external_validation/baselines/barrier_certified_energy_composer_v5/adapter_template.py` (reference_adapter, 1382 bytes, sha256 `1CA57B6A679BDF24E71A1C0BE4C2B471CA03394F646468C425387DE3AA6D476E`)
- `external_validation/baselines/barrier_certified_energy_composer_v5/reference_adapter_metadata.json` (reference_adapter, 568 bytes, sha256 `43927773BC52B3BA31376C956CEC5269715957DFDFCE8EE3E209DCEEFE8EF092`)
- `external_validation/baselines/behavior_cloned_skill_chain/README.md` (reference_adapter, 573 bytes, sha256 `FCAEB08E7673407BFA59D65D3907F0BD698E4F83B6706A5977979817D24F86D5`)
- `external_validation/baselines/behavior_cloned_skill_chain/adapter.py` (reference_adapter, 830 bytes, sha256 `9B3548FB33CAB6503F8BF9F6189FEDC2177897E83C3FDF2D657CA6E1019F4890`)
- `external_validation/baselines/behavior_cloned_skill_chain/adapter_metadata.json` (reference_adapter, 908 bytes, sha256 `B106212F137437E28CCD427964050D121DAAF0226C1CCAB6741892C0FC82B8E5`)
- `external_validation/baselines/behavior_cloned_skill_chain/adapter_template.py` (reference_adapter, 1360 bytes, sha256 `24CA6024E5579059A98B914F220A93F160339194321D4535D43C1F92DE20031C`)
- `external_validation/baselines/behavior_cloned_skill_chain/reference_adapter_metadata.json` (reference_adapter, 541 bytes, sha256 `D49DAEFFB6BE02DF858C415B13157FC783CE3864C909A9E144E809439F7E3A3F`)
- `external_validation/baselines/cem_trajectory_composer/README.md` (reference_adapter, 545 bytes, sha256 `0946653BE0F0B0FB358606134466B281BB77A16B90D5DEEDBD0FF57E1F6BBB84`)
- `external_validation/baselines/cem_trajectory_composer/adapter.py` (reference_adapter, 826 bytes, sha256 `81B7FFAE412D296A7A5E9D0ADEF0BBE2031FB4D4FB08B65DD6408F1101668FDB`)
- `external_validation/baselines/cem_trajectory_composer/adapter_metadata.json` (reference_adapter, 896 bytes, sha256 `3D378902B62133F9254647A08F6DAADEF8533792CF4B1571006AABA11300AE7F`)
- `external_validation/baselines/cem_trajectory_composer/adapter_template.py` (reference_adapter, 1353 bytes, sha256 `234831ED15A10B02595E3C9719D214D48CE4713CD1A308AF5A107B67F0C73BCB`)
- `external_validation/baselines/cem_trajectory_composer/reference_adapter_metadata.json` (reference_adapter, 529 bytes, sha256 `517511503ED732E656A3CAE1B8173FB0890DDED96C284CAE30F5428F8A002B08`)
- `external_validation/baselines/diffusion_skill_stitcher/README.md` (reference_adapter, 573 bytes, sha256 `5E976F6F69CCBE499D32D3A8C310CF72D253C3C5A6BE0AFA2DECB076F6E61F03`)
- `external_validation/baselines/diffusion_skill_stitcher/adapter.py` (reference_adapter, 827 bytes, sha256 `B16C610BCB5906C72BFD7495792D5635546513E91BC44CAC98C9C5DA3F3177BF`)
- `external_validation/baselines/diffusion_skill_stitcher/adapter_metadata.json` (reference_adapter, 901 bytes, sha256 `1A9F6E0279B315D8D934EDA017322C311522D0BF054807004F8B9294752DCE11`)
- `external_validation/baselines/diffusion_skill_stitcher/adapter_template.py` (reference_adapter, 1349 bytes, sha256 `06D1D5E0F6620D82D4CAD6846C5C01F3CFA1EB041A4B32564E593EAE0596F12F`)
- `external_validation/baselines/diffusion_skill_stitcher/reference_adapter_metadata.json` (reference_adapter, 532 bytes, sha256 `35EB7CAE4718930995DA80B1F88B059C91BD179E903618C044BF77BD3BBE02C7`)
- `external_validation/baselines/energy_compatibility_heuristic/README.md` (reference_adapter, 563 bytes, sha256 `23584AE8545EE1A0102859E90B9C21B162613E8FE3122D2D20CF8760283CC7B4`)
- `external_validation/baselines/energy_compatibility_heuristic/adapter.py` (reference_adapter, 833 bytes, sha256 `C59B9E9BA7621A12731D0228488B990593915A23A884FC2042842D550637FC59`)
- `external_validation/baselines/energy_compatibility_heuristic/adapter_metadata.json` (reference_adapter, 917 bytes, sha256 `C0C4320D90F2528D1D9EF8FC3CECABE0D8FB7F1FCC1461E1751599C6ED75E73C`)
- `external_validation/baselines/energy_compatibility_heuristic/adapter_template.py` (reference_adapter, 1361 bytes, sha256 `448EB993EA40FF694DA66445BFF9AB32EE823AED2B227A9713340FFE715C8674`)
- `external_validation/baselines/energy_compatibility_heuristic/reference_adapter_metadata.json` (reference_adapter, 550 bytes, sha256 `18D60A2A2F1687319F36DA9BCE9B119B8B8128F1BE4942240E77F05E241692C9`)
- `external_validation/baselines/greedy_module_sequence/README.md` (reference_adapter, 549 bytes, sha256 `8715C836C7104D96DF53BA45FDC1D360429DB75BAF0B16C7755B81115AEC3DDD`)
- `external_validation/baselines/greedy_module_sequence/adapter.py` (reference_adapter, 825 bytes, sha256 `8C9F465960077E3B8A67DC398B236C2C1C0E4F253E51366A56EA77E5ED5CC963`)
- `external_validation/baselines/greedy_module_sequence/adapter_metadata.json` (reference_adapter, 903 bytes, sha256 `2B505A71BC4C5B1CCDEB8A0ADA8A8D85A5078F06C848505E2BB63C8C51FED928`)
- `external_validation/baselines/greedy_module_sequence/adapter_template.py` (reference_adapter, 1356 bytes, sha256 `B743F7AF1ED2F9B793C33A953181F20D380148FCA1A19EB1FBF78F3C960490E5`)
- `external_validation/baselines/greedy_module_sequence/reference_adapter_metadata.json` (reference_adapter, 526 bytes, sha256 `DCCBF2DD75F13658266157E0AD797AFCE6E9DA96B92EAA7A3387A8BDCE090407`)
- `external_validation/baselines/option_graph_planner/README.md` (reference_adapter, 540 bytes, sha256 `92B3638F3BC4820106C17EFFE1B5B532A9439896AA5F40EFF25080DF365DD6F3`)
- `external_validation/baselines/option_graph_planner/adapter.py` (reference_adapter, 823 bytes, sha256 `BA19AC254B64D5F79600E44EE88A748FC237D3910BA592014D732E632535B22D`)
- `external_validation/baselines/option_graph_planner/adapter_metadata.json` (reference_adapter, 902 bytes, sha256 `A8F51CA80D58510CDA2755542BBC05976B1A20E6187D6AD81D48662246B1C1D7`)
- `external_validation/baselines/option_graph_planner/adapter_template.py` (reference_adapter, 1347 bytes, sha256 `37CC41F6592A0DE904C9A965CC2CA59B8819D66C1263D7A52AA35ABC4554408A`)
- `external_validation/baselines/option_graph_planner/reference_adapter_metadata.json` (reference_adapter, 520 bytes, sha256 `4FCA52468D2B02DDFCEAA9B2A89381E9723CF910F89DC33AB995E6A11368F02D`)
- `external_validation/baselines/oracle_basin_composer/README.md` (reference_adapter, 544 bytes, sha256 `1102E0CF983E3C73B12D474A18D4888C8F0627FB7218E65E5BF09422F05F106C`)
- `external_validation/baselines/oracle_basin_composer/adapter.py` (reference_adapter, 824 bytes, sha256 `22B834792A1AC0F9A11EA3D410F0DFEBA8E59D6CE6521B6A46E7DB2A41379AC9`)
- `external_validation/baselines/oracle_basin_composer/adapter_metadata.json` (reference_adapter, 884 bytes, sha256 `F20102B841C0FEA9235D64E102F4E006006A3307612587E1E1D021C0854D9971`)
- `external_validation/baselines/oracle_basin_composer/adapter_template.py` (reference_adapter, 1353 bytes, sha256 `7B09E8FFCE08B752951FEEA5FB45389237EE379BD8145167AC94FAF5EF659682`)
- `external_validation/baselines/oracle_basin_composer/reference_adapter_metadata.json` (reference_adapter, 520 bytes, sha256 `E63495717F7B98EB850CB7714E65D20B870763DDC397D5AE9BBA861D8DC79CF1`)
- `external_validation/baselines/proposed_energy_landscape_composer_v4_1/README.md` (reference_adapter, 548 bytes, sha256 `B8710D8EC54B83C86CCDCC126C91A1BF2BD3DF58B65401AF86177CF642B48A4D`)
- `external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter.py` (reference_adapter, 842 bytes, sha256 `ADE2084726B6A6DE7B2F90DFA6A1C4F5D2614551079E978AF9B849A794C6A540`)
- `external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter_metadata.json` (reference_adapter, 917 bytes, sha256 `E303F937C8D9729A65A8B6338E1A8054E8DFC70A3A167B2002D5CE9CBDFB5575`)
- `external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter_template.py` (reference_adapter, 1367 bytes, sha256 `F5FFC2A3ECDCAD7FBAFEF80732DBE7BB935F4597207A1F7D5A7132617A6C59FC`)
- `external_validation/baselines/proposed_energy_landscape_composer_v4_1/reference_adapter_metadata.json` (reference_adapter, 577 bytes, sha256 `3D0F0E9C90265776C4B7A18D0E11FC5AE1EF03CCF32862F7EB30D0B6543C2E97`)
- `external_validation/baselines/residual_rl_composer/README.md` (reference_adapter, 536 bytes, sha256 `F82714E119B5060E8C2DBCD545D6DC6CC2BB0598A9E97E10C5588BDE43880E1D`)
- `external_validation/baselines/residual_rl_composer/adapter.py` (reference_adapter, 823 bytes, sha256 `5B72C98DC049FC0476451EE9E89A0F94D2E50DC1B20AF7CB327D6A60404919FF`)
- `external_validation/baselines/residual_rl_composer/adapter_metadata.json` (reference_adapter, 902 bytes, sha256 `A92754C51C3DA1B4FEDEF3189B505337DF38D77AD032EF478EF789BD3C34F841`)
- `external_validation/baselines/residual_rl_composer/adapter_template.py` (reference_adapter, 1353 bytes, sha256 `19621501AB64E0FF4DF19F254AFA067BEBDBE0C664E8FC2241D17B266548E85B`)
- `external_validation/baselines/residual_rl_composer/reference_adapter_metadata.json` (reference_adapter, 520 bytes, sha256 `834E64EE4A38F2B90C5D7D15E8711C05B670DA42794D8AF70C992D7017601CA1`)
- `external_validation/baselines/stable_dmp_handoff/README.md` (reference_adapter, 528 bytes, sha256 `F7AC06E3E55B8F7E40F7FC7C1E1A35224C5D4AFDFE3049AAFA0592C3420C37F9`)
- `external_validation/baselines/stable_dmp_handoff/adapter.py` (reference_adapter, 821 bytes, sha256 `3C16F0F4178F4F9A6FA6EEB88CF0CC7EB5A78890351C0EB2DDCFBCF6BC031F89`)
- `external_validation/baselines/stable_dmp_handoff/adapter_metadata.json` (reference_adapter, 895 bytes, sha256 `03B3636B904E8102650A0DA4F2A2031B28209AEDF804973A7DB0E200E4A9A441`)
- `external_validation/baselines/stable_dmp_handoff/adapter_template.py` (reference_adapter, 1346 bytes, sha256 `BE886A06D39D0E10DD8FE1D89058F4B1A229D3A149A71737CB5A263AC5634D56`)
- `external_validation/baselines/stable_dmp_handoff/reference_adapter_metadata.json` (reference_adapter, 514 bytes, sha256 `1F13C312604CABE911505F547A790EF6E04404FA1B07A401E542831B78AF7018`)
- `external_validation/baselines/tamp_feasibility_screen/README.md` (reference_adapter, 536 bytes, sha256 `AFB6167D7396D999B1CAABA383E48B7E095A005ACBB1FE7F04E934F5FBC07135`)
- `external_validation/baselines/tamp_feasibility_screen/adapter.py` (reference_adapter, 826 bytes, sha256 `1664C0DB0B62CAAE96F3BB2DDE13956797A82FC00BFA11D12C8F2E06C51C6AA9`)
- `external_validation/baselines/tamp_feasibility_screen/adapter_metadata.json` (reference_adapter, 917 bytes, sha256 `330EEB19A95AFA214EA099FE7A8090F3E4A9BCF601E3FB46A3BB4BE9AE863F81`)
- `external_validation/baselines/tamp_feasibility_screen/adapter_template.py` (reference_adapter, 1364 bytes, sha256 `CD27F1B2F93E955C941944DB2F79B7E7727B9D0C56A676F272621C1E3E48E1D9`)
- `external_validation/baselines/tamp_feasibility_screen/reference_adapter_metadata.json` (reference_adapter, 529 bytes, sha256 `DA8DBB10C331A0FE572D5ADF7BBDACABDE29664E78BEFADA1BFC7CEA377F0987`)
- `external_validation/blind_evaluation_protocol.md` (operator_facing_input, 1490 bytes, sha256 `C63EE57CBCDFAF81F0EE595599FF6B876888638F826A9676F3D7ECA5A46ACE31`)
- `external_validation/blinded_operator_sheet.csv` (operator_facing_input, 492933 bytes, sha256 `BAAF6BC6B7BFA0DAD346498D8C7FACEE413FD2A0844E5F833A519BBAD4BEEBF5`)
- `external_validation/collection_job_checklist.csv` (operator_facing_input, 8609 bytes, sha256 `2ACB0609C9240407B17A89B07D968050FCDCE0C1E076BC6E00DB6B48F09D5388`)
- `external_validation/collection_job_commands.ps1` (operator_facing_input, 6023 bytes, sha256 `859953B47DAE87355D0370D55FA56721AF7440388852BA4BA5FF3A2ACBF40C41`)
- `external_validation/collection_job_commands.sh` (operator_facing_input, 8168 bytes, sha256 `707515D35111212BCD150D528ADCDBA6A8C0F5B0537D33CD0F823DC505DE5AB1`)
- `external_validation/collection_job_packet.json` (operator_facing_input, 18160 bytes, sha256 `3FFB936BC442B13421393A684E7A2BC80ED29DB5FD2B2DBC4429B96821EDEB02`)
- `external_validation/collection_job_packet.md` (operator_facing_input, 14838 bytes, sha256 `8F307AE6F9E06E49C3B7DC6E327D0024D96D7506628068B1D0131614678B0F8C`)
- `external_validation/collection_machine_bootstrap.json` (operator_facing_input, 5895 bytes, sha256 `4DABFEF074B1DFCA43723A415300E5ECAF969BA57928496E9928787DDB65EDEE`)
- `external_validation/collection_machine_bootstrap.md` (operator_facing_input, 3912 bytes, sha256 `05ADB92A7DBD845061F7575CCE5ED32412F9AFFF37574029E6B7E3204AF9C848`)
- `external_validation/collection_machine_bootstrap.ps1` (operator_facing_input, 2330 bytes, sha256 `B50B58B3A30AE2F73BBD647E844D026E75E1750A0B4E43B55CCC6F99C48E166D`)
- `external_validation/collection_machine_bootstrap.sh` (operator_facing_input, 2776 bytes, sha256 `E5046E68D3AD2BC624B74F3CC361AD93D76D1979733ABDE50911DAE704F17268`)
- `external_validation/collection_runbook.md` (operator_facing_input, 5942 bytes, sha256 `728A4D84B20D20D6D290A15E60F5833721BD5CFB1CBFE7B291CAD0954DDEC978`)
- `external_validation/config_manifest_packet.json` (operator_facing_input, 10400 bytes, sha256 `C2343059481F025643AA423598FFC975E02A0E23A64E12B5736109658272C49F`)
- `external_validation/config_manifest_packet.md` (operator_facing_input, 5445 bytes, sha256 `920AEAF0C567DDC48AFFD382B5405DE001BA0828EECA3E46BD3F65AB4ECB396B`)
- `external_validation/config_manifest_work_orders.csv` (operator_facing_input, 3406 bytes, sha256 `3AC4E5EAC96AFE64DCEF3E3ABE25235FB7BAC9D3B7BF106B58FD27C2C601A06E`)
- `external_validation/config_schema_v1.json` (operator_facing_input, 1823 bytes, sha256 `6936B85F4D47F87CC509E272E37F577BD3FF2EC0B505EEAEE0C3180207189573`)
- `external_validation/config_templates/cable_route_insert.json` (config_template, 1590 bytes, sha256 `2CE483630DF76B8CCADC2E5C051C5AF6C37473A70C43979C170C8BD4C2038C75`)
- `external_validation/config_templates/door_open_navigation.json` (config_template, 1591 bytes, sha256 `29BA40F9BC94F385814E489F56FB99FFE39E228F22268FF9DE46AD241DCA461D`)
- `external_validation/config_templates/drawer_to_pick_transfer.json` (config_template, 1574 bytes, sha256 `A9DCD9D9A117607982ED7D6A51D1626091CA45FE76CAD91059B94327C208E727`)
- `external_validation/config_templates/peg_place_regrasp.json` (config_template, 1575 bytes, sha256 `5F8C51F458A125A00FB60A461E5ABCD190EAC710660A1D9D71FD3E4159098F9C`)
- `external_validation/configs/README.md` (operator_facing_input, 1442 bytes, sha256 `A54334B0AA891AAE8D43FB8A44360433713A59D067B999E52FAC5E2E6F1AF156`)
- `external_validation/configs/cable_route_insert.json` (prepared_config_input, 2034 bytes, sha256 `8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E`)
- `external_validation/configs/door_open_navigation.json` (prepared_config_input, 2005 bytes, sha256 `13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61`)
- `external_validation/configs/drawer_to_pick_transfer.json` (prepared_config_input, 2046 bytes, sha256 `1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471`)
- `external_validation/configs/peg_place_regrasp.json` (prepared_config_input, 1989 bytes, sha256 `021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9`)
- `external_validation/evidence_intake_ledger.csv` (operator_facing_input, 27303 bytes, sha256 `92CE1249896D06559B8C6199716A841A8F08ED883222B1C617325E07D9826D71`)
- `external_validation/evidence_intake_ledger.json` (operator_facing_input, 43816 bytes, sha256 `BA2A6A50BCFB44FDF7531CF71BCBEBB68D3E9B3D8851F75BB5F11CED1F8D24D9`)
- `external_validation/evidence_intake_ledger.md` (operator_facing_input, 11214 bytes, sha256 `8E8E11E9AA7A949FC3C34FE40B5F64D960178E8285C1D794415CFDF44BAB0F87`)
- `external_validation/fidelity_acceptance_draft.json` (operator_facing_input, 25345 bytes, sha256 `6BA4C9CC96AA1C46F92CB2F785127069307E5F9A378F82DAC41F650D142A2C4B`)
- `external_validation/fidelity_acceptance_draft.md` (operator_facing_input, 6026 bytes, sha256 `546C9C73DDC58EDC55CDB8BB473A2A55B2C4C1EBCE5552DD22A11B5387448410`)
- `external_validation/fidelity_acceptance_template.json` (operator_facing_input, 4582 bytes, sha256 `0BED23F5E73145C7D3283605C0EFDCCF0970CBC989CAAC6DF4E45445D30496E0`)
- `external_validation/fidelity_provenance_packet.json` (operator_facing_input, 20161 bytes, sha256 `0319F0754DCD893BE1C9EC98A26FD30DF63037F6543868C729E007E4D1125782`)
- `external_validation/fidelity_provenance_packet.md` (operator_facing_input, 3674 bytes, sha256 `FF138E663BDFCDDC47BE9CC671FB472DC82D3126AEDC7B0EBA3B9AC7B68476CF`)
- `external_validation/fidelity_provenance_work_orders.csv` (operator_facing_input, 11772 bytes, sha256 `7E26F05053D899036351634D075F4F1B3CE8AC7464A581C27EEC3C1CD65DBCDA`)
- `external_validation/independent_validation_launch_ticket.md` (operator_facing_input, 8219 bytes, sha256 `ABE7F32CBFEB5D4C48C1838008BB51C74F4F7C6349AC09B6108C47AB1EE1C7D1`)
- `external_validation/independent_validation_route.md` (operator_facing_input, 7270 bytes, sha256 `10B4246BF3F6F32F052E89EACD2FE1CB7CB2CB9ACB8C77876CF88915EFBA3379`)
- `external_validation/independent_validation_route_matrix.csv` (operator_facing_input, 2115 bytes, sha256 `02E059F84400B4054939012707D7FD43A6F4BDAF3CEF5560A760CBD06BBAAB4E`)
- `external_validation/log_schema_v1.json` (operator_facing_input, 3055 bytes, sha256 `BF2194D543F83448F03BBD9ADB5310C9BDE7313228EA876BE7FE75CD788A4917`)
- `external_validation/manifest_assembly_checklist.csv` (operator_facing_input, 11089 bytes, sha256 `572827C87C44B677B5897E2215FB3741E38000A40C23AF5141AFBC923D31FAEA`)
- `external_validation/manifest_precollection_draft.json` (operator_facing_input, 44176 bytes, sha256 `8C993B9FD0AEFD072FE81D052808BB20691B497B725877C7D1D13B2802A91D29`)
- `external_validation/manifest_precollection_draft.md` (operator_facing_input, 11366 bytes, sha256 `0DB9BB55D0E70B38E9C96321298309A9C54977E6B137258EF6FA2C0DF8879B43`)
- `external_validation/maniskill_task_bindings.json` (operator_facing_input, 2159 bytes, sha256 `448A0430B88097618D463319DBD599334D28D533F81BA2FE783C3B80DE4EFBC5`)
- `external_validation/method_alias_map.json` (operator_facing_input, 3261 bytes, sha256 `B56A11CB20914B2FD2649DA647F7722DE43D6B04DE3E89704A8CD3F952A4E031`)
- `external_validation/method_config_candidates.csv` (operator_facing_input, 6436 bytes, sha256 `BBFDEAAA8563980BCD0CDE8002DA50676B1B7F1B68A238CCC39CEEEEDCBB4EF5`)
- `external_validation/method_config_candidates/barrier_certified_energy_composer_v5.json` (method_config_candidate, 3502 bytes, sha256 `0DF7FB36D51A1866B46716F0601E46E81B815849675D0C6CAB8FB4037B801872`)
- `external_validation/method_config_candidates/behavior_cloned_skill_chain.json` (method_config_candidate, 3494 bytes, sha256 `BCFB1DAAE14267E91CC9FE9AA08083FFF90625B255C81FA74E47647018A969C2`)
- `external_validation/method_config_candidates/cem_trajectory_composer.json` (method_config_candidate, 3458 bytes, sha256 `BA1A268A3FBADB9E86286B11B6B9E593BEFB448586493CFBB4CDFDE8C6661C99`)
- `external_validation/method_config_candidates/diffusion_skill_stitcher.json` (method_config_candidate, 3478 bytes, sha256 `4F44159059554664F238B144C1D65395CDE4417F89308ABD8C3DC09EDB02165B`)
- `external_validation/method_config_candidates/energy_compatibility_heuristic.json` (method_config_candidate, 3480 bytes, sha256 `ED6FB2887EFB80342705CA1528597B8AE4FB890C28B285660FD9C0443FA0903C`)
- `external_validation/method_config_candidates/greedy_module_sequence.json` (method_config_candidate, 3465 bytes, sha256 `4158524DEB92394F50D7550D295D67860F9D2D92F4C1D06B13FA668B1F1F7DFA`)
- `external_validation/method_config_candidates/option_graph_planner.json` (method_config_candidate, 3447 bytes, sha256 `DE3E0198432E4CF42F017C473EED3CF889B60FE5B85B642C55C44A1FF02410AD`)
- `external_validation/method_config_candidates/proposed_energy_landscape_composer_v4_1.json` (method_config_candidate, 3483 bytes, sha256 `7331767D0D76C6507C4F586F2FD093ADAF7FF0DF07CAB50A1A4FD164D8CEABB3`)
- `external_validation/method_config_candidates/residual_rl_composer.json` (method_config_candidate, 3438 bytes, sha256 `4A0CE8A9FD2BE847325029A688ED912635342D4F0159FF454828FA228C5F302F`)
- `external_validation/method_config_candidates/stable_dmp_handoff.json` (method_config_candidate, 3426 bytes, sha256 `0AD7209C0E2023CE462624C5A10EB09AC5EA7A249D86CA47A4EBC20F852639EF`)
- `external_validation/method_config_candidates/tamp_feasibility_screen.json` (method_config_candidate, 3444 bytes, sha256 `18F846DB89B1C852DF378A3ED9A205389141AE2C56D0D9E27210401973620EFB`)
- `external_validation/method_config_materialization_plan.json` (operator_facing_input, 33495 bytes, sha256 `BD209F79FB82612573D745A9E394858B25787B82A9DAA9B38694E6279E31F9FB`)
- `external_validation/method_config_materialization_plan.md` (operator_facing_input, 3650 bytes, sha256 `EE02B6996F22C1F4FB47AF876B57DA980245CABB8B41027F4C8D4EBBF3C651D9`)
- `external_validation/method_implementation_packet.json` (operator_facing_input, 116640 bytes, sha256 `A7D425325142127BB94219E86F7C446634733081908C7B3E2370545F94856F4F`)
- `external_validation/method_implementation_packet.md` (operator_facing_input, 65478 bytes, sha256 `3DE09E528AEFCE8CD40F93781902C4EB69F9D79770C744D9C80D479657B46375`)
- `external_validation/method_implementation_work_orders.csv` (operator_facing_input, 10122 bytes, sha256 `A3823158957383F5EAC54FF2AC0D5E21440E2034FCFAC05FB75B91ADD2798E79`)
- `external_validation/method_manifest_cutover_checklist.csv` (operator_facing_input, 8096 bytes, sha256 `A7C212C2F99ABFE921D5C5128446E1DE908996C5B789D9BFF6F2B5DA926DF899`)
- `external_validation/method_manifest_cutover_checklist.md` (operator_facing_input, 4333 bytes, sha256 `D21F7033199CA20BA8610BAC8777E385EC1790FBF2A447B25EF1D12883942765`)
- `external_validation/method_reference_provenance.csv` (operator_facing_input, 7830 bytes, sha256 `7F6A5967DE10AC5A49200726082D0600A3EF70984B94DC414A35AA90BD97CCAC`)
- `external_validation/operator_record_sheet.csv` (operator_facing_input, 710130 bytes, sha256 `3286764C655EA1F5209A93A2D4C5596941EF22F621BA11282867F62C5D22785D`)
- `external_validation/pilot_smoke_packet.json` (operator_facing_input, 3268 bytes, sha256 `D70209BEC7554552BA799AEF79717DE0E660F49901240D36D27635EAA6E4B598`)
- `external_validation/pilot_smoke_packet.md` (operator_facing_input, 2089 bytes, sha256 `935DE117EF6D0DD1212A93296328CBAD0C0F91BEDBF9E50DB0E7F3672ABABDEC`)
- `external_validation/pilot_smoke_work_orders.csv` (operator_facing_input, 1033 bytes, sha256 `5F18D7641041AD7B7F9AD394AFE8A4CB7ADE880E2A0B6ECBA4A7F568DD821F3E`)
- `external_validation/platform_onboarding_packet.json` (operator_facing_input, 13488 bytes, sha256 `E018EEA1A5AA720E1C1541051FB6E2EEFD6868886D72AB01488A467854A879E3`)
- `external_validation/platform_onboarding_packet.md` (operator_facing_input, 10602 bytes, sha256 `36ED55138F7E43B5B57380493F2F8A1911DB37FFE173B71BFF3BECC50CE3A967`)
- `external_validation/platform_qualification_checklist.md` (operator_facing_input, 3275 bytes, sha256 `76F4BF45C6E2799185830A4EC0C0A2CED92556E5EED9B827915698CEF0012B4A`)
- `external_validation/postcollection_evidence_seal.csv` (operator_facing_input, 1823 bytes, sha256 `13BAF77EC36A4B28D9BD2602DA5E316F5799D1C68071DB9A11A23262D34F804C`)
- `external_validation/postcollection_evidence_seal.json` (operator_facing_input, 6584 bytes, sha256 `93B1E2C1B1BF26434ACF344DA8A8412380EFE3A985F4126661A5E563FD2CB03D`)
- `external_validation/postcollection_evidence_seal.md` (operator_facing_input, 4655 bytes, sha256 `C282452CA1E0553BCC0F148F08067B13C31D7EC7D49A0C7894BB25C10F54DF46`)
- `external_validation/precollection_freeze_receipt.csv` (operator_facing_input, 6712 bytes, sha256 `1AED534F9E19B18B5451EA50E2403CB064BB06288BCAB46978E5EB0907832D47`)
- `external_validation/precollection_freeze_receipt.json` (operator_facing_input, 28005 bytes, sha256 `C0E805F70F38D08243A011764E42F786B9E7DB4A00B8F72E68A18B7E6E771794`)
- `external_validation/precollection_freeze_receipt.md` (operator_facing_input, 9558 bytes, sha256 `FF4F1C41AEDDEE1D61399EA8CDE981D9947E86DEAEAF3AE3AEA9908102D1D35D`)
- `external_validation/reference_adapter_report.md` (operator_facing_input, 3098 bytes, sha256 `F64B68656335697769F9E7E60F19D974CF5D36D118D94B1296A7368CF49F4C2C`)
- `external_validation/render_host_qualification_brief.md` (operator_facing_input, 6332 bytes, sha256 `5F3317883345DE601B48E0B729077EF1EF4F74D73082200AB83E18EA1BAC38D5`)
- `external_validation/render_machine_qualification_packet.md` (operator_facing_input, 5074 bytes, sha256 `28E676EC5C5BCE5FC05C3A314CD431472AEEBCBDFE3A098D59483DA7B044B201`)
- `external_validation/render_resource_sweep_work_orders.csv` (operator_facing_input, 1467 bytes, sha256 `E14EF76A1BB322CCC7B48AADBA04121672C44714D2D3B466C046A053497370AC`)
- `external_validation/rollout_evidence_packet.json` (operator_facing_input, 13937 bytes, sha256 `90E5146448F7D9CFAC24742E123DFBA91A6F00A1B3C4937D54B10E28FFA03E79`)
- `external_validation/rollout_evidence_packet.md` (operator_facing_input, 4898 bytes, sha256 `A22D860C7AC83F885D68926F1CFD976F2E8D747BFAC1D6A433AE7817B1220CC2`)
- `external_validation/rollout_evidence_work_orders.csv` (operator_facing_input, 4811 bytes, sha256 `7EE1DB977ABE2C371E0892342BCE0589582E9FDE47AA8E101F32AB9DB4245125`)
- `external_validation/runner/README.md` (operator_facing_input, 4725 bytes, sha256 `B6C32EF7B58465B2EC16C17CB4731589017095E81582225747957F4EF2F9AC5F`)
- `external_validation/runner/backend_contract.py` (operator_facing_input, 3269 bytes, sha256 `724802B452269859B9F9686942CC9788A078B907EDD32EC9C857CF5A1427801A`)
- `external_validation/runner/backend_templates/__init__.py` (runner_backend_template, 81 bytes, sha256 `B0A9A94890CA8216D679695638C5C96A92303895686FCB56C8FC8B09239C9723`)
- `external_validation/runner/backend_templates/isaac_backend.py` (runner_backend_template, 296 bytes, sha256 `7E6DE08F8DBE31D379E03E8FB5233BABE98BE8C649D1FC2D46CDE711E50E40AE`)
- `external_validation/runner/backend_templates/maniskill_backend.py` (runner_backend_template, 299 bytes, sha256 `57C8C99918AF4480A1ABF1118B5FF38F738E0CAFF23B36D8376F40B18A4FC9FD`)
- `external_validation/runner/backend_templates/mujoco_robosuite_backend.py` (runner_backend_template, 299 bytes, sha256 `B67540FF5DF2ABB57CAAF30F6C58960E874CA82D13990899F8FF34892B5B7253`)
- `external_validation/runner/backend_templates/robot_lab_backend.py` (runner_backend_template, 304 bytes, sha256 `EE4971A48430683585DC4CA899A9C3BECA7659A70710F4E5E3A9439F1ED6EFB9`)
- `external_validation/runner/maniskill_reference_backend.py` (operator_facing_input, 24292 bytes, sha256 `B02E244CF41FBABA7CC1382CED8B2F9701E015E7D1E9679805A006694355783F`)
- `external_validation/runner/real_collection_runner.py` (operator_facing_input, 29149 bytes, sha256 `3C35D3CDC8EF3A54E518242D371BF95E5C554BC656DA536D7DD01B0040CAB133`)
- `external_validation/statistical_analysis_plan.json` (operator_facing_input, 7101 bytes, sha256 `CADC94E4F3A6A3898B99151C79BD437EB8D997A9F488BD673D205A70420CD65E`)
- `external_validation/statistical_analysis_plan.md` (operator_facing_input, 2933 bytes, sha256 `D90A4A0735E78DE60A2DA21043B32AB7717BDF14EF3AF7619837C9037CC16E90`)
- `external_validation/task_cards/cable_route_insert.md` (task_card, 1388 bytes, sha256 `566488FB9C2DA53C06ED1A3E0CF4D1196D2504E841C97C470268F7AFFCAB034B`)
- `external_validation/task_cards/door_open_navigation.md` (task_card, 1391 bytes, sha256 `EDA0E523C3BF62F5215E18D3E782427F24FC316912221F2338719D98D5BF721E`)
- `external_validation/task_cards/drawer_to_pick_transfer.md` (task_card, 1377 bytes, sha256 `0C335887FC667DB914B0C95B05B3C4EAFEFAE1A01D99195E8DBF39FFD4A302FC`)
- `external_validation/task_cards/peg_place_regrasp.md` (task_card, 1372 bytes, sha256 `357F6A44637AD1D55E6E98775B60640FE0E7C0A32FE0C1707FC5863C00D3CDB9`)
- `requirements.txt` (operator_facing_input, 89 bytes, sha256 `A2D11E893CA2585FFC7D208B887FADAD3D48F376565BD9A6E662FC968F3BF028`)
- `results/external_ablation_collection_audit.json` (generated_non_evidence_report, 15552 bytes, sha256 `586E5A58D35A79EAB496934C9FD2C09421B364CAC09F05C722FD0552A841A885`)
- `results/external_ablation_collection_audit.md` (generated_non_evidence_report, 4221 bytes, sha256 `CE3703F13541AAFB56EA072107D224E585DBFCB3025B97C9940A6DCEA536D545`)
- `results/external_ablation_collection_packet_self_test.json` (generated_non_evidence_report, 5078 bytes, sha256 `30FD2E9624834B38B24343B2D547964CC878043FE15AF38F42005731CFC23952`)
- `results/external_ablation_collection_packet_self_test.md` (generated_non_evidence_report, 3402 bytes, sha256 `CA4711AC594E3A04C9B8C93E026C2B747DA1E8439CB4C481436B479D97A198B8`)
- `results/external_acquisition_packet.json` (generated_non_evidence_report, 59304 bytes, sha256 `81C138917A4CEE3F39BFB429448056DA14E22CDA8E390C65C12FA0141F428C85`)
- `results/external_acquisition_packet.md` (generated_non_evidence_report, 36129 bytes, sha256 `6B2BDBDBD25C74F1C770D743573543D5E99E6D2EB3ADB1A77013213BF8205FF9`)
- `results/external_adapter_contract_audit.json` (generated_non_evidence_report, 3130 bytes, sha256 `D61D6618070F133A1D7CC78921B0EDB9AF0EA4B8ED530745BAC9E5EC0BA2EC26`)
- `results/external_adapter_contract_audit.md` (generated_non_evidence_report, 2201 bytes, sha256 `428CC91812FBF6316521F5C531D9569AB48B04B2ACF26CDE37FDE9B588BE760B`)
- `results/external_adapter_scaffold_audit.json` (generated_non_evidence_report, 6541 bytes, sha256 `92A41EBF2DEE4066D5D294C8420492D6E4B934A1F1B601AD4CB8F90390AC2C4A`)
- `results/external_adapter_scaffold_audit.md` (generated_non_evidence_report, 2987 bytes, sha256 `F7F2A7E3738A610C9B878A36280BC507EC26D972DC0D0EDC01F77D2107681DC0`)
- `results/external_analysis_plan_audit.json` (generated_non_evidence_report, 3710 bytes, sha256 `982BBF2F8E794FD9E9658B5D07E8155A4D02381599E331439EEDAD49354F7DF0`)
- `results/external_analysis_plan_audit.md` (generated_non_evidence_report, 3080 bytes, sha256 `78AEEC8E8117DEC437F26D338B15857BD30522C4294ED4864ECAC7DD561660CE`)
- `results/external_backend_contract_audit.json` (generated_non_evidence_report, 2747 bytes, sha256 `1FBD0B682B1767D97988FEDA2D3192ECBA78D27E5760A90FDDC8D38B7C268876`)
- `results/external_backend_contract_audit.md` (generated_non_evidence_report, 2159 bytes, sha256 `F92AE6D33D05582267F4D1F11D0886F6510B396E98A96C38C082043A8315601B`)
- `results/external_backend_integration_audit.json` (generated_non_evidence_report, 4354 bytes, sha256 `A0AFAB8C887092622ADAC984227E23D20AB746326B17B53FD0D717CF962406A3`)
- `results/external_backend_integration_audit.md` (generated_non_evidence_report, 3585 bytes, sha256 `9EAE89FC0CF94F5859C38DB24CEBBCE3711BE4DF394E8C52ACA7AF8A9B349D1B`)
- `results/external_backend_integration_packet_self_test.json` (generated_non_evidence_report, 3369 bytes, sha256 `13F2077240B1D60A8FC77FC21F94D16AA02BBD1B1E18CC0075FFB2F46AF610E6`)
- `results/external_backend_integration_packet_self_test.md` (generated_non_evidence_report, 2273 bytes, sha256 `8BA73C4D2C4BA100D1F9B9E89C5016449F1C0F74A72C6444475DC7D508CA42D7`)
- `results/external_baseline_contract_audit.json` (generated_non_evidence_report, 5745 bytes, sha256 `03A42F96435C226D0998FA49344CD1A71905676B4722B217691393D63AF93A75`)
- `results/external_baseline_contract_audit.md` (generated_non_evidence_report, 2697 bytes, sha256 `7A12C9AE1BF7BC6938F7E749F95EB648F436B9A4E5A8F1E6EA1F7A251CE17616`)
- `results/external_baseline_contract_self_test.json` (generated_non_evidence_report, 4570 bytes, sha256 `1419CF2E5B627110688F2783D557121605367E74D8A53B54F61577203B1464AC`)
- `results/external_baseline_contract_self_test.md` (generated_non_evidence_report, 2053 bytes, sha256 `B76525DE32F07A4CC50E30A93D62CACED393059BB7C02B2514E367E870AA16D1`)
- `results/external_blind_eval_audit.json` (generated_non_evidence_report, 1972 bytes, sha256 `BC754C10B0E0FBDAD9EEB57371302F4199EEBE49894149CA4C58405357A638BF`)
- `results/external_blind_eval_audit.md` (generated_non_evidence_report, 1183 bytes, sha256 `9EC804D278A6BEBB749B193C799210EEC6894349742C2D4363E877BF8D4A5B96`)
- `results/external_collection_job_packet_audit.json` (generated_non_evidence_report, 18290 bytes, sha256 `6E836E64823A73ACD851E0B1D3773CA46BE81B41A7D97B5E38614886676A8108`)
- `results/external_collection_job_packet_audit.md` (generated_non_evidence_report, 14844 bytes, sha256 `374C5D80DF23014DA6CBB002F5572D7CC6C1BBD33B6745F4663F527D0F62CA69`)
- `results/external_collection_machine_bootstrap_audit.json` (generated_non_evidence_report, 5966 bytes, sha256 `042037EF9223C6555FF9515D4D51112CFE550111444FAB4EF126FCCC593DE8BF`)
- `results/external_collection_machine_bootstrap_audit.md` (generated_non_evidence_report, 3918 bytes, sha256 `1CB439E9F005B4FA17FD46288CFC168DAC16165E38D3BC6E5B62AEC3C48FFAB0`)
- `results/external_collection_plan.json` (generated_non_evidence_report, 147907 bytes, sha256 `499A6C1E503727DAEEBF2F22BDE5EDB9E89A5D58A47071AF4E6685D283D2ECEC`)
- `results/external_collection_plan.md` (generated_non_evidence_report, 6287 bytes, sha256 `0C336204F3A25C6A9385F4B4349488BC99550F57317F8C6F22AF6BB14785EE6F`)
- `results/external_collection_readiness_audit.json` (generated_non_evidence_report, 8125 bytes, sha256 `8AC215A38BD0E7BBF44A20C547A4ED43CDD76960DCE679ADAF46B24D8C02422E`)
- `results/external_collection_readiness_audit.md` (generated_non_evidence_report, 4059 bytes, sha256 `E74D7C135F7D1377312C89D53C695C5D85E7FC134FB9B08634DFA900DEA9B08D`)
- `results/external_config_manifest_audit.json` (generated_non_evidence_report, 3589 bytes, sha256 `A46DED8E5FF2E9E9FAB155569F9FA4FD8FDA633E062962180781B9DCB360D972`)
- `results/external_config_manifest_audit.md` (generated_non_evidence_report, 2890 bytes, sha256 `F2F65F83DD6EA9A14BBCFDFC21604551D29ACA5BB6BC34B0465D388F1C88E3F7`)
- `results/external_config_manifest_packet_self_test.json` (generated_non_evidence_report, 3256 bytes, sha256 `04E797AA2F169E04EB87B50103039B07751A2A974A40BD339EA163BE04E67FFF`)
- `results/external_config_manifest_packet_self_test.md` (generated_non_evidence_report, 2197 bytes, sha256 `89DF86C6957A00FBE63D622B7C2557113B5B1315C58A8E0C16CFE602C93A7DF4`)
- `results/external_config_materialization_plan.json` (generated_non_evidence_report, 3186 bytes, sha256 `EB1436D71B2E51AA6117679956D4563284DB846A7A0C62E41AE2B4EFE0B02E5F`)
- `results/external_config_materialization_plan.md` (generated_non_evidence_report, 1976 bytes, sha256 `2C7F8786129C013277B149D934B1FD8CD964C03E88D7E5856DB5EDEEA5CFA6EC`)
- `results/external_config_materialization_self_test.json` (generated_non_evidence_report, 1694 bytes, sha256 `8E431465B676772A1E9811A5A8995137852D1D9787297133B7F8CA7C5E407E38`)
- `results/external_config_materialization_self_test.md` (generated_non_evidence_report, 1583 bytes, sha256 `68F0715870671EE91325D86E2CCDDD4004EC4BD7258B2F31A2F5A6EB6A57AEED`)
- `results/external_config_template_audit.json` (generated_non_evidence_report, 1418 bytes, sha256 `364A4CEA5B063E5EA45A639D52E9EEE7628941F2722496D6A2E47CE787CA2106`)
- `results/external_config_template_audit.md` (generated_non_evidence_report, 797 bytes, sha256 `4CC337580323BADB03441EE8478DDDEF19CC9857F1B0B032264B78DB6A947DF7`)
- `results/external_evidence_closure_brief.json` (generated_non_evidence_report, 14730 bytes, sha256 `32F1C65535FBDDD5561B851836268EC9E15D2ECCF7FC10617CF4C0F25DD881A3`)
- `results/external_evidence_closure_brief.md` (generated_non_evidence_report, 11318 bytes, sha256 `7A284EC84C024910358918C31EFBF71D21B42FBF5C8E572CF35634802304CFAA`)
- `results/external_evidence_closure_brief_self_test.json` (generated_non_evidence_report, 1900 bytes, sha256 `B1F71ABFFDA61CA54AC32090175E432215AF5BCEF7AF9FB0FEC3CDF59971B66C`)
- `results/external_evidence_closure_brief_self_test.md` (generated_non_evidence_report, 1695 bytes, sha256 `F91532B6AA1FCE8411F78942F739AA7380CBBB18666020EA91DAF95D2EA9FD3F`)
- `results/external_evidence_intake_ledger_audit.json` (generated_non_evidence_report, 43816 bytes, sha256 `BA2A6A50BCFB44FDF7531CF71BCBEBB68D3E9B3D8851F75BB5F11CED1F8D24D9`)
- `results/external_evidence_intake_ledger_audit.md` (generated_non_evidence_report, 11214 bytes, sha256 `8E8E11E9AA7A949FC3C34FE40B5F64D960178E8285C1D794415CFDF44BAB0F87`)
- `results/external_evidence_intake_ledger_self_test.json` (generated_non_evidence_report, 4918 bytes, sha256 `8D7BE9FD0DC01C342310C05204C5CE6E7CE9D80438EE3AA3A15EB009A8C35A65`)
- `results/external_evidence_intake_ledger_self_test.md` (generated_non_evidence_report, 3208 bytes, sha256 `FBF43341203E6E22F7242738679E687E6A670393FE620D9746609DB397D67F3A`)
- `results/external_evidence_preflight.json` (generated_non_evidence_report, 12344 bytes, sha256 `D163EA7B1E6DC2EFBBF26DC10C324A5CB76CD216BEB969C316D5A994F8DCE0B1`)
- `results/external_evidence_preflight.md` (generated_non_evidence_report, 4745 bytes, sha256 `B68911C22003E7E03E48D7486AB58F53AD10457F0C25ABCD47A134E37A247892`)
- `results/external_evidence_preflight_self_test.json` (generated_non_evidence_report, 1979 bytes, sha256 `C3C990BFBEAE0869391A438CBAAA21E703B1D19B6B2A4476A0ED09F0B620159E`)
- `results/external_evidence_preflight_self_test.md` (generated_non_evidence_report, 1935 bytes, sha256 `56651DAF3A7D8D04D58F11CB96CF9CC12F6ABCA1D385952B74A24A7DDF302EC6`)
- `results/external_execution_readiness_audit.json` (generated_non_evidence_report, 44265 bytes, sha256 `B496CEF5B6A4347D6FC9EAAA18A198175E07CCBCBC6C577DA33A7499536249F8`)
- `results/external_execution_readiness_audit.md` (generated_non_evidence_report, 34373 bytes, sha256 `97B0197A422E572EB49622BB1EA1C62831FB240146E22A5CA625FDD8FDFD92B6`)
- `results/external_execution_readiness_self_test.json` (generated_non_evidence_report, 2457 bytes, sha256 `660E0EB6AE6FDE0B4DF88E4C4BD0FDA28057A7EFBFBFE08B41023D7229A2739A`)
- `results/external_execution_readiness_self_test.md` (generated_non_evidence_report, 2324 bytes, sha256 `EF8EEDD6D7F4D7941BF0FFD7C73D0968165DFEC82BDD51466F69392082D41DCC`)
- `results/external_fidelity_acceptance_audit.json` (generated_non_evidence_report, 9807 bytes, sha256 `23846A8DFE65737A9EFB04A4231D05ADE15749DAED64DE6AFE5F466F941AA3C5`)
- `results/external_fidelity_acceptance_audit.md` (generated_non_evidence_report, 7443 bytes, sha256 `8C45FD1ACECFF00BB09050A896BD4D0086F90D7DB70D0C40C6AF2F00EC45363A`)
- `results/external_fidelity_acceptance_draft_audit.json` (generated_non_evidence_report, 6143 bytes, sha256 `B3D9C76BD4CDB5250AEF88ED012D785A3C76BE8DB68F5F250D4FA810302D433C`)
- `results/external_fidelity_acceptance_draft_audit.md` (generated_non_evidence_report, 5016 bytes, sha256 `FEDF26B27936C9DCE973F36254D8F400EFBDA0A20BEAF1DB53BC3FA4AFC296E9`)
- `results/external_fidelity_provenance_audit.json` (generated_non_evidence_report, 3921 bytes, sha256 `16A8CE8CA3AAD52C12CD463D99C2F6E6FDB95F92C1F89EF30E38BABA114BC7CC`)
- `results/external_fidelity_provenance_audit.md` (generated_non_evidence_report, 3043 bytes, sha256 `51D23B1B9CCC2C39901B11EEF4DB9F5308AB9C4688AF24E70DDAE187EB2EF319`)
- `results/external_fidelity_provenance_packet_self_test.json` (generated_non_evidence_report, 3398 bytes, sha256 `2D19AAB6627C06621C59F4E2CD67072E0D1A2F601310E6F9D48CDD59C4047877`)
- `results/external_fidelity_provenance_packet_self_test.md` (generated_non_evidence_report, 2200 bytes, sha256 `9D507B4F91F90FB796DBB3898508F3424D77CD1C1DD2EA6FEC30219D9ECB6DF7`)
- `results/external_manifest_builder_self_test.json` (generated_non_evidence_report, 2674 bytes, sha256 `30008478A73C62389E341A6D9F839DBDE2B2EC5807173E949646F1CB861909E8`)
- `results/external_manifest_builder_self_test.md` (generated_non_evidence_report, 2348 bytes, sha256 `83CC75004A0B4C959D91B489A9809CEA43D95D4E81376D5D3C93C4819710D54E`)
- `results/external_method_config_materialization_audit.json` (generated_non_evidence_report, 33567 bytes, sha256 `9AD446480FF0179BFD791DEFB24203C4DEDA83D33D29D69A3FB525452372007E`)
- `results/external_method_config_materialization_audit.md` (generated_non_evidence_report, 3651 bytes, sha256 `ABEA5CABFD6ACE447CBB141086C8AC658EF0D8209806091F06B85C4B2E209200`)
- `results/external_method_config_materialization_self_test.json` (generated_non_evidence_report, 2716 bytes, sha256 `3B35F48F01469C1A440B86E29272E48A143BDD34F65B0295043E6DB944276B99`)
- `results/external_method_config_materialization_self_test.md` (generated_non_evidence_report, 2279 bytes, sha256 `B8F77E791ED07E609465D7D43248FAF1F1EA765DB5D7DD26CFD222D36D085A51`)
- `results/external_method_implementation_audit.json` (generated_non_evidence_report, 6510 bytes, sha256 `F8AA15870753DC4E6B4F681ACEF956A4C49ADAF3A12A98C32091582474021FAC`)
- `results/external_method_implementation_audit.md` (generated_non_evidence_report, 4783 bytes, sha256 `8A318351DC5AA27C081AB65BE30E28AA60115DA7B416076CEE74B5892754C313`)
- `results/external_method_implementation_packet_self_test.json` (generated_non_evidence_report, 3571 bytes, sha256 `8211193F5044C041B9464E60EA9691268A25B501BF26010E33B1B5EAD93AD189`)
- `results/external_method_implementation_packet_self_test.md` (generated_non_evidence_report, 1906 bytes, sha256 `292524B8333A2755E2314324E3201A64F8AA2FA584E5EEFFF37262B2442C064D`)
- `results/external_operator_packet.json` (generated_non_evidence_report, 60708 bytes, sha256 `447311F26752746D5B73E9454ADA8B6B1B5E8F08AEE84B7663A0F51B3EFCC1DD`)
- `results/external_operator_packet.md` (generated_non_evidence_report, 29123 bytes, sha256 `4E0DC50F472891D2559A7B23EA8885747E459AFEFC55FA108403043F44B1B7C6`)
- `results/external_pairing_integrity_audit.json` (generated_non_evidence_report, 525 bytes, sha256 `D4ABAA9C2083D8B5932139DFEE0B1D79B4C7C97ACB9088C2E55245B26F624148`)
- `results/external_pairing_integrity_audit.md` (generated_non_evidence_report, 693 bytes, sha256 `4AD20017AC4F06A5B63E1D5CA3001F8EE9E7159739C99633C567109F1B37D7AD`)
- `results/external_pilot_smoke_audit.json` (generated_non_evidence_report, 1878 bytes, sha256 `6CFA9CB9774A330AD5F161218DE856240F13969CD36E6E5FDFCA80EBE4E9AF36`)
- `results/external_pilot_smoke_audit.md` (generated_non_evidence_report, 1203 bytes, sha256 `1DFC88D3CC0406275C0EAFA6FF5EADB8683515CF9D312C5DEADD4285688951CA`)
- `results/external_pilot_smoke_packet_audit.json` (generated_non_evidence_report, 3212 bytes, sha256 `8FA86BDA60C07FDDEE20AD497081DC299100302A15E751A3BEBBEEA15365C331`)
- `results/external_pilot_smoke_packet_audit.md` (generated_non_evidence_report, 1790 bytes, sha256 `684869BB5A12AB93D254C35B90856DEAD3BC8CA512ACC68DEF4D78F2CAFE39DA`)
- `results/external_platform_onboarding_audit.json` (generated_non_evidence_report, 8651 bytes, sha256 `589D10B28568271935FC5641332088E66F56C15651725030EA680C65064AC45D`)
- `results/external_platform_onboarding_audit.md` (generated_non_evidence_report, 6712 bytes, sha256 `17CB000711FF8B08691DB0455B5C5CFF0592B474CCF99F2BD1B07C49A067C6D3`)
- `results/external_platform_probe.json` (generated_non_evidence_report, 13741 bytes, sha256 `F6111A1F07E29BCD17EE532F09F147D0D8707E28D153200AF1997675B3804CA5`)
- `results/external_platform_probe.md` (generated_non_evidence_report, 2287 bytes, sha256 `3ED7CB9D15B83408733665AC1B46492F1EABD342A8A59E61D754B2E56E0ADBA4`)
- `results/external_postcollection_evidence_seal_audit.json` (generated_non_evidence_report, 8720 bytes, sha256 `D0F4D0ED189B831F0477CC0D61FA7A7E3C541B711852B25FCD12CA7FD721CFA7`)
- `results/external_postcollection_evidence_seal_audit.md` (generated_non_evidence_report, 6001 bytes, sha256 `23960959EF57EB7619E71EAABB078911B95D04D172C6D8A70F74537D666F526A`)
- `results/external_postcollection_seal_consistency_audit.json` (generated_non_evidence_report, 7173 bytes, sha256 `91D1C2818F2F135D642077A778C1DDA98565224068060732B86D08A998C99789`)
- `results/external_postcollection_seal_consistency_audit.md` (generated_non_evidence_report, 6445 bytes, sha256 `6168B8A8BAFE5B0A81E1FB6B96B7AB9907C987D9AA74C66F8BDDADD5090B6DE2`)
- `results/external_precollection_freeze_receipt_audit.json` (generated_non_evidence_report, 19940 bytes, sha256 `F7608495670BF7E6D7ED0E655853FA47059769549E725C98C35F9F1374E71BF4`)
- `results/external_precollection_freeze_receipt_audit.md` (generated_non_evidence_report, 8705 bytes, sha256 `34A78964169DF1A23241324E7B6996D5F57A1376B834DBC92352049CBB70C70F`)
- `results/external_precollection_manifest_draft_audit.json` (generated_non_evidence_report, 6588 bytes, sha256 `5EA5219C264B754DCDEB65B3DC107C99FCF834E6909BF707082ABCB537A548BF`)
- `results/external_precollection_manifest_draft_audit.md` (generated_non_evidence_report, 2674 bytes, sha256 `04D1E0D920D763EAABCBF93FD3378BA2B261C7DCEF43EE0E6E2125C6B5CD89E5`)
- `results/external_precollection_manifest_draft_self_test.json` (generated_non_evidence_report, 3385 bytes, sha256 `D530D2B631D268DE928F1389E2FBF257C7440896C4B7E7AE00E8839ADB0FDBCA`)
- `results/external_precollection_manifest_draft_self_test.md` (generated_non_evidence_report, 3130 bytes, sha256 `10577AC2610322792005A9A18278EAA1280448FE0B5EDE7D28F5CB5903F8AA0E`)
- `results/external_reference_adapter_audit.json` (generated_non_evidence_report, 7424 bytes, sha256 `2E182A83556263635731AD6969E2976D0138B18056B562E9DF8E1AE2D6E0CB52`)
- `results/external_reference_adapter_audit.md` (generated_non_evidence_report, 2402 bytes, sha256 `E3B1EF1B04EDC6635605B205E7AE4AADACED64241281A5FCA1F12A26550DE0D6`)
- `results/external_release_package_audit.json` (generated_non_evidence_report, 490 bytes, sha256 `D760B589BD12AA51882D2C99B501475A6103FCABAFCF86A6E1744F9235E91278`)
- `results/external_release_package_audit.md` (generated_non_evidence_report, 606 bytes, sha256 `891E153CCAF9A412318D6D224EE16156CD16222A56CE143662337D4B08BE8751`)
- `results/external_rollout_evidence_audit.json` (generated_non_evidence_report, 3681 bytes, sha256 `46E851EEDF315D592F1DF5BFF09FEE9FB328CF47E9B7E7511B5E9A2AC976B03A`)
- `results/external_rollout_evidence_audit.md` (generated_non_evidence_report, 2864 bytes, sha256 `4B1F04F3BE6024753737B613769EA2DD15F1AEC7172F028555456A9598D91800`)
- `results/external_rollout_evidence_packet_self_test.json` (generated_non_evidence_report, 2713 bytes, sha256 `5284BF4024EEC09653DDCB8F33992BBE71EBCDD21181CBBBFBCBB3AD4588F3F4`)
- `results/external_rollout_evidence_packet_self_test.md` (generated_non_evidence_report, 1822 bytes, sha256 `13BC71E7E3312394418F2B85E5D298302CAB539442183A2547CE3AC8923A43D7`)
- `results/external_runbook_audit.json` (generated_non_evidence_report, 4028 bytes, sha256 `43902C49CC5F56F717A42A6F52E0F28926C98EC512F85DCF30172B5E4C0E7DE8`)
- `results/external_runbook_audit.md` (generated_non_evidence_report, 2232 bytes, sha256 `8C7754CC5E121EF88D0240010A2A595B64E78819E757BE237D8024F353AA814C`)
- `results/external_runner_harness_audit.json` (generated_non_evidence_report, 3277 bytes, sha256 `9221FD3F3334D182AAE1F5C3C19947EEB342C6A0EE2E331EE43ABC4DEC036270`)
- `results/external_runner_harness_audit.md` (generated_non_evidence_report, 2291 bytes, sha256 `1920465D2991DE966CBEFF7C2C4C708A197B801F4FDB08435E18D4EC009D2B7A`)
- `results/fidelity_acceptance_materialization_plan.json` (generated_non_evidence_report, 7902 bytes, sha256 `DB2A03DA3C14C49B566E716B3A3C00055B5E990CCE1ED04171C30C5FDCCFFFEE`)
- `results/fidelity_acceptance_materialization_plan.md` (generated_non_evidence_report, 5837 bytes, sha256 `572A7B01E90B901065142A09BBE2416E0F1E190463D0F96CA208E8536BA5078E`)
- `results/independent_validation_launch_ticket_audit.json` (generated_non_evidence_report, 4670 bytes, sha256 `BC8AFAEB693AD1D1B2C3A520053615BB43139D9C8D3EA13F053303FC9866E6BA`)
- `results/independent_validation_launch_ticket_audit.md` (generated_non_evidence_report, 2413 bytes, sha256 `6E5B8C07E9A73CDBBF50589791820C361CCB285CAB30AC76B6E1CAEC7F41E7B9`)
- `results/independent_validation_route_audit.json` (generated_non_evidence_report, 8182 bytes, sha256 `279F757785C1226CADD5CB50240E20114859261FAEA0882F81BD594132F453F9`)
- `results/independent_validation_route_audit.md` (generated_non_evidence_report, 1807 bytes, sha256 `81BC82F771937391FE904EE175EAAE85AE78080C5866D5874092E8AD822C5CE1`)
- `results/maniskill_backend_readiness_audit.json` (generated_non_evidence_report, 4908 bytes, sha256 `8C18BCEF67ABC8AB243E2CB9FA7DE1E3FC730B43B11D22EEDF2905502BE3DC6E`)
- `results/maniskill_backend_readiness_audit.md` (generated_non_evidence_report, 3057 bytes, sha256 `E61161970286DA1A3EA5F8662624350E924C548EF244BCA17CCBAB0B93CC73E4`)
- `results/maniskill_env_smoke_probe.json` (generated_non_evidence_report, 13635 bytes, sha256 `3A13C3BFB4F4CE7369E0D2B6D8B01C7ED4C57BD3DC1E34E36104B6589D59C860`)
- `results/maniskill_env_smoke_probe.md` (generated_non_evidence_report, 2044 bytes, sha256 `7DE60A2FA9A7C2C2F73FD7D1021B4DB9AC0D676495EB99D482AA38C61BD97DAD`)
- `results/maniskill_fidelity_metadata_probe.json` (generated_non_evidence_report, 29603 bytes, sha256 `2D453A436E2135437D9529045DC04E0E3DF7357FB6AB45DAE004C549AFA51F1F`)
- `results/maniskill_fidelity_metadata_probe.md` (generated_non_evidence_report, 3182 bytes, sha256 `94FE873908607EE198278AF04CDCEA4087E4288AB033761D809F65F30CED7DCD`)
- `results/maniskill_pilot_runtime_liveness_audit.json` (generated_non_evidence_report, 20132 bytes, sha256 `00050B6188681B0FBE8C862136137B40ED2B1F55FE8093397E6ADF6D45BB27E0`)
- `results/maniskill_pilot_runtime_liveness_audit.md` (generated_non_evidence_report, 10288 bytes, sha256 `6B14A2B093412999111FDA3EF21EF309EEF495254F723C269FD5761EA1EE6F1C`)
- `results/maniskill_reference_collection_preflight_audit.json` (generated_non_evidence_report, 4062 bytes, sha256 `327EE4D89B2EA6C6F5609818DE533465BB53693FD4D3A502EDB0CEC3EB9F5F06`)
- `results/maniskill_reference_collection_preflight_audit.md` (generated_non_evidence_report, 1325 bytes, sha256 `28691987D608EA40FA50EBD7BCA64E7240E5583DCEDFC72E729829EDDF35F942`)
- `results/maniskill_render_host_qualification_brief_audit.json` (generated_non_evidence_report, 9280 bytes, sha256 `ED41481A03FD36038C1EE5D0E3C89D5CF9272A379220B6CE4779CBCAC512EE8C`)
- `results/maniskill_render_host_qualification_brief_audit.md` (generated_non_evidence_report, 2393 bytes, sha256 `DFA02A29866AF98452E84D720B5A270F9997FD11F150119BE7FF494AA5C7E1AC`)
- `results/maniskill_render_machine_qualification.json` (generated_non_evidence_report, 5426 bytes, sha256 `6C63AC79D94BFC129C68F78C335120CA7A621B44BAEA49889258C3BB12777AAD`)
- `results/maniskill_render_machine_qualification.md` (generated_non_evidence_report, 5074 bytes, sha256 `28E676EC5C5BCE5FC05C3A314CD431472AEEBCBDFE3A098D59483DA7B044B201`)
- `results/maniskill_render_resource_sweep.json` (generated_non_evidence_report, 26710 bytes, sha256 `CDC41DA58A92614DF81D438A43885B6041582B3F822AD660BA5C6BA64468D048`)
- `results/maniskill_render_resource_sweep.md` (generated_non_evidence_report, 3674 bytes, sha256 `5BDE7CFD292DB6D1D54E8720F5BA869DDAF599C203F13FF5BACD04094B47F4CE`)
- `results/maniskill_render_video_preflight_audit.json` (generated_non_evidence_report, 60381 bytes, sha256 `3AD488236C55C898D167A56CC79176B03DC1072A167B5A80C583ADD72384FE03`)
- `results/maniskill_render_video_preflight_audit.md` (generated_non_evidence_report, 7606 bytes, sha256 `726C3C6F1798EFB19AC31D27D8668612046F9BACBCA9549EBC22C350E7F07625`)
- `results/maniskill_task_binding_probe.json` (generated_non_evidence_report, 9710 bytes, sha256 `8B2BADB696E8A8E5FC9E867EC6D11A9DB89F8D1017CEA54E1B6AA3086DCD3C17`)
- `results/maniskill_task_binding_probe.md` (generated_non_evidence_report, 1844 bytes, sha256 `8F529132821A124537E0C2DBD170E5865F8E8E4426124A82F310D83BF5B1E6AD`)
- `scripts/audit_external_backend_contract.py` (operator_command_source, 15394 bytes, sha256 `6A2A65A7AA73B04C438AFF9B85115589397D8DDF3496A93632E7A178D7230E4C`)
- `scripts/audit_external_collection_readiness.py` (operator_command_source, 21878 bytes, sha256 `748684CAD3D389F6A7971E1EB686FF6D1F3751E003B6E94391C3D6222C59A1F7`)
- `scripts/audit_external_evidence.py` (operator_command_source, 29377 bytes, sha256 `45D90F489F1908BBAD5CADC23BF40091BA8F48145AD85D4307D60EEFCBB9C8BD`)
- `scripts/audit_external_fidelity_acceptance.py` (operator_command_source, 22854 bytes, sha256 `6BED3E4B7519761F200328AF4672DCC1BF665FC6BC4E993B6CC69A744FE4C9E3`)
- `scripts/audit_external_pairing_integrity.py` (operator_command_source, 13495 bytes, sha256 `237BF15844DA317A1B86A64312986A583D3A27987DB075537F6B44B8A014C0DB`)
- `scripts/audit_external_pilot_smoke.py` (operator_command_source, 10042 bytes, sha256 `13BB2E31C5E8331D1C53B5E060E399FEB83C520FC83AF91FA350FC591D417C25`)
- `scripts/audit_external_postcollection_seal_consistency.py` (operator_command_source, 18353 bytes, sha256 `9FF4097A5E16801B827C02CF780436754D2228F914A465FBA1B5B4C0D1B50BF9`)
- `scripts/audit_external_release_package.py` (operator_command_source, 10688 bytes, sha256 `58C5BD8059691A70B713B286DBCB3856957AA1C1670C8280C7D835095719B603`)
- `scripts/audit_maniskill_backend_readiness.py` (operator_command_source, 9758 bytes, sha256 `B7A7DF42D33DF948872B373A35423AF97B1AD2F1B2A0409B22A725116D8C9F0B`)
- `scripts/audit_maniskill_pilot_runtime_liveness.py` (operator_command_source, 42208 bytes, sha256 `8027DFE39132E74D2DA72ACD352C323E9D57FF6196D1FD7BA048A839308A4915`)
- `scripts/audit_maniskill_reference_collection_preflight.py` (operator_command_source, 8466 bytes, sha256 `A9B57E8629AF6556AF8BB31B0CD10081E1BA1BEC5FBB1178650CD587FDFFAD7B`)
- `scripts/audit_maniskill_render_resource_sweep.py` (operator_command_source, 13151 bytes, sha256 `18B611180395204F02858123DE3D999DE23F2127738552D4C36E59114CBC14E8`)
- `scripts/audit_maniskill_render_video_preflight.py` (operator_command_source, 34149 bytes, sha256 `8C1A9DC9ABD2322FB40AAA5970AB4B19ABBE5F978205D99C224A85A2AC3F9E8D`)
- `scripts/build_external_ablation_collection_packet.py` (operator_command_source, 18684 bytes, sha256 `B3607507835C3E394A0B10F2CA73BD3C110AD46449DC1B9F27E809CB39540FD4`)
- `scripts/build_external_acquisition_packet.py` (operator_command_source, 98463 bytes, sha256 `51D5892E36E02C0042F53C6C80A0AA5FA83A9A34AEE552B49DF7A28FADBF6BBF`)
- `scripts/build_external_analysis_plan.py` (operator_command_source, 18694 bytes, sha256 `27C516ABD36E7B7FF1B3F11E712E5C7E18FE7F6FCFA672090BF28AE67E078CA7`)
- `scripts/build_external_backend_integration_packet.py` (operator_command_source, 20959 bytes, sha256 `D4DEDBB66FDFE045078041987AE27C4105292AC60D22840623BD0233C197C57F`)
- `scripts/build_external_baseline_contract.py` (operator_command_source, 20272 bytes, sha256 `8A3B79C50463A4974D5EF4C1CCBA409F45030C4867E3694B0C0C65B6E7E78E98`)
- `scripts/build_external_collection_job_packet.py` (operator_command_source, 43915 bytes, sha256 `FAA9CFC76AB213E827CF603308E59C32E63849A006FDC40B8C586F700EF4C945`)
- `scripts/build_external_collection_machine_bootstrap.py` (operator_command_source, 19569 bytes, sha256 `285BACFF2821C2E6EABB453DE43406B36FEAA97AD2EF943782095B3D12C51569`)
- `scripts/build_external_config_manifest_packet.py` (operator_command_source, 21003 bytes, sha256 `2C52F840F30A0D6DE34F473952EEA0245C1B122E2FFF71BB6D652890F8095DD6`)
- `scripts/build_external_evidence_closure_brief.py` (operator_command_source, 23131 bytes, sha256 `7AEE21F03D0C5DD4D120432E4699BF79644CF54BEACEC0478F8F42DC061326D1`)
- `scripts/build_external_evidence_intake_ledger.py` (operator_command_source, 24156 bytes, sha256 `FF98BE0BEF8C649BA90C330D2559DDECDEF53EEE3FD1A35E539AFDC961AB718D`)
- `scripts/build_external_fidelity_acceptance_draft.py` (operator_command_source, 40461 bytes, sha256 `BA615558785FB0B4A660C2CDC68A1A7334542BEC3A85DDAC5304FC97D6227E5D`)
- `scripts/build_external_fidelity_provenance_packet.py` (operator_command_source, 23371 bytes, sha256 `992BABFC2F0B20DE876F2B66835DAB9863C8DED28E4DA075DE916A1BA8355736`)
- `scripts/build_external_manifest.py` (operator_command_source, 33515 bytes, sha256 `FA9F3890C25B2FEA0F484520C38270BDE202F02317734563983522F3237EA09D`)
- `scripts/build_external_method_implementation_packet.py` (operator_command_source, 57664 bytes, sha256 `C166221116A089779E0111AE13BDB75CC1625849486A1C116AF8534D264334AF`)
- `scripts/build_external_operator_handoff_bundle.py` (operator_command_source, 111508 bytes, sha256 `E608409F5706A8380327563CA7EDF0D3FE30334E4D62D9640DE3254B5463C1AF`)
- `scripts/build_external_operator_packet.py` (operator_command_source, 71405 bytes, sha256 `2A06BF8BADB9A1BFC340309980E1A0AA45A1410E30F9BEED69E524E6A12D6C6C`)
- `scripts/build_external_pilot_smoke_packet.py` (operator_command_source, 11266 bytes, sha256 `F3A2D24716D7DCE1D337453137191E821E1F81ADBAA8ABF446C2446E489C00CE`)
- `scripts/build_external_platform_onboarding.py` (operator_command_source, 32058 bytes, sha256 `87CB7C475846CFCE3849B835621097DA3362DC9EBE5411794EBF13C792941AB2`)
- `scripts/build_external_postcollection_evidence_seal.py` (operator_command_source, 22280 bytes, sha256 `B608377416DBF26842358294D7BC6CE239C3BF37571BD22EAF986788878087C9`)
- `scripts/build_external_precollection_freeze_receipt.py` (operator_command_source, 31882 bytes, sha256 `AD9EA284B5CD164BA39FA560F9CC748D9574E8A229F01F3BB50BB0FE18237803`)
- `scripts/build_external_precollection_manifest_draft.py` (operator_command_source, 30743 bytes, sha256 `633034AB414080287C0E767AA88F9CCA5179423B12EF39785D52C0F6CEF55E41`)
- `scripts/build_external_rollout_evidence_packet.py` (operator_command_source, 23096 bytes, sha256 `08C85AA06AA704107282CAF145AD000F5C76EC307B1B85B86341C529706A9575`)
- `scripts/build_independent_validation_launch_ticket.py` (operator_command_source, 23060 bytes, sha256 `74ACB83D792272DA6FA1BD3DA8EAE73F86B250B4FC65663C082B15EE3F05F1D1`)
- `scripts/build_maniskill_render_host_qualification_brief.py` (operator_command_source, 20727 bytes, sha256 `9035B44F0DBF6D8CB94D3B74E84BCAC4EE6F9A7AAE3F3335278E29D09C987B30`)
- `scripts/build_maniskill_render_machine_qualification.py` (operator_command_source, 25508 bytes, sha256 `4E289392972D00904159144AF20E7F70686D0981982F1838220313ACC4BF6D72`)
- `scripts/materialize_external_configs.py` (operator_command_source, 12746 bytes, sha256 `EA207DCFDCCC9593CBFEC993C22D3EDA8F493124D1EBEB6A240D793C4AC80A25`)
- `scripts/materialize_external_method_configs.py` (operator_command_source, 19093 bytes, sha256 `0F0150BE7B57C12F3B08EA6CC5E604301424BDBC44F1BE2752E2598FDB2A96C7`)
- `scripts/materialize_fidelity_acceptance.py` (operator_command_source, 23450 bytes, sha256 `63085D7ED6B71B37B5367F18E9154F273EF0774F81C5656BDF0806CC54D41C73`)
- `scripts/probe_external_platform.py` (operator_command_source, 14122 bytes, sha256 `67456EAE975E43F2D87B7233670D57D5E353C7034E2636E500BB3B38806C05DC`)
- `scripts/probe_maniskill_env_smoke.py` (operator_command_source, 18252 bytes, sha256 `CAD9777638492EDE99F187BCFF89E1CAE85024FE5FEE8D7374AFBFC2516D4F02`)
- `scripts/probe_maniskill_fidelity_metadata.py` (operator_command_source, 21099 bytes, sha256 `2EC0606C2AAF6E7C9B298B202748005D563BD47C5DDCC88F060A657B52DF88AB`)
- `scripts/probe_maniskill_task_bindings.py` (operator_command_source, 12426 bytes, sha256 `AC9A26FDA7512B17AD35589525DF3A41E7C5CF28C164850C4F835466C69D92E2`)
- `scripts/self_test_external_ablation_collection_packet.py` (operator_command_source, 19709 bytes, sha256 `1BB0221CB8543E546956C0374DB956BDE90D1224BAD59FCF008D9E4236C1B5C9`)
- `scripts/self_test_external_backend_integration_packet.py` (operator_command_source, 20717 bytes, sha256 `3F52D905E7F103EEE1A19972FB2CD28CDD7F43CBF15E1B010EF7C9B8D0886A58`)
- `scripts/self_test_external_baseline_contract.py` (operator_command_source, 17692 bytes, sha256 `B0BC8E8E4C7B31D6AF525613754940382A2B4CFC97D970C80C0BC7225AA478C1`)
- `scripts/self_test_external_config_manifest_packet.py` (operator_command_source, 20765 bytes, sha256 `63009129D2131F4A26021C481C4217B1B960720628FDDCDF59C8DE9E2123E47E`)
- `scripts/self_test_external_config_materialization.py` (operator_command_source, 16029 bytes, sha256 `DAA183552AEBFA55954764BB0040DD0C2F7EAFA38E8C6CAD5EE2A342C1B10893`)
- `scripts/self_test_external_evidence_closure_brief.py` (operator_command_source, 12399 bytes, sha256 `288677748D45A2F27FCB298B30D56C714DB2FFDD9903DB471E9630C4BED0FDFE`)
- `scripts/self_test_external_evidence_intake_ledger.py` (operator_command_source, 19856 bytes, sha256 `2F1D56BA3DF248BEB9E6AE5817DBBCBE8AA4879A8B4698CF41ECB38B4B3CB6CE`)
- `scripts/self_test_external_evidence_preflight.py` (operator_command_source, 17751 bytes, sha256 `347C396D9808A010989F9EF26CFAD4BBB6EC59397BEA94487810DE8E65F30E61`)
- `scripts/self_test_external_execution_readiness.py` (operator_command_source, 16911 bytes, sha256 `C5A772E2EE1BB1E4C9590A4B0C5DFBCEC048C4B9AF4097F5A34ECE685BB7E9F0`)
- `scripts/self_test_external_fidelity_provenance_packet.py` (operator_command_source, 20975 bytes, sha256 `C97A785DE5949F4C25576E10A938188CDEFF2306A1F6D5B0FFDEFFF595B34F41`)
- `scripts/self_test_external_manifest_builder.py` (operator_command_source, 17160 bytes, sha256 `BC85BA411F1250745D6691CF8C388D94CFB65084C1FBC9405E845C58FBFF7366`)
- `scripts/self_test_external_method_config_materialization.py` (operator_command_source, 23458 bytes, sha256 `A87E0763657DBCBC96D92FCD5DC48CE0080B902CB6A63C09E991AA8A75595C7A`)
- `scripts/self_test_external_method_implementation_packet.py` (operator_command_source, 20450 bytes, sha256 `6033FA1D708803B9ED1C8CE5E579A3CFB822B8BED4B137A27AE72C38A4C8C4A1`)
- `scripts/self_test_external_precollection_manifest_draft.py` (operator_command_source, 20529 bytes, sha256 `7C8179C6D686A7FC06080017A9AE4A091129CCB19ED1E31996533356A6DA8A96`)
- `scripts/self_test_external_rollout_evidence_packet.py` (operator_command_source, 18852 bytes, sha256 `8DEB0903A57E335E25EF4BF73CC476070BF5B28E7A1067F61A81DC3F25CBB6EF`)
- `scripts/validate_external_adapters.py` (operator_command_source, 31757 bytes, sha256 `1D2E383FF5A68C99CBC109F5B92BC41007DD9080A3C43E8692A86D065608F584`)
- `scripts/validate_external_configs.py` (operator_command_source, 14385 bytes, sha256 `1522E1D91E1EFBB74054528E7EF8AA65375EA0753BCE8E2FB9C5872FACF36693`)
- `scripts/validate_external_rollouts.py` (operator_command_source, 40403 bytes, sha256 `8BABA43D78D9DFC7A75844E392A3734C0DE91BCD2C47F517CF8C05A100EA2D34`)

## Checks

- `pass` `operator_packet_is_no_go_non_evidence`: start_state='DO_NOT_COLLECT_YET', strict_evidence_ready=False
- `pass` `acquisition_maps_all_remaining_blockers`: missing_requirements=4
- `pass` `closure_brief_maps_minimum_proof_package`: closure_items=4, haonan_dependency=False, self_test=True
- `pass` `independent_validation_launch_ticket_included`: launch_state='DO_NOT_START_COLLECTION_YET', render_state='DO_NOT_COLLECT_RENDER_MACHINE', haonan_dependency=False
- `pass` `strict_evidence_gates_remain_fail_closed`: analysis=False, onboarding=False, reference_backend_official=False, preflight=False, release=False, pairing=False
- `pass` `bundle_files_exist`: missing=[], total_missing=0
- `pass` `bundle_excludes_rollout_evidence_artifacts`: forbidden_included=[]
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `external_collection_job_packet_included`: job_state='DO_NOT_START_COLLECTION_YET', steps=17, blockers=4
- `pass` `collection_machine_bootstrap_included`: bootstrap_state='READY_TO_BOOTSTRAP_EXTERNAL_MACHINE', command='external_validation/collection_machine_bootstrap.ps1'
- `pass` `precollection_manifest_draft_included`: configs=4, method_configs=11, method_gaps=11, rollout_gaps=8
- `pass` `precollection_manifest_draft_self_test_included`: temporary_draft_ready=True, candidate_hash_drift=True, source_report_drift=True
- `pass` `handoff_has_task_config_and_baseline_assets`: category_counts={'baseline_spec': 12, 'config_template': 4, 'generated_non_evidence_report': 136, 'method_config_candidate': 11, 'operator_command_source': 63, 'operator_facing_input': 93, 'prepared_config_input': 4, 'reference_adapter': 60, 'runner_backend_template': 5, 'task_card': 4}
- `pass` `analysis_plan_included`: analysis_plan_ready=True, strict_evidence_ready=False
- `pass` `platform_onboarding_included`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `fidelity_metadata_probe_included`: strict_metadata_ready=True, primary_metadata_missing=[]
- `pass` `fidelity_provenance_packet_included`: fidelity_provenance_packet_ready=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_provenance_packet_self_test_included`: temporary_ready=True, strict_command_drift_rejected=True, real_outputs_untouched=True
- `pass` `fidelity_acceptance_draft_included`: draft_ready=True, remaining_operator_inputs=9, acceptance_ready=False
- `pass` `fidelity_acceptance_materializer_included`: write_enabled=False, acceptance_write_ready=False
- `pass` `backend_integration_packet_included`: backend_integration_packet_ready=True, strict_backend_ready=False
- `pass` `backend_integration_packet_self_test_included`: temporary_ready=True, strict_command_drift_rejected=True, real_outputs_untouched=True
- `pass` `maniskill_reference_backend_included`: backend_contract_ready=True, video_writer_ready=True, official_collection_ready=False
- `pass` `maniskill_reference_collection_preflight_included`: contract_ready=True, collection_ready=False, blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `config_materialization_self_test_included`: temporary_plan_ready=True, confirmed_write_fixture_ready=True, real_outputs_untouched=True
- `pass` `config_manifest_packet_included`: config_manifest_packet_ready=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `rollout_evidence_packet_included`: rollout_evidence_packet_ready=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `ablation_collection_packet_included`: work_order_count=5, expected_ablation_records=600, manifest_ablation_evidence_ready=False
- `pass` `ablation_collection_packet_self_test_included`: temporary_packet_ready=True, work_order_artifact_command_drift_rejected=True, strict_command_drift_rejected=True
- `pass` `evidence_intake_ledger_included`: mapped=37/37, groups=8
- `pass` `evidence_intake_ledger_self_test_included`: temporary_ledger_ready=True, unmapped_failure_rejected=True, strict_command_drift_rejected=True
- `pass` `precollection_freeze_receipt_included`: locked_artifacts=42, candidate_method_configs=11, freeze_receipt_ready=False
- `pass` `postcollection_evidence_seal_included`: sealed_artifacts=11, records=0, videos=0, seal_ready=False
- `pass` `postcollection_seal_consistency_gate_included`: matched=11, records=0, videos=0, consistency_ready=False
- `pass` `pilot_smoke_packet_included`: pilot_smoke_packet_ready=True, strict_evidence_ready=False
- `pass` `maniskill_render_video_preflight_included`: render_video_ready=False, env_count=4, blocking=['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); OpenCabinetDrawer-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); OpenCabinetDoor-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); PullCubeTool-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done)']
- `pass` `maniskill_render_resource_sweep_included`: any_ready=False, records=3, classes=['vulkan_descriptor_pool_exhaustion']
- `pass` `maniskill_pilot_runtime_liveness_included`: pilot_runtime_ready=False, runner_io_ready=False, render_video_ready=False, timed_out=False, records=0, videos=0, diagnostic_fallbacks=1, failure_summary='official video guard rejected diagnostic fallback sidecar before JSONL write after progress stage record_video_start'
- `pass` `maniskill_render_machine_qualification_included`: qualification_state='DO_NOT_COLLECT_RENDER_MACHINE', render_machine_qualified=False, blocking=12
- `pass` `maniskill_render_host_qualification_brief_included`: host_state='RENDER_HOST_NOT_QUALIFIED', collection_state='DO_NOT_COLLECT_RENDER_MACHINE', classes=['vulkan_descriptor_pool_exhaustion']
- `pass` `method_implementation_packet_included`: method_implementation_packet_ready=True, strict_adapter_evidence_ready=False
- `pass` `baseline_contract_self_test_included`: methods=12, implementations_ready=False, self_test=True
- `pass` `method_config_materialization_included`: candidate_configs=11, strict_adapter_evidence_ready=False, oracle_excluded=True
- `pass` `method_config_materialization_self_test_included`: temporary_materialization_ready=True, candidate_hash_drift=True, real_outputs_untouched=True
- `pass` `operator_actions_cover_evidence_collection`: missing=[]
- `pass` `post_collection_commands_cover_strict_gates`: commands=10
- `pass` `file_hashes_are_recorded`: hashed_files=392
