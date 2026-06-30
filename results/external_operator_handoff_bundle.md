# External Operator Handoff Bundle

Passed: `true`.
Not evidence: `true`.
Strict evidence ready: `false`.
Start state: `DO_NOT_COLLECT_YET`.
Included files: `339`.

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
- `generated_non_evidence_report`: `106`
- `method_config_candidate`: `11`
- `operator_command_source`: `47`
- `operator_facing_input`: `86`
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

- `README.md` (operator_facing_input, 32388 bytes, sha256 `26443BF753FD81EBF4594A8C19A3A4AC67DB3B426275293F2A03A21634C99789`)
- `docs/haonan_yilun_outreach_package.md` (operator_facing_input, 14198 bytes, sha256 `62C8BFD6CAEAF3D3F4A44A9B74B6B6E0D420FCBD59925A8A3C867586D716F0B8`)
- `docs/independent_validation_protocol.md` (operator_facing_input, 21796 bytes, sha256 `7EDFEE348BE624FC1BA8818A88D526CC53B3632F3D31A1500A19F9C5A868FC2E`)
- `docs/reproducibility_checklist.md` (operator_facing_input, 23236 bytes, sha256 `D85E3D8F47E576D1B727D49BF1DA9CE9D0EEFAB4859EEEDC9C4E2EDE641FCC96`)
- `docs/submission_readiness_decision.md` (operator_facing_input, 22626 bytes, sha256 `169F8C3C8BCEF68458BCC9DD12E35ACC2CB55B133B317E6B7EF66D11BF46D8A9`)
- `external_validation/README.md` (operator_facing_input, 34698 bytes, sha256 `5E0E6D9D7D06DC4AB8F664ACC65BEEAEE65799B48D82753722812C08BBFB261B`)
- `external_validation/ablation_collection_packet.json` (operator_facing_input, 5212 bytes, sha256 `93E9ED0730D12385B9C02230FC10B0469D4EEDCE85EFA58FF83ADB6D0FE6E0EA`)
- `external_validation/ablation_collection_packet.md` (operator_facing_input, 3695 bytes, sha256 `BBA79EF72B352B4799A1EE7322BC1A20A0E996F71C9CCB8DF2F98307B455ED99`)
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
- `external_validation/collection_job_packet.json` (operator_facing_input, 17743 bytes, sha256 `B74B08B146454A8AE9BC94AEB1059EAF355F509573CBD18C54E65D0AA70E2EAD`)
- `external_validation/collection_job_packet.md` (operator_facing_input, 14616 bytes, sha256 `F4860EF625547478173C792F5FC93D1B1C27BAF4CF7301CA030B476ED3E96A11`)
- `external_validation/collection_machine_bootstrap.json` (operator_facing_input, 5510 bytes, sha256 `5BFAA5DFA12C2693810B0E4546611CDC61BD69861D45D32613E47C4F18F72D85`)
- `external_validation/collection_machine_bootstrap.md` (operator_facing_input, 3741 bytes, sha256 `89C65B68674F88B4B66392D0D9C96CE5AF97CEBBE673B558CD8339F9FF7D279E`)
- `external_validation/collection_machine_bootstrap.ps1` (operator_facing_input, 2330 bytes, sha256 `B50B58B3A30AE2F73BBD647E844D026E75E1750A0B4E43B55CCC6F99C48E166D`)
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
- `external_validation/evidence_intake_ledger.json` (operator_facing_input, 43344 bytes, sha256 `A34133E4B58D01490A3D0D0786E7A5FE52352F7F645D16EC657B2D519D6A6DBE`)
- `external_validation/evidence_intake_ledger.md` (operator_facing_input, 10804 bytes, sha256 `FA9C782BB76805252EF226F7FD3B4977D8A36B84C0BA59094D0E92CD50A2FF89`)
- `external_validation/fidelity_acceptance_draft.json` (operator_facing_input, 25345 bytes, sha256 `6BA4C9CC96AA1C46F92CB2F785127069307E5F9A378F82DAC41F650D142A2C4B`)
- `external_validation/fidelity_acceptance_draft.md` (operator_facing_input, 6026 bytes, sha256 `546C9C73DDC58EDC55CDB8BB473A2A55B2C4C1EBCE5552DD22A11B5387448410`)
- `external_validation/fidelity_acceptance_template.json` (operator_facing_input, 4582 bytes, sha256 `0BED23F5E73145C7D3283605C0EFDCCF0970CBC989CAAC6DF4E45445D30496E0`)
- `external_validation/fidelity_provenance_packet.json` (operator_facing_input, 20161 bytes, sha256 `0319F0754DCD893BE1C9EC98A26FD30DF63037F6543868C729E007E4D1125782`)
- `external_validation/fidelity_provenance_packet.md` (operator_facing_input, 3674 bytes, sha256 `FF138E663BDFCDDC47BE9CC671FB472DC82D3126AEDC7B0EBA3B9AC7B68476CF`)
- `external_validation/fidelity_provenance_work_orders.csv` (operator_facing_input, 11772 bytes, sha256 `7E26F05053D899036351634D075F4F1B3CE8AC7464A581C27EEC3C1CD65DBCDA`)
- `external_validation/independent_validation_route.md` (operator_facing_input, 7270 bytes, sha256 `10B4246BF3F6F32F052E89EACD2FE1CB7CB2CB9ACB8C77876CF88915EFBA3379`)
- `external_validation/independent_validation_route_matrix.csv` (operator_facing_input, 2115 bytes, sha256 `02E059F84400B4054939012707D7FD43A6F4BDAF3CEF5560A760CBD06BBAAB4E`)
- `external_validation/log_schema_v1.json` (operator_facing_input, 3055 bytes, sha256 `BF2194D543F83448F03BBD9ADB5310C9BDE7313228EA876BE7FE75CD788A4917`)
- `external_validation/manifest_assembly_checklist.csv` (operator_facing_input, 11089 bytes, sha256 `572827C87C44B677B5897E2215FB3741E38000A40C23AF5141AFBC923D31FAEA`)
- `external_validation/manifest_precollection_draft.json` (operator_facing_input, 44176 bytes, sha256 `0CEA5A80DCAB8942D78F110C16BF7032AA62BBFC120DA7DCFAC5C42F2551AC2D`)
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
- `external_validation/method_config_materialization_plan.json` (operator_facing_input, 33081 bytes, sha256 `46924247617A3D86168888FA411EA957C82C1992FB66D82BC00CB87AAE9E153F`)
- `external_validation/method_config_materialization_plan.md` (operator_facing_input, 3422 bytes, sha256 `5BB83B2C4B1601858113FD2F8F9203B469EF2BC3C9AA37880E23FBAA384A1D53`)
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
- `external_validation/postcollection_evidence_seal.csv` (operator_facing_input, 1823 bytes, sha256 `2315A8695630ECED6EBF1C9A2DFC3DFAD4BA48609B82B7CD232C0E49BB786F65`)
- `external_validation/postcollection_evidence_seal.json` (operator_facing_input, 6584 bytes, sha256 `8438C9260339D4A63051F3CDC0AFDC918EE091F70CB77CDE53F2A84164A954CD`)
- `external_validation/postcollection_evidence_seal.md` (operator_facing_input, 4655 bytes, sha256 `7DEC4DF0DA7BA05C3331858DE1A64D73D501ECEC94A083A7B1D0F4FE64F3B049`)
- `external_validation/precollection_freeze_receipt.csv` (operator_facing_input, 6712 bytes, sha256 `EA4CF561CDA7B423AD704BC73634C5FAB1B25006CB14CC3931EE9DE621458A32`)
- `external_validation/precollection_freeze_receipt.json` (operator_facing_input, 28749 bytes, sha256 `052D2AF19E5CFF9E887117B529ADF48387C5D6DB452035682345BB930818ED89`)
- `external_validation/precollection_freeze_receipt.md` (operator_facing_input, 9558 bytes, sha256 `2C6B0DDF070822559A09FECAABF1F151693AB8814613452C48FAF15B23BC676F`)
- `external_validation/reference_adapter_report.md` (operator_facing_input, 3098 bytes, sha256 `F64B68656335697769F9E7E60F19D974CF5D36D118D94B1296A7368CF49F4C2C`)
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
- `results/external_ablation_collection_audit.json` (generated_non_evidence_report, 5211 bytes, sha256 `42DBE738EC9F7787C52F7A50B456BEEFA872ACECD813E66CA5855608684E4679`)
- `results/external_ablation_collection_audit.md` (generated_non_evidence_report, 3695 bytes, sha256 `BBA79EF72B352B4799A1EE7322BC1A20A0E996F71C9CCB8DF2F98307B455ED99`)
- `results/external_acquisition_packet.json` (generated_non_evidence_report, 59292 bytes, sha256 `E979B897017D6AC8E42EC50212331A6BD599AF243739889BFC06491B65C367C6`)
- `results/external_acquisition_packet.md` (generated_non_evidence_report, 36117 bytes, sha256 `9BAD100EECFC75C195232634DE7D7EEB1BF439799B3853AEDCC3549352AB9F90`)
- `results/external_adapter_contract_audit.json` (generated_non_evidence_report, 3130 bytes, sha256 `D61D6618070F133A1D7CC78921B0EDB9AF0EA4B8ED530745BAC9E5EC0BA2EC26`)
- `results/external_adapter_contract_audit.md` (generated_non_evidence_report, 2201 bytes, sha256 `428CC91812FBF6316521F5C531D9569AB48B04B2ACF26CDE37FDE9B588BE760B`)
- `results/external_adapter_scaffold_audit.json` (generated_non_evidence_report, 6541 bytes, sha256 `92A41EBF2DEE4066D5D294C8420492D6E4B934A1F1B601AD4CB8F90390AC2C4A`)
- `results/external_adapter_scaffold_audit.md` (generated_non_evidence_report, 2987 bytes, sha256 `F7F2A7E3738A610C9B878A36280BC507EC26D972DC0D0EDC01F77D2107681DC0`)
- `results/external_analysis_plan_audit.json` (generated_non_evidence_report, 3710 bytes, sha256 `982BBF2F8E794FD9E9658B5D07E8155A4D02381599E331439EEDAD49354F7DF0`)
- `results/external_analysis_plan_audit.md` (generated_non_evidence_report, 3080 bytes, sha256 `78AEEC8E8117DEC437F26D338B15857BD30522C4294ED4864ECAC7DD561660CE`)
- `results/external_backend_contract_audit.json` (generated_non_evidence_report, 2747 bytes, sha256 `1FBD0B682B1767D97988FEDA2D3192ECBA78D27E5760A90FDDC8D38B7C268876`)
- `results/external_backend_contract_audit.md` (generated_non_evidence_report, 2159 bytes, sha256 `F92AE6D33D05582267F4D1F11D0886F6510B396E98A96C38C082043A8315601B`)
- `results/external_backend_integration_audit.json` (generated_non_evidence_report, 4194 bytes, sha256 `6D985329EDAB8BAAD99EBACF4F45A1263DD0E115F6FBD9A08209A0B13C1C3294`)
- `results/external_backend_integration_audit.md` (generated_non_evidence_report, 3487 bytes, sha256 `76B8CC5C8BD05A99798DC03B3EAD866D649858DBE34735EC4E4CA8F704D52614`)
- `results/external_baseline_contract_audit.json` (generated_non_evidence_report, 5254 bytes, sha256 `3D6D8B08A0894F96387CB91CBB00BBF659527C18BD0D9EA8A35A480ED30AB70C`)
- `results/external_baseline_contract_audit.md` (generated_non_evidence_report, 2454 bytes, sha256 `5D214E40E4DCD0E680C8F63D327FE2CA33FDE99CF046E1D27A59BA1DFA7C7D30`)
- `results/external_blind_eval_audit.json` (generated_non_evidence_report, 1972 bytes, sha256 `BC754C10B0E0FBDAD9EEB57371302F4199EEBE49894149CA4C58405357A638BF`)
- `results/external_blind_eval_audit.md` (generated_non_evidence_report, 1183 bytes, sha256 `9EC804D278A6BEBB749B193C799210EEC6894349742C2D4363E877BF8D4A5B96`)
- `results/external_collection_job_packet_audit.json` (generated_non_evidence_report, 17873 bytes, sha256 `9D02C547036CF06E3FFF3B4ED33994FCDB031255CE6E890B86373DC3F5B2F28D`)
- `results/external_collection_job_packet_audit.md` (generated_non_evidence_report, 14622 bytes, sha256 `A6AE1D5685E70291378D58638E2529C4588D5090D2193BD1E74E96220510AB28`)
- `results/external_collection_machine_bootstrap_audit.json` (generated_non_evidence_report, 5581 bytes, sha256 `BEF70CC831C395F5FCA3B1F2D6838362ABDE77EC09B1687C27C01D445338EAB6`)
- `results/external_collection_machine_bootstrap_audit.md` (generated_non_evidence_report, 3747 bytes, sha256 `3AE8EF1988C040BDD2FF165D79D8D9B92174317E080C1B9D7CA0DB0EA985565A`)
- `results/external_collection_plan.json` (generated_non_evidence_report, 147907 bytes, sha256 `499A6C1E503727DAEEBF2F22BDE5EDB9E89A5D58A47071AF4E6685D283D2ECEC`)
- `results/external_collection_plan.md` (generated_non_evidence_report, 6287 bytes, sha256 `0C336204F3A25C6A9385F4B4349488BC99550F57317F8C6F22AF6BB14785EE6F`)
- `results/external_collection_readiness_audit.json` (generated_non_evidence_report, 8125 bytes, sha256 `8AC215A38BD0E7BBF44A20C547A4ED43CDD76960DCE679ADAF46B24D8C02422E`)
- `results/external_collection_readiness_audit.md` (generated_non_evidence_report, 4059 bytes, sha256 `E74D7C135F7D1377312C89D53C695C5D85E7FC134FB9B08634DFA900DEA9B08D`)
- `results/external_config_manifest_audit.json` (generated_non_evidence_report, 3471 bytes, sha256 `71888C39980962B4AAE8E67DC2338CEB8F2DBA603BC85DF0BF6B50BE7720EF92`)
- `results/external_config_manifest_audit.md` (generated_non_evidence_report, 2772 bytes, sha256 `C0F299190160578330B0923D01ABC38B9DEAD06CD291DE4EE16F3F8984837539`)
- `results/external_config_materialization_plan.json` (generated_non_evidence_report, 3186 bytes, sha256 `EB1436D71B2E51AA6117679956D4563284DB846A7A0C62E41AE2B4EFE0B02E5F`)
- `results/external_config_materialization_plan.md` (generated_non_evidence_report, 1976 bytes, sha256 `2C7F8786129C013277B149D934B1FD8CD964C03E88D7E5856DB5EDEEA5CFA6EC`)
- `results/external_config_template_audit.json` (generated_non_evidence_report, 1418 bytes, sha256 `364A4CEA5B063E5EA45A639D52E9EEE7628941F2722496D6A2E47CE787CA2106`)
- `results/external_config_template_audit.md` (generated_non_evidence_report, 797 bytes, sha256 `4CC337580323BADB03441EE8478DDDEF19CC9857F1B0B032264B78DB6A947DF7`)
- `results/external_evidence_intake_ledger_audit.json` (generated_non_evidence_report, 43344 bytes, sha256 `A34133E4B58D01490A3D0D0786E7A5FE52352F7F645D16EC657B2D519D6A6DBE`)
- `results/external_evidence_intake_ledger_audit.md` (generated_non_evidence_report, 10804 bytes, sha256 `FA9C782BB76805252EF226F7FD3B4977D8A36B84C0BA59094D0E92CD50A2FF89`)
- `results/external_evidence_preflight.json` (generated_non_evidence_report, 12344 bytes, sha256 `D163EA7B1E6DC2EFBBF26DC10C324A5CB76CD216BEB969C316D5A994F8DCE0B1`)
- `results/external_evidence_preflight.md` (generated_non_evidence_report, 4745 bytes, sha256 `B68911C22003E7E03E48D7486AB58F53AD10457F0C25ABCD47A134E37A247892`)
- `results/external_evidence_preflight_self_test.json` (generated_non_evidence_report, 1979 bytes, sha256 `C3C990BFBEAE0869391A438CBAAA21E703B1D19B6B2A4476A0ED09F0B620159E`)
- `results/external_evidence_preflight_self_test.md` (generated_non_evidence_report, 1935 bytes, sha256 `56651DAF3A7D8D04D58F11CB96CF9CC12F6ABCA1D385952B74A24A7DDF302EC6`)
- `results/external_execution_readiness_audit.json` (generated_non_evidence_report, 41689 bytes, sha256 `7053059EB9C521BAB0912B08190731B439C7F707F48D2EE06B6B63144007B303`)
- `results/external_execution_readiness_audit.md` (generated_non_evidence_report, 32293 bytes, sha256 `568FF4481FF39A1B04757B5502AC8AD6DD6DBEE4DEA1F0EC034B96D8ED6B763B`)
- `results/external_execution_readiness_self_test.json` (generated_non_evidence_report, 2069 bytes, sha256 `C8A4099B6CE8FC2D7AEA75B0382F67552F6B98C8F28B57F8FC73CB2290DC4218`)
- `results/external_execution_readiness_self_test.md` (generated_non_evidence_report, 2015 bytes, sha256 `9CBEEBA007F62474D332CC662595E8172EB297CB1434D19306D4FD74E72DE3FE`)
- `results/external_fidelity_acceptance_audit.json` (generated_non_evidence_report, 9807 bytes, sha256 `23846A8DFE65737A9EFB04A4231D05ADE15749DAED64DE6AFE5F466F941AA3C5`)
- `results/external_fidelity_acceptance_audit.md` (generated_non_evidence_report, 7443 bytes, sha256 `8C45FD1ACECFF00BB09050A896BD4D0086F90D7DB70D0C40C6AF2F00EC45363A`)
- `results/external_fidelity_acceptance_draft_audit.json` (generated_non_evidence_report, 6143 bytes, sha256 `B3D9C76BD4CDB5250AEF88ED012D785A3C76BE8DB68F5F250D4FA810302D433C`)
- `results/external_fidelity_acceptance_draft_audit.md` (generated_non_evidence_report, 5016 bytes, sha256 `FEDF26B27936C9DCE973F36254D8F400EFBDA0A20BEAF1DB53BC3FA4AFC296E9`)
- `results/external_fidelity_provenance_audit.json` (generated_non_evidence_report, 3739 bytes, sha256 `F49E47CA1664A1116AA61A30D46C17C90672D378A40981B0C6991448297D4598`)
- `results/external_fidelity_provenance_audit.md` (generated_non_evidence_report, 2923 bytes, sha256 `42CDDD09212070C7D7E38968E2E42130C5F2696CC432F0CA69B0D7064FD644C6`)
- `results/external_manifest_builder_self_test.json` (generated_non_evidence_report, 2674 bytes, sha256 `30008478A73C62389E341A6D9F839DBDE2B2EC5807173E949646F1CB861909E8`)
- `results/external_manifest_builder_self_test.md` (generated_non_evidence_report, 2348 bytes, sha256 `83CC75004A0B4C959D91B489A9809CEA43D95D4E81376D5D3C93C4819710D54E`)
- `results/external_method_config_materialization_audit.json` (generated_non_evidence_report, 33153 bytes, sha256 `5DC60C246B1C8CCF6D20F780F5D97B46E016C548EFCFDD72EE7E6925A4EDD7F2`)
- `results/external_method_config_materialization_audit.md` (generated_non_evidence_report, 3423 bytes, sha256 `9FE77F7B1D8976A4AA3A7A60FB26431D8733D1698EBC5CEE23C16676CBE13C7A`)
- `results/external_method_implementation_audit.json` (generated_non_evidence_report, 6510 bytes, sha256 `F8AA15870753DC4E6B4F681ACEF956A4C49ADAF3A12A98C32091582474021FAC`)
- `results/external_method_implementation_audit.md` (generated_non_evidence_report, 4783 bytes, sha256 `8A318351DC5AA27C081AB65BE30E28AA60115DA7B416076CEE74B5892754C313`)
- `results/external_operator_packet.json` (generated_non_evidence_report, 62046 bytes, sha256 `20C0C78B75DAA0511617A64B2D18625FB3715592118828BF013895B0F5B5A9ED`)
- `results/external_operator_packet.md` (generated_non_evidence_report, 29112 bytes, sha256 `CFE29BDAD74411141D33744CDB16CE90DBABEB8326324E93B91C69A0D830F38C`)
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
- `results/external_precollection_freeze_receipt_audit.json` (generated_non_evidence_report, 19940 bytes, sha256 `3362252FAACB015236E0D88243AF11A78CF858A34B29B0CF1FD91F0BC809FCE7`)
- `results/external_precollection_freeze_receipt_audit.md` (generated_non_evidence_report, 8705 bytes, sha256 `19AF16EF52768CAFA6AA4F1FA5BB4BD823E8B4A0C9909941642A0196BE0D790A`)
- `results/external_precollection_manifest_draft_audit.json` (generated_non_evidence_report, 6087 bytes, sha256 `07EE4E9808332F06F3161609A98533A848963DA41D0312F7147AF7FDEC465D42`)
- `results/external_precollection_manifest_draft_audit.md` (generated_non_evidence_report, 2359 bytes, sha256 `8C63C4993CCB03FE653A25F37B3139BD50452E7E8C2AB0B23BE355129307120D`)
- `results/external_reference_adapter_audit.json` (generated_non_evidence_report, 7424 bytes, sha256 `2E182A83556263635731AD6969E2976D0138B18056B562E9DF8E1AE2D6E0CB52`)
- `results/external_reference_adapter_audit.md` (generated_non_evidence_report, 2402 bytes, sha256 `E3B1EF1B04EDC6635605B205E7AE4AADACED64241281A5FCA1F12A26550DE0D6`)
- `results/external_release_package_audit.json` (generated_non_evidence_report, 490 bytes, sha256 `D760B589BD12AA51882D2C99B501475A6103FCABAFCF86A6E1744F9235E91278`)
- `results/external_release_package_audit.md` (generated_non_evidence_report, 606 bytes, sha256 `891E153CCAF9A412318D6D224EE16156CD16222A56CE143662337D4B08BE8751`)
- `results/external_rollout_evidence_audit.json` (generated_non_evidence_report, 3681 bytes, sha256 `46E851EEDF315D592F1DF5BFF09FEE9FB328CF47E9B7E7511B5E9A2AC976B03A`)
- `results/external_rollout_evidence_audit.md` (generated_non_evidence_report, 2864 bytes, sha256 `4B1F04F3BE6024753737B613769EA2DD15F1AEC7172F028555456A9598D91800`)
- `results/external_runbook_audit.json` (generated_non_evidence_report, 4028 bytes, sha256 `43902C49CC5F56F717A42A6F52E0F28926C98EC512F85DCF30172B5E4C0E7DE8`)
- `results/external_runbook_audit.md` (generated_non_evidence_report, 2232 bytes, sha256 `8C7754CC5E121EF88D0240010A2A595B64E78819E757BE237D8024F353AA814C`)
- `results/external_runner_harness_audit.json` (generated_non_evidence_report, 3277 bytes, sha256 `9221FD3F3334D182AAE1F5C3C19947EEB342C6A0EE2E331EE43ABC4DEC036270`)
- `results/external_runner_harness_audit.md` (generated_non_evidence_report, 2291 bytes, sha256 `1920465D2991DE966CBEFF7C2C4C708A197B801F4FDB08435E18D4EC009D2B7A`)
- `results/fidelity_acceptance_materialization_plan.json` (generated_non_evidence_report, 9209 bytes, sha256 `6A7D96A5F604DB5FAD8283FC5418CC97DB11C365637EB2CF1F9211C9FD527479`)
- `results/fidelity_acceptance_materialization_plan.md` (generated_non_evidence_report, 5840 bytes, sha256 `A6B9435F3C7FBF9B8632D396EB599B4A1341E0EA4354BD6786832169E753698B`)
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
- `results/maniskill_render_machine_qualification.json` (generated_non_evidence_report, 5426 bytes, sha256 `6C63AC79D94BFC129C68F78C335120CA7A621B44BAEA49889258C3BB12777AAD`)
- `results/maniskill_render_machine_qualification.md` (generated_non_evidence_report, 5074 bytes, sha256 `28E676EC5C5BCE5FC05C3A314CD431472AEEBCBDFE3A098D59483DA7B044B201`)
- `results/maniskill_render_resource_sweep.json` (generated_non_evidence_report, 26710 bytes, sha256 `CDC41DA58A92614DF81D438A43885B6041582B3F822AD660BA5C6BA64468D048`)
- `results/maniskill_render_resource_sweep.md` (generated_non_evidence_report, 3674 bytes, sha256 `5BDE7CFD292DB6D1D54E8720F5BA869DDAF599C203F13FF5BACD04094B47F4CE`)
- `results/maniskill_render_video_preflight_audit.json` (generated_non_evidence_report, 60314 bytes, sha256 `1365D912692FBF72544AA2C2980C60D2B82F242F5562354F690A0530F3E90167`)
- `results/maniskill_render_video_preflight_audit.md` (generated_non_evidence_report, 7582 bytes, sha256 `033875B78831A23DC646D5DE6E76B89ED5F4F3FEBD0E8A41B0C75FE2BE822C3E`)
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
- `scripts/build_external_ablation_collection_packet.py` (operator_command_source, 13282 bytes, sha256 `9EBCC4A29A134B7E73E1FE5722916F66CF1F89C24E78CB6FA5EEA922A77B0382`)
- `scripts/build_external_acquisition_packet.py` (operator_command_source, 98463 bytes, sha256 `51D5892E36E02C0042F53C6C80A0AA5FA83A9A34AEE552B49DF7A28FADBF6BBF`)
- `scripts/build_external_analysis_plan.py` (operator_command_source, 18694 bytes, sha256 `27C516ABD36E7B7FF1B3F11E712E5C7E18FE7F6FCFA672090BF28AE67E078CA7`)
- `scripts/build_external_backend_integration_packet.py` (operator_command_source, 20172 bytes, sha256 `8BCA04F29A5F058AD4A5EE786FBF26F7E11136081BD1B11994FDF1DE3AACC506`)
- `scripts/build_external_collection_job_packet.py` (operator_command_source, 34657 bytes, sha256 `7328EDF6989A347CEADC1152087AAA4219D194561B13DEE624B4D2AE0BF3D46D`)
- `scripts/build_external_collection_machine_bootstrap.py` (operator_command_source, 15819 bytes, sha256 `9A82BB080F8997ED83061E38742C318062B642E19730952B72721D0EF2E12F73`)
- `scripts/build_external_config_manifest_packet.py` (operator_command_source, 20797 bytes, sha256 `756C0C5B64F4F0DB6C1E45742096A2BCE03AA346C34D91A834ED196296839EB8`)
- `scripts/build_external_evidence_intake_ledger.py` (operator_command_source, 20347 bytes, sha256 `5EBC37FA435940B2159DC9FED6493DA19608BDF09EC976809810472800A596BB`)
- `scripts/build_external_fidelity_acceptance_draft.py` (operator_command_source, 40461 bytes, sha256 `BA615558785FB0B4A660C2CDC68A1A7334542BEC3A85DDAC5304FC97D6227E5D`)
- `scripts/build_external_fidelity_provenance_packet.py` (operator_command_source, 22396 bytes, sha256 `59A021ED6C8E25FB78A21C3B52183496032001ECEA0380624B8A5DA8E8F1A097`)
- `scripts/build_external_manifest.py` (operator_command_source, 33515 bytes, sha256 `FA9F3890C25B2FEA0F484520C38270BDE202F02317734563983522F3237EA09D`)
- `scripts/build_external_method_implementation_packet.py` (operator_command_source, 57664 bytes, sha256 `C166221116A089779E0111AE13BDB75CC1625849486A1C116AF8534D264334AF`)
- `scripts/build_external_operator_handoff_bundle.py` (operator_command_source, 77697 bytes, sha256 `125CA19750106D0B8E3186796AD254BBB66F64E93967801F6D2F84D641C232D4`)
- `scripts/build_external_operator_packet.py` (operator_command_source, 71405 bytes, sha256 `2A06BF8BADB9A1BFC340309980E1A0AA45A1410E30F9BEED69E524E6A12D6C6C`)
- `scripts/build_external_pilot_smoke_packet.py` (operator_command_source, 11266 bytes, sha256 `F3A2D24716D7DCE1D337453137191E821E1F81ADBAA8ABF446C2446E489C00CE`)
- `scripts/build_external_platform_onboarding.py` (operator_command_source, 32058 bytes, sha256 `87CB7C475846CFCE3849B835621097DA3362DC9EBE5411794EBF13C792941AB2`)
- `scripts/build_external_postcollection_evidence_seal.py` (operator_command_source, 22280 bytes, sha256 `B608377416DBF26842358294D7BC6CE239C3BF37571BD22EAF986788878087C9`)
- `scripts/build_external_precollection_freeze_receipt.py` (operator_command_source, 31882 bytes, sha256 `AD9EA284B5CD164BA39FA560F9CC748D9574E8A229F01F3BB50BB0FE18237803`)
- `scripts/build_external_precollection_manifest_draft.py` (operator_command_source, 25700 bytes, sha256 `A1C00CBD25ACD432F7FCADC7672383B3F21CA805CDC82AEB181961B614BBE967`)
- `scripts/build_external_rollout_evidence_packet.py` (operator_command_source, 23096 bytes, sha256 `08C85AA06AA704107282CAF145AD000F5C76EC307B1B85B86341C529706A9575`)
- `scripts/build_maniskill_render_machine_qualification.py` (operator_command_source, 25508 bytes, sha256 `4E289392972D00904159144AF20E7F70686D0981982F1838220313ACC4BF6D72`)
- `scripts/materialize_external_configs.py` (operator_command_source, 12746 bytes, sha256 `EA207DCFDCCC9593CBFEC993C22D3EDA8F493124D1EBEB6A240D793C4AC80A25`)
- `scripts/materialize_external_method_configs.py` (operator_command_source, 14561 bytes, sha256 `92B531FB3AD8155D891CAE7D5FE9900F807DF642526AC913B8248BFB0FE2EEB4`)
- `scripts/materialize_fidelity_acceptance.py` (operator_command_source, 23450 bytes, sha256 `63085D7ED6B71B37B5367F18E9154F273EF0774F81C5656BDF0806CC54D41C73`)
- `scripts/probe_external_platform.py` (operator_command_source, 14122 bytes, sha256 `67456EAE975E43F2D87B7233670D57D5E353C7034E2636E500BB3B38806C05DC`)
- `scripts/probe_maniskill_env_smoke.py` (operator_command_source, 18252 bytes, sha256 `CAD9777638492EDE99F187BCFF89E1CAE85024FE5FEE8D7374AFBFC2516D4F02`)
- `scripts/probe_maniskill_fidelity_metadata.py` (operator_command_source, 21099 bytes, sha256 `2EC0606C2AAF6E7C9B298B202748005D563BD47C5DDCC88F060A657B52DF88AB`)
- `scripts/probe_maniskill_task_bindings.py` (operator_command_source, 12426 bytes, sha256 `AC9A26FDA7512B17AD35589525DF3A41E7C5CF28C164850C4F835466C69D92E2`)
- `scripts/self_test_external_evidence_preflight.py` (operator_command_source, 17751 bytes, sha256 `347C396D9808A010989F9EF26CFAD4BBB6EC59397BEA94487810DE8E65F30E61`)
- `scripts/self_test_external_execution_readiness.py` (operator_command_source, 14646 bytes, sha256 `27454171F04FF0D2342D631BC6B484A3C113AD71998B49EC0188BA50553F6571`)
- `scripts/self_test_external_manifest_builder.py` (operator_command_source, 17160 bytes, sha256 `BC85BA411F1250745D6691CF8C388D94CFB65084C1FBC9405E845C58FBFF7366`)
- `scripts/validate_external_adapters.py` (operator_command_source, 31757 bytes, sha256 `1D2E383FF5A68C99CBC109F5B92BC41007DD9080A3C43E8692A86D065608F584`)
- `scripts/validate_external_configs.py` (operator_command_source, 14385 bytes, sha256 `1522E1D91E1EFBB74054528E7EF8AA65375EA0753BCE8E2FB9C5872FACF36693`)
- `scripts/validate_external_rollouts.py` (operator_command_source, 40403 bytes, sha256 `8BABA43D78D9DFC7A75844E392A3734C0DE91BCD2C47F517CF8C05A100EA2D34`)

## Checks

- `pass` `operator_packet_is_no_go_non_evidence`: start_state='DO_NOT_COLLECT_YET', strict_evidence_ready=False
- `pass` `acquisition_maps_all_remaining_blockers`: missing_requirements=4
- `pass` `strict_evidence_gates_remain_fail_closed`: analysis=False, onboarding=False, reference_backend_official=False, preflight=False, release=False, pairing=False
- `pass` `bundle_files_exist`: missing=[], total_missing=0
- `pass` `bundle_excludes_rollout_evidence_artifacts`: forbidden_included=[]
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `external_collection_job_packet_included`: job_state='DO_NOT_START_COLLECTION_YET', steps=17, blockers=4
- `pass` `collection_machine_bootstrap_included`: bootstrap_state='READY_TO_BOOTSTRAP_EXTERNAL_MACHINE', command='external_validation/collection_machine_bootstrap.ps1'
- `pass` `precollection_manifest_draft_included`: configs=4, method_configs=11, method_gaps=11, rollout_gaps=8
- `pass` `handoff_has_task_config_and_baseline_assets`: category_counts={'baseline_spec': 12, 'config_template': 4, 'generated_non_evidence_report': 106, 'method_config_candidate': 11, 'operator_command_source': 47, 'operator_facing_input': 86, 'prepared_config_input': 4, 'reference_adapter': 60, 'runner_backend_template': 5, 'task_card': 4}
- `pass` `analysis_plan_included`: analysis_plan_ready=True, strict_evidence_ready=False
- `pass` `platform_onboarding_included`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `fidelity_metadata_probe_included`: strict_metadata_ready=True, primary_metadata_missing=[]
- `pass` `fidelity_provenance_packet_included`: fidelity_provenance_packet_ready=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_acceptance_draft_included`: draft_ready=True, remaining_operator_inputs=9, acceptance_ready=False
- `pass` `fidelity_acceptance_materializer_included`: write_enabled=False, acceptance_write_ready=False
- `pass` `backend_integration_packet_included`: backend_integration_packet_ready=True, strict_backend_ready=False
- `pass` `maniskill_reference_backend_included`: backend_contract_ready=True, video_writer_ready=True, official_collection_ready=False
- `pass` `maniskill_reference_collection_preflight_included`: contract_ready=True, collection_ready=False, blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `config_manifest_packet_included`: config_manifest_packet_ready=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `rollout_evidence_packet_included`: rollout_evidence_packet_ready=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `ablation_collection_packet_included`: work_order_count=5, expected_ablation_records=600, manifest_ablation_evidence_ready=False
- `pass` `evidence_intake_ledger_included`: mapped=37/37, groups=8
- `pass` `precollection_freeze_receipt_included`: locked_artifacts=42, candidate_method_configs=11, freeze_receipt_ready=False
- `pass` `postcollection_evidence_seal_included`: sealed_artifacts=11, records=0, videos=0, seal_ready=False
- `pass` `postcollection_seal_consistency_gate_included`: matched=11, records=0, videos=0, consistency_ready=False
- `pass` `pilot_smoke_packet_included`: pilot_smoke_packet_ready=True, strict_evidence_ready=False
- `pass` `maniskill_render_video_preflight_included`: render_video_ready=False, env_count=4, blocking=['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); OpenCabinetDrawer-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); OpenCabinetDoor-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); PullCubeTool-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done)']
- `pass` `maniskill_render_resource_sweep_included`: any_ready=False, records=3, classes=['vulkan_descriptor_pool_exhaustion']
- `pass` `maniskill_pilot_runtime_liveness_included`: pilot_runtime_ready=False, runner_io_ready=False, render_video_ready=False, timed_out=False, records=0, videos=0, diagnostic_fallbacks=1, failure_summary='official video guard rejected diagnostic fallback sidecar before JSONL write after progress stage record_video_start'
- `pass` `maniskill_render_machine_qualification_included`: qualification_state='DO_NOT_COLLECT_RENDER_MACHINE', render_machine_qualified=False, blocking=12
- `pass` `method_implementation_packet_included`: method_implementation_packet_ready=True, strict_adapter_evidence_ready=False
- `pass` `method_config_materialization_included`: candidate_configs=11, strict_adapter_evidence_ready=False, oracle_excluded=True
- `pass` `operator_actions_cover_evidence_collection`: missing=[]
- `pass` `post_collection_commands_cover_strict_gates`: commands=10
- `pass` `file_hashes_are_recorded`: hashed_files=339
