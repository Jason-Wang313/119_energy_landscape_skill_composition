# External Operator Handoff Bundle

Passed: `true`.
Not evidence: `true`.
Strict evidence ready: `false`.
Start state: `DO_NOT_COLLECT_YET`.
Included files: `218`.

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
- `generated_non_evidence_report`: `58`
- `operator_command_source`: `23`
- `operator_facing_input`: `48`
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

- `README.md` (operator_facing_input, 13359 bytes, sha256 `6C12DB9AF2B8DC237DA103762907BCF285BEA8AC24460985F6DFA6FE360B1268`)
- `docs/haonan_yilun_outreach_package.md` (operator_facing_input, 10500 bytes, sha256 `F6F46A389ACE8C9FF527034AA12CCB88CCCE98763CEACDCE15C2FBE4A3730FBF`)
- `docs/independent_validation_protocol.md` (operator_facing_input, 21347 bytes, sha256 `AD9BFC5B473586D61A60EF9AE60E07AB60F81783D3BD7DD22421C910B2E8DB5E`)
- `docs/reproducibility_checklist.md` (operator_facing_input, 14688 bytes, sha256 `05032C3C17DD4491C67672780BE343BEA357377536D7F06F31FC7DF09BF30297`)
- `docs/submission_readiness_decision.md` (operator_facing_input, 4757 bytes, sha256 `8EFCB2D0D377E474DBF719CF1A8B4F9530738311349436EBE9EDBF51FF1CE21E`)
- `external_validation/README.md` (operator_facing_input, 25917 bytes, sha256 `559F3D5E43FEA391030B39AEE0FD72B5E4B3F4D16BC4B54461ABD17A64F57177`)
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
- `external_validation/collection_runbook.md` (operator_facing_input, 3943 bytes, sha256 `D9BE952620E7EE35DEAE630A4A81DCA56B42C44D2095B7A996D8B7B3A98B98F1`)
- `external_validation/config_manifest_packet.json` (operator_facing_input, 9996 bytes, sha256 `4BBC0D288C9642336249A57C94F8B00691525C6D0E707CBD2748B145938A12F0`)
- `external_validation/config_manifest_packet.md` (operator_facing_input, 5369 bytes, sha256 `1A2733FBA14EC0FD157C29AC6381DF6186165FEE610B1D934084B40CDC19DBF6`)
- `external_validation/config_manifest_work_orders.csv` (operator_facing_input, 3406 bytes, sha256 `A49F99D98E2CC167A0880B9BD86DB5857B5FC99B74E6F1FECEC401B81DE3FCF7`)
- `external_validation/config_schema_v1.json` (operator_facing_input, 1823 bytes, sha256 `6936B85F4D47F87CC509E272E37F577BD3FF2EC0B505EEAEE0C3180207189573`)
- `external_validation/config_templates/cable_route_insert.json` (config_template, 1590 bytes, sha256 `2CE483630DF76B8CCADC2E5C051C5AF6C37473A70C43979C170C8BD4C2038C75`)
- `external_validation/config_templates/door_open_navigation.json` (config_template, 1591 bytes, sha256 `29BA40F9BC94F385814E489F56FB99FFE39E228F22268FF9DE46AD241DCA461D`)
- `external_validation/config_templates/drawer_to_pick_transfer.json` (config_template, 1574 bytes, sha256 `A9DCD9D9A117607982ED7D6A51D1626091CA45FE76CAD91059B94327C208E727`)
- `external_validation/config_templates/peg_place_regrasp.json` (config_template, 1575 bytes, sha256 `5F8C51F458A125A00FB60A461E5ABCD190EAC710660A1D9D71FD3E4159098F9C`)
- `external_validation/configs/README.md` (operator_facing_input, 1442 bytes, sha256 `A54334B0AA891AAE8D43FB8A44360433713A59D067B999E52FAC5E2E6F1AF156`)
- `external_validation/configs/cable_route_insert.json` (prepared_config_input, 1502 bytes, sha256 `15D687A12F9213E1EB410876203CE93F73E667C30E039685E151438017B3D7AD`)
- `external_validation/configs/door_open_navigation.json` (prepared_config_input, 1503 bytes, sha256 `39697F0BA1ECBE013C1790455F26B68C927EEF97415A2BB49C6FD1440DEBEA9C`)
- `external_validation/configs/drawer_to_pick_transfer.json` (prepared_config_input, 1486 bytes, sha256 `EABEA38D21F936A46C69E566D0324F7C42A8693CAA1D441B81C7E87B595FCA0D`)
- `external_validation/configs/peg_place_regrasp.json` (prepared_config_input, 1487 bytes, sha256 `8D041F5E869F4D81E2352D77A01C85EE585DF2040E45987750DF84B86EA94086`)
- `external_validation/fidelity_acceptance_template.json` (operator_facing_input, 4582 bytes, sha256 `0BED23F5E73145C7D3283605C0EFDCCF0970CBC989CAAC6DF4E45445D30496E0`)
- `external_validation/fidelity_provenance_packet.json` (operator_facing_input, 12922 bytes, sha256 `7AF17664BD85D35BA25CAE9BD591B2B03CC9DA793915E802E6C48EC8D7E20A76`)
- `external_validation/fidelity_provenance_packet.md` (operator_facing_input, 2636 bytes, sha256 `C6E6CBE038B035209EAAFAFE4F4C0B354BBE139C94B4C1B87153F6BF6A1C7D16`)
- `external_validation/fidelity_provenance_work_orders.csv` (operator_facing_input, 6268 bytes, sha256 `D43A559C22123A09867A23519CB7A27BC08DA9C9E976E9B42E2AEE7482DF2142`)
- `external_validation/independent_validation_route.md` (operator_facing_input, 7270 bytes, sha256 `10B4246BF3F6F32F052E89EACD2FE1CB7CB2CB9ACB8C77876CF88915EFBA3379`)
- `external_validation/independent_validation_route_matrix.csv` (operator_facing_input, 2115 bytes, sha256 `02E059F84400B4054939012707D7FD43A6F4BDAF3CEF5560A760CBD06BBAAB4E`)
- `external_validation/log_schema_v1.json` (operator_facing_input, 3055 bytes, sha256 `BF2194D543F83448F03BBD9ADB5310C9BDE7313228EA876BE7FE75CD788A4917`)
- `external_validation/method_alias_map.json` (operator_facing_input, 3261 bytes, sha256 `B56A11CB20914B2FD2649DA647F7722DE43D6B04DE3E89704A8CD3F952A4E031`)
- `external_validation/method_implementation_packet.json` (operator_facing_input, 30341 bytes, sha256 `204CEB4C21FE47243E725D6F22A80B1129B73674BB3FE421FAFE89CF0142FCA2`)
- `external_validation/method_implementation_packet.md` (operator_facing_input, 11808 bytes, sha256 `4D5984349CBBD00EE0AE33B1373BDBC16532C4D1CC55D0FAC64A633B5ABD719B`)
- `external_validation/method_implementation_work_orders.csv` (operator_facing_input, 8334 bytes, sha256 `76AF1F73B62B0DA469EB8D59195D52246399AB74387D8217D922BA29338AA11A`)
- `external_validation/operator_record_sheet.csv` (operator_facing_input, 710130 bytes, sha256 `3286764C655EA1F5209A93A2D4C5596941EF22F621BA11282867F62C5D22785D`)
- `external_validation/pilot_smoke_packet.json` (operator_facing_input, 3268 bytes, sha256 `D70209BEC7554552BA799AEF79717DE0E660F49901240D36D27635EAA6E4B598`)
- `external_validation/pilot_smoke_packet.md` (operator_facing_input, 2089 bytes, sha256 `935DE117EF6D0DD1212A93296328CBAD0C0F91BEDBF9E50DB0E7F3672ABABDEC`)
- `external_validation/pilot_smoke_work_orders.csv` (operator_facing_input, 1033 bytes, sha256 `5F18D7641041AD7B7F9AD394AFE8A4CB7ADE880E2A0B6ECBA4A7F568DD821F3E`)
- `external_validation/platform_onboarding_packet.json` (operator_facing_input, 9129 bytes, sha256 `B86546D506529D20AAB4D844B74093D1783259676A80781E6873D68A81619041`)
- `external_validation/platform_onboarding_packet.md` (operator_facing_input, 7014 bytes, sha256 `13684E95CC64693041910012FD6FB96A2EFCDD59F536B40F33B98A1659CF0B4B`)
- `external_validation/platform_qualification_checklist.md` (operator_facing_input, 3275 bytes, sha256 `76F4BF45C6E2799185830A4EC0C0A2CED92556E5EED9B827915698CEF0012B4A`)
- `external_validation/reference_adapter_report.md` (operator_facing_input, 2987 bytes, sha256 `525DB17402A642EA131C1FD5BC69B3DEEC90248A5A58BE891119DEFD4B01E696`)
- `external_validation/rollout_evidence_packet.json` (operator_facing_input, 13301 bytes, sha256 `82AA510C884F7BA399C4707ADD453DE2A45FCD262EADDFEEE56C862A4371E2FC`)
- `external_validation/rollout_evidence_packet.md` (operator_facing_input, 4592 bytes, sha256 `279BC7FD9051008289B7D15E3EB59D59DB1815F0B8AA73003094008533AF2A5F`)
- `external_validation/rollout_evidence_work_orders.csv` (operator_facing_input, 4513 bytes, sha256 `C20FE327337FA1FC2988744B8DE9419F67BEBF4F4D0B10FDA2EB2BAD4CAAC642`)
- `external_validation/runner/README.md` (operator_facing_input, 2701 bytes, sha256 `8ABB774A04DBD8DBA24902251F234504E5990B3EDDAF59C3D690E10480B5F637`)
- `external_validation/runner/backend_contract.py` (operator_facing_input, 3269 bytes, sha256 `724802B452269859B9F9686942CC9788A078B907EDD32EC9C857CF5A1427801A`)
- `external_validation/runner/backend_templates/__init__.py` (runner_backend_template, 81 bytes, sha256 `B0A9A94890CA8216D679695638C5C96A92303895686FCB56C8FC8B09239C9723`)
- `external_validation/runner/backend_templates/isaac_backend.py` (runner_backend_template, 296 bytes, sha256 `7E6DE08F8DBE31D379E03E8FB5233BABE98BE8C649D1FC2D46CDE711E50E40AE`)
- `external_validation/runner/backend_templates/maniskill_backend.py` (runner_backend_template, 299 bytes, sha256 `57C8C99918AF4480A1ABF1118B5FF38F738E0CAFF23B36D8376F40B18A4FC9FD`)
- `external_validation/runner/backend_templates/mujoco_robosuite_backend.py` (runner_backend_template, 299 bytes, sha256 `B67540FF5DF2ABB57CAAF30F6C58960E874CA82D13990899F8FF34892B5B7253`)
- `external_validation/runner/backend_templates/robot_lab_backend.py` (runner_backend_template, 304 bytes, sha256 `EE4971A48430683585DC4CA899A9C3BECA7659A70710F4E5E3A9439F1ED6EFB9`)
- `external_validation/runner/real_collection_runner.py` (operator_facing_input, 15097 bytes, sha256 `E18DDE573F0269B387FADD3E3BC6BCCC4620A685000281D15FD50E8E184FB071`)
- `external_validation/statistical_analysis_plan.json` (operator_facing_input, 6430 bytes, sha256 `DD8E777F808918A3C6CFDA34CE5089DAE4DC5F2A32013FF24ECE1518DF54B7ED`)
- `external_validation/statistical_analysis_plan.md` (operator_facing_input, 2382 bytes, sha256 `DE86C46420657DE2449F902F3E18208E4FFD2DF615940CED17631E39F7E1F9C9`)
- `external_validation/task_cards/cable_route_insert.md` (task_card, 1388 bytes, sha256 `566488FB9C2DA53C06ED1A3E0CF4D1196D2504E841C97C470268F7AFFCAB034B`)
- `external_validation/task_cards/door_open_navigation.md` (task_card, 1391 bytes, sha256 `EDA0E523C3BF62F5215E18D3E782427F24FC316912221F2338719D98D5BF721E`)
- `external_validation/task_cards/drawer_to_pick_transfer.md` (task_card, 1377 bytes, sha256 `0C335887FC667DB914B0C95B05B3C4EAFEFAE1A01D99195E8DBF39FFD4A302FC`)
- `external_validation/task_cards/peg_place_regrasp.md` (task_card, 1372 bytes, sha256 `357F6A44637AD1D55E6E98775B60640FE0E7C0A32FE0C1707FC5863C00D3CDB9`)
- `results/external_acquisition_packet.json` (generated_non_evidence_report, 23594 bytes, sha256 `20A7D0C18F627EE8129BE5088E1B8035A20BBB7DD20A9BC081A202B5731B8D8C`)
- `results/external_acquisition_packet.md` (generated_non_evidence_report, 15843 bytes, sha256 `DDD4A9342BE6B0364E3DEFCE45C2A4CCE7FFCF987D32765A84514D4374A1A7C4`)
- `results/external_adapter_contract_audit.json` (generated_non_evidence_report, 3130 bytes, sha256 `D61D6618070F133A1D7CC78921B0EDB9AF0EA4B8ED530745BAC9E5EC0BA2EC26`)
- `results/external_adapter_contract_audit.md` (generated_non_evidence_report, 2081 bytes, sha256 `A0F6DCFD392001050CB3999D1992FB8B365C8766FE3001F25B2BC5C64DC694DD`)
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
- `results/external_collection_plan.json` (generated_non_evidence_report, 145820 bytes, sha256 `371D7B68DED4A475D9AB785BEB9785F3E50ADA46289CE4A1C7137E2C206D715D`)
- `results/external_collection_plan.md` (generated_non_evidence_report, 4288 bytes, sha256 `8DFB16FE7CAA1F0287D6EC494F20DB680F80DCD02E28A59981A85E7318019041`)
- `results/external_collection_readiness_audit.json` (generated_non_evidence_report, 4152 bytes, sha256 `5329616DDFF9F59D1FB6C8DABA214BCDC8FC0123093953AA187990C08B28128D`)
- `results/external_collection_readiness_audit.md` (generated_non_evidence_report, 2303 bytes, sha256 `2D035F57BDC9565C73537ACB55A001DBCFDA4D7635A5118FA4CFC7C5D4F34CCC`)
- `results/external_config_manifest_audit.json` (generated_non_evidence_report, 3329 bytes, sha256 `FADE1CF1343AA5DD13AE8E849FC6EF64F7402784A3AA1EE7E80AA9E696904DAF`)
- `results/external_config_manifest_audit.md` (generated_non_evidence_report, 2692 bytes, sha256 `8983B4D5E441C849E10537F87A4006FB8805E862D0EAFD66824E6BFD492CA68C`)
- `results/external_config_materialization_plan.json` (generated_non_evidence_report, 2945 bytes, sha256 `5B6D82E89D0EA1E3064FE9582974189C2F8C425CF945FC408030279685891D73`)
- `results/external_config_materialization_plan.md` (generated_non_evidence_report, 1873 bytes, sha256 `324C49D2E2F1B4772F8979E3C4E5FBA04B813A9D05FCADAF32DBD09121D9A887`)
- `results/external_config_template_audit.json` (generated_non_evidence_report, 1418 bytes, sha256 `364A4CEA5B063E5EA45A639D52E9EEE7628941F2722496D6A2E47CE787CA2106`)
- `results/external_config_template_audit.md` (generated_non_evidence_report, 797 bytes, sha256 `4CC337580323BADB03441EE8478DDDEF19CC9857F1B0B032264B78DB6A947DF7`)
- `results/external_evidence_preflight.json` (generated_non_evidence_report, 12344 bytes, sha256 `D163EA7B1E6DC2EFBBF26DC10C324A5CB76CD216BEB969C316D5A994F8DCE0B1`)
- `results/external_evidence_preflight.md` (generated_non_evidence_report, 4745 bytes, sha256 `B68911C22003E7E03E48D7486AB58F53AD10457F0C25ABCD47A134E37A247892`)
- `results/external_execution_readiness_audit.json` (generated_non_evidence_report, 26931 bytes, sha256 `C51925E76F65F73B16D7918E11735D2B515F351E7CE8E7F330971CBE55691E2D`)
- `results/external_execution_readiness_audit.md` (generated_non_evidence_report, 20545 bytes, sha256 `072DEC2DB289B2F3954E5E8F3B2D0942D24CB94F19076FCFE35B9B6AD4018D21`)
- `results/external_fidelity_acceptance_audit.json` (generated_non_evidence_report, 7157 bytes, sha256 `BDCB4A5BB6B441B3426803A5F18EBA003528818FBE3A303A324D95B9A20732F0`)
- `results/external_fidelity_acceptance_audit.md` (generated_non_evidence_report, 5313 bytes, sha256 `768F42B68BEE3F0FC7C0F5DE78EC3CD4FFFED70AB05FF4756838A4323A924422`)
- `results/external_fidelity_provenance_audit.json` (generated_non_evidence_report, 2793 bytes, sha256 `48A591C5C0AE0AAC65906B97EDD00EC8AC462AFF2EFB9F8A9AFA986C6B25791E`)
- `results/external_fidelity_provenance_audit.md` (generated_non_evidence_report, 2041 bytes, sha256 `C6FA590A031FE943C38C5548CFE1927103CF75A459E6E55B450DD8D392077E37`)
- `results/external_method_implementation_audit.json` (generated_non_evidence_report, 2523 bytes, sha256 `41840782DC3EB5F94401B7771DCE32581B62CBAED0CBC2DADD5BDFB0406ACA63`)
- `results/external_method_implementation_audit.md` (generated_non_evidence_report, 1912 bytes, sha256 `428B997AE9D07EF6B24950444186AAC256634822B715B632D2BC4F2451C2C2E1`)
- `results/external_operator_packet.json` (generated_non_evidence_report, 19118 bytes, sha256 `13B1BE6315C03F7B1AE6C1D6E3C80AAF7A574C7921970EDCCBB8DC18DE3290C5`)
- `results/external_operator_packet.md` (generated_non_evidence_report, 5777 bytes, sha256 `C1A2137DF628B43F7ADE057FC731A008C40509721F8F3C707EC329A66A7DF609`)
- `results/external_pairing_integrity_audit.json` (generated_non_evidence_report, 525 bytes, sha256 `D4ABAA9C2083D8B5932139DFEE0B1D79B4C7C97ACB9088C2E55245B26F624148`)
- `results/external_pairing_integrity_audit.md` (generated_non_evidence_report, 693 bytes, sha256 `4AD20017AC4F06A5B63E1D5CA3001F8EE9E7159739C99633C567109F1B37D7AD`)
- `results/external_pilot_smoke_audit.json` (generated_non_evidence_report, 1878 bytes, sha256 `6CFA9CB9774A330AD5F161218DE856240F13969CD36E6E5FDFCA80EBE4E9AF36`)
- `results/external_pilot_smoke_audit.md` (generated_non_evidence_report, 1203 bytes, sha256 `1DFC88D3CC0406275C0EAFA6FF5EADB8683515CF9D312C5DEADD4285688951CA`)
- `results/external_pilot_smoke_packet_audit.json` (generated_non_evidence_report, 3212 bytes, sha256 `8FA86BDA60C07FDDEE20AD497081DC299100302A15E751A3BEBBEEA15365C331`)
- `results/external_pilot_smoke_packet_audit.md` (generated_non_evidence_report, 1790 bytes, sha256 `684869BB5A12AB93D254C35B90856DEAD3BC8CA512ACC68DEF4D78F2CAFE39DA`)
- `results/external_platform_onboarding_audit.json` (generated_non_evidence_report, 4807 bytes, sha256 `2DE9FE5A3492C3A47BA00A4E562CDDE9D694602F5B212B40F76F54A4FBAF174A`)
- `results/external_platform_onboarding_audit.md` (generated_non_evidence_report, 3512 bytes, sha256 `DCEA83DEB28B60647F4497B2B6F108566EB9674CA661771FDC38649E3026A3A4`)
- `results/external_reference_adapter_audit.json` (generated_non_evidence_report, 7221 bytes, sha256 `C341090F0BC92E54D21475C79ADB505D32F073A222FFD3954498747F292EEF9E`)
- `results/external_reference_adapter_audit.md` (generated_non_evidence_report, 2169 bytes, sha256 `744DB8DDE3E8D1F48EBFD5B6D4E2619A0EFC963937423D1007376F673B68E191`)
- `results/external_release_package_audit.json` (generated_non_evidence_report, 490 bytes, sha256 `D760B589BD12AA51882D2C99B501475A6103FCABAFCF86A6E1744F9235E91278`)
- `results/external_release_package_audit.md` (generated_non_evidence_report, 521 bytes, sha256 `3AE844E453A4C34A902E906E950E7F0821B25C9DCA309DF7A957087EBB1589D6`)
- `results/external_rollout_evidence_audit.json` (generated_non_evidence_report, 3381 bytes, sha256 `4FFA079B4C7A67B4FC2F6E400D3FA70D1DC3101A4070FC15754FF9FC122B305F`)
- `results/external_rollout_evidence_audit.md` (generated_non_evidence_report, 2566 bytes, sha256 `89FE156606AD8BCE8B3174FA4A02DF006D5BD8E1A593E82636C00D115EF9FF86`)
- `results/external_runbook_audit.json` (generated_non_evidence_report, 2160 bytes, sha256 `FDDDDCED20BAD8BFA15A82467C5DE0ADF9D3D2BBFACAE4B6387C1BD517ED9B3A`)
- `results/external_runbook_audit.md` (generated_non_evidence_report, 1425 bytes, sha256 `2E23CAC4EEBACF8FB9A88A1D3ED1F3731A8843FAE7D011AF2CAF108E8BFCAF5E`)
- `results/external_runner_harness_audit.json` (generated_non_evidence_report, 2617 bytes, sha256 `5B6926F8C6D48FA073DC31C9E7F1401A8586715BF55F2825065AD3DD9C2AC3A5`)
- `results/external_runner_harness_audit.md` (generated_non_evidence_report, 1879 bytes, sha256 `AFA9D2B06EC9B5E7A96D871165C35DC84EA2ECFC54AF09810A2D3094C9BA0F74`)
- `results/independent_validation_route_audit.json` (generated_non_evidence_report, 8182 bytes, sha256 `279F757785C1226CADD5CB50240E20114859261FAEA0882F81BD594132F453F9`)
- `results/independent_validation_route_audit.md` (generated_non_evidence_report, 1807 bytes, sha256 `81BC82F771937391FE904EE175EAAE85AE78080C5866D5874092E8AD822C5CE1`)
- `scripts/audit_external_backend_contract.py` (operator_command_source, 15394 bytes, sha256 `6A2A65A7AA73B04C438AFF9B85115589397D8DDF3496A93632E7A178D7230E4C`)
- `scripts/audit_external_collection_readiness.py` (operator_command_source, 15351 bytes, sha256 `02F0F9E7A06FE1B8E12941F93894ED8369C385EECE79E97ADCAB4E05D59DC64B`)
- `scripts/audit_external_evidence.py` (operator_command_source, 25791 bytes, sha256 `5ADA192E92BA159F1E3EC96FDE31818546F8350F200B804B53D40601EDE64CC8`)
- `scripts/audit_external_fidelity_acceptance.py` (operator_command_source, 17816 bytes, sha256 `896A4DD0B7A4E5012FB347F9810F24235611515FF1A9488D3B9FE07823E4A40E`)
- `scripts/audit_external_pairing_integrity.py` (operator_command_source, 13495 bytes, sha256 `237BF15844DA317A1B86A64312986A583D3A27987DB075537F6B44B8A014C0DB`)
- `scripts/audit_external_pilot_smoke.py` (operator_command_source, 10042 bytes, sha256 `13BB2E31C5E8331D1C53B5E060E399FEB83C520FC83AF91FA350FC591D417C25`)
- `scripts/audit_external_release_package.py` (operator_command_source, 9195 bytes, sha256 `C7AAE093CBACD927A3803C328DDCD5316F5A624842FDCF8C9E30F878AD5D6804`)
- `scripts/build_external_acquisition_packet.py` (operator_command_source, 37593 bytes, sha256 `7BB5B0503D36DEAE887578A71508A3AB894D74F420360625A15E3E48F43D3B9B`)
- `scripts/build_external_analysis_plan.py` (operator_command_source, 16556 bytes, sha256 `58146063D30C8D028FF8307AC787B7B5CDE73628949E2BEE1E2042AF46895869`)
- `scripts/build_external_backend_integration_packet.py` (operator_command_source, 19894 bytes, sha256 `9BB1413B2D478C383C0F77FB32D83F645B6B506EF65B8F6DB6A6FA760D22DAAA`)
- `scripts/build_external_config_manifest_packet.py` (operator_command_source, 19489 bytes, sha256 `11DE0FBAE1BBC0F9071EE775964F554C945CE62FF9E049212EA3674110514C94`)
- `scripts/build_external_fidelity_provenance_packet.py` (operator_command_source, 19652 bytes, sha256 `749151831A5CCBD3727D5880EC726F3DE6AC951D29BF802C9176FDF5A1209C2A`)
- `scripts/build_external_manifest.py` (operator_command_source, 19782 bytes, sha256 `4F5A002BCFF1FA189D98623E1D1FB7DAEB65604C200B7FE68CB757C96552BB16`)
- `scripts/build_external_method_implementation_packet.py` (operator_command_source, 16186 bytes, sha256 `2BBE4A63230A15DC53D69B3D5798765D61EA7F07944B6FBD533AD1F9788FE101`)
- `scripts/build_external_operator_handoff_bundle.py` (operator_command_source, 32911 bytes, sha256 `93594F583BD015FC854612ED709E17F32A827EE3C353B7CC767905B2594E19A2`)
- `scripts/build_external_operator_packet.py` (operator_command_source, 12368 bytes, sha256 `42C5CAFD17D0144293A85BBBC79DC892716918833D686FE9CC27C295075C7C38`)
- `scripts/build_external_pilot_smoke_packet.py` (operator_command_source, 11266 bytes, sha256 `F3A2D24716D7DCE1D337453137191E821E1F81ADBAA8ABF446C2446E489C00CE`)
- `scripts/build_external_platform_onboarding.py` (operator_command_source, 19708 bytes, sha256 `D72F04E2C99DD55944CE3D857D22A4591A34748375AFDCE3FCBAE359AF03BEA8`)
- `scripts/build_external_rollout_evidence_packet.py` (operator_command_source, 22665 bytes, sha256 `E273634CCB595A0952C81F83B65355BDCDE61596F02B6BC390A268462377C611`)
- `scripts/materialize_external_configs.py` (operator_command_source, 10778 bytes, sha256 `2FF62B2A9C97C41412D3A774F1650A214ADE8EA0DB75BC02DCEE1ABA44F27A2A`)
- `scripts/validate_external_adapters.py` (operator_command_source, 16734 bytes, sha256 `0D59CA82FB8B3F919654AEBA695F643CFCDEFE1B8BF72DC618E73B116CF7E2BF`)
- `scripts/validate_external_configs.py` (operator_command_source, 12127 bytes, sha256 `C65128DE2996E6A5BE29A9BD54B8C4544C04172029016247B5A2D9FA1E78A21A`)
- `scripts/validate_external_rollouts.py` (operator_command_source, 17713 bytes, sha256 `C1477292CEC690F82C6EBD536F3F2531BFE736E891F0EA44D8E6584C5C8385FD`)

## Checks

- `pass` `operator_packet_is_no_go_non_evidence`: start_state='DO_NOT_COLLECT_YET', strict_evidence_ready=False
- `pass` `acquisition_maps_all_remaining_blockers`: missing_requirements=4
- `pass` `strict_evidence_gates_remain_fail_closed`: analysis=False, onboarding=False, preflight=False, release=False, pairing=False
- `pass` `bundle_files_exist`: missing=[], total_missing=0
- `pass` `bundle_excludes_rollout_evidence_artifacts`: forbidden_included=[]
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `handoff_has_task_config_and_baseline_assets`: category_counts={'baseline_spec': 12, 'config_template': 4, 'generated_non_evidence_report': 58, 'operator_command_source': 23, 'operator_facing_input': 48, 'prepared_config_input': 4, 'reference_adapter': 60, 'runner_backend_template': 5, 'task_card': 4}
- `pass` `analysis_plan_included`: analysis_plan_ready=True, strict_evidence_ready=False
- `pass` `platform_onboarding_included`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `fidelity_provenance_packet_included`: fidelity_provenance_packet_ready=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `backend_integration_packet_included`: backend_integration_packet_ready=True, strict_backend_ready=False
- `pass` `config_manifest_packet_included`: config_manifest_packet_ready=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `rollout_evidence_packet_included`: rollout_evidence_packet_ready=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `pilot_smoke_packet_included`: pilot_smoke_packet_ready=True, strict_evidence_ready=False
- `pass` `method_implementation_packet_included`: method_implementation_packet_ready=True, strict_adapter_evidence_ready=False
- `pass` `operator_actions_cover_evidence_collection`: missing=[]
- `pass` `post_collection_commands_cover_strict_gates`: commands=8
- `pass` `file_hashes_are_recorded`: hashed_files=218
