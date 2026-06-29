# Fidelity Acceptance Materializer Self-Test

Passed: `true`.
Not evidence: `true`.

This self-test exercises the guarded fidelity-acceptance materializer on temporary files only. It verifies that a clean matching checkout can write a temporary acceptance file, while stale commits, mismatched skill-library hashes, and dirty checkouts are rejected before any write.

## Checks

- `pass` `matching_clean_checkout_writes_temp_acceptance`: {'name': 'matching_clean_checkout', 'raised': False, 'error': '', 'output_exists': True, 'payload_passed': True, 'acceptance_write_ready': True, 'candidate_acceptance_ready': True, 'written_version': 'paper119_fidelity_acceptance_v1', 'written_acceptance_ready': True}
- `pass` `stale_commit_rejected_without_temp_write`: {'name': 'stale_commit', 'raised': True, 'error': 'refusing to write fidelity acceptance because materialization checks did not pass', 'output_exists': False, 'payload_passed': None, 'acceptance_write_ready': None, 'candidate_acceptance_ready': None, 'written_version': None, 'written_acceptance_ready': None}
- `pass` `mismatched_skill_hash_rejected_without_temp_write`: {'name': 'mismatched_skill_hash', 'raised': True, 'error': 'refusing to write fidelity acceptance because materialization checks did not pass', 'output_exists': False, 'payload_passed': None, 'acceptance_write_ready': None, 'candidate_acceptance_ready': None, 'written_version': None, 'written_acceptance_ready': None}
- `pass` `dirty_checkout_rejected_without_temp_write`: {'name': 'dirty_checkout', 'raised': True, 'error': 'refusing to write fidelity acceptance because materialization checks did not pass', 'output_exists': False, 'payload_passed': None, 'acceptance_write_ready': None, 'candidate_acceptance_ready': None, 'written_version': None, 'written_acceptance_ready': None}
- `pass` `pycache_excluded_from_skill_library_hash`: {'digest_before': 'B2A0D85F3C34B1305AD3C1668B08704E0F10701A9AFA17BEC6B6B4486B399ECF', 'digest_after': 'B2A0D85F3C34B1305AD3C1668B08704E0F10701A9AFA17BEC6B6B4486B399ECF', 'unchanged_after_pyc_mutation': True}
- `pass` `real_acceptance_file_not_touched`: before=None, after=None
