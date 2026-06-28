# External Operator Handoff Bundle

Passed: `true`.
Not evidence: `true`.
Strict evidence ready: `false`.
Start state: `DO_NOT_COLLECT_YET`.
Included files: `254`.

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

Actual collection command after the strict gate passes:

```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```

Post-collection strict gates:

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
- `generated_non_evidence_report`: `78`
- `operator_command_source`: `33`
- `operator_facing_input`: `54`
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

- `README.md` (operator_facing_input, 18830 bytes, sha256 `90342BC31975CB6BBC1836753E10D5485FC8EFB3D192D1EF0BAAAE25D161A061`)
- `docs/haonan_yilun_outreach_package.md` (operator_facing_input, 11271 bytes, sha256 `84E63615B072645AE5AAB57190A091224E7151BD37FF5C961ABE7FF4CA7B8C35`)
- `docs/independent_validation_protocol.md` (operator_facing_input, 21628 bytes, sha256 `D5A1269B3AFA2DFCE6270E32C6348D60894A4E6ACF4C7C3790ABCDAF8E83E718`)
- `docs/reproducibility_checklist.md` (operator_facing_input, 16452 bytes, sha256 `8FE531CED57C6073F841103269CA4E4C4A664953B8A851ABAE88A32DF29F9EBE`)
- `docs/submission_readiness_decision.md` (operator_facing_input, 9502 bytes, sha256 `F3CDEC0731125DEFEDF3A17CE34F6ADFA87B81E72E85FD92079404A136D493E2`)
- `external_validation/README.md` (operator_facing_input, 32120 bytes, sha256 `2260A952708EDDF7DAD4DCBB3296B33B11FA9A7B3A452EDF693323891B3F33A6`)
- `external_validation/backend_integration_packet.json` (operator_facing_input, 8780 bytes, sha256 `16DABB38BE7289B2F0162776F007690559AD3A439CD350FFBEB0F639409DD2FE`)
- `external_validation/backend_integration_packet.md` (operator_facing_input, 5380 bytes, sha256 `B116851BC510B18DFF01E4ECF626EA0F05C5ECFDE29648B8F58A5BA0D22A18A4`)
- `external_validation/backend_integration_work_orders.csv` (operator_facing_input, 3369 bytes, sha256 `4EE6D3336C44A04576A2720BEA35A664613A907B33E771952FDBBFB64DFDACE3`)
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
- `external_validation/collection_runbook.md` (operator_facing_input, 5185 bytes, sha256 `76D0B534701B7871E4AF3366A971036493F7DD0879A68D458497D6ACC305E434`)
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
- `external_validation/fidelity_acceptance_draft.json` (operator_facing_input, 26039 bytes, sha256 `0E07DB657FD7F8665347C90451CAF679A4B13BA3263447DD2F54D2F4FCB93959`)
- `external_validation/fidelity_acceptance_draft.md` (operator_facing_input, 6080 bytes, sha256 `B429A97DAF03D6E24228A53273C42E8867F9FA5106C50E095B6BEFAAB55DD905`)
- `external_validation/fidelity_acceptance_template.json` (operator_facing_input, 4582 bytes, sha256 `0BED23F5E73145C7D3283605C0EFDCCF0970CBC989CAAC6DF4E45445D30496E0`)
- `external_validation/fidelity_provenance_packet.json` (operator_facing_input, 19181 bytes, sha256 `C676A6CF4AE5A89183F337FDF05F6D398598B5323BA956ABBAF5117F63E65173`)
- `external_validation/fidelity_provenance_packet.md` (operator_facing_input, 3686 bytes, sha256 `964171E407B866552CA6A4CB3FE7C5FE4F491C0F5CCEF5775DCF24038A91531E`)
- `external_validation/fidelity_provenance_work_orders.csv` (operator_facing_input, 11360 bytes, sha256 `CABBC9C837CBC49CFBFFD531A46CED360FB58F25F85B59235BA31789217DFA12`)
- `external_validation/independent_validation_route.md` (operator_facing_input, 7270 bytes, sha256 `10B4246BF3F6F32F052E89EACD2FE1CB7CB2CB9ACB8C77876CF88915EFBA3379`)
- `external_validation/independent_validation_route_matrix.csv` (operator_facing_input, 2115 bytes, sha256 `02E059F84400B4054939012707D7FD43A6F4BDAF3CEF5560A760CBD06BBAAB4E`)
- `external_validation/log_schema_v1.json` (operator_facing_input, 3055 bytes, sha256 `BF2194D543F83448F03BBD9ADB5310C9BDE7313228EA876BE7FE75CD788A4917`)
- `external_validation/manifest_assembly_checklist.csv` (operator_facing_input, 10417 bytes, sha256 `3A92EDDE50739CAFB7DEEBD138D99B35A6DFE01CD527A8220250831271C6DE1B`)
- `external_validation/maniskill_task_bindings.json` (operator_facing_input, 2159 bytes, sha256 `448A0430B88097618D463319DBD599334D28D533F81BA2FE783C3B80DE4EFBC5`)
- `external_validation/method_alias_map.json` (operator_facing_input, 3261 bytes, sha256 `B56A11CB20914B2FD2649DA647F7722DE43D6B04DE3E89704A8CD3F952A4E031`)
- `external_validation/method_implementation_packet.json` (operator_facing_input, 58166 bytes, sha256 `394250F820244E9CD04B6A1CB1A504E42BE61156459F1DDC3C59C1229B5C2E9B`)
- `external_validation/method_implementation_packet.md` (operator_facing_input, 33131 bytes, sha256 `3F676CE958F42CC732D04D2D0184F0B425410FB2CE123354359961206D4B0BB4`)
- `external_validation/method_implementation_work_orders.csv` (operator_facing_input, 8718 bytes, sha256 `2D33E0D723C20A473C651EB7426534CF8A56DE99D748CE21A6F074CD290CD2F9`)
- `external_validation/method_reference_provenance.csv` (operator_facing_input, 7830 bytes, sha256 `7F6A5967DE10AC5A49200726082D0600A3EF70984B94DC414A35AA90BD97CCAC`)
- `external_validation/operator_record_sheet.csv` (operator_facing_input, 710130 bytes, sha256 `3286764C655EA1F5209A93A2D4C5596941EF22F621BA11282867F62C5D22785D`)
- `external_validation/pilot_smoke_packet.json` (operator_facing_input, 3268 bytes, sha256 `D70209BEC7554552BA799AEF79717DE0E660F49901240D36D27635EAA6E4B598`)
- `external_validation/pilot_smoke_packet.md` (operator_facing_input, 2089 bytes, sha256 `935DE117EF6D0DD1212A93296328CBAD0C0F91BEDBF9E50DB0E7F3672ABABDEC`)
- `external_validation/pilot_smoke_work_orders.csv` (operator_facing_input, 1033 bytes, sha256 `5F18D7641041AD7B7F9AD394AFE8A4CB7ADE880E2A0B6ECBA4A7F568DD821F3E`)
- `external_validation/platform_onboarding_packet.json` (operator_facing_input, 13337 bytes, sha256 `B274B3B3119EF0DBD1B4E9B9FAD55C3CF9646A9BC224876845741A9086297590`)
- `external_validation/platform_onboarding_packet.md` (operator_facing_input, 10459 bytes, sha256 `FF7709CBF3A3D9B33B80D8E567A1F94FED14B168F1EB7D0D920C1EDC893916E4`)
- `external_validation/platform_qualification_checklist.md` (operator_facing_input, 3275 bytes, sha256 `76F4BF45C6E2799185830A4EC0C0A2CED92556E5EED9B827915698CEF0012B4A`)
- `external_validation/reference_adapter_report.md` (operator_facing_input, 3098 bytes, sha256 `F64B68656335697769F9E7E60F19D974CF5D36D118D94B1296A7368CF49F4C2C`)
- `external_validation/rollout_evidence_packet.json` (operator_facing_input, 13301 bytes, sha256 `82AA510C884F7BA399C4707ADD453DE2A45FCD262EADDFEEE56C862A4371E2FC`)
- `external_validation/rollout_evidence_packet.md` (operator_facing_input, 4592 bytes, sha256 `279BC7FD9051008289B7D15E3EB59D59DB1815F0B8AA73003094008533AF2A5F`)
- `external_validation/rollout_evidence_work_orders.csv` (operator_facing_input, 4513 bytes, sha256 `C20FE327337FA1FC2988744B8DE9419F67BEBF4F4D0B10FDA2EB2BAD4CAAC642`)
- `external_validation/runner/README.md` (operator_facing_input, 4138 bytes, sha256 `80645DFB94931204E465763F3C91B7CBED3F144D1B3C3F15D7AD8386EE5BA7F1`)
- `external_validation/runner/backend_contract.py` (operator_facing_input, 3269 bytes, sha256 `724802B452269859B9F9686942CC9788A078B907EDD32EC9C857CF5A1427801A`)
- `external_validation/runner/backend_templates/__init__.py` (runner_backend_template, 81 bytes, sha256 `B0A9A94890CA8216D679695638C5C96A92303895686FCB56C8FC8B09239C9723`)
- `external_validation/runner/backend_templates/isaac_backend.py` (runner_backend_template, 296 bytes, sha256 `7E6DE08F8DBE31D379E03E8FB5233BABE98BE8C649D1FC2D46CDE711E50E40AE`)
- `external_validation/runner/backend_templates/maniskill_backend.py` (runner_backend_template, 299 bytes, sha256 `57C8C99918AF4480A1ABF1118B5FF38F738E0CAFF23B36D8376F40B18A4FC9FD`)
- `external_validation/runner/backend_templates/mujoco_robosuite_backend.py` (runner_backend_template, 299 bytes, sha256 `B67540FF5DF2ABB57CAAF30F6C58960E874CA82D13990899F8FF34892B5B7253`)
- `external_validation/runner/backend_templates/robot_lab_backend.py` (runner_backend_template, 304 bytes, sha256 `EE4971A48430683585DC4CA899A9C3BECA7659A70710F4E5E3A9439F1ED6EFB9`)
- `external_validation/runner/maniskill_reference_backend.py` (operator_facing_input, 21858 bytes, sha256 `3479C8AEA42FC8BCDFF30B8108AD70733136945748F02785A18100FAAEF3A255`)
- `external_validation/runner/real_collection_runner.py` (operator_facing_input, 15097 bytes, sha256 `E18DDE573F0269B387FADD3E3BC6BCCC4620A685000281D15FD50E8E184FB071`)
- `external_validation/statistical_analysis_plan.json` (operator_facing_input, 6430 bytes, sha256 `DD8E777F808918A3C6CFDA34CE5089DAE4DC5F2A32013FF24ECE1518DF54B7ED`)
- `external_validation/statistical_analysis_plan.md` (operator_facing_input, 2382 bytes, sha256 `DE86C46420657DE2449F902F3E18208E4FFD2DF615940CED17631E39F7E1F9C9`)
- `external_validation/task_cards/cable_route_insert.md` (task_card, 1388 bytes, sha256 `566488FB9C2DA53C06ED1A3E0CF4D1196D2504E841C97C470268F7AFFCAB034B`)
- `external_validation/task_cards/door_open_navigation.md` (task_card, 1391 bytes, sha256 `EDA0E523C3BF62F5215E18D3E782427F24FC316912221F2338719D98D5BF721E`)
- `external_validation/task_cards/drawer_to_pick_transfer.md` (task_card, 1377 bytes, sha256 `0C335887FC667DB914B0C95B05B3C4EAFEFAE1A01D99195E8DBF39FFD4A302FC`)
- `external_validation/task_cards/peg_place_regrasp.md` (task_card, 1372 bytes, sha256 `357F6A44637AD1D55E6E98775B60640FE0E7C0A32FE0C1707FC5863C00D3CDB9`)
- `results/external_acquisition_packet.json` (generated_non_evidence_report, 39339 bytes, sha256 `E99838D1A747A23C0A8C8BC661C30DCF158D9AB2ECF23EC1BAE3C29463F44271`)
- `results/external_acquisition_packet.md` (generated_non_evidence_report, 25910 bytes, sha256 `5E24E2FCB2617B12904B5261D79DEC38361DA554EAC0CDADFC0269880B1B3E42`)
- `results/external_adapter_contract_audit.json` (generated_non_evidence_report, 3130 bytes, sha256 `D61D6618070F133A1D7CC78921B0EDB9AF0EA4B8ED530745BAC9E5EC0BA2EC26`)
- `results/external_adapter_contract_audit.md` (generated_non_evidence_report, 2086 bytes, sha256 `B3D1ACCEBFCE1AEB4E3B7CECB567EB7E5070FD97517FB188DF4BA08B8F9DF0E3`)
- `results/external_adapter_scaffold_audit.json` (generated_non_evidence_report, 6541 bytes, sha256 `92A41EBF2DEE4066D5D294C8420492D6E4B934A1F1B601AD4CB8F90390AC2C4A`)
- `results/external_adapter_scaffold_audit.md` (generated_non_evidence_report, 2987 bytes, sha256 `F7F2A7E3738A610C9B878A36280BC507EC26D972DC0D0EDC01F77D2107681DC0`)
- `results/external_analysis_plan_audit.json` (generated_non_evidence_report, 3101 bytes, sha256 `231A2F04C087753A5C46D7707B363646F2E6221ECA97937D4DC6CDF1AD54692D`)
- `results/external_analysis_plan_audit.md` (generated_non_evidence_report, 2533 bytes, sha256 `7ABA403AF40670BDFC8B6FF5D9A896F090914669CB41F9BAEF0AC9FDEE6159B0`)
- `results/external_backend_contract_audit.json` (generated_non_evidence_report, 2747 bytes, sha256 `1FBD0B682B1767D97988FEDA2D3192ECBA78D27E5760A90FDDC8D38B7C268876`)
- `results/external_backend_contract_audit.md` (generated_non_evidence_report, 2159 bytes, sha256 `F92AE6D33D05582267F4D1F11D0886F6510B396E98A96C38C082043A8315601B`)
- `results/external_backend_integration_audit.json` (generated_non_evidence_report, 4055 bytes, sha256 `E1065972C68B0463D9E0DC234C4A7BA5A7C0D8F94A259A031CE0840C2C8CB4FB`)
- `results/external_backend_integration_audit.md` (generated_non_evidence_report, 3352 bytes, sha256 `BECF783C0C359AFFB01595162EFA704914CC300A0AAD4DB8B15E2CF4F34F1AA2`)
- `results/external_baseline_contract_audit.json` (generated_non_evidence_report, 5254 bytes, sha256 `3D6D8B08A0894F96387CB91CBB00BBF659527C18BD0D9EA8A35A480ED30AB70C`)
- `results/external_baseline_contract_audit.md` (generated_non_evidence_report, 2454 bytes, sha256 `5D214E40E4DCD0E680C8F63D327FE2CA33FDE99CF046E1D27A59BA1DFA7C7D30`)
- `results/external_blind_eval_audit.json` (generated_non_evidence_report, 1972 bytes, sha256 `BC754C10B0E0FBDAD9EEB57371302F4199EEBE49894149CA4C58405357A638BF`)
- `results/external_blind_eval_audit.md` (generated_non_evidence_report, 1183 bytes, sha256 `9EC804D278A6BEBB749B193C799210EEC6894349742C2D4363E877BF8D4A5B96`)
- `results/external_collection_plan.json` (generated_non_evidence_report, 147126 bytes, sha256 `B7E2EF5CD36F397464B7D660AD003F784E9FFA111F803D1FFFB7D9AE6BBD623A`)
- `results/external_collection_plan.md` (generated_non_evidence_report, 5530 bytes, sha256 `DCEDFA3B914A373BF93B9CABCD930AD8EFAE61029D2BD84DB61DC325230F536E`)
- `results/external_collection_readiness_audit.json` (generated_non_evidence_report, 4152 bytes, sha256 `5329616DDFF9F59D1FB6C8DABA214BCDC8FC0123093953AA187990C08B28128D`)
- `results/external_collection_readiness_audit.md` (generated_non_evidence_report, 2303 bytes, sha256 `2D035F57BDC9565C73537ACB55A001DBCFDA4D7635A5118FA4CFC7C5D4F34CCC`)
- `results/external_config_manifest_audit.json` (generated_non_evidence_report, 3471 bytes, sha256 `71888C39980962B4AAE8E67DC2338CEB8F2DBA603BC85DF0BF6B50BE7720EF92`)
- `results/external_config_manifest_audit.md` (generated_non_evidence_report, 2772 bytes, sha256 `C0F299190160578330B0923D01ABC38B9DEAD06CD291DE4EE16F3F8984837539`)
- `results/external_config_materialization_plan.json` (generated_non_evidence_report, 3186 bytes, sha256 `EB1436D71B2E51AA6117679956D4563284DB846A7A0C62E41AE2B4EFE0B02E5F`)
- `results/external_config_materialization_plan.md` (generated_non_evidence_report, 1976 bytes, sha256 `2C7F8786129C013277B149D934B1FD8CD964C03E88D7E5856DB5EDEEA5CFA6EC`)
- `results/external_config_template_audit.json` (generated_non_evidence_report, 1418 bytes, sha256 `364A4CEA5B063E5EA45A639D52E9EEE7628941F2722496D6A2E47CE787CA2106`)
- `results/external_config_template_audit.md` (generated_non_evidence_report, 797 bytes, sha256 `4CC337580323BADB03441EE8478DDDEF19CC9857F1B0B032264B78DB6A947DF7`)
- `results/external_evidence_preflight.json` (generated_non_evidence_report, 12344 bytes, sha256 `D163EA7B1E6DC2EFBBF26DC10C324A5CB76CD216BEB969C316D5A994F8DCE0B1`)
- `results/external_evidence_preflight.md` (generated_non_evidence_report, 4745 bytes, sha256 `B68911C22003E7E03E48D7486AB58F53AD10457F0C25ABCD47A134E37A247892`)
- `results/external_execution_readiness_audit.json` (generated_non_evidence_report, 32403 bytes, sha256 `887EFE40ADFE649792919A62D72C878C5CA925B0F4626D4BAAEE3DB669F1CE08`)
- `results/external_execution_readiness_audit.md` (generated_non_evidence_report, 25081 bytes, sha256 `FA6B7A2BA012D88EC18EE45AA31DCC76E2148355DDC68674078603BA8465C2D1`)
- `results/external_fidelity_acceptance_audit.json` (generated_non_evidence_report, 7157 bytes, sha256 `BDCB4A5BB6B441B3426803A5F18EBA003528818FBE3A303A324D95B9A20732F0`)
- `results/external_fidelity_acceptance_audit.md` (generated_non_evidence_report, 5313 bytes, sha256 `768F42B68BEE3F0FC7C0F5DE78EC3CD4FFFED70AB05FF4756838A4323A924422`)
- `results/external_fidelity_acceptance_draft_audit.json` (generated_non_evidence_report, 6107 bytes, sha256 `7D68263EDC1CEC914607AF3005C7565023BB0891C022503688B7A74A6AB3CC2F`)
- `results/external_fidelity_acceptance_draft_audit.md` (generated_non_evidence_report, 4980 bytes, sha256 `FAE32B6023D273425E9A561CFD92F52A32994F25A5435351C75163D9FD5527F3`)
- `results/external_fidelity_provenance_audit.json` (generated_non_evidence_report, 3802 bytes, sha256 `531EC1ED010CCCD2138237094ADE19E62C4B11260CB877EACE6EDD06D4117D18`)
- `results/external_fidelity_provenance_audit.md` (generated_non_evidence_report, 2986 bytes, sha256 `3EB901F308352BD9E61C6C82D2704448506BB2DDD3DFECB9373121F5CA607F67`)
- `results/external_method_implementation_audit.json` (generated_non_evidence_report, 4331 bytes, sha256 `A3A3235E819C3124BD968BD50EC8EF2AF8AFA6266845DC742B87D70C559A2CF3`)
- `results/external_method_implementation_audit.md` (generated_non_evidence_report, 3162 bytes, sha256 `D1CAC60300E4DAD7112597A98376BFAD58B94E3C96D115D04294F93D2C85271C`)
- `results/external_operator_packet.json` (generated_non_evidence_report, 37291 bytes, sha256 `C74F83BA61105C332C96826B5E7D34D459B3E9CB8604C447B349BBE635094BF1`)
- `results/external_operator_packet.md` (generated_non_evidence_report, 14335 bytes, sha256 `DB2EED259E49797348E7534E6B037B48D10324AF1CB70786229BB7E3FEE432F7`)
- `results/external_pairing_integrity_audit.json` (generated_non_evidence_report, 525 bytes, sha256 `D4ABAA9C2083D8B5932139DFEE0B1D79B4C7C97ACB9088C2E55245B26F624148`)
- `results/external_pairing_integrity_audit.md` (generated_non_evidence_report, 693 bytes, sha256 `4AD20017AC4F06A5B63E1D5CA3001F8EE9E7159739C99633C567109F1B37D7AD`)
- `results/external_pilot_smoke_audit.json` (generated_non_evidence_report, 1878 bytes, sha256 `6CFA9CB9774A330AD5F161218DE856240F13969CD36E6E5FDFCA80EBE4E9AF36`)
- `results/external_pilot_smoke_audit.md` (generated_non_evidence_report, 1203 bytes, sha256 `1DFC88D3CC0406275C0EAFA6FF5EADB8683515CF9D312C5DEADD4285688951CA`)
- `results/external_pilot_smoke_packet_audit.json` (generated_non_evidence_report, 3212 bytes, sha256 `8FA86BDA60C07FDDEE20AD497081DC299100302A15E751A3BEBBEEA15365C331`)
- `results/external_pilot_smoke_packet_audit.md` (generated_non_evidence_report, 1790 bytes, sha256 `684869BB5A12AB93D254C35B90856DEAD3BC8CA512ACC68DEF4D78F2CAFE39DA`)
- `results/external_platform_onboarding_audit.json` (generated_non_evidence_report, 8196 bytes, sha256 `C6660F4A749D41E0AB4FB07589526249EF12A0339FA54170648461BFECAF38D7`)
- `results/external_platform_onboarding_audit.md` (generated_non_evidence_report, 6381 bytes, sha256 `4F6DE951424279045E153C48055277689AF5FCE6FA12112C9B9743A6C796C748`)
- `results/external_platform_probe.json` (generated_non_evidence_report, 12121 bytes, sha256 `3FB3273B09C39CB246BA2722250C7338A5F8CB0A295974D937A6CBA96C82AF61`)
- `results/external_platform_probe.md` (generated_non_evidence_report, 2287 bytes, sha256 `9D0A853416C46561696F4CB8C2D03CA5D786E464951F39F0DEB787B2ED7924D1`)
- `results/external_reference_adapter_audit.json` (generated_non_evidence_report, 7424 bytes, sha256 `2E182A83556263635731AD6969E2976D0138B18056B562E9DF8E1AE2D6E0CB52`)
- `results/external_reference_adapter_audit.md` (generated_non_evidence_report, 2402 bytes, sha256 `E3B1EF1B04EDC6635605B205E7AE4AADACED64241281A5FCA1F12A26550DE0D6`)
- `results/external_release_package_audit.json` (generated_non_evidence_report, 490 bytes, sha256 `D760B589BD12AA51882D2C99B501475A6103FCABAFCF86A6E1744F9235E91278`)
- `results/external_release_package_audit.md` (generated_non_evidence_report, 521 bytes, sha256 `3AE844E453A4C34A902E906E950E7F0821B25C9DCA309DF7A957087EBB1589D6`)
- `results/external_rollout_evidence_audit.json` (generated_non_evidence_report, 3381 bytes, sha256 `4FFA079B4C7A67B4FC2F6E400D3FA70D1DC3101A4070FC15754FF9FC122B305F`)
- `results/external_rollout_evidence_audit.md` (generated_non_evidence_report, 2566 bytes, sha256 `89FE156606AD8BCE8B3174FA4A02DF006D5BD8E1A593E82636C00D115EF9FF86`)
- `results/external_runbook_audit.json` (generated_non_evidence_report, 3531 bytes, sha256 `66713C3D887EF6DA066B2991EC5AFA2545A2A0927E6AABE9B9614361065A1749`)
- `results/external_runbook_audit.md` (generated_non_evidence_report, 2061 bytes, sha256 `31D3C9077086EBA0564594FCB185F246761EAEF9E045BB1AF1E2694DE9C5947A`)
- `results/external_runner_harness_audit.json` (generated_non_evidence_report, 2617 bytes, sha256 `5B6926F8C6D48FA073DC31C9E7F1401A8586715BF55F2825065AD3DD9C2AC3A5`)
- `results/external_runner_harness_audit.md` (generated_non_evidence_report, 1879 bytes, sha256 `AFA9D2B06EC9B5E7A96D871165C35DC84EA2ECFC54AF09810A2D3094C9BA0F74`)
- `results/fidelity_acceptance_materialization_plan.json` (generated_non_evidence_report, 6746 bytes, sha256 `5CC2D08CD0911AF65B6C8DE52257CA8C46F02AF7C7B4C646B0E7D9EBF995FAE7`)
- `results/fidelity_acceptance_materialization_plan.md` (generated_non_evidence_report, 4702 bytes, sha256 `46403A20FDD14746DFDEF59015D1974CBFF02FC9E21DFF8C944758BA5E680E8C`)
- `results/independent_validation_route_audit.json` (generated_non_evidence_report, 8182 bytes, sha256 `279F757785C1226CADD5CB50240E20114859261FAEA0882F81BD594132F453F9`)
- `results/independent_validation_route_audit.md` (generated_non_evidence_report, 1807 bytes, sha256 `81BC82F771937391FE904EE175EAAE85AE78080C5866D5874092E8AD822C5CE1`)
- `results/maniskill_backend_readiness_audit.json` (generated_non_evidence_report, 4908 bytes, sha256 `95F64B7933F2045FA46934C3A11108586F309D75BC46FEC37EF8094A82551600`)
- `results/maniskill_backend_readiness_audit.md` (generated_non_evidence_report, 3057 bytes, sha256 `D0235D466AEF1F013CB1EB14E75691D5C34370E7B3D6360E7A736A94167DCCDD`)
- `results/maniskill_env_smoke_probe.json` (generated_non_evidence_report, 13636 bytes, sha256 `CA3B08871C1E212BF46C2168C27C6B95DAAFD81959DC07C55961BB6ED57F05CE`)
- `results/maniskill_env_smoke_probe.md` (generated_non_evidence_report, 2044 bytes, sha256 `7DE60A2FA9A7C2C2F73FD7D1021B4DB9AC0D676495EB99D482AA38C61BD97DAD`)
- `results/maniskill_fidelity_metadata_probe.json` (generated_non_evidence_report, 34325 bytes, sha256 `4C588E6BD1777BB32E5E1CA09AFDF831E53CC9CE7A2740516B569113BCE293B6`)
- `results/maniskill_fidelity_metadata_probe.md` (generated_non_evidence_report, 3204 bytes, sha256 `0A63990319D5C3518BF802412F526D441A022AB1AE542D8A5EE6F18C40F9CCC6`)
- `results/maniskill_pilot_runtime_liveness_audit.json` (generated_non_evidence_report, 3793 bytes, sha256 `9A07316CD06D83D6C731C0596DAF7C027558A43F73542100A4690919647EA57E`)
- `results/maniskill_pilot_runtime_liveness_audit.md` (generated_non_evidence_report, 2586 bytes, sha256 `0C58ECB14FC5D3D5750D5EEA2204A10D44A90702FC4B03D67DD67CBB1DB7F71B`)
- `results/maniskill_reference_collection_preflight_audit.json` (generated_non_evidence_report, 4062 bytes, sha256 `327EE4D89B2EA6C6F5609818DE533465BB53693FD4D3A502EDB0CEC3EB9F5F06`)
- `results/maniskill_reference_collection_preflight_audit.md` (generated_non_evidence_report, 1325 bytes, sha256 `28691987D608EA40FA50EBD7BCA64E7240E5583DCEDFC72E729829EDDF35F942`)
- `results/maniskill_render_video_preflight_audit.json` (generated_non_evidence_report, 38170 bytes, sha256 `2EF5249F6B839E90773F76A267468D576079145481730CA04DF619C33E845A45`)
- `results/maniskill_render_video_preflight_audit.md` (generated_non_evidence_report, 6047 bytes, sha256 `481874C9DC33E3B17F0FFD0F570F84C9895E586B45ECE44339D2FB562A08D848`)
- `results/maniskill_task_binding_probe.json` (generated_non_evidence_report, 9710 bytes, sha256 `8B2BADB696E8A8E5FC9E867EC6D11A9DB89F8D1017CEA54E1B6AA3086DCD3C17`)
- `results/maniskill_task_binding_probe.md` (generated_non_evidence_report, 1844 bytes, sha256 `8F529132821A124537E0C2DBD170E5865F8E8E4426124A82F310D83BF5B1E6AD`)
- `scripts/audit_external_backend_contract.py` (operator_command_source, 15394 bytes, sha256 `6A2A65A7AA73B04C438AFF9B85115589397D8DDF3496A93632E7A178D7230E4C`)
- `scripts/audit_external_collection_readiness.py` (operator_command_source, 15559 bytes, sha256 `D57C161EF11EEC793D785A336514D1CEBB0A4E6691FFFEE5CEE70AA6C5384828`)
- `scripts/audit_external_evidence.py` (operator_command_source, 25791 bytes, sha256 `5ADA192E92BA159F1E3EC96FDE31818546F8350F200B804B53D40601EDE64CC8`)
- `scripts/audit_external_fidelity_acceptance.py` (operator_command_source, 17816 bytes, sha256 `896A4DD0B7A4E5012FB347F9810F24235611515FF1A9488D3B9FE07823E4A40E`)
- `scripts/audit_external_pairing_integrity.py` (operator_command_source, 13495 bytes, sha256 `237BF15844DA317A1B86A64312986A583D3A27987DB075537F6B44B8A014C0DB`)
- `scripts/audit_external_pilot_smoke.py` (operator_command_source, 10042 bytes, sha256 `13BB2E31C5E8331D1C53B5E060E399FEB83C520FC83AF91FA350FC591D417C25`)
- `scripts/audit_external_release_package.py` (operator_command_source, 9195 bytes, sha256 `C7AAE093CBACD927A3803C328DDCD5316F5A624842FDCF8C9E30F878AD5D6804`)
- `scripts/audit_maniskill_backend_readiness.py` (operator_command_source, 9758 bytes, sha256 `B7A7DF42D33DF948872B373A35423AF97B1AD2F1B2A0409B22A725116D8C9F0B`)
- `scripts/audit_maniskill_pilot_runtime_liveness.py` (operator_command_source, 17928 bytes, sha256 `1CEC8D61C0FA61F29988E20A87AF81BCE1A2A7EA83E90024DCA488BC818AD862`)
- `scripts/audit_maniskill_reference_collection_preflight.py` (operator_command_source, 8466 bytes, sha256 `A9B57E8629AF6556AF8BB31B0CD10081E1BA1BEC5FBB1178650CD587FDFFAD7B`)
- `scripts/audit_maniskill_render_video_preflight.py` (operator_command_source, 23862 bytes, sha256 `9DC6E8E4FD2FCAD45BB9AFBD318AADA10BA990C2D4FB43BA45F1FEFE9CCD7D74`)
- `scripts/build_external_acquisition_packet.py` (operator_command_source, 64223 bytes, sha256 `9517BA3995CA1FEDAFFC86F147850F430C61091D963903AE23FC61EDC3503246`)
- `scripts/build_external_analysis_plan.py` (operator_command_source, 16556 bytes, sha256 `58146063D30C8D028FF8307AC787B7B5CDE73628949E2BEE1E2042AF46895869`)
- `scripts/build_external_backend_integration_packet.py` (operator_command_source, 19894 bytes, sha256 `9BB1413B2D478C383C0F77FB32D83F645B6B506EF65B8F6DB6A6FA760D22DAAA`)
- `scripts/build_external_config_manifest_packet.py` (operator_command_source, 20688 bytes, sha256 `3A7C195E4C4841C3C4C368326E7A1E09E1A10DFBD27A76CE6EDF541F34C9B1E8`)
- `scripts/build_external_fidelity_acceptance_draft.py` (operator_command_source, 40250 bytes, sha256 `03AC359424B54D42E5724BBEE7D8B56EA4A844E09A99DA6752FF38F6E130F764`)
- `scripts/build_external_fidelity_provenance_packet.py` (operator_command_source, 22331 bytes, sha256 `0F61DEC8809A6636131EE22680355EED2A4A02533F9C06ED824229152C0B7F18`)
- `scripts/build_external_manifest.py` (operator_command_source, 31129 bytes, sha256 `D5683DCE578A7CA7218AE9B1FBC7024B83B3D5D30E5225A30A02E0EDF92C4DF8`)
- `scripts/build_external_method_implementation_packet.py` (operator_command_source, 28878 bytes, sha256 `D5E4F2BB3EE78EA2D6324414EE9397788AE0A685FEA6FA8ED6248F3CE9AD819B`)
- `scripts/build_external_operator_handoff_bundle.py` (operator_command_source, 50281 bytes, sha256 `9D6A287405882681DFBBD08947483B6B64DE7EA9B3D7E6F0765A7437D50D7F99`)
- `scripts/build_external_operator_packet.py` (operator_command_source, 33217 bytes, sha256 `C332146A5532841394B64CBFB68CDF1DB1FF1338973A4B7CEE672F3A93263A72`)
- `scripts/build_external_pilot_smoke_packet.py` (operator_command_source, 11266 bytes, sha256 `F3A2D24716D7DCE1D337453137191E821E1F81ADBAA8ABF446C2446E489C00CE`)
- `scripts/build_external_platform_onboarding.py` (operator_command_source, 31790 bytes, sha256 `671A747E75A90369A6DBF89537119FD649E4501EC02F0D860B13E06355748414`)
- `scripts/build_external_rollout_evidence_packet.py` (operator_command_source, 22665 bytes, sha256 `E273634CCB595A0952C81F83B65355BDCDE61596F02B6BC390A268462377C611`)
- `scripts/materialize_external_configs.py` (operator_command_source, 12746 bytes, sha256 `EA207DCFDCCC9593CBFEC993C22D3EDA8F493124D1EBEB6A240D793C4AC80A25`)
- `scripts/materialize_fidelity_acceptance.py` (operator_command_source, 18376 bytes, sha256 `2EA9A97E8491370A52054A19CEEC6292F6D1CFFAF4E16851CB56EC88A27485EF`)
- `scripts/probe_external_platform.py` (operator_command_source, 14122 bytes, sha256 `67456EAE975E43F2D87B7233670D57D5E353C7034E2636E500BB3B38806C05DC`)
- `scripts/probe_maniskill_env_smoke.py` (operator_command_source, 18252 bytes, sha256 `CAD9777638492EDE99F187BCFF89E1CAE85024FE5FEE8D7374AFBFC2516D4F02`)
- `scripts/probe_maniskill_fidelity_metadata.py` (operator_command_source, 21099 bytes, sha256 `2EC0606C2AAF6E7C9B298B202748005D563BD47C5DDCC88F060A657B52DF88AB`)
- `scripts/probe_maniskill_task_bindings.py` (operator_command_source, 12426 bytes, sha256 `AC9A26FDA7512B17AD35589525DF3A41E7C5CF28C164850C4F835466C69D92E2`)
- `scripts/validate_external_adapters.py` (operator_command_source, 23706 bytes, sha256 `CD62A588525DAEEE146D19C38DADCD7B4A5020FE07B513347B547AC58C17D27D`)
- `scripts/validate_external_configs.py` (operator_command_source, 13456 bytes, sha256 `E4875A2327A767BB52D09C05B31D1625CB1B888A8E9DA657CBB4FEAA0C736467`)
- `scripts/validate_external_rollouts.py` (operator_command_source, 17713 bytes, sha256 `C1477292CEC690F82C6EBD536F3F2531BFE736E891F0EA44D8E6584C5C8385FD`)

## Checks

- `pass` `operator_packet_is_no_go_non_evidence`: start_state='DO_NOT_COLLECT_YET', strict_evidence_ready=False
- `pass` `acquisition_maps_all_remaining_blockers`: missing_requirements=4
- `pass` `strict_evidence_gates_remain_fail_closed`: analysis=False, onboarding=False, reference_backend_official=False, preflight=False, release=False, pairing=False
- `pass` `bundle_files_exist`: missing=[], total_missing=0
- `pass` `bundle_excludes_rollout_evidence_artifacts`: forbidden_included=[]
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `handoff_has_task_config_and_baseline_assets`: category_counts={'baseline_spec': 12, 'config_template': 4, 'generated_non_evidence_report': 78, 'operator_command_source': 33, 'operator_facing_input': 54, 'prepared_config_input': 4, 'reference_adapter': 60, 'runner_backend_template': 5, 'task_card': 4}
- `pass` `analysis_plan_included`: analysis_plan_ready=True, strict_evidence_ready=False
- `pass` `platform_onboarding_included`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `fidelity_metadata_probe_included`: strict_metadata_ready=True, primary_metadata_missing=[]
- `pass` `fidelity_provenance_packet_included`: fidelity_provenance_packet_ready=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_acceptance_draft_included`: draft_ready=True, remaining_operator_inputs=10, acceptance_ready=False
- `pass` `fidelity_acceptance_materializer_included`: write_enabled=False, acceptance_write_ready=False
- `pass` `backend_integration_packet_included`: backend_integration_packet_ready=True, strict_backend_ready=False
- `pass` `maniskill_reference_backend_included`: backend_contract_ready=True, video_writer_ready=True, official_collection_ready=False
- `pass` `maniskill_reference_collection_preflight_included`: contract_ready=True, collection_ready=False, blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `config_manifest_packet_included`: config_manifest_packet_ready=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `rollout_evidence_packet_included`: rollout_evidence_packet_ready=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `pilot_smoke_packet_included`: pilot_smoke_packet_ready=True, strict_evidence_ready=False
- `pass` `maniskill_render_video_preflight_included`: render_video_ready=False, env_count=4, blocking=['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; OpenCabinetDrawer-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; OpenCabinetDoor-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory; PullCubeTool-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory']
- `pass` `maniskill_pilot_runtime_liveness_included`: pilot_runtime_ready=False, runner_io_ready=True, render_video_ready=False, timed_out=False, records=1, videos=1, diagnostic_fallbacks=1, failure_summary='runner wrote quarantined schema-valid row/video using diagnostic non-evidence video fallback; render-backed video remains unavailable'
- `pass` `method_implementation_packet_included`: method_implementation_packet_ready=True, strict_adapter_evidence_ready=False
- `pass` `operator_actions_cover_evidence_collection`: missing=[]
- `pass` `post_collection_commands_cover_strict_gates`: commands=8
- `pass` `file_hashes_are_recorded`: hashed_files=254
