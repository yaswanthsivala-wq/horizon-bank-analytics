# Constraint and reference enforcement matrix

Static design only. All business-table enforcement is deferred; foundation SQL creates none. Source: the sole Sprint 2 inventory and approved cross-field rules. The mapping covers each field; the following register covers every declared PK and explicit scalar FK plus typed fields. Composite and semantic contracts also require the family checks below. Absence of an explicit FK token in prose never authorizes an unchecked reference.

| ID | Future enforcement | Acceptance / negative case |
| --- | --- | --- |
| PK-01 | Exact logical PK as primary key; source-qualified alternate uniqueness within approved selection scope | Duplicate selected natural identity fails; preserved correction versions coexist |
| COL-01 | NOT NULL, bounded varchar, checks/domain lookup; preserve classification and leading zeros | Required null, overflow, unmapped code fail; no truncation |
| COND-01 | Row CHECK for local conditions; deferred constraint trigger for cross-row status/applicability | Each inventory C condition tested true/missing and false/optional |
| REF-01 | Typed scalar FK with matching parent SQL type; index referencing columns where justified | Missing parent fails; no unsafe ON DELETE CASCADE through retained evidence |
| REF-02 | Composite FK uses full parent key in documented order; no partial-key lookup | Same ID in different namespace/date/version cannot cross-link |
| TR-01 | Normalized physical binding plus target-specific full-key children; declarative FK to target, deferred completeness/type/owner trigger and target-delete protection | Exactly one approved target kind/full key; wrong type, missing child, extra child and dangling target fail |
| NUM-01 | Validate raw lexical scale/minor units/finite value before numeric cast; exact sums/counts and exact ratio representation | Excess scale never rounded into acceptance; threshold boundaries and zero denominator checked |
| TIME-01 | timestamptz(6), ordered half-open intervals, zone-aware boundary rules; validate source precision before cast | Ambiguous/nonexistent unqualified local time fails; endpoint transfers resolve once |
| SEL-01 | Selected interval projection keyed by publication/candidate + stable subject + role; GiST exclusion where suitable, plus completeness validation | Overlap rejected only among selected versions; gap rejected at required attribution instants |
| IMM-01 | Revoke direct UPDATE/DELETE; guarded append/correction functions and acyclic predecessor constraints; lifecycle deletion through approved path only | Original evidence immutable; illegal identity-changing predecessor fails |
| FIN-01 | Deferred cross-row/payment checks and publication-gate queries with serialization/locking around concurrent changes | Gross posted=allocations+unapplied; adjustments capped; no float/tolerance |
| PUB-01 | Candidate freeze, membership full-key checks, rechecked gates and atomic successful-release pointer | Concurrent corrections/release cannot expose mixed versions |
| LIFE-01 | Approved expiry/hold/dependency checks and audit-envelope migration before removal | No orphan live analytical key; audit survival uses explicit envelope |

## Typed reference physical contract

Propose security.reference_binding and target-specific binding children as physical helpers only, DEFERRED. Each binding resolves the exact approved target/full key or approved typed literal variant, not a serialized string/JSON substitute. Children use the parent's true SQL types and full composite keys. The binding kind is constrained by the referencing logical field's whitelist; unrecognized kinds fail closed. A deferred constraint trigger enforces exactly one child, context-specific target/version applicability and completeness. A physical field-specific usage relation records the referencing row for delete/hold dependency checks. Target deletion is blocked by FK until permitted users of the binding migrate to an explicit DD-10 provenance-envelope alternative. Analytical bindings cannot use expired-payload envelopes. No orphan-capable polymorphic FK is accepted.

Natural-identity typed fields are value tuples rather than necessarily links to one row: define approved component children and full-tuple uniqueness, retain original namespace/types and selected-publication rules. Typed scope literals use field-specific code/date/number/reference child variants with exactly-one validation. These helpers do not change logical cardinality; if physical mapping cannot preserve it, stop affected work and enter change control.

Composite families: source_extract (source_system/entity_name/business_date/revision); mapping_entry (mapping_version/source_system/domain_code/raw_value); risk_evidence (assessment_key/condition_id); retention_schedule (schedule_version/category_code); all membership identities and remaining composite PKs below. Resolve full parents; no partial-key surrogate inference. Dependency/cycle order is physical DDL first, then constraints before any load, not permanently disabled enforcement.

## Primary-key inventory

| Entity | Exact logical PK | Enforcement state |
| --- | --- | --- |
| branch | branch_key | PK-01; deferred |
| customer | customer_key | PK-01; deferred |
| customer_identity | identity_key | PK-01; deferred |
| customer_version | customer_version_key | PK-01; deferred |
| account | account_key | PK-01; deferred |
| account_customer | account_key + customer_key + relationship_role + valid_from | PK-01; deferred |
| transaction | transaction_key | PK-01; deferred |
| loan | loan_key | PK-01; deferred |
| loan_customer | loan_key + customer_key + relationship_role + valid_from | PK-01; deferred |
| loan_snapshot | snapshot_version | PK-01; deferred |
| loan_payment | payment_key | PK-01; deferred |
| fraud_alert | alert_key | PK-01; deferred |
| complaint | complaint_key | PK-01; deferred |
| complaint_snapshot | snapshot_version | PK-01; deferred |
| risk_assessment | assessment_key | PK-01; deferred |
| risk_evidence | assessment_key + condition_id | PK-01; deferred |
| rule_config | configuration_version + parameter_id | PK-01; deferred |
| pipeline_run | run_id | PK-01; deferred |
| source_extract | source_system + entity_name + business_date + revision | PK-01; deferred |
| quality_exception | exception_key | PK-01; deferred |
| reconciliation_result | reconciliation_key | PK-01; deferred |
| export_event | event_key | PK-01; deferred |
| complaint_history_event | history_event_key | PK-01; deferred |
| loan_snapshot_publication | publication_version + loan_key + business_date | PK-01; deferred |
| complaint_snapshot_publication | publication_version + complaint_key + business_date | PK-01; deferred |
| historical_coverage | coverage_key | PK-01; deferred |
| risk_evidence_item | evidence_item_key | PK-01; deferred |
| rc01_comparison | comparison_key | PK-01; deferred |
| account_restriction_state | state_version | PK-01; deferred |
| fraud_alert_state | state_version | PK-01; deferred |
| publication | publication_version | PK-01; deferred |
| catalog_version | catalog_version | PK-01; deferred |
| rule_version | rule_version | PK-01; deferred |
| configuration_version | configuration_version | PK-01; deferred |
| mapping_version | mapping_version | PK-01; deferred |
| catalog_rule | catalog_version + condition_id | PK-01; deferred |
| mapping_entry | mapping_version + source_system + domain_code + raw_value | PK-01; deferred |
| mapping_eligibility | mapping_version + source_system + domain_code + raw_value + eligibility_code | PK-01; deferred |
| applied_mapping | owner_entity + owner_version_key + mapping_version + usage_code | PK-01; deferred |
| run_extract | run_id + source_system + entity_name + business_date + revision | PK-01; deferred |
| source_reference | source_reference_key | PK-01; deferred |
| control_population | population_key | PK-01; deferred |
| population_member | population_key + criterion_code + member_value | PK-01; deferred |
| source_financial_control | source_system + entity_name + business_date + revision + amount_field + currency + population_key | PK-01; deferred |
| export_filter | event_key + filter_code + member_number | PK-01; deferred |
| recalculation_impact | impact_key | PK-01; deferred |
| recalculation_customer | impact_key + customer_key | PK-01; deferred |
| date_dimension | date_key | PK-01; deferred |
| transaction_publication | publication_version + source_system + source_transaction_id + business_date | PK-01; deferred |
| loan_payment_publication | publication_version + source_system + source_payment_id + business_date | PK-01; deferred |
| access_policy | policy_version | PK-01; deferred |
| access_entitlement | entitlement_id | PK-01; deferred |
| entitlement_scope | entitlement_id + scope_number | PK-01; deferred |
| investigation_case | case_key | PK-01; deferred |
| case_evidence_link | case_key + item_number | PK-01; deferred |
| governance_action | action_id | PK-01; deferred |
| governance_review | action_id + review_number | PK-01; deferred |
| export_entitlement | event_key + entitlement_id | PK-01; deferred |
| export_approval | event_key + action_id | PK-01; deferred |
| rc01_investigation_projection | case_key + projection_item_key | PK-01; deferred |
| gate_ruleset | gate_ruleset_version | PK-01; deferred |
| gate_rule | gate_ruleset_version + rule_id | PK-01; deferred |
| publication_candidate | candidate_id | PK-01; deferred |
| candidate_source | candidate_id + source_system + entity_name | PK-01; deferred |
| candidate_control | control_result_id | PK-01; deferred |
| candidate_population | candidate_id + population_key + stage | PK-01; deferred |
| candidate_coverage | candidate_id + population_key + result_type | PK-01; deferred |
| candidate_evidence | candidate_id + evidence_number | PK-01; deferred |
| quality_exclusion | action_id | PK-01; deferred |
| exclusion_record | action_id + record_number | PK-01; deferred |
| exclusion_impact | action_id + impact_number | PK-01; deferred |
| publication_decision | decision_id | PK-01; deferred |
| decision_participant | decision_id + responsibility + member_number | PK-01; deferred |
| publication_notification | notification_id | PK-01; deferred |
| notification_recipient | notification_id + responsibility + member_number | PK-01; deferred |
| retention_schedule | schedule_version + category_code | PK-01; deferred |
| retention_item | item_id | PK-01; deferred |
| provenance_envelope | envelope_id | PK-01; deferred |
| lifecycle_reference | reference_id | PK-01; deferred |
| restricted_token_mapping | mapping_id | PK-01; deferred |
| retention_hold | hold_id | PK-01; deferred |
| hold_scope | hold_id + member_number | PK-01; deferred |
| hold_review | hold_id + review_number | PK-01; deferred |
| disposal_batch | batch_id | PK-01; deferred |
| disposal_scope | batch_id + item_id | PK-01; deferred |
| disposal_job | job_id | PK-01; deferred |
| disposal_item | result_id | PK-01; deferred |
| disposal_category_total | job_id + category_code | PK-01; deferred |
| backup_copy | backup_id | PK-01; deferred |
| restore_validation | restore_id | PK-01; deferred |
| access_attempt | attempt_id | PK-01; deferred |
| loan_schedule | schedule_version | PK-01; deferred |
| loan_obligation | obligation_version | PK-01; deferred |
| payment_allocation | allocation_version | PK-01; deferred |
| payment_unapplied | unapplied_version | PK-01; deferred |
| payment_adjustment | adjustment_key | PK-01; deferred |
| loan_account | loan_account_version | PK-01; deferred |
| payment_transaction_link | link_version | PK-01; deferred |
| loan_contract_publication | publication_version + entity_name + natural_identity | PK-01; deferred |
| organizational_unit | organization_key | PK-01; deferred |
| region | region_version | PK-01; deferred |
| organizational_successor | successor_version | PK-01; deferred |
| account_branch_assignment | assignment_version | PK-01; deferred |
| loan_branch_assignment | assignment_version | PK-01; deferred |
| complaint_branch_assignment | assignment_version | PK-01; deferred |
| branch_attribution | attribution_key | PK-01; deferred |
| organization_publication | publication_version + entity_name + natural_identity | PK-01; deferred |
| successor_scope_mapping | scope_mapping_version | PK-01; deferred |
| scope_resolution | resolution_key | PK-01; deferred |

## Explicit scalar FK inventory

| Child field | Parent field | Plan |
| --- | --- | --- |
| branch.region_version | region.region_version | REF-01; deferred |
| branch.organization_key | organizational_unit.organization_key | REF-01; deferred |
| branch.supersedes_branch_key | branch.branch_key | REF-01; deferred |
| branch.correction_action_id | governance_action.action_id | REF-01; deferred |
| customer_identity.customer_key | customer.customer_key | REF-01; deferred |
| customer_version.customer_key | customer.customer_key | REF-01; deferred |
| customer_version.branch_key | branch.branch_key | REF-01; deferred |
| account.branch_key | branch.branch_key | REF-01; deferred |
| account_customer.account_key | account.account_key | REF-01; deferred |
| account_customer.customer_key | customer.customer_key | REF-01; deferred |
| transaction.account_key | account.account_key | REF-01; deferred |
| transaction.branch_key | branch.branch_key | REF-01; deferred |
| transaction.supersedes_event_key | transaction.transaction_key | REF-01; deferred |
| loan.branch_key | branch.branch_key | REF-01; deferred |
| loan_customer.loan_key | loan.loan_key | REF-01; deferred |
| loan_customer.customer_key | customer.customer_key | REF-01; deferred |
| loan_snapshot.loan_key | loan.loan_key | REF-01; deferred |
| loan_snapshot.supersedes_snapshot_version | loan_snapshot.snapshot_version | REF-01; deferred |
| loan_payment.loan_key | loan.loan_key | REF-01; deferred |
| loan_payment.supersedes_event_key | loan_payment.payment_key | REF-01; deferred |
| fraud_alert.customer_key | customer.customer_key | REF-01; deferred |
| fraud_alert.transaction_key | transaction.transaction_key | REF-01; deferred |
| complaint.customer_key | customer.customer_key | REF-01; deferred |
| complaint.branch_key | branch.branch_key | REF-01; deferred |
| complaint_snapshot.complaint_key | complaint.complaint_key | REF-01; deferred |
| complaint_snapshot.branch_key | branch.branch_key | REF-01; deferred |
| complaint_snapshot.supersedes_snapshot_version | complaint_snapshot.snapshot_version | REF-01; deferred |
| risk_assessment.customer_key | customer.customer_key | REF-01; deferred |
| risk_assessment.rule_version | configuration_version.configuration_version | REF-01; deferred |
| risk_assessment.catalog_version | catalog_version.catalog_version | REF-01; deferred |
| risk_assessment.publication_version | publication.publication_version | REF-01; deferred |
| risk_evidence.assessment_key | risk_assessment.assessment_key | REF-01; deferred |
| risk_evidence.rule_version | rule_version.rule_version | REF-01; deferred |
| rule_config.configuration_version | configuration_version.configuration_version | REF-01; deferred |
| pipeline_run.publication_version | publication.publication_version | REF-01; deferred |
| quality_exception.run_id | pipeline_run.run_id | REF-01; deferred |
| reconciliation_result.run_id | pipeline_run.run_id | REF-01; deferred |
| reconciliation_result.population_key | control_population.population_key | REF-01; deferred |
| export_event.policy_version | access_policy.policy_version | REF-01; deferred |
| export_event.publication_version | publication.publication_version | REF-01; deferred |
| complaint_history_event.complaint_key | complaint.complaint_key | REF-01; deferred |
| complaint_history_event.publication_version | publication.publication_version | REF-01; deferred |
| loan_snapshot_publication.publication_version | publication.publication_version | REF-01; deferred |
| loan_snapshot_publication.loan_key | loan.loan_key | REF-01; deferred |
| loan_snapshot_publication.snapshot_version | loan_snapshot.snapshot_version | REF-01; deferred |
| complaint_snapshot_publication.publication_version | publication.publication_version | REF-01; deferred |
| complaint_snapshot_publication.complaint_key | complaint.complaint_key | REF-01; deferred |
| complaint_snapshot_publication.snapshot_version | complaint_snapshot.snapshot_version | REF-01; deferred |
| historical_coverage.publication_version | publication.publication_version | REF-01; deferred |
| risk_evidence_item.source_reference_key | source_reference.source_reference_key | REF-01; deferred |
| risk_evidence_item.comparison_key | rc01_comparison.comparison_key | REF-01; deferred |
| rc01_comparison.transaction_key | transaction.transaction_key | REF-01; deferred |
| rc01_comparison.account_key | account.account_key | REF-01; deferred |
| rc01_comparison.customer_key | customer.customer_key | REF-01; deferred |
| rc01_comparison.rule_version | rule_version.rule_version | REF-01; deferred |
| rc01_comparison.publication_version | publication.publication_version | REF-01; deferred |
| rc01_comparison.supersedes_comparison_key | rc01_comparison.comparison_key | REF-01; deferred |
| account_restriction_state.account_key | account.account_key | REF-01; deferred |
| account_restriction_state.publication_version | publication.publication_version | REF-01; deferred |
| account_restriction_state.supersedes_state_version | account_restriction_state.state_version | REF-01; deferred |
| fraud_alert_state.alert_key | fraud_alert.alert_key | REF-01; deferred |
| fraud_alert_state.publication_version | publication.publication_version | REF-01; deferred |
| fraud_alert_state.supersedes_state_version | fraud_alert_state.state_version | REF-01; deferred |
| publication.supersedes_version | publication.publication_version | REF-01; deferred |
| publication.run_id | pipeline_run.run_id | REF-01; deferred |
| publication.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| catalog_version.supersedes_version | catalog_version.catalog_version | REF-01; deferred |
| rule_version.supersedes_version | rule_version.rule_version | REF-01; deferred |
| rule_version.configuration_version | configuration_version.configuration_version | REF-01; deferred |
| configuration_version.supersedes_version | configuration_version.configuration_version | REF-01; deferred |
| mapping_version.supersedes_version | mapping_version.mapping_version | REF-01; deferred |
| catalog_rule.catalog_version | catalog_version.catalog_version | REF-01; deferred |
| catalog_rule.rule_version | rule_version.rule_version | REF-01; deferred |
| mapping_entry.mapping_version | mapping_version.mapping_version | REF-01; deferred |
| applied_mapping.mapping_version | mapping_version.mapping_version | REF-01; deferred |
| run_extract.run_id | pipeline_run.run_id | REF-01; deferred |
| source_reference.run_id | pipeline_run.run_id | REF-01; deferred |
| control_population.publication_version | publication.publication_version | REF-01; deferred |
| population_member.population_key | control_population.population_key | REF-01; deferred |
| source_financial_control.population_key | control_population.population_key | REF-01; deferred |
| export_filter.event_key | export_event.event_key | REF-01; deferred |
| recalculation_impact.old_publication_version | publication.publication_version | REF-01; deferred |
| recalculation_impact.new_publication_version | publication.publication_version | REF-01; deferred |
| recalculation_customer.impact_key | recalculation_impact.impact_key | REF-01; deferred |
| recalculation_customer.customer_key | customer.customer_key | REF-01; deferred |
| transaction_publication.publication_version | publication.publication_version | REF-01; deferred |
| transaction_publication.transaction_key | transaction.transaction_key | REF-01; deferred |
| loan_payment_publication.publication_version | publication.publication_version | REF-01; deferred |
| loan_payment_publication.payment_key | loan_payment.payment_key | REF-01; deferred |
| access_entitlement.policy_version | access_policy.policy_version | REF-01; deferred |
| access_entitlement.approval_reference | governance_action.action_id | REF-01; deferred |
| entitlement_scope.entitlement_id | access_entitlement.entitlement_id | REF-01; deferred |
| case_evidence_link.case_key | investigation_case.case_key | REF-01; deferred |
| governance_review.action_id | governance_action.action_id | REF-01; deferred |
| export_entitlement.event_key | export_event.event_key | REF-01; deferred |
| export_entitlement.entitlement_id | access_entitlement.entitlement_id | REF-01; deferred |
| export_approval.event_key | export_event.event_key | REF-01; deferred |
| export_approval.action_id | governance_action.action_id | REF-01; deferred |
| rc01_investigation_projection.case_key | investigation_case.case_key | REF-01; deferred |
| gate_rule.gate_ruleset_version | gate_ruleset.gate_ruleset_version | REF-01; deferred |
| publication_candidate.run_id | pipeline_run.run_id | REF-01; deferred |
| publication_candidate.gate_ruleset_version | gate_ruleset.gate_ruleset_version | REF-01; deferred |
| publication_candidate.prior_successful_version | publication.publication_version | REF-01; deferred |
| publication_candidate.predecessor_version | publication.publication_version | REF-01; deferred |
| candidate_source.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| candidate_control.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| candidate_control.population_key | control_population.population_key | REF-01; deferred |
| candidate_population.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| candidate_population.population_key | control_population.population_key | REF-01; deferred |
| candidate_coverage.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| candidate_coverage.population_key | control_population.population_key | REF-01; deferred |
| candidate_evidence.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| quality_exclusion.action_id | governance_action.action_id | REF-01; deferred |
| quality_exclusion.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| exclusion_record.action_id | quality_exclusion.action_id | REF-01; deferred |
| exclusion_record.source_reference_key | source_reference.source_reference_key | REF-01; deferred |
| exclusion_impact.action_id | quality_exclusion.action_id | REF-01; deferred |
| publication_decision.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| publication_decision.publication_version | publication.publication_version | REF-01; deferred |
| publication_decision.release_action_id | governance_action.action_id | REF-01; deferred |
| publication_decision.retained_publication_version | publication.publication_version | REF-01; deferred |
| decision_participant.decision_id | publication_decision.decision_id | REF-01; deferred |
| decision_participant.action_id | governance_action.action_id | REF-01; deferred |
| publication_notification.candidate_id | publication_candidate.candidate_id | REF-01; deferred |
| publication_notification.decision_id | publication_decision.decision_id | REF-01; deferred |
| notification_recipient.notification_id | publication_notification.notification_id | REF-01; deferred |
| retention_schedule.approval_action_id | governance_action.action_id | REF-01; deferred |
| retention_item.envelope_id | provenance_envelope.envelope_id | REF-01; deferred |
| provenance_envelope.deletion_evidence_id | disposal_item.result_id | REF-01; deferred |
| lifecycle_reference.owner_envelope_id | provenance_envelope.envelope_id | REF-01; deferred |
| lifecycle_reference.target_envelope_id | provenance_envelope.envelope_id | REF-01; deferred |
| restricted_token_mapping.retention_item_id | retention_item.item_id | REF-01; deferred |
| retention_hold.approval_action_id | governance_action.action_id | REF-01; deferred |
| retention_hold.release_action_id | governance_action.action_id | REF-01; deferred |
| hold_scope.hold_id | retention_hold.hold_id | REF-01; deferred |
| hold_review.hold_id | retention_hold.hold_id | REF-01; deferred |
| hold_review.action_id | governance_action.action_id | REF-01; deferred |
| disposal_batch.approval_action_id | governance_action.action_id | REF-01; deferred |
| disposal_scope.batch_id | disposal_batch.batch_id | REF-01; deferred |
| disposal_scope.item_id | retention_item.item_id | REF-01; deferred |
| disposal_job.batch_id | disposal_batch.batch_id | REF-01; deferred |
| disposal_item.job_id | disposal_job.job_id | REF-01; deferred |
| disposal_item.item_id | retention_item.item_id | REF-01; deferred |
| disposal_category_total.job_id | disposal_job.job_id | REF-01; deferred |
| restore_validation.backup_id | backup_copy.backup_id | REF-01; deferred |
| access_attempt.policy_version | access_policy.policy_version | REF-01; deferred |
| loan_schedule.loan_key | loan.loan_key | REF-01; deferred |
| loan_schedule.supersedes_schedule_version | loan_schedule.schedule_version | REF-01; deferred |
| loan_obligation.schedule_version | loan_schedule.schedule_version | REF-01; deferred |
| loan_obligation.loan_key | loan.loan_key | REF-01; deferred |
| loan_obligation.supersedes_obligation_version | loan_obligation.obligation_version | REF-01; deferred |
| payment_allocation.payment_key | loan_payment.payment_key | REF-01; deferred |
| payment_allocation.obligation_version | loan_obligation.obligation_version | REF-01; deferred |
| payment_allocation.supersedes_allocation_version | payment_allocation.allocation_version | REF-01; deferred |
| payment_unapplied.payment_key | loan_payment.payment_key | REF-01; deferred |
| payment_unapplied.supersedes_unapplied_version | payment_unapplied.unapplied_version | REF-01; deferred |
| payment_adjustment.original_payment_key | loan_payment.payment_key | REF-01; deferred |
| payment_adjustment.supersedes_event_key | payment_adjustment.adjustment_key | REF-01; deferred |
| loan_account.loan_key | loan.loan_key | REF-01; deferred |
| loan_account.account_key | account.account_key | REF-01; deferred |
| loan_account.supersedes_relationship_version | loan_account.loan_account_version | REF-01; deferred |
| payment_transaction_link.payment_key | loan_payment.payment_key | REF-01; deferred |
| payment_transaction_link.transaction_key | transaction.transaction_key | REF-01; deferred |
| payment_transaction_link.review_action_id | governance_action.action_id | REF-01; deferred |
| payment_transaction_link.supersedes_link_version | payment_transaction_link.link_version | REF-01; deferred |
| loan_contract_publication.publication_version | publication.publication_version | REF-01; deferred |
| region.organization_key | organizational_unit.organization_key | REF-01; deferred |
| region.supersedes_version | region.region_version | REF-01; deferred |
| region.approval_action_id | governance_action.action_id | REF-01; deferred |
| organizational_successor.predecessor_key | organizational_unit.organization_key | REF-01; deferred |
| organizational_successor.successor_key | organizational_unit.organization_key | REF-01; deferred |
| organizational_successor.supersedes_version | organizational_successor.successor_version | REF-01; deferred |
| organizational_successor.approval_action_id | governance_action.action_id | REF-01; deferred |
| account_branch_assignment.account_key | account.account_key | REF-01; deferred |
| account_branch_assignment.branch_key | branch.branch_key | REF-01; deferred |
| account_branch_assignment.supersedes_version | account_branch_assignment.assignment_version | REF-01; deferred |
| account_branch_assignment.approval_action_id | governance_action.action_id | REF-01; deferred |
| loan_branch_assignment.loan_key | loan.loan_key | REF-01; deferred |
| loan_branch_assignment.branch_key | branch.branch_key | REF-01; deferred |
| loan_branch_assignment.supersedes_version | loan_branch_assignment.assignment_version | REF-01; deferred |
| loan_branch_assignment.approval_action_id | governance_action.action_id | REF-01; deferred |
| complaint_branch_assignment.complaint_key | complaint.complaint_key | REF-01; deferred |
| complaint_branch_assignment.branch_key | branch.branch_key | REF-01; deferred |
| complaint_branch_assignment.supersedes_version | complaint_branch_assignment.assignment_version | REF-01; deferred |
| complaint_branch_assignment.approval_action_id | governance_action.action_id | REF-01; deferred |
| branch_attribution.publication_version | publication.publication_version | REF-01; deferred |
| branch_attribution.branch_key | branch.branch_key | REF-01; deferred |
| branch_attribution.region_version | region.region_version | REF-01; deferred |
| branch_attribution.source_reference_key | source_reference.source_reference_key | REF-01; deferred |
| branch_attribution.basis_attribution_key | branch_attribution.attribution_key | REF-01; deferred |
| branch_attribution.supplied_branch_key | branch.branch_key | REF-01; deferred |
| branch_attribution.review_action_id | governance_action.action_id | REF-01; deferred |
| organization_publication.publication_version | publication.publication_version | REF-01; deferred |
| successor_scope_mapping.current_branch_key | organizational_unit.organization_key | REF-01; deferred |
| successor_scope_mapping.historical_branch_key | organizational_unit.organization_key | REF-01; deferred |
| successor_scope_mapping.approval_action_id | governance_action.action_id | REF-01; deferred |
| successor_scope_mapping.supersedes_version | successor_scope_mapping.scope_mapping_version | REF-01; deferred |
| scope_resolution.access_attempt_id | access_attempt.attempt_id | REF-01; deferred |
| scope_resolution.export_event_key | export_event.event_key | REF-01; deferred |
| scope_resolution.entitlement_id | access_entitlement.entitlement_id | REF-01; deferred |
| scope_resolution.branch_identity | organizational_unit.organization_key | REF-01; deferred |
| scope_resolution.current_branch_version | branch.branch_key | REF-01; deferred |
| scope_resolution.scope_mapping_version | successor_scope_mapping.scope_mapping_version | REF-01; deferred |

## Explicit typed-field inventory

| Logical field | Plan |
| --- | --- |
| applied_mapping.owner_version_key | TR-01; deferred |
| source_reference.owner_version_key | TR-01; deferred |
| entitlement_scope.scope_value | TR-01; deferred |
| case_evidence_link.owner_version_key | TR-01; deferred |
| governance_action.subject_reference | TR-01; deferred |
| candidate_source.extract_reference | TR-01; deferred |
| candidate_evidence.owner_version_key | TR-01; deferred |
| lifecycle_reference.live_target | TR-01; deferred |
| restricted_token_mapping.restricted_reference | TR-01; deferred |
| hold_scope.scope_reference | TR-01; deferred |
| loan_contract_publication.natural_identity | TR-01; deferred |
| loan_contract_publication.selected_version | TR-01; deferred |
| branch_attribution.owner_version_key | TR-01; deferred |
| branch_attribution.assignment_version | TR-01; deferred |
| organization_publication.natural_identity | TR-01; deferred |
| organization_publication.selected_version | TR-01; deferred |

## Required semantic families beyond FK syntax

Coverage includes: applied_mapping/source_reference owner full keys; run_extract/source_financial_control extract tuple; catalog_rule/rule_config configuration parents; mapping_eligibility full mapping entry; risk evidence/item five-condition uniqueness and observation parents; publication membership entity/date agreement; case evidence and assigned-scope parents; export entitlement/approval/filter children; correction predecessor identity/acyclicity; loan schedule/obligation/allocation same-loan and currency invariants; adjustment original POSTED reference; exactly one REPORTING account; organization stable identity/nonreuse and selected assignment cardinality; current scope mapping approvals; lifecycle hold/disposal/reference parents. Each is a deferred implementation test family, not a claim that a SQL parser establishes behavior.

## Static compatibility observation

Eight approval/review reference fields have logical varchar(128) while governance_action.action_id is varchar(100). Preserve both approved bounds: PostgreSQL varchar-compatible FK equality still restricts accepted children to existing parent values. This is not permission to widen the parent or truncate the child. No semantic change is needed; later tests must include 101-character unmatched child rejection. Internal-key versus bigint references map consistently to bigint. Exact physical binding-child choices remain deferred engineering detail, with the full-key completeness contract mandatory before loads.
