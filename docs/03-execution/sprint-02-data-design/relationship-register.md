# Derived relationship register — 2026-09-20

Derived only from the [authoritative dictionary](field-level-dictionary.md). This register lists declared foreign-key references; cardinality is **not asserted** here (see the [ERDs](data-model.md) and approved policies). This is not a physical constraint list and changes no approved design decision.

## Counts

| Measure | Computed value | Method |
| --- | --- | --- |
| Explicit FK references (N1) | 203 | Count literal FK entity.field targets in field definitions |
| Distinct child→parent entity pairs (N2) | 195 | Deduplicate child entity and parent entity from Section 1 |
| FK-mentioning field rows (N3) | 240 | Count field definitions containing the standalone token FK, including implicit/composite references |

Entities are second-level headings whose section contains a Logical PK line. Field rows are the five-column tables under those headings; headers and separator rows are excluded. Explicit targets match the case-sensitive pattern `\bFK\s+([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)`. No target is inferred from narrative or composite references. Section 2 contains 37 rows; their definitions are reproduced verbatim. Review reference values 203/195/240 match the computed results.

## Section 1 — Explicit FK targets

| Child entity | Child field | Parent entity | Parent field |
| --- | --- | --- | --- |
| branch | region_version | region | region_version |
| branch | organization_key | organizational_unit | organization_key |
| branch | supersedes_branch_key | branch | branch_key |
| branch | correction_action_id | governance_action | action_id |
| customer_identity | customer_key | customer | customer_key |
| customer_version | customer_key | customer | customer_key |
| customer_version | branch_key | branch | branch_key |
| account | branch_key | branch | branch_key |
| account_customer | account_key | account | account_key |
| account_customer | customer_key | customer | customer_key |
| transaction | account_key | account | account_key |
| transaction | branch_key | branch | branch_key |
| transaction | supersedes_event_key | transaction | transaction_key |
| loan | branch_key | branch | branch_key |
| loan_customer | loan_key | loan | loan_key |
| loan_customer | customer_key | customer | customer_key |
| loan_snapshot | loan_key | loan | loan_key |
| loan_snapshot | supersedes_snapshot_version | loan_snapshot | snapshot_version |
| loan_payment | loan_key | loan | loan_key |
| loan_payment | supersedes_event_key | loan_payment | payment_key |
| fraud_alert | customer_key | customer | customer_key |
| fraud_alert | transaction_key | transaction | transaction_key |
| complaint | customer_key | customer | customer_key |
| complaint | branch_key | branch | branch_key |
| complaint_snapshot | complaint_key | complaint | complaint_key |
| complaint_snapshot | branch_key | branch | branch_key |
| complaint_snapshot | supersedes_snapshot_version | complaint_snapshot | snapshot_version |
| risk_assessment | customer_key | customer | customer_key |
| risk_assessment | rule_version | configuration_version | configuration_version |
| risk_assessment | catalog_version | catalog_version | catalog_version |
| risk_assessment | publication_version | publication | publication_version |
| risk_evidence | assessment_key | risk_assessment | assessment_key |
| risk_evidence | rule_version | rule_version | rule_version |
| rule_config | configuration_version | configuration_version | configuration_version |
| pipeline_run | publication_version | publication | publication_version |
| quality_exception | run_id | pipeline_run | run_id |
| reconciliation_result | run_id | pipeline_run | run_id |
| reconciliation_result | population_key | control_population | population_key |
| export_event | policy_version | access_policy | policy_version |
| export_event | publication_version | publication | publication_version |
| complaint_history_event | complaint_key | complaint | complaint_key |
| complaint_history_event | publication_version | publication | publication_version |
| loan_snapshot_publication | publication_version | publication | publication_version |
| loan_snapshot_publication | loan_key | loan | loan_key |
| loan_snapshot_publication | snapshot_version | loan_snapshot | snapshot_version |
| complaint_snapshot_publication | publication_version | publication | publication_version |
| complaint_snapshot_publication | complaint_key | complaint | complaint_key |
| complaint_snapshot_publication | snapshot_version | complaint_snapshot | snapshot_version |
| historical_coverage | publication_version | publication | publication_version |
| risk_evidence_item | source_reference_key | source_reference | source_reference_key |
| risk_evidence_item | comparison_key | rc01_comparison | comparison_key |
| rc01_comparison | transaction_key | transaction | transaction_key |
| rc01_comparison | account_key | account | account_key |
| rc01_comparison | customer_key | customer | customer_key |
| rc01_comparison | rule_version | rule_version | rule_version |
| rc01_comparison | publication_version | publication | publication_version |
| rc01_comparison | supersedes_comparison_key | rc01_comparison | comparison_key |
| account_restriction_state | account_key | account | account_key |
| account_restriction_state | publication_version | publication | publication_version |
| account_restriction_state | supersedes_state_version | account_restriction_state | state_version |
| fraud_alert_state | alert_key | fraud_alert | alert_key |
| fraud_alert_state | publication_version | publication | publication_version |
| fraud_alert_state | supersedes_state_version | fraud_alert_state | state_version |
| publication | supersedes_version | publication | publication_version |
| publication | run_id | pipeline_run | run_id |
| publication | candidate_id | publication_candidate | candidate_id |
| catalog_version | supersedes_version | catalog_version | catalog_version |
| rule_version | supersedes_version | rule_version | rule_version |
| rule_version | configuration_version | configuration_version | configuration_version |
| configuration_version | supersedes_version | configuration_version | configuration_version |
| mapping_version | supersedes_version | mapping_version | mapping_version |
| catalog_rule | catalog_version | catalog_version | catalog_version |
| catalog_rule | rule_version | rule_version | rule_version |
| mapping_entry | mapping_version | mapping_version | mapping_version |
| applied_mapping | mapping_version | mapping_version | mapping_version |
| run_extract | run_id | pipeline_run | run_id |
| source_reference | run_id | pipeline_run | run_id |
| control_population | publication_version | publication | publication_version |
| population_member | population_key | control_population | population_key |
| source_financial_control | population_key | control_population | population_key |
| export_filter | event_key | export_event | event_key |
| recalculation_impact | old_publication_version | publication | publication_version |
| recalculation_impact | new_publication_version | publication | publication_version |
| recalculation_customer | impact_key | recalculation_impact | impact_key |
| recalculation_customer | customer_key | customer | customer_key |
| transaction_publication | publication_version | publication | publication_version |
| transaction_publication | transaction_key | transaction | transaction_key |
| loan_payment_publication | publication_version | publication | publication_version |
| loan_payment_publication | payment_key | loan_payment | payment_key |
| access_entitlement | policy_version | access_policy | policy_version |
| access_entitlement | approval_reference | governance_action | action_id |
| entitlement_scope | entitlement_id | access_entitlement | entitlement_id |
| case_evidence_link | case_key | investigation_case | case_key |
| governance_review | action_id | governance_action | action_id |
| export_entitlement | event_key | export_event | event_key |
| export_entitlement | entitlement_id | access_entitlement | entitlement_id |
| export_approval | event_key | export_event | event_key |
| export_approval | action_id | governance_action | action_id |
| rc01_investigation_projection | case_key | investigation_case | case_key |
| gate_rule | gate_ruleset_version | gate_ruleset | gate_ruleset_version |
| publication_candidate | run_id | pipeline_run | run_id |
| publication_candidate | gate_ruleset_version | gate_ruleset | gate_ruleset_version |
| publication_candidate | prior_successful_version | publication | publication_version |
| publication_candidate | predecessor_version | publication | publication_version |
| candidate_source | candidate_id | publication_candidate | candidate_id |
| candidate_control | candidate_id | publication_candidate | candidate_id |
| candidate_control | population_key | control_population | population_key |
| candidate_population | candidate_id | publication_candidate | candidate_id |
| candidate_population | population_key | control_population | population_key |
| candidate_coverage | candidate_id | publication_candidate | candidate_id |
| candidate_coverage | population_key | control_population | population_key |
| candidate_evidence | candidate_id | publication_candidate | candidate_id |
| quality_exclusion | action_id | governance_action | action_id |
| quality_exclusion | candidate_id | publication_candidate | candidate_id |
| exclusion_record | action_id | quality_exclusion | action_id |
| exclusion_record | source_reference_key | source_reference | source_reference_key |
| exclusion_impact | action_id | quality_exclusion | action_id |
| publication_decision | candidate_id | publication_candidate | candidate_id |
| publication_decision | publication_version | publication | publication_version |
| publication_decision | release_action_id | governance_action | action_id |
| publication_decision | retained_publication_version | publication | publication_version |
| decision_participant | decision_id | publication_decision | decision_id |
| decision_participant | action_id | governance_action | action_id |
| publication_notification | candidate_id | publication_candidate | candidate_id |
| publication_notification | decision_id | publication_decision | decision_id |
| notification_recipient | notification_id | publication_notification | notification_id |
| retention_schedule | approval_action_id | governance_action | action_id |
| retention_item | envelope_id | provenance_envelope | envelope_id |
| provenance_envelope | deletion_evidence_id | disposal_item | result_id |
| lifecycle_reference | owner_envelope_id | provenance_envelope | envelope_id |
| lifecycle_reference | target_envelope_id | provenance_envelope | envelope_id |
| restricted_token_mapping | retention_item_id | retention_item | item_id |
| retention_hold | approval_action_id | governance_action | action_id |
| retention_hold | release_action_id | governance_action | action_id |
| hold_scope | hold_id | retention_hold | hold_id |
| hold_review | hold_id | retention_hold | hold_id |
| hold_review | action_id | governance_action | action_id |
| disposal_batch | approval_action_id | governance_action | action_id |
| disposal_scope | batch_id | disposal_batch | batch_id |
| disposal_scope | item_id | retention_item | item_id |
| disposal_job | batch_id | disposal_batch | batch_id |
| disposal_item | job_id | disposal_job | job_id |
| disposal_item | item_id | retention_item | item_id |
| disposal_category_total | job_id | disposal_job | job_id |
| restore_validation | backup_id | backup_copy | backup_id |
| access_attempt | policy_version | access_policy | policy_version |
| loan_schedule | loan_key | loan | loan_key |
| loan_schedule | supersedes_schedule_version | loan_schedule | schedule_version |
| loan_obligation | schedule_version | loan_schedule | schedule_version |
| loan_obligation | loan_key | loan | loan_key |
| loan_obligation | supersedes_obligation_version | loan_obligation | obligation_version |
| payment_allocation | payment_key | loan_payment | payment_key |
| payment_allocation | obligation_version | loan_obligation | obligation_version |
| payment_allocation | supersedes_allocation_version | payment_allocation | allocation_version |
| payment_unapplied | payment_key | loan_payment | payment_key |
| payment_unapplied | supersedes_unapplied_version | payment_unapplied | unapplied_version |
| payment_adjustment | original_payment_key | loan_payment | payment_key |
| payment_adjustment | supersedes_event_key | payment_adjustment | adjustment_key |
| loan_account | loan_key | loan | loan_key |
| loan_account | account_key | account | account_key |
| loan_account | supersedes_relationship_version | loan_account | loan_account_version |
| payment_transaction_link | payment_key | loan_payment | payment_key |
| payment_transaction_link | transaction_key | transaction | transaction_key |
| payment_transaction_link | review_action_id | governance_action | action_id |
| payment_transaction_link | supersedes_link_version | payment_transaction_link | link_version |
| loan_contract_publication | publication_version | publication | publication_version |
| region | organization_key | organizational_unit | organization_key |
| region | supersedes_version | region | region_version |
| region | approval_action_id | governance_action | action_id |
| organizational_successor | predecessor_key | organizational_unit | organization_key |
| organizational_successor | successor_key | organizational_unit | organization_key |
| organizational_successor | supersedes_version | organizational_successor | successor_version |
| organizational_successor | approval_action_id | governance_action | action_id |
| account_branch_assignment | account_key | account | account_key |
| account_branch_assignment | branch_key | branch | branch_key |
| account_branch_assignment | supersedes_version | account_branch_assignment | assignment_version |
| account_branch_assignment | approval_action_id | governance_action | action_id |
| loan_branch_assignment | loan_key | loan | loan_key |
| loan_branch_assignment | branch_key | branch | branch_key |
| loan_branch_assignment | supersedes_version | loan_branch_assignment | assignment_version |
| loan_branch_assignment | approval_action_id | governance_action | action_id |
| complaint_branch_assignment | complaint_key | complaint | complaint_key |
| complaint_branch_assignment | branch_key | branch | branch_key |
| complaint_branch_assignment | supersedes_version | complaint_branch_assignment | assignment_version |
| complaint_branch_assignment | approval_action_id | governance_action | action_id |
| branch_attribution | publication_version | publication | publication_version |
| branch_attribution | branch_key | branch | branch_key |
| branch_attribution | region_version | region | region_version |
| branch_attribution | source_reference_key | source_reference | source_reference_key |
| branch_attribution | basis_attribution_key | branch_attribution | attribution_key |
| branch_attribution | supplied_branch_key | branch | branch_key |
| branch_attribution | review_action_id | governance_action | action_id |
| organization_publication | publication_version | publication | publication_version |
| successor_scope_mapping | current_branch_key | organizational_unit | organization_key |
| successor_scope_mapping | historical_branch_key | organizational_unit | organization_key |
| successor_scope_mapping | approval_action_id | governance_action | action_id |
| successor_scope_mapping | supersedes_version | successor_scope_mapping | scope_mapping_version |
| scope_resolution | access_attempt_id | access_attempt | attempt_id |
| scope_resolution | export_event_key | export_event | event_key |
| scope_resolution | entitlement_id | access_entitlement | entitlement_id |
| scope_resolution | branch_identity | organizational_unit | organization_key |
| scope_resolution | current_branch_version | branch | branch_key |
| scope_resolution | scope_mapping_version | successor_scope_mapping | scope_mapping_version |

## Section 2 — Composite or implicit FK mentions

Parent target for every row: **see definition — not machine-resolved**.

| Child entity | Field | Definition text (verbatim) |
| --- | --- | --- |
| quality_exception | source_system | Composite FK to source_extract; extract_id alone is not a qualified key |
| quality_exception | entity_name | Composite FK to source_extract; extract_id alone is not a qualified key |
| quality_exception | business_date | Composite FK to source_extract; extract_id alone is not a qualified key |
| quality_exception | revision | Composite FK to source_extract; extract_id alone is not a qualified key |
| reconciliation_result | source_system | Composite FK to source_extract; extract_id alone is not a qualified key |
| reconciliation_result | entity_name | Composite FK to source_extract; extract_id alone is not a qualified key |
| reconciliation_result | business_date | Composite FK to source_extract; extract_id alone is not a qualified key |
| reconciliation_result | revision | Composite FK to source_extract; extract_id alone is not a qualified key |
| risk_evidence_item | assessment_key | Composite FK with condition_id to risk_evidence |
| risk_evidence_item | condition_id | Composite FK with assessment_key to risk_evidence |
| mapping_eligibility | mapping_version | Composite FK to mapping_entry |
| mapping_eligibility | source_system | Composite FK to mapping_entry |
| mapping_eligibility | domain_code | Composite FK to mapping_entry |
| mapping_eligibility | raw_value | Composite FK to mapping_entry |
| applied_mapping | owner_version_key | Logical FK to the named owner entity PK tuple/version, including composite keys; not serialized text or an invented surrogate |
| run_extract | source_system | Composite FK source_extract |
| run_extract | entity_name | Composite FK source_extract |
| run_extract | business_date | Composite FK source_extract |
| run_extract | revision | Composite FK source_extract |
| source_reference | source_system | Composite FK source_extract |
| source_reference | entity_name | Composite FK source_extract |
| source_reference | business_date | Composite FK source_extract |
| source_reference | revision | Composite FK source_extract |
| source_reference | owner_version_key | Logical FK to the named owner entity PK tuple/version, including composite keys; not serialized text or an invented surrogate |
| source_financial_control | source_system | Composite FK source_extract |
| source_financial_control | entity_name | Composite FK source_extract |
| source_financial_control | business_date | Composite FK source_extract |
| source_financial_control | revision | Composite FK source_extract |
| case_evidence_link | owner_version_key | FK to named entity full PK; raw references stay restricted and hidden from ordinary navigation |
| candidate_control | gate_ruleset_version | Composite FK with rule_id to gate_rule; matches candidate ruleset |
| candidate_control | rule_id | Composite FK with gate_ruleset_version to gate_rule |
| quality_exclusion | source_system | Composite source_extract FK |
| quality_exclusion | entity_name | Composite source_extract FK |
| quality_exclusion | business_date | Composite source_extract FK |
| quality_exclusion | revision | Composite source_extract FK; approval scoped to this delivered revision |
| retention_item | schedule_version | Composite FK with category_code to retention_schedule |
| retention_item | category_code | Composite FK with schedule_version to retention_schedule |
