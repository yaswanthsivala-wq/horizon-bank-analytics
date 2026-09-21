# Index and partition strategy

Start unpartitioned for authoritative keyed parents and initial correctness testing. PK/alternate-key indexes preserve approved identities. Add B-tree indexes for FK lookup, source identity/revision, predecessor, publication/date membership, case evidence, entitlement principal/role/effective state and lifecycle dependencies. Index choices must reference concrete access paths; measure plans only in separately authorized execution.

GiST with btree_gist supports selected-interval equality/range exclusion; historical superseded rows must not be constrained as simultaneously selected. Consider BRIN for append-correlated event dates and monthly RANGE partitions for large snapshot/risk/raw tables only after measurement. No partition is dropped merely because its date range is old: holds, late records, original anchors and child dependencies require eligibility proof.

PostgreSQL partitioned primary/unique constraints require compatible partition-key inclusion. Do not expand approved logical uniqueness to silently allow duplicate keys across months. Options for later review: retain unpartitioned authoritative identity table with FK-bound partitioned payload, or defer partitioning. Any representation must preserve one logical fact and full-key references; inability to enforce approved uniqueness enters change control. No partitioned business tables are authored here.

Proposed indexes do not constitute achieved performance, concurrency or storage capacity. PD02 starts with integrity, not guessed tuning. Later tests compare native-grain row counts/totals and query plans before/after each index/partition change.
