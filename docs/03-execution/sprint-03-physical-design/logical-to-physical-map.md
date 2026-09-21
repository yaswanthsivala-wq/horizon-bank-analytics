# WP-PD01 logical-to-physical mapping

Status: proposed physical design; not executed. Approved logical inventory is unchanged. One named base table per logical entity is proposed below; no business table is created by foundation SQL. Schema placement is an access/storage boundary, not a new grain. Classification/requiredness/source derivations remain authoritative in the Sprint 2 inventory.

All R columns are NOT NULL; O remain nullable only under their approved conditions; C uses explicit conditional validators. PKs are NOT NULL regardless of prose. The constraint matrix defines future enforcement, not implemented guarantees. Source aliases remain proposed until authorized fixture confirmation.

Typed fields map to a physical binding identifier and normalized target-specific key children (TR-01). The binding is not an invented business ID: one binding represents exactly the original typed full key/value. Exact-ratio fields map to numerator/denominator (NUM-01), never rounded substitutes. Column bounds are proposed exactly as approved; pre-cast validation must precede bounded numeric/text insertion. SQL identifiers are schema-qualified and quoted where necessary, including transaction. All implementation is DEFERRED beyond PD01.

| Logical entity | Proposed physical base table | Logical primary key preserved | State |
| --- | --- | --- | --- |
| branch | curated.branch | branch_key | Deferred business DDL |
| customer | curated.customer | customer_key | Deferred business DDL |
| customer_identity | curated.customer_identity | identity_key | Deferred business DDL |
| customer_version | curated.customer_version | customer_version_key | Deferred business DDL |
| account | curated.account | account_key | Deferred business DDL |
| account_customer | curated.account_customer | account_key + customer_key + relationship_role + valid_from | Deferred business DDL |
| transaction | curated.transaction | transaction_key | Deferred business DDL |
| loan | curated.loan | loan_key | Deferred business DDL |
| loan_customer | curated.loan_customer | loan_key + customer_key + relationship_role + valid_from | Deferred business DDL |
| loan_snapshot | curated.loan_snapshot | snapshot_version | Deferred business DDL |
| loan_payment | curated.loan_payment | payment_key | Deferred business DDL |
| fraud_alert | curated.fraud_alert | alert_key | Deferred business DDL |
| complaint | curated.complaint | complaint_key | Deferred business DDL |
| complaint_snapshot | curated.complaint_snapshot | snapshot_version | Deferred business DDL |
| risk_assessment | curated.risk_assessment | assessment_key | Deferred business DDL |
| risk_evidence | curated.risk_evidence | assessment_key + condition_id | Deferred business DDL |
| rule_config | config.rule_config | configuration_version + parameter_id | Deferred business DDL |
| pipeline_run | audit.pipeline_run | run_id | Deferred business DDL |
| source_extract | audit.source_extract | source_system + entity_name + business_date + revision | Deferred business DDL |
| quality_exception | audit.quality_exception | exception_key | Deferred business DDL |
| reconciliation_result | audit.reconciliation_result | reconciliation_key | Deferred business DDL |
| export_event | audit.export_event | event_key | Deferred business DDL |
| complaint_history_event | curated.complaint_history_event | history_event_key | Deferred business DDL |
| loan_snapshot_publication | curated.loan_snapshot_publication | publication_version + loan_key + business_date | Deferred business DDL |
| complaint_snapshot_publication | curated.complaint_snapshot_publication | publication_version + complaint_key + business_date | Deferred business DDL |
| historical_coverage | curated.historical_coverage | coverage_key | Deferred business DDL |
| risk_evidence_item | curated.risk_evidence_item | evidence_item_key | Deferred business DDL |
| rc01_comparison | curated.rc01_comparison | comparison_key | Deferred business DDL |
| account_restriction_state | curated.account_restriction_state | state_version | Deferred business DDL |
| fraud_alert_state | curated.fraud_alert_state | state_version | Deferred business DDL |
| publication | audit.publication | publication_version | Deferred business DDL |
| catalog_version | config.catalog_version | catalog_version | Deferred business DDL |
| rule_version | config.rule_version | rule_version | Deferred business DDL |
| configuration_version | config.configuration_version | configuration_version | Deferred business DDL |
| mapping_version | config.mapping_version | mapping_version | Deferred business DDL |
| catalog_rule | config.catalog_rule | catalog_version + condition_id | Deferred business DDL |
| mapping_entry | config.mapping_entry | mapping_version + source_system + domain_code + raw_value | Deferred business DDL |
| mapping_eligibility | config.mapping_eligibility | mapping_version + source_system + domain_code + raw_value + eligibility_code | Deferred business DDL |
| applied_mapping | audit.applied_mapping | owner_entity + owner_version_key + mapping_version + usage_code | Deferred business DDL |
| run_extract | audit.run_extract | run_id + source_system + entity_name + business_date + revision | Deferred business DDL |
| source_reference | audit.source_reference | source_reference_key | Deferred business DDL |
| control_population | audit.control_population | population_key | Deferred business DDL |
| population_member | audit.population_member | population_key + criterion_code + member_value | Deferred business DDL |
| source_financial_control | audit.source_financial_control | source_system + entity_name + business_date + revision + amount_field + currency + population_key | Deferred business DDL |
| export_filter | audit.export_filter | event_key + filter_code + member_number | Deferred business DDL |
| recalculation_impact | audit.recalculation_impact | impact_key | Deferred business DDL |
| recalculation_customer | audit.recalculation_customer | impact_key + customer_key | Deferred business DDL |
| date_dimension | config.date_dimension | date_key | Deferred business DDL |
| transaction_publication | curated.transaction_publication | publication_version + source_system + source_transaction_id + business_date | Deferred business DDL |
| loan_payment_publication | curated.loan_payment_publication | publication_version + source_system + source_payment_id + business_date | Deferred business DDL |
| access_policy | security.access_policy | policy_version | Deferred business DDL |
| access_entitlement | security.access_entitlement | entitlement_id | Deferred business DDL |
| entitlement_scope | security.entitlement_scope | entitlement_id + scope_number | Deferred business DDL |
| investigation_case | security.investigation_case | case_key | Deferred business DDL |
| case_evidence_link | security.case_evidence_link | case_key + item_number | Deferred business DDL |
| governance_action | audit.governance_action | action_id | Deferred business DDL |
| governance_review | audit.governance_review | action_id + review_number | Deferred business DDL |
| export_entitlement | audit.export_entitlement | event_key + entitlement_id | Deferred business DDL |
| export_approval | audit.export_approval | event_key + action_id | Deferred business DDL |
| rc01_investigation_projection | curated.rc01_investigation_projection | case_key + projection_item_key | Deferred business DDL |
| gate_ruleset | config.gate_ruleset | gate_ruleset_version | Deferred business DDL |
| gate_rule | config.gate_rule | gate_ruleset_version + rule_id | Deferred business DDL |
| publication_candidate | audit.publication_candidate | candidate_id | Deferred business DDL |
| candidate_source | audit.candidate_source | candidate_id + source_system + entity_name | Deferred business DDL |
| candidate_control | audit.candidate_control | control_result_id | Deferred business DDL |
| candidate_population | audit.candidate_population | candidate_id + population_key + stage | Deferred business DDL |
| candidate_coverage | audit.candidate_coverage | candidate_id + population_key + result_type | Deferred business DDL |
| candidate_evidence | audit.candidate_evidence | candidate_id + evidence_number | Deferred business DDL |
| quality_exclusion | audit.quality_exclusion | action_id | Deferred business DDL |
| exclusion_record | audit.exclusion_record | action_id + record_number | Deferred business DDL |
| exclusion_impact | audit.exclusion_impact | action_id + impact_number | Deferred business DDL |
| publication_decision | audit.publication_decision | decision_id | Deferred business DDL |
| decision_participant | audit.decision_participant | decision_id + responsibility + member_number | Deferred business DDL |
| publication_notification | audit.publication_notification | notification_id | Deferred business DDL |
| notification_recipient | audit.notification_recipient | notification_id + responsibility + member_number | Deferred business DDL |
| retention_schedule | config.retention_schedule | schedule_version + category_code | Deferred business DDL |
| retention_item | audit.retention_item | item_id | Deferred business DDL |
| provenance_envelope | audit.provenance_envelope | envelope_id | Deferred business DDL |
| lifecycle_reference | audit.lifecycle_reference | reference_id | Deferred business DDL |
| restricted_token_mapping | security.restricted_token_mapping | mapping_id | Deferred business DDL |
| retention_hold | audit.retention_hold | hold_id | Deferred business DDL |
| hold_scope | audit.hold_scope | hold_id + member_number | Deferred business DDL |
| hold_review | audit.hold_review | hold_id + review_number | Deferred business DDL |
| disposal_batch | audit.disposal_batch | batch_id | Deferred business DDL |
| disposal_scope | audit.disposal_scope | batch_id + item_id | Deferred business DDL |
| disposal_job | audit.disposal_job | job_id | Deferred business DDL |
| disposal_item | audit.disposal_item | result_id | Deferred business DDL |
| disposal_category_total | audit.disposal_category_total | job_id + category_code | Deferred business DDL |
| backup_copy | audit.backup_copy | backup_id | Deferred business DDL |
| restore_validation | audit.restore_validation | restore_id | Deferred business DDL |
| access_attempt | audit.access_attempt | attempt_id | Deferred business DDL |
| loan_schedule | curated.loan_schedule | schedule_version | Deferred business DDL |
| loan_obligation | curated.loan_obligation | obligation_version | Deferred business DDL |
| payment_allocation | curated.payment_allocation | allocation_version | Deferred business DDL |
| payment_unapplied | curated.payment_unapplied | unapplied_version | Deferred business DDL |
| payment_adjustment | curated.payment_adjustment | adjustment_key | Deferred business DDL |
| loan_account | curated.loan_account | loan_account_version | Deferred business DDL |
| payment_transaction_link | curated.payment_transaction_link | link_version | Deferred business DDL |
| loan_contract_publication | curated.loan_contract_publication | publication_version + entity_name + natural_identity | Deferred business DDL |
| organizational_unit | curated.organizational_unit | organization_key | Deferred business DDL |
| region | curated.region | region_version | Deferred business DDL |
| organizational_successor | curated.organizational_successor | successor_version | Deferred business DDL |
| account_branch_assignment | curated.account_branch_assignment | assignment_version | Deferred business DDL |
| loan_branch_assignment | curated.loan_branch_assignment | assignment_version | Deferred business DDL |
| complaint_branch_assignment | curated.complaint_branch_assignment | assignment_version | Deferred business DDL |
| branch_attribution | curated.branch_attribution | attribution_key | Deferred business DDL |
| organization_publication | curated.organization_publication | publication_version + entity_name + natural_identity | Deferred business DDL |
| successor_scope_mapping | security.successor_scope_mapping | scope_mapping_version | Deferred business DDL |
| scope_resolution | audit.scope_resolution | resolution_key | Deferred business DDL |

## Exhaustive field mapping

### branch

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| branch_key | curated.branch.branch_key | bigint | R | PK-01; deferred |
| branch_id | curated.branch.branch_id | varchar(128) | R | COL-01; deferred |
| branch_name | curated.branch.branch_name | varchar(200) | R | COL-01; deferred |
| region_id | curated.branch.region_id | varchar(128) | R | COL-01; deferred |
| valid_from | curated.branch.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.branch.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |
| source_system | curated.branch.source_system | varchar(50) | R | COL-01; deferred |
| region_version | curated.branch.region_version | varchar(128) | R | COL-01, REF-01, TIME-01; deferred |
| organization_key | curated.branch.organization_key | varchar(128) | R | COL-01, REF-01; deferred |
| source_version | curated.branch.source_version | varchar(128) | R | COL-01; deferred |
| supersedes_branch_key | curated.branch.supersedes_branch_key | bigint | C: correction | COL-01, REF-01, COND-01; deferred |
| correction_action_id | curated.branch.correction_action_id | varchar(128) | C: correction | COL-01, REF-01, COND-01, TIME-01; deferred |
| affected_from | curated.branch.affected_from | timestamptz(6) | C: correction | COL-01, COND-01, TIME-01; deferred |
| affected_to | curated.branch.affected_to | timestamptz(6) | O: open-ended or not correction | COL-01, TIME-01; deferred |
| correction_reason | curated.branch.correction_reason | varchar(200) | C: correction | COL-01, COND-01; deferred |
| original_effective_end | curated.branch.original_effective_end | timestamptz(6) | C: ended interval | COL-01, COND-01, TIME-01; deferred |

### customer

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| customer_key | curated.customer.customer_key | bigint | R | PK-01; deferred |
| display_name | curated.customer.display_name | varchar(200) | R | COL-01; deferred |
| synthetic_master_id | curated.customer.synthetic_master_id | varchar(128) | R | COL-01; deferred |
| contact | curated.customer.contact | varchar(254) | O: not applicable or not supplied; supplied values must validate | COL-01; deferred |
| source_system | curated.customer.source_system | varchar(50) | R | COL-01; deferred |
| source_customer_id | curated.customer.source_customer_id | varchar(128) | R | COL-01; deferred |

### customer_identity

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| identity_key | curated.customer_identity.identity_key | bigint | R | PK-01; deferred |
| customer_key | curated.customer_identity.customer_key | bigint | R | COL-01, REF-01; deferred |
| source_system | curated.customer_identity.source_system | varchar(50) | R | COL-01; deferred |
| source_customer_id | curated.customer_identity.source_customer_id | varchar(128) | R | COL-01; deferred |
| valid_from | curated.customer_identity.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.customer_identity.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |
| match_method | curated.customer_identity.match_method | varchar(50) | R | COL-01; deferred |
| review_state | curated.customer_identity.review_state | varchar(50) | R | COL-01; deferred |
| approval_reference | curated.customer_identity.approval_reference | varchar(100) | C: approved identity mapping | COL-01, COND-01; deferred |

### customer_version

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| customer_version_key | curated.customer_version.customer_version_key | bigint | R | PK-01; deferred |
| customer_key | curated.customer_version.customer_key | bigint | R | COL-01, REF-01; deferred |
| segment | curated.customer_version.segment | varchar(50) | R | COL-01; deferred |
| branch_key | curated.customer_version.branch_key | bigint | R | COL-01, REF-01; deferred |
| valid_from | curated.customer_version.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.customer_version.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |

### account

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| account_key | curated.account.account_key | bigint | R | PK-01; deferred |
| source_account_id | curated.account.source_account_id | varchar(128) | R | COL-01; deferred |
| account_number | curated.account.account_number | varchar(128) | R | COL-01; deferred |
| masked_account | curated.account.masked_account | varchar(128) | R | COL-01; deferred |
| branch_key | curated.account.branch_key | bigint | R | COL-01, REF-01; deferred |
| account_type | curated.account.account_type | varchar(50) | R | COL-01; deferred |
| opened_date | curated.account.opened_date | date | R | COL-01; deferred |
| closed_date | curated.account.closed_date | date | C: closed account | COL-01, COND-01; deferred |
| source_system | curated.account.source_system | varchar(50) | R | COL-01; deferred |

### account_customer

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| account_key | curated.account_customer.account_key | bigint | R | PK-01, REF-01; deferred |
| customer_key | curated.account_customer.customer_key | bigint | R | PK-01, REF-01; deferred |
| relationship_role | curated.account_customer.relationship_role | varchar(50) | R | PK-01; deferred |
| valid_from | curated.account_customer.valid_from | timestamptz(6) | R | PK-01, TIME-01; deferred |
| valid_to | curated.account_customer.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |

### transaction

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| transaction_key | curated.transaction.transaction_key | bigint | R | PK-01; deferred |
| source_transaction_id | curated.transaction.source_transaction_id | varchar(128) | R | COL-01; deferred |
| account_key | curated.transaction.account_key | bigint | R | COL-01, REF-01; deferred |
| branch_key | curated.transaction.branch_key | bigint | R | COL-01, REF-01; deferred |
| occurred_at | curated.transaction.occurred_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| amount | curated.transaction.amount | numeric(20,4) | R | COL-01, NUM-01; deferred |
| currency | curated.transaction.currency | char(3) | R | COL-01; deferred |
| transaction_type | curated.transaction.transaction_type | varchar(50) | R | COL-01; deferred |
| raw_status | curated.transaction.raw_status | varchar(50) | R | COL-01; deferred |
| status | curated.transaction.status | varchar(50) | R | COL-01; deferred |
| source_system | curated.transaction.source_system | varchar(50) | R | COL-01; deferred |
| source_initiating_customer_id | curated.transaction.source_initiating_customer_id | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01; deferred |
| debit_credit_direction | curated.transaction.debit_credit_direction | varchar(50) | R | COL-01; deferred |
| absolute_comparison_amount | curated.transaction.absolute_comparison_amount | numeric(20,4) | C: eligible RC-01 comparison | COL-01, NUM-01, COND-01; deferred |
| business_date | curated.transaction.business_date | date | R | COL-01; deferred |
| source_version | curated.transaction.source_version | varchar(128) | R | COL-01; deferred |
| batch_revision | curated.transaction.batch_revision | integer | R | COL-01; deferred |
| supersedes_event_key | curated.transaction.supersedes_event_key | bigint | O | COL-01, REF-01; deferred |

### loan

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| loan_key | curated.loan.loan_key | bigint | R | PK-01; deferred |
| source_loan_id | curated.loan.source_loan_id | varchar(128) | R | COL-01; deferred |
| branch_key | curated.loan.branch_key | bigint | R | COL-01, REF-01; deferred |
| loan_type | curated.loan.loan_type | varchar(50) | R | COL-01; deferred |
| originated_date | curated.loan.originated_date | date | R | COL-01; deferred |
| source_system | curated.loan.source_system | varchar(50) | R | COL-01; deferred |
| contractual_currency | curated.loan.contractual_currency | char(3) | R | COL-01; deferred |

### loan_customer

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| loan_key | curated.loan_customer.loan_key | bigint | R | PK-01, REF-01; deferred |
| customer_key | curated.loan_customer.customer_key | bigint | R | PK-01, REF-01; deferred |
| relationship_role | curated.loan_customer.relationship_role | varchar(50) | R | PK-01; deferred |
| valid_from | curated.loan_customer.valid_from | timestamptz(6) | R | PK-01, TIME-01; deferred |
| valid_to | curated.loan_customer.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |

### loan_snapshot

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| loan_key | curated.loan_snapshot.loan_key | bigint | R | COL-01, REF-01; deferred |
| business_date | curated.loan_snapshot.business_date | date | R | COL-01; deferred |
| currency | curated.loan_snapshot.currency | char(3) | R | COL-01; deferred |
| days_past_due | curated.loan_snapshot.days_past_due | integer | R | COL-01; deferred |
| status | curated.loan_snapshot.status | varchar(50) | R | COL-01; deferred |
| as_of_cutoff_at | curated.loan_snapshot.as_of_cutoff_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| batch_revision | curated.loan_snapshot.batch_revision | integer | R | COL-01; deferred |
| source_version | curated.loan_snapshot.source_version | varchar(128) | R | COL-01; deferred |
| snapshot_version | curated.loan_snapshot.snapshot_version | varchar(128) | R | PK-01; deferred |
| reconstruction_reference | curated.loan_snapshot.reconstruction_reference | varchar(100) | C: reliably reconstructed snapshot | COL-01, COND-01; deferred |
| state_availability | curated.loan_snapshot.state_availability | varchar(50) | R | COL-01; deferred |
| supersedes_snapshot_version | curated.loan_snapshot.supersedes_snapshot_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| correction_reference | curated.loan_snapshot.correction_reference | varchar(100) | C: corrected version | COL-01, COND-01; deferred |
| outstanding_principal | curated.loan_snapshot.outstanding_principal | numeric(20,4) | R | COL-01, NUM-01; deferred |

### loan_payment

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| payment_key | curated.loan_payment.payment_key | bigint | R | PK-01; deferred |
| source_payment_id | curated.loan_payment.source_payment_id | varchar(128) | R | COL-01; deferred |
| loan_key | curated.loan_payment.loan_key | bigint | R | COL-01, REF-01; deferred |
| paid_at | curated.loan_payment.paid_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| amount | curated.loan_payment.amount | numeric(20,4) | R | COL-01, NUM-01; deferred |
| currency | curated.loan_payment.currency | char(3) | R | COL-01; deferred |
| source_system | curated.loan_payment.source_system | varchar(50) | R | COL-01; deferred |
| business_date | curated.loan_payment.business_date | date | R | COL-01; deferred |
| source_version | curated.loan_payment.source_version | varchar(128) | R | COL-01; deferred |
| batch_revision | curated.loan_payment.batch_revision | integer | R | COL-01; deferred |
| supersedes_event_key | curated.loan_payment.supersedes_event_key | bigint | O | COL-01, REF-01; deferred |
| raw_status | curated.loan_payment.raw_status | varchar(50) | R | COL-01; deferred |
| status | curated.loan_payment.status | varchar(50) | R | COL-01; deferred |
| correction_reference | curated.loan_payment.correction_reference | varchar(100) | C: corrected event version | COL-01, COND-01; deferred |
| posted_at | curated.loan_payment.posted_at | timestamptz(6) | C: POSTED | COL-01, COND-01, TIME-01; deferred |

### fraud_alert

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| alert_key | curated.fraud_alert.alert_key | bigint | R | PK-01; deferred |
| source_alert_id | curated.fraud_alert.source_alert_id | varchar(128) | R | COL-01; deferred |
| customer_key | curated.fraud_alert.customer_key | bigint | R | COL-01, REF-01; deferred |
| transaction_key | curated.fraud_alert.transaction_key | bigint | O: alert linked to transaction | COL-01, REF-01; deferred |
| alert_time | curated.fraud_alert.alert_time | timestamptz(6) | R | COL-01, TIME-01; deferred |
| severity | curated.fraud_alert.severity | varchar(50) | R | COL-01; deferred |
| case_status | curated.fraud_alert.case_status | varchar(50) | R | COL-01; deferred |
| reason | curated.fraud_alert.reason | varchar(1000) | R | COL-01; deferred |
| source_system | curated.fraud_alert.source_system | varchar(50) | R | COL-01; deferred |

### complaint

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| complaint_key | curated.complaint.complaint_key | bigint | R | PK-01; deferred |
| source_complaint_id | curated.complaint.source_complaint_id | varchar(128) | R | COL-01; deferred |
| customer_key | curated.complaint.customer_key | bigint | R | COL-01, REF-01; deferred |
| branch_key | curated.complaint.branch_key | bigint | R | COL-01, REF-01; deferred |
| priority | curated.complaint.priority | varchar(50) | R | COL-01; deferred |
| channel | curated.complaint.channel | varchar(50) | R | COL-01; deferred |
| status | curated.complaint.status | varchar(50) | R | COL-01; deferred |
| source_system | curated.complaint.source_system | varchar(50) | R | COL-01; deferred |
| created_at | curated.complaint.created_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| priority_at_creation | curated.complaint.priority_at_creation | varchar(50) | C: SLA evaluation | COL-01, COND-01; deferred |
| closed_at | curated.complaint.closed_at | timestamptz(6) | C: closed selected state | COL-01, COND-01, TIME-01; deferred |
| final_closed_at | curated.complaint.final_closed_at | timestamptz(6) | C: finally closed in selected publication | COL-01, COND-01, TIME-01; deferred |

### complaint_snapshot

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| complaint_key | curated.complaint_snapshot.complaint_key | bigint | R | COL-01, REF-01; deferred |
| business_date | curated.complaint_snapshot.business_date | date | R | COL-01; deferred |
| branch_key | curated.complaint_snapshot.branch_key | bigint | R | COL-01, REF-01; deferred |
| priority | curated.complaint_snapshot.priority | varchar(50) | R | COL-01; deferred |
| channel | curated.complaint_snapshot.channel | varchar(50) | R | COL-01; deferred |
| status | curated.complaint_snapshot.status | varchar(50) | R | COL-01; deferred |
| as_of_cutoff_at | curated.complaint_snapshot.as_of_cutoff_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| batch_revision | curated.complaint_snapshot.batch_revision | integer | R | COL-01; deferred |
| source_version | curated.complaint_snapshot.source_version | varchar(128) | R | COL-01; deferred |
| snapshot_version | curated.complaint_snapshot.snapshot_version | varchar(128) | R | PK-01; deferred |
| reconstruction_reference | curated.complaint_snapshot.reconstruction_reference | varchar(100) | C: reliably reconstructed snapshot | COL-01, COND-01; deferred |
| created_at | curated.complaint_snapshot.created_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| priority_at_creation | curated.complaint_snapshot.priority_at_creation | varchar(50) | C: SLA evaluation | COL-01, COND-01; deferred |
| closed_at | curated.complaint_snapshot.closed_at | timestamptz(6) | C: closed selected state | COL-01, COND-01, TIME-01; deferred |
| state_availability | curated.complaint_snapshot.state_availability | varchar(50) | R | COL-01; deferred |
| supersedes_snapshot_version | curated.complaint_snapshot.supersedes_snapshot_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| correction_reference | curated.complaint_snapshot.correction_reference | varchar(100) | C: corrected version | COL-01, COND-01; deferred |

### risk_assessment

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| assessment_key | curated.risk_assessment.assessment_key | bigint | R | PK-01; deferred |
| customer_key | curated.risk_assessment.customer_key | bigint | R | COL-01, REF-01; deferred |
| business_date | curated.risk_assessment.business_date | date | R | COL-01; deferred |
| evidence_state | curated.risk_assessment.evidence_state | varchar(50) | R | COL-01; deferred |
| rule_version | curated.risk_assessment.rule_version | varchar(128) | C: evaluated assessment | COL-01, REF-01, COND-01; deferred |
| catalog_version | curated.risk_assessment.catalog_version | varchar(128) | C: evaluated assessment | COL-01, REF-01, COND-01; deferred |
| assessment_at | curated.risk_assessment.assessment_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| unknown_count | curated.risk_assessment.unknown_count | bigint | C: valid catalog evaluation | COL-01, COND-01; deferred |
| unavailable_reason | curated.risk_assessment.unavailable_reason | varchar(100) | C: unavailable assessment | COL-01, COND-01; deferred |
| publication_version | curated.risk_assessment.publication_version | varchar(128) | C: published assessment | COL-01, REF-01, COND-01; deferred |
| triggered_count | curated.risk_assessment.triggered_count | bigint | C: valid catalog evaluation | COL-01, COND-01; deferred |
| classification | curated.risk_assessment.classification | varchar(50) | R | COL-01; deferred |

### risk_evidence

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| assessment_key | curated.risk_evidence.assessment_key | bigint | R | PK-01, REF-01; deferred |
| condition_id | curated.risk_evidence.condition_id | varchar(50) | R | PK-01; deferred |
| trigger_state | curated.risk_evidence.trigger_state | varchar(50) | R | COL-01; deferred |
| observed_value | curated.risk_evidence.observed_value | numeric(28,8) | C: applicable valid numeric condition observation | COL-01, NUM-01, COND-01; deferred |
| threshold | curated.risk_evidence.threshold | numeric(28,8) | C: numeric configured threshold | COL-01, NUM-01, COND-01; deferred |
| rule_version | curated.risk_evidence.rule_version | varchar(128) | C: evaluable condition | COL-01, REF-01, COND-01; deferred |
| missing_evidence_reason | curated.risk_evidence.missing_evidence_reason | varchar(100) | C: Unknown | COL-01, COND-01; deferred |
| threshold_reference | curated.risk_evidence.threshold_reference | varchar(100) | C: configured condition | COL-01, COND-01; deferred |

### rule_config

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| parameter_id | config.rule_config.parameter_id | varchar(50) | R | PK-01; deferred |
| value_type | config.rule_config.value_type | varchar(50) | R | COL-01; deferred |
| configuration_version | config.rule_config.configuration_version | varchar(128) | R | PK-01, REF-01; deferred |
| numeric_value | config.rule_config.numeric_value | numeric(28,8) | C: matching value_type | COL-01, NUM-01, COND-01; deferred |
| integer_value | config.rule_config.integer_value | bigint | C: matching value_type | COL-01, COND-01; deferred |
| code_value | config.rule_config.code_value | varchar(50) | C: matching value_type | COL-01, COND-01; deferred |
| reference_value | config.rule_config.reference_value | varchar(100) | C: matching value_type | COL-01, COND-01; deferred |
| boolean_value | config.rule_config.boolean_value | boolean | C: matching value_type | COL-01, COND-01; deferred |

### pipeline_run

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| run_id | audit.pipeline_run.run_id | varchar(128) | R | PK-01; deferred |
| business_date | audit.pipeline_run.business_date | date | R | COL-01; deferred |
| started_at | audit.pipeline_run.started_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| status | audit.pipeline_run.status | varchar(50) | R | COL-01; deferred |
| source_rows | audit.pipeline_run.source_rows | bigint | C: corresponding measured control available | COL-01, COND-01; deferred |
| accepted_rows | audit.pipeline_run.accepted_rows | bigint | C: corresponding measured control available | COL-01, COND-01; deferred |
| rejected_rows | audit.pipeline_run.rejected_rows | bigint | C: corresponding measured control available | COL-01, COND-01; deferred |
| excluded_rows | audit.pipeline_run.excluded_rows | bigint | C: corresponding measured control available | COL-01, COND-01; deferred |
| required_cells | audit.pipeline_run.required_cells | bigint | C: corresponding measured control available | COL-01, COND-01; deferred |
| present_cells | audit.pipeline_run.present_cells | bigint | C: corresponding measured control available | COL-01, COND-01; deferred |
| unavailable_reason | audit.pipeline_run.unavailable_reason | varchar(100) | C: unavailable run control | COL-01, COND-01; deferred |
| ended_at | audit.pipeline_run.ended_at | timestamptz(6) | C: attempt ended | COL-01, COND-01, TIME-01; deferred |
| readiness_at | audit.pipeline_run.readiness_at | timestamptz(6) | C: publication ready | COL-01, COND-01, TIME-01; deferred |
| publication_version | audit.pipeline_run.publication_version | varchar(128) | C: successful publication | COL-01, REF-01, COND-01; deferred |

### source_extract

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| extract_id | audit.source_extract.extract_id | varchar(128) | R | COL-01; deferred |
| source_system | audit.source_extract.source_system | varchar(50) | R | PK-01; deferred |
| entity_name | audit.source_extract.entity_name | varchar(50) | R | PK-01; deferred |
| business_date | audit.source_extract.business_date | date | R | PK-01; deferred |
| revision | audit.source_extract.revision | integer | R | PK-01; deferred |
| delivery_mode | audit.source_extract.delivery_mode | varchar(50) | R | COL-01; deferred |
| schema_version | audit.source_extract.schema_version | varchar(128) | R | COL-01; deferred |
| cutoff_at | audit.source_extract.cutoff_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| extracted_at | audit.source_extract.extracted_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| checksum | audit.source_extract.checksum | varchar(128) | R | COL-01; deferred |
| row_count | audit.source_extract.row_count | bigint | R | COL-01; deferred |
| checksum_algorithm | audit.source_extract.checksum_algorithm | varchar(50) | R | COL-01; deferred |
| checksum_encoding | audit.source_extract.checksum_encoding | varchar(50) | R | COL-01; deferred |
| content_encoding | audit.source_extract.content_encoding | varchar(50) | R | COL-01; deferred |
| checksum_scope_reference | audit.source_extract.checksum_scope_reference | varchar(100) | R | COL-01; deferred |

### quality_exception

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| exception_key | audit.quality_exception.exception_key | bigint | R | PK-01; deferred |
| run_id | audit.quality_exception.run_id | varchar(128) | R | COL-01, REF-01; deferred |
| extract_id | audit.quality_exception.extract_id | varchar(128) | R | COL-01; deferred |
| row_locator | audit.quality_exception.row_locator | varchar(100) | O: not applicable or not supplied; supplied values must validate | COL-01; deferred |
| rule_id | audit.quality_exception.rule_id | varchar(50) | R | COL-01; deferred |
| reason_code | audit.quality_exception.reason_code | varchar(100) | R | COL-01; deferred |
| severity | audit.quality_exception.severity | varchar(50) | R | COL-01; deferred |
| disposition | audit.quality_exception.disposition | varchar(50) | R | COL-01; deferred |
| source_system | audit.quality_exception.source_system | varchar(50) | R | COL-01, REF-02; deferred |
| entity_name | audit.quality_exception.entity_name | varchar(50) | R | COL-01, REF-02; deferred |
| business_date | audit.quality_exception.business_date | date | R | COL-01, REF-02; deferred |
| revision | audit.quality_exception.revision | integer | R | COL-01, REF-02; deferred |

### reconciliation_result

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| reconciliation_key | audit.reconciliation_result.reconciliation_key | bigint | R | PK-01; deferred |
| run_id | audit.reconciliation_result.run_id | varchar(128) | R | COL-01, REF-01; deferred |
| extract_id | audit.reconciliation_result.extract_id | varchar(128) | R | COL-01; deferred |
| measure | audit.reconciliation_result.measure | varchar(50) | R | COL-01; deferred |
| currency | audit.reconciliation_result.currency | char(3) | O: not applicable or not supplied; supplied values must validate | COL-01; deferred |
| explanation_reference | audit.reconciliation_result.explanation_reference | varchar(100) | O: not applicable or not supplied; supplied values must validate | COL-01; deferred |
| population_key | audit.reconciliation_result.population_key | bigint | R | COL-01, REF-01; deferred |
| source_value | audit.reconciliation_result.source_value | numeric(28,4) | C: available financial comparison | COL-01, NUM-01, COND-01; deferred |
| target_value | audit.reconciliation_result.target_value | numeric(28,4) | C: available financial comparison | COL-01, NUM-01, COND-01; deferred |
| explained_adjustment | audit.reconciliation_result.explained_adjustment | numeric(28,4) | C: available financial comparison | COL-01, NUM-01, COND-01; deferred |
| variance | audit.reconciliation_result.variance | numeric(28,4) | C: available financial comparison | COL-01, NUM-01, COND-01; deferred |
| source_count | audit.reconciliation_result.source_count | bigint | C: available count comparison | COL-01, COND-01; deferred |
| target_count | audit.reconciliation_result.target_count | bigint | C: available count comparison | COL-01, COND-01; deferred |
| adjustment_count | audit.reconciliation_result.adjustment_count | bigint | C: available count comparison | COL-01, COND-01; deferred |
| count_variance | audit.reconciliation_result.count_variance | bigint | C: available count comparison | COL-01, COND-01; deferred |
| unavailable_reason | audit.reconciliation_result.unavailable_reason | varchar(100) | C: unavailable comparison | COL-01, COND-01; deferred |
| source_system | audit.reconciliation_result.source_system | varchar(50) | R | COL-01, REF-02; deferred |
| entity_name | audit.reconciliation_result.entity_name | varchar(50) | R | COL-01, REF-02; deferred |
| business_date | audit.reconciliation_result.business_date | date | R | COL-01, REF-02; deferred |
| revision | audit.reconciliation_result.revision | integer | R | COL-01, REF-02; deferred |
| status | audit.reconciliation_result.status | varchar(50) | R | COL-01; deferred |

### export_event

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| event_key | audit.export_event.event_key | bigint | R | PK-01; deferred |
| user_identity | audit.export_event.user_identity | varchar(128) | R | COL-01; deferred |
| active_role | audit.export_event.active_role | varchar(50) | C: selected role supplied | COL-01, COND-01; deferred |
| policy_version | audit.export_event.policy_version | varchar(128) | R | COL-01, REF-01; deferred |
| report | audit.export_event.report | varchar(200) | R | COL-01; deferred |
| format | audit.export_event.format | varchar(50) | R | COL-01; deferred |
| requested_at | audit.export_event.requested_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| authorization_checked_at | audit.export_event.authorization_checked_at | timestamptz(6) | C: execution or terminal denial | COL-01, COND-01, TIME-01; deferred |
| completed_at | audit.export_event.completed_at | timestamptz(6) | C: terminal attempt | COL-01, COND-01, TIME-01; deferred |
| decision | audit.export_event.decision | varchar(50) | C: terminal attempt | COL-01, COND-01; deferred |
| denial_reason | audit.export_event.denial_reason | varchar(100) | C: denied attempt | COL-01, COND-01; deferred |
| publication_version | audit.export_event.publication_version | varchar(128) | C: selected publication exists | COL-01, REF-01, COND-01; deferred |
| row_count | audit.export_event.row_count | bigint | C: measured output count | COL-01, COND-01; deferred |
| output_classification | audit.export_event.output_classification | varchar(50) | R | COL-01; deferred |
| duration_seconds | audit.export_event.duration_seconds | numeric(28,8) | C: completed measured attempt | COL-01, NUM-01, COND-01; deferred |

### complaint_history_event

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| history_event_key | curated.complaint_history_event.history_event_key | bigint | R | PK-01; deferred |
| complaint_key | curated.complaint_history_event.complaint_key | bigint | R | COL-01, REF-01; deferred |
| event_type | curated.complaint_history_event.event_type | varchar(50) | R | COL-01; deferred |
| event_at | curated.complaint_history_event.event_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| source_version | curated.complaint_history_event.source_version | varchar(128) | R | COL-01; deferred |
| publication_version | curated.complaint_history_event.publication_version | varchar(128) | C: published history | COL-01, REF-01, COND-01; deferred |

### loan_snapshot_publication

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| publication_version | curated.loan_snapshot_publication.publication_version | varchar(128) | R | PK-01, REF-01; deferred |
| loan_key | curated.loan_snapshot_publication.loan_key | bigint | R | PK-01, REF-01; deferred |
| business_date | curated.loan_snapshot_publication.business_date | date | R | PK-01; deferred |
| snapshot_version | curated.loan_snapshot_publication.snapshot_version | varchar(128) | R | COL-01, REF-01; deferred |

### complaint_snapshot_publication

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| publication_version | curated.complaint_snapshot_publication.publication_version | varchar(128) | R | PK-01, REF-01; deferred |
| complaint_key | curated.complaint_snapshot_publication.complaint_key | bigint | R | PK-01, REF-01; deferred |
| business_date | curated.complaint_snapshot_publication.business_date | date | R | PK-01; deferred |
| snapshot_version | curated.complaint_snapshot_publication.snapshot_version | varchar(128) | R | COL-01, REF-01; deferred |

### historical_coverage

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| coverage_key | curated.historical_coverage.coverage_key | bigint | R | PK-01; deferred |
| entity_name | curated.historical_coverage.entity_name | varchar(50) | R | COL-01; deferred |
| source_system | curated.historical_coverage.source_system | varchar(50) | R | COL-01; deferred |
| source_record_id | curated.historical_coverage.source_record_id | varchar(128) | R | COL-01; deferred |
| business_date | curated.historical_coverage.business_date | date | R | COL-01; deferred |
| publication_version | curated.historical_coverage.publication_version | varchar(128) | C: published coverage | COL-01, REF-01, COND-01; deferred |
| state_availability | curated.historical_coverage.state_availability | varchar(50) | R | COL-01; deferred |
| unavailable_reason | curated.historical_coverage.unavailable_reason | varchar(100) | R | COL-01; deferred |

### risk_evidence_item

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| evidence_item_key | curated.risk_evidence_item.evidence_item_key | bigint | R | PK-01; deferred |
| assessment_key | curated.risk_evidence_item.assessment_key | bigint | R | COL-01, REF-02; deferred |
| condition_id | curated.risk_evidence_item.condition_id | varchar(50) | R | COL-01, REF-02; deferred |
| source_reference_key | curated.risk_evidence_item.source_reference_key | bigint | R | COL-01, REF-01; deferred |
| comparison_key | curated.risk_evidence_item.comparison_key | bigint | C: RC-01 comparison evidence | COL-01, REF-01, COND-01; deferred |
| observed_value | curated.risk_evidence_item.observed_value | numeric(28,8) | C: numeric observation | COL-01, NUM-01, COND-01; deferred |
| observed_at | curated.risk_evidence_item.observed_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| correction_reference | curated.risk_evidence_item.correction_reference | varchar(100) | C: corrected observation | COL-01, COND-01; deferred |

### rc01_comparison

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| comparison_key | curated.rc01_comparison.comparison_key | bigint | R | PK-01; deferred |
| transaction_key | curated.rc01_comparison.transaction_key | bigint | R | COL-01, REF-01; deferred |
| account_key | curated.rc01_comparison.account_key | bigint | R | COL-01, REF-01; deferred |
| customer_key | curated.rc01_comparison.customer_key | bigint | C: resolved valid initiator or sole owner | COL-01, REF-01, COND-01; deferred |
| signed_source_amount | curated.rc01_comparison.signed_source_amount | numeric(20,4) | C: valid supplied amount | COL-01, NUM-01, COND-01; deferred |
| absolute_comparison_amount | curated.rc01_comparison.absolute_comparison_amount | numeric(20,4) | C: eligible comparison | COL-01, NUM-01, COND-01; deferred |
| debit_credit_direction | curated.rc01_comparison.debit_credit_direction | varchar(50) | C: supplied valid direction | COL-01, COND-01; deferred |
| event_at | curated.rc01_comparison.event_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| window_start | curated.rc01_comparison.window_start | timestamptz(6) | R | COL-01, TIME-01; deferred |
| window_end | curated.rc01_comparison.window_end | timestamptz(6) | R | COL-01, TIME-01; deferred |
| history_count | curated.rc01_comparison.history_count | bigint | C: available history | COL-01, COND-01; deferred |
| prior_amount_sum | curated.rc01_comparison.prior_amount_sum | numeric(28,4) | C: complete valid prior evidence | COL-01, NUM-01, COND-01; deferred |
| prior_average | curated.rc01_comparison.prior_average | numeric(28,8) | C: exactly representable valid mean | COL-01, NUM-01, COND-01; deferred |
| multiplier | curated.rc01_comparison.multiplier | numeric(28,8) | R | COL-01, NUM-01; deferred |
| currency | curated.rc01_comparison.currency | char(3) | C: valid mapped currency | COL-01, COND-01; deferred |
| window_complete | curated.rc01_comparison.window_complete | boolean | R | COL-01; deferred |
| attribution_method | curated.rc01_comparison.attribution_method | varchar(50) | R | COL-01; deferred |
| missing_evidence_reason | curated.rc01_comparison.missing_evidence_reason | varchar(100) | C: Unknown | COL-01, COND-01; deferred |
| recalculation_revision | curated.rc01_comparison.recalculation_revision | integer | R | COL-01; deferred |
| rule_version | curated.rc01_comparison.rule_version | varchar(128) | R | COL-01, REF-01; deferred |
| publication_version | curated.rc01_comparison.publication_version | varchar(128) | C: published evidence | COL-01, REF-01, COND-01; deferred |
| supersedes_comparison_key | curated.rc01_comparison.supersedes_comparison_key | bigint | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |

### account_restriction_state

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| state_version | curated.account_restriction_state.state_version | varchar(128) | R | PK-01; deferred |
| account_key | curated.account_restriction_state.account_key | bigint | R | COL-01, REF-01; deferred |
| effective_from | curated.account_restriction_state.effective_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| effective_to | curated.account_restriction_state.effective_to | timestamptz(6) | O: not applicable or not supplied; supplied values must validate | COL-01, TIME-01; deferred |
| state_as_of_at | curated.account_restriction_state.state_as_of_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| source_version | curated.account_restriction_state.source_version | varchar(128) | R | COL-01; deferred |
| publication_version | curated.account_restriction_state.publication_version | varchar(128) | C: published state | COL-01, REF-01, COND-01; deferred |
| supersedes_state_version | curated.account_restriction_state.supersedes_state_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| raw_risk_restriction_status | curated.account_restriction_state.raw_risk_restriction_status | varchar(50) | R | COL-01; deferred |
| risk_restriction_status | curated.account_restriction_state.risk_restriction_status | varchar(50) | C: valid approved mapping | COL-01, COND-01; deferred |

### fraud_alert_state

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| state_version | curated.fraud_alert_state.state_version | varchar(128) | R | PK-01; deferred |
| alert_key | curated.fraud_alert_state.alert_key | bigint | R | COL-01, REF-01; deferred |
| effective_from | curated.fraud_alert_state.effective_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| effective_to | curated.fraud_alert_state.effective_to | timestamptz(6) | O: not applicable or not supplied; supplied values must validate | COL-01, TIME-01; deferred |
| state_as_of_at | curated.fraud_alert_state.state_as_of_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| source_version | curated.fraud_alert_state.source_version | varchar(128) | R | COL-01; deferred |
| publication_version | curated.fraud_alert_state.publication_version | varchar(128) | C: published state | COL-01, REF-01, COND-01; deferred |
| supersedes_state_version | curated.fraud_alert_state.supersedes_state_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| raw_case_status | curated.fraud_alert_state.raw_case_status | varchar(50) | R | COL-01; deferred |
| case_status | curated.fraud_alert_state.case_status | varchar(50) | C: valid approved mapping | COL-01, COND-01; deferred |
| raw_severity | curated.fraud_alert_state.raw_severity | varchar(50) | R | COL-01; deferred |
| severity | curated.fraud_alert_state.severity | varchar(50) | C: valid approved mapping | COL-01, COND-01; deferred |

### publication

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| publication_version | audit.publication.publication_version | varchar(128) | R | PK-01; deferred |
| approval_reference | audit.publication.approval_reference | varchar(100) | C: approved or successfully published version | COL-01, COND-01; deferred |
| status | audit.publication.status | varchar(50) | R | COL-01; deferred |
| supersedes_version | audit.publication.supersedes_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| business_date | audit.publication.business_date | date | R | COL-01; deferred |
| run_id | audit.publication.run_id | varchar(128) | R | COL-01, REF-01; deferred |
| candidate_id | audit.publication.candidate_id | varchar(128) | R | COL-01, REF-01; deferred |
| published_at | audit.publication.published_at | timestamptz(6) | C: released publication | COL-01, COND-01, TIME-01; deferred |

### catalog_version

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| catalog_version | config.catalog_version.catalog_version | varchar(128) | R | PK-01; deferred |
| approval_reference | config.catalog_version.approval_reference | varchar(100) | C: approved or successfully published version | COL-01, COND-01; deferred |
| status | config.catalog_version.status | varchar(50) | R | COL-01; deferred |
| supersedes_version | config.catalog_version.supersedes_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| valid_from | config.catalog_version.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | config.catalog_version.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |

### rule_version

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| rule_version | config.rule_version.rule_version | varchar(128) | R | PK-01; deferred |
| approval_reference | config.rule_version.approval_reference | varchar(100) | C: approved or successfully published version | COL-01, COND-01; deferred |
| status | config.rule_version.status | varchar(50) | R | COL-01; deferred |
| supersedes_version | config.rule_version.supersedes_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| valid_from | config.rule_version.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | config.rule_version.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |
| condition_id | config.rule_version.condition_id | varchar(50) | R | COL-01; deferred |
| configuration_version | config.rule_version.configuration_version | varchar(128) | R | COL-01, REF-01; deferred |

### configuration_version

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| configuration_version | config.configuration_version.configuration_version | varchar(128) | R | PK-01; deferred |
| approval_reference | config.configuration_version.approval_reference | varchar(100) | C: approved or successfully published version | COL-01, COND-01; deferred |
| status | config.configuration_version.status | varchar(50) | R | COL-01; deferred |
| supersedes_version | config.configuration_version.supersedes_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| valid_from | config.configuration_version.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | config.configuration_version.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |

### mapping_version

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| mapping_version | config.mapping_version.mapping_version | varchar(128) | R | PK-01; deferred |
| approval_reference | config.mapping_version.approval_reference | varchar(100) | C: approved or successfully published version | COL-01, COND-01; deferred |
| status | config.mapping_version.status | varchar(50) | R | COL-01; deferred |
| supersedes_version | config.mapping_version.supersedes_version | varchar(128) | O: not applicable or not supplied; supplied values must validate | COL-01, REF-01; deferred |
| valid_from | config.mapping_version.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | config.mapping_version.valid_to | timestamptz(6) | O: open-ended interval | COL-01, TIME-01; deferred |

### catalog_rule

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| catalog_version | config.catalog_rule.catalog_version | varchar(128) | R | PK-01, REF-01; deferred |
| condition_id | config.catalog_rule.condition_id | varchar(50) | R | PK-01; deferred |
| rule_version | config.catalog_rule.rule_version | varchar(128) | R | COL-01, REF-01; deferred |

### mapping_entry

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| mapping_version | config.mapping_entry.mapping_version | varchar(128) | R | PK-01, REF-01; deferred |
| source_system | config.mapping_entry.source_system | varchar(50) | R | PK-01; deferred |
| domain_code | config.mapping_entry.domain_code | varchar(50) | R | PK-01; deferred |
| raw_value | config.mapping_entry.raw_value | varchar(50) | R | PK-01; deferred |
| canonical_value | config.mapping_entry.canonical_value | varchar(50) | R | COL-01; deferred |

### mapping_eligibility

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| mapping_version | config.mapping_eligibility.mapping_version | varchar(128) | R | PK-01, REF-02; deferred |
| source_system | config.mapping_eligibility.source_system | varchar(50) | R | PK-01, REF-02; deferred |
| domain_code | config.mapping_eligibility.domain_code | varchar(50) | R | PK-01, REF-02; deferred |
| raw_value | config.mapping_eligibility.raw_value | varchar(50) | R | PK-01, REF-02; deferred |
| eligibility_code | config.mapping_eligibility.eligibility_code | varchar(50) | R | PK-01; deferred |
| is_eligible | config.mapping_eligibility.is_eligible | boolean | R | COL-01; deferred |

### applied_mapping

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| owner_entity | audit.applied_mapping.owner_entity | varchar(50) | R | PK-01; deferred |
| mapping_version | audit.applied_mapping.mapping_version | varchar(128) | R | PK-01, REF-01; deferred |
| usage_code | audit.applied_mapping.usage_code | varchar(50) | R | PK-01; deferred |
| owner_version_key | audit.applied_mapping.owner_version_key -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | PK-01, TR-01, REF-02; deferred |

### run_extract

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| run_id | audit.run_extract.run_id | varchar(128) | R | PK-01, REF-01; deferred |
| source_system | audit.run_extract.source_system | varchar(50) | R | PK-01, REF-02; deferred |
| entity_name | audit.run_extract.entity_name | varchar(50) | R | PK-01, REF-02; deferred |
| business_date | audit.run_extract.business_date | date | R | PK-01, REF-02; deferred |
| revision | audit.run_extract.revision | integer | R | PK-01, REF-02; deferred |

### source_reference

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| source_reference_key | audit.source_reference.source_reference_key | bigint | R | PK-01; deferred |
| owner_entity | audit.source_reference.owner_entity | varchar(50) | R | COL-01; deferred |
| source_system | audit.source_reference.source_system | varchar(50) | R | COL-01, REF-02; deferred |
| entity_name | audit.source_reference.entity_name | varchar(50) | R | COL-01, REF-02; deferred |
| business_date | audit.source_reference.business_date | date | R | COL-01, REF-02; deferred |
| revision | audit.source_reference.revision | integer | R | COL-01, REF-02; deferred |
| source_record_id | audit.source_reference.source_record_id | varchar(128) | C: event/master source row | COL-01, COND-01; deferred |
| source_version | audit.source_reference.source_version | varchar(128) | C: source state/version evidence | COL-01, COND-01; deferred |
| source_updated_at | audit.source_reference.source_updated_at | timestamptz(6) | C: supplied by source contract | COL-01, COND-01, TIME-01; deferred |
| record_operation | audit.source_reference.record_operation | varchar(50) | C: supplied operation | COL-01, COND-01; deferred |
| row_number | audit.source_reference.row_number | bigint | R | COL-01; deferred |
| ingested_at | audit.source_reference.ingested_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| run_id | audit.source_reference.run_id | varchar(128) | R | COL-01, REF-01; deferred |
| owner_version_key | audit.source_reference.owner_version_key -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01, REF-02; deferred |

### control_population

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| population_key | audit.control_population.population_key | bigint | R | PK-01; deferred |
| entity_name | audit.control_population.entity_name | varchar(50) | R | COL-01; deferred |
| business_date | audit.control_population.business_date | date | R | COL-01; deferred |
| publication_version | audit.control_population.publication_version | varchar(128) | C: published target control | COL-01, REF-01, COND-01; deferred |

### population_member

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| population_key | audit.population_member.population_key | bigint | R | PK-01, REF-01; deferred |
| criterion_code | audit.population_member.criterion_code | varchar(50) | R | PK-01; deferred |
| member_value | audit.population_member.member_value | varchar(128) | R | PK-01; deferred |

### source_financial_control

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| source_system | audit.source_financial_control.source_system | varchar(50) | R | PK-01, REF-02; deferred |
| entity_name | audit.source_financial_control.entity_name | varchar(50) | R | PK-01, REF-02; deferred |
| business_date | audit.source_financial_control.business_date | date | R | PK-01, REF-02; deferred |
| revision | audit.source_financial_control.revision | integer | R | PK-01, REF-02; deferred |
| amount_field | audit.source_financial_control.amount_field | varchar(50) | R | PK-01; deferred |
| currency | audit.source_financial_control.currency | char(3) | R | PK-01; deferred |
| population_key | audit.source_financial_control.population_key | bigint | R | PK-01, REF-01; deferred |
| control_total | audit.source_financial_control.control_total | numeric(28,4) | C: available valid control | COL-01, NUM-01, COND-01; deferred |
| unavailable_reason | audit.source_financial_control.unavailable_reason | varchar(100) | C: unavailable control | COL-01, COND-01; deferred |

### export_filter

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| event_key | audit.export_filter.event_key | bigint | R | PK-01, REF-01; deferred |
| filter_code | audit.export_filter.filter_code | varchar(50) | R | PK-01; deferred |
| member_number | audit.export_filter.member_number | bigint | R | PK-01; deferred |
| code_value | audit.export_filter.code_value | varchar(50) | C: code filter | COL-01, COND-01; deferred |
| reference_value | audit.export_filter.reference_value | varchar(100) | C: reference filter | COL-01, COND-01; deferred |
| date_value | audit.export_filter.date_value | date | C: date filter | COL-01, COND-01; deferred |
| instant_value | audit.export_filter.instant_value | timestamptz(6) | C: instant filter | COL-01, COND-01, TIME-01; deferred |
| numeric_value | audit.export_filter.numeric_value | numeric(28,8) | C: numeric filter | COL-01, NUM-01, COND-01; deferred |

### recalculation_impact

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| impact_key | audit.recalculation_impact.impact_key | bigint | R | PK-01; deferred |
| corrected_event_date | audit.recalculation_impact.corrected_event_date | date | R | COL-01; deferred |
| through_date | audit.recalculation_impact.through_date | date | R | COL-01; deferred |
| old_publication_version | audit.recalculation_impact.old_publication_version | varchar(128) | R | COL-01, REF-01; deferred |
| new_publication_version | audit.recalculation_impact.new_publication_version | varchar(128) | C: successful corrected publication | COL-01, REF-01, COND-01; deferred |
| validation_reference | audit.recalculation_impact.validation_reference | varchar(100) | C: corrected publication | COL-01, COND-01; deferred |
| reconciliation_reference | audit.recalculation_impact.reconciliation_reference | varchar(100) | C: corrected publication | COL-01, COND-01; deferred |

### recalculation_customer

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| impact_key | audit.recalculation_customer.impact_key | bigint | R | PK-01, REF-01; deferred |
| customer_key | audit.recalculation_customer.customer_key | bigint | R | PK-01, REF-01; deferred |

### date_dimension

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| date_key | config.date_dimension.date_key | bigint | R | PK-01; deferred |
| calendar_date | config.date_dimension.calendar_date | date | R | COL-01; deferred |
| month | config.date_dimension.month | integer | R | COL-01; deferred |
| quarter | config.date_dimension.quarter | integer | R | COL-01; deferred |
| year | config.date_dimension.year | integer | R | COL-01; deferred |

### transaction_publication

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| publication_version | curated.transaction_publication.publication_version | varchar(128) | R | PK-01, REF-01; deferred |
| source_system | curated.transaction_publication.source_system | varchar(50) | R | PK-01; deferred |
| source_transaction_id | curated.transaction_publication.source_transaction_id | varchar(128) | R | PK-01; deferred |
| business_date | curated.transaction_publication.business_date | date | R | PK-01; deferred |
| transaction_key | curated.transaction_publication.transaction_key | bigint | R | COL-01, REF-01; deferred |

### loan_payment_publication

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| publication_version | curated.loan_payment_publication.publication_version | varchar(128) | R | PK-01, REF-01; deferred |
| source_system | curated.loan_payment_publication.source_system | varchar(50) | R | PK-01; deferred |
| source_payment_id | curated.loan_payment_publication.source_payment_id | varchar(128) | R | PK-01; deferred |
| business_date | curated.loan_payment_publication.business_date | date | R | PK-01; deferred |
| payment_key | curated.loan_payment_publication.payment_key | bigint | R | COL-01, REF-01; deferred |

### access_policy

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| policy_version | security.access_policy.policy_version | varchar(128) | R | PK-01; deferred |
| valid_from | security.access_policy.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | security.access_policy.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| approval_reference | security.access_policy.approval_reference | varchar(100) | R | COL-01; deferred |

### access_entitlement

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| entitlement_id | security.access_entitlement.entitlement_id | varchar(128) | R | PK-01; deferred |
| user_identity | security.access_entitlement.user_identity | varchar(128) | R | COL-01; deferred |
| active_role | security.access_entitlement.active_role | varchar(50) | R | COL-01; deferred |
| permission_code | security.access_entitlement.permission_code | varchar(50) | R | COL-01; deferred |
| effect | security.access_entitlement.effect | varchar(50) | R | COL-01; deferred |
| policy_version | security.access_entitlement.policy_version | varchar(128) | R | COL-01, REF-01; deferred |
| valid_from | security.access_entitlement.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | security.access_entitlement.valid_to | timestamptz(6) | O: open-ended except time-bound grants | COL-01, TIME-01; deferred |
| revoked_at | security.access_entitlement.revoked_at | timestamptz(6) | C: revoked | COL-01, COND-01, TIME-01; deferred |
| requester_identity | security.access_entitlement.requester_identity | varchar(128) | R | COL-01; deferred |
| implementer_identity | security.access_entitlement.implementer_identity | varchar(128) | C: implemented entitlement | COL-01, COND-01; deferred |
| approval_reference | security.access_entitlement.approval_reference | varchar(100) | C: approved entitlement | COL-01, REF-01, COND-01; deferred |

### entitlement_scope

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| entitlement_id | security.entitlement_scope.entitlement_id | varchar(128) | R | PK-01, REF-01; deferred |
| scope_number | security.entitlement_scope.scope_number | bigint | R | PK-01; deferred |
| scope_type | security.entitlement_scope.scope_type | varchar(50) | R | COL-01; deferred |
| scope_value | security.entitlement_scope.scope_value -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01; deferred |

### investigation_case

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| case_key | security.investigation_case.case_key | varchar(128) | R | PK-01; deferred |
| case_type | security.investigation_case.case_type | varchar(50) | R | COL-01; deferred |

### case_evidence_link

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| case_key | security.case_evidence_link.case_key | varchar(128) | R | PK-01, REF-01; deferred |
| item_number | security.case_evidence_link.item_number | bigint | R | PK-01; deferred |
| owner_entity | security.case_evidence_link.owner_entity | varchar(50) | R | COL-01; deferred |
| owner_version_key | security.case_evidence_link.owner_version_key -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01; deferred |

### governance_action

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| action_id | audit.governance_action.action_id | varchar(100) | R | PK-01; deferred |
| action_type | audit.governance_action.action_type | varchar(50) | R | COL-01; deferred |
| requester_identity | audit.governance_action.requester_identity | varchar(128) | R | COL-01; deferred |
| subject_entity | audit.governance_action.subject_entity | varchar(50) | R | COL-01; deferred |
| subject_reference | audit.governance_action.subject_reference -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01; deferred |
| reason_code | audit.governance_action.reason_code | varchar(100) | R | COL-01; deferred |
| effective_from | audit.governance_action.effective_from | timestamptz(6) | C: approved effective action | COL-01, COND-01, TIME-01; deferred |
| effective_to | audit.governance_action.effective_to | timestamptz(6) | C: time-bound action | COL-01, COND-01, TIME-01; deferred |
| status | audit.governance_action.status | varchar(50) | R | COL-01; deferred |
| history_analysis_reference | audit.governance_action.history_analysis_reference | varchar(100) | C: merge, split or retirement | COL-01, COND-01; deferred |
| correction_reference | audit.governance_action.correction_reference | varchar(100) | C: merge, split or retirement | COL-01, COND-01; deferred |
| audit_reference | audit.governance_action.audit_reference | varchar(100) | R | COL-01; deferred |
| publisher_identity | audit.governance_action.publisher_identity | varchar(128) | C: published rule change | COL-01, COND-01; deferred |

### governance_review

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| action_id | audit.governance_review.action_id | varchar(100) | R | PK-01, REF-01; deferred |
| review_number | audit.governance_review.review_number | bigint | R | PK-01; deferred |
| reviewer_identity | audit.governance_review.reviewer_identity | varchar(128) | R | COL-01; deferred |
| reviewer_responsibility | audit.governance_review.reviewer_responsibility | varchar(50) | R | COL-01; deferred |
| decision | audit.governance_review.decision | varchar(50) | R | COL-01; deferred |
| reviewed_at | audit.governance_review.reviewed_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| evidence_reference | audit.governance_review.evidence_reference | varchar(100) | R | COL-01; deferred |

### export_entitlement

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| event_key | audit.export_entitlement.event_key | bigint | R | PK-01, REF-01; deferred |
| entitlement_id | audit.export_entitlement.entitlement_id | varchar(128) | R | PK-01, REF-01; deferred |
| evaluated_at | audit.export_entitlement.evaluated_at | timestamptz(6) | R | COL-01, TIME-01; deferred |

### export_approval

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| event_key | audit.export_approval.event_key | bigint | R | PK-01, REF-01; deferred |
| action_id | audit.export_approval.action_id | varchar(100) | R | PK-01, REF-01; deferred |

### rc01_investigation_projection

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| case_key | curated.rc01_investigation_projection.case_key | varchar(128) | R | PK-01, REF-01; deferred |
| projection_item_key | curated.rc01_investigation_projection.projection_item_key | varchar(128) | R | PK-01; deferred |
| current_comparison_amount | curated.rc01_investigation_projection.current_comparison_amount | numeric(20,4) | C: valid current amount | COL-01, NUM-01, COND-01; deferred |
| prior_average | curated.rc01_investigation_projection.prior_average_numerator + prior_average_denominator | numeric numerator + bigint denominator; exact ratio representation | C: available prior evidence | COL-01, NUM-01, COND-01; deferred |
| multiplier | curated.rc01_investigation_projection.multiplier | numeric(28,8) | C: configured comparison | COL-01, NUM-01, COND-01; deferred |
| currency | curated.rc01_investigation_projection.currency | char(3) | C: valid known currency | COL-01, COND-01; deferred |
| window_start | curated.rc01_investigation_projection.window_start | timestamptz(6) | R | COL-01, TIME-01; deferred |
| window_end | curated.rc01_investigation_projection.window_end | timestamptz(6) | R | COL-01, TIME-01; deferred |
| history_count | curated.rc01_investigation_projection.history_count | bigint | C: available history | COL-01, COND-01; deferred |
| trigger_state | curated.rc01_investigation_projection.trigger_state | varchar(50) | R | COL-01; deferred |
| missing_evidence_reason | curated.rc01_investigation_projection.missing_evidence_reason | varchar(100) | C: missing evidence | COL-01, COND-01; deferred |

### gate_ruleset

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| gate_ruleset_version | config.gate_ruleset.gate_ruleset_version | varchar(128) | R | PK-01; deferred |
| approval_reference | config.gate_ruleset.approval_reference | varchar(100) | R | COL-01; deferred |
| effective_from | config.gate_ruleset.effective_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| effective_to | config.gate_ruleset.effective_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |

### gate_rule

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| gate_ruleset_version | config.gate_rule.gate_ruleset_version | varchar(128) | R | PK-01, REF-01; deferred |
| rule_id | config.gate_rule.rule_id | varchar(50) | R | PK-01; deferred |
| definition_reference | config.gate_rule.definition_reference | varchar(100) | R | COL-01; deferred |

### publication_candidate

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| candidate_id | audit.publication_candidate.candidate_id | varchar(128) | R | PK-01; deferred |
| run_id | audit.publication_candidate.run_id | varchar(128) | R | COL-01, REF-01; deferred |
| business_date | audit.publication_candidate.business_date | date | R | COL-01; deferred |
| gate_ruleset_version | audit.publication_candidate.gate_ruleset_version | varchar(128) | R | COL-01, REF-01; deferred |
| created_at | audit.publication_candidate.created_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| gate_at | audit.publication_candidate.gate_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| prior_successful_version | audit.publication_candidate.prior_successful_version | varchar(128) | C: prior successful publication exists | COL-01, REF-01, COND-01; deferred |
| predecessor_version | audit.publication_candidate.predecessor_version | varchar(128) | C: correction/restatement | COL-01, REF-01, COND-01; deferred |
| affected_from | audit.publication_candidate.affected_from | date | C: correction/restatement | COL-01, COND-01; deferred |
| affected_through | audit.publication_candidate.affected_through | date | C: correction/restatement | COL-01, COND-01; deferred |
| unavailable_reason | audit.publication_candidate.unavailable_reason | varchar(100) | C: missing required candidate evidence | COL-01, COND-01; deferred |

### candidate_source

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| candidate_id | audit.candidate_source.candidate_id | varchar(128) | R | PK-01, REF-01; deferred |
| source_system | audit.candidate_source.source_system | varchar(50) | R | PK-01; deferred |
| entity_name | audit.candidate_source.entity_name | varchar(50) | R | PK-01; deferred |
| business_date | audit.candidate_source.business_date | date | R | COL-01; deferred |
| revision | audit.candidate_source.revision | integer | C: revision supplied | COL-01, COND-01; deferred |
| receipt_state | audit.candidate_source.receipt_state | varchar(50) | R | COL-01; deferred |
| received_at | audit.candidate_source.received_at | timestamptz(6) | C: content received | COL-01, COND-01, TIME-01; deferred |
| contract_reference | audit.candidate_source.contract_reference | varchar(100) | C: approved source contract exists | COL-01, COND-01; deferred |
| allowance_deadline_at | audit.candidate_source.allowance_deadline_at | timestamptz(6) | C: approved delivery allowance exists | COL-01, COND-01, TIME-01; deferred |
| checksum | audit.candidate_source.checksum | varchar(128) | C: supplied/computable delivered content | COL-01, COND-01; deferred |
| checksum_algorithm | audit.candidate_source.checksum_algorithm | varchar(50) | C: checksum evidence available | COL-01, COND-01; deferred |
| checksum_encoding | audit.candidate_source.checksum_encoding | varchar(50) | C: checksum evidence available | COL-01, COND-01; deferred |
| content_encoding | audit.candidate_source.content_encoding | varchar(50) | C: delivered content metadata available | COL-01, COND-01; deferred |
| schema_version | audit.candidate_source.schema_version | varchar(128) | C: supplied schema version | COL-01, COND-01; deferred |
| extract_reference | audit.candidate_source.extract_reference -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | C: accepted manifest available | COL-01, TR-01, COND-01; deferred |
| receipt_evidence_reference | audit.candidate_source.receipt_evidence_reference | varchar(100) | C: received content | COL-01, COND-01; deferred |
| unavailable_reason | audit.candidate_source.unavailable_reason | varchar(100) | C: missing/invalid delivery or metadata | COL-01, COND-01; deferred |

### candidate_control

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| control_result_id | audit.candidate_control.control_result_id | varchar(128) | R | PK-01; deferred |
| candidate_id | audit.candidate_control.candidate_id | varchar(128) | R | COL-01, REF-01; deferred |
| gate_ruleset_version | audit.candidate_control.gate_ruleset_version | varchar(128) | R | COL-01, REF-02; deferred |
| rule_id | audit.candidate_control.rule_id | varchar(50) | R | COL-01, REF-02; deferred |
| population_key | audit.candidate_control.population_key | bigint | C: measurable scoped population | COL-01, REF-01, COND-01; deferred |
| result | audit.candidate_control.result | varchar(50) | R | COL-01; deferred |
| base_severity | audit.candidate_control.base_severity | varchar(50) | R | COL-01; deferred |
| effective_severity | audit.candidate_control.effective_severity | varchar(50) | R | COL-01; deferred |
| reason_code | audit.candidate_control.reason_code | varchar(100) | C: failure, limitation or unavailable check | COL-01, COND-01; deferred |
| evaluated_at | audit.candidate_control.evaluated_at | timestamptz(6) | C: evaluation executed | COL-01, COND-01, TIME-01; deferred |
| evidence_reference | audit.candidate_control.evidence_reference | varchar(100) | C: supporting check evidence available | COL-01, COND-01; deferred |

### candidate_population

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| candidate_id | audit.candidate_population.candidate_id | varchar(128) | R | PK-01, REF-01; deferred |
| population_key | audit.candidate_population.population_key | bigint | R | PK-01, REF-01; deferred |
| stage | audit.candidate_population.stage | varchar(50) | R | PK-01; deferred |
| received_rows | audit.candidate_population.received_rows | bigint | C: measured | COL-01, COND-01; deferred |
| accepted_rows | audit.candidate_population.accepted_rows | bigint | C: measured | COL-01, COND-01; deferred |
| quarantined_rows | audit.candidate_population.quarantined_rows | bigint | C: measured | COL-01, COND-01; deferred |
| excluded_rows | audit.candidate_population.excluded_rows | bigint | C: measured | COL-01, COND-01; deferred |
| required_cells | audit.candidate_population.required_cells | bigint | C: measured applicable population | COL-01, COND-01; deferred |
| present_cells | audit.candidate_population.present_cells | bigint | C: measured applicable population | COL-01, COND-01; deferred |
| completeness_state | audit.candidate_population.completeness_state | varchar(50) | R | COL-01; deferred |
| unavailable_reason | audit.candidate_population.unavailable_reason | varchar(100) | C: unavailable/empty measurement | COL-01, COND-01; deferred |

### candidate_coverage

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| candidate_id | audit.candidate_coverage.candidate_id | varchar(128) | R | PK-01, REF-01; deferred |
| population_key | audit.candidate_coverage.population_key | bigint | R | PK-01, REF-01; deferred |
| result_type | audit.candidate_coverage.result_type | varchar(50) | R | PK-01; deferred |
| total_count | audit.candidate_coverage.total_count | bigint | C: measurable population | COL-01, COND-01; deferred |
| unknown_count | audit.candidate_coverage.unknown_count | bigint | C: measurable population | COL-01, COND-01; deferred |
| unavailable_count | audit.candidate_coverage.unavailable_count | bigint | C: measurable population | COL-01, COND-01; deferred |
| coverage_state | audit.candidate_coverage.coverage_state | varchar(50) | R | COL-01; deferred |
| reason_reference | audit.candidate_coverage.reason_reference | varchar(100) | C: unknown/unavailable or limitation | COL-01, COND-01; deferred |

### candidate_evidence

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| candidate_id | audit.candidate_evidence.candidate_id | varchar(128) | R | PK-01, REF-01; deferred |
| evidence_number | audit.candidate_evidence.evidence_number | bigint | R | PK-01; deferred |
| evidence_type | audit.candidate_evidence.evidence_type | varchar(50) | R | COL-01; deferred |
| owner_entity | audit.candidate_evidence.owner_entity | varchar(50) | R | COL-01; deferred |
| owner_version_key | audit.candidate_evidence.owner_version_key -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01; deferred |

### quality_exclusion

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| action_id | audit.quality_exclusion.action_id | varchar(100) | R | PK-01, REF-01; deferred |
| candidate_id | audit.quality_exclusion.candidate_id | varchar(128) | R | COL-01, REF-01; deferred |
| source_system | audit.quality_exclusion.source_system | varchar(50) | R | COL-01, REF-02; deferred |
| entity_name | audit.quality_exclusion.entity_name | varchar(50) | R | COL-01, REF-02; deferred |
| business_date | audit.quality_exclusion.business_date | date | R | COL-01, REF-02; deferred |
| revision | audit.quality_exclusion.revision | integer | R | COL-01, REF-02; deferred |
| reason_code | audit.quality_exclusion.reason_code | varchar(100) | R | COL-01; deferred |
| affected_rows | audit.quality_exclusion.affected_rows | bigint | R | COL-01; deferred |
| required_cells | audit.quality_exclusion.required_cells | bigint | R | COL-01; deferred |
| present_cells | audit.quality_exclusion.present_cells | bigint | R | COL-01; deferred |
| sensitive_or_risk_impact | audit.quality_exclusion.sensitive_or_risk_impact | boolean | R | COL-01; deferred |
| evidence_reference | audit.quality_exclusion.evidence_reference | varchar(100) | R | COL-01; deferred |

### exclusion_record

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| action_id | audit.exclusion_record.action_id | varchar(100) | R | PK-01, REF-01; deferred |
| record_number | audit.exclusion_record.record_number | bigint | R | PK-01; deferred |
| source_reference_key | audit.exclusion_record.source_reference_key | bigint | R | COL-01, REF-01; deferred |
| impact_reference | audit.exclusion_record.impact_reference | varchar(100) | R | COL-01; deferred |

### exclusion_impact

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| action_id | audit.exclusion_impact.action_id | varchar(100) | R | PK-01, REF-01; deferred |
| impact_number | audit.exclusion_impact.impact_number | bigint | R | PK-01; deferred |
| field_or_kpi | audit.exclusion_impact.field_or_kpi | varchar(100) | R | COL-01; deferred |
| currency | audit.exclusion_impact.currency | char(3) | C: monetary impact | COL-01, COND-01; deferred |
| signed_amount | audit.exclusion_impact.signed_amount | numeric(28,4) | C: measurable monetary impact | COL-01, NUM-01, COND-01; deferred |
| impact_state | audit.exclusion_impact.impact_state | varchar(50) | R | COL-01; deferred |
| evidence_reference | audit.exclusion_impact.evidence_reference | varchar(100) | R | COL-01; deferred |

### publication_decision

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| decision_id | audit.publication_decision.decision_id | varchar(128) | R | PK-01; deferred |
| candidate_id | audit.publication_decision.candidate_id | varchar(128) | R | COL-01, REF-01; deferred |
| decision | audit.publication_decision.decision | varchar(50) | R | COL-01; deferred |
| reason_code | audit.publication_decision.reason_code | varchar(100) | R | COL-01; deferred |
| decided_at | audit.publication_decision.decided_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| publication_version | audit.publication_decision.publication_version | varchar(128) | C: a publication version exists | COL-01, REF-01, COND-01; deferred |
| release_action_id | audit.publication_decision.release_action_id | varchar(100) | C: release approved | COL-01, REF-01, COND-01; deferred |
| retained_publication_version | audit.publication_decision.retained_publication_version | varchar(128) | C: prior success retained | COL-01, REF-01, COND-01; deferred |
| prior_state | audit.publication_decision.prior_state | varchar(50) | R | COL-01; deferred |
| display_age_seconds | audit.publication_decision.display_age_seconds | bigint | C: retained version served at decision instant | COL-01, COND-01; deferred |
| stale_reason | audit.publication_decision.stale_reason | varchar(100) | C: prior version served because current candidate blocked | COL-01, COND-01; deferred |

### decision_participant

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| decision_id | audit.decision_participant.decision_id | varchar(128) | R | PK-01, REF-01; deferred |
| responsibility | audit.decision_participant.responsibility | varchar(50) | R | PK-01; deferred |
| member_number | audit.decision_participant.member_number | bigint | R | PK-01; deferred |
| principal_id | audit.decision_participant.principal_id | varchar(128) | C: identity known | COL-01, COND-01; deferred |
| participation_state | audit.decision_participant.participation_state | varchar(50) | R | COL-01; deferred |
| action_id | audit.decision_participant.action_id | varchar(100) | C: governed review/execution action | COL-01, REF-01, COND-01; deferred |
| acted_at | audit.decision_participant.acted_at | timestamptz(6) | C: action performed | COL-01, COND-01, TIME-01; deferred |

### publication_notification

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| notification_id | audit.publication_notification.notification_id | varchar(128) | R | PK-01; deferred |
| candidate_id | audit.publication_notification.candidate_id | varchar(128) | R | COL-01, REF-01; deferred |
| decision_id | audit.publication_notification.decision_id | varchar(128) | C: associated decision exists | COL-01, REF-01, COND-01; deferred |
| trigger_type | audit.publication_notification.trigger_type | varchar(50) | R | COL-01; deferred |
| triggered_at | audit.publication_notification.triggered_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| notified_at | audit.publication_notification.notified_at | timestamptz(6) | C: sent | COL-01, COND-01, TIME-01; deferred |
| reason_code | audit.publication_notification.reason_code | varchar(100) | R | COL-01; deferred |
| status | audit.publication_notification.status | varchar(50) | R | COL-01; deferred |

### notification_recipient

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| notification_id | audit.notification_recipient.notification_id | varchar(128) | R | PK-01, REF-01; deferred |
| responsibility | audit.notification_recipient.responsibility | varchar(50) | R | PK-01; deferred |
| member_number | audit.notification_recipient.member_number | bigint | R | PK-01; deferred |
| principal_id | audit.notification_recipient.principal_id | varchar(128) | C: assigned recipient exists | COL-01, COND-01; deferred |
| status | audit.notification_recipient.status | varchar(50) | R | COL-01; deferred |
| acknowledged_at | audit.notification_recipient.acknowledged_at | timestamptz(6) | C: acknowledged | COL-01, COND-01, TIME-01; deferred |

### retention_schedule

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| schedule_version | config.retention_schedule.schedule_version | varchar(128) | R | PK-01; deferred |
| category_code | config.retention_schedule.category_code | varchar(50) | R | PK-01; deferred |
| anchor_type | config.retention_schedule.anchor_type | varchar(50) | R | COL-01; deferred |
| period_rule | config.retention_schedule.period_rule | varchar(100) | R | COL-01; deferred |
| approval_action_id | config.retention_schedule.approval_action_id | varchar(100) | R | COL-01, REF-01; deferred |
| valid_from | config.retention_schedule.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | config.retention_schedule.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |

### retention_item

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| item_id | audit.retention_item.item_id | varchar(128) | R | PK-01; deferred |
| schedule_version | audit.retention_item.schedule_version | varchar(128) | R | COL-01, REF-02; deferred |
| category_code | audit.retention_item.category_code | varchar(50) | R | COL-01, REF-02; deferred |
| envelope_id | audit.retention_item.envelope_id | varchar(128) | R | COL-01, REF-01; deferred |
| anchor_date | audit.retention_item.anchor_date | date | C: date-based rule | COL-01, COND-01; deferred |
| anchor_at | audit.retention_item.anchor_at | timestamptz(6) | C: instant-based rule | COL-01, COND-01, TIME-01; deferred |
| anchor_state | audit.retention_item.anchor_state | varchar(50) | R | COL-01; deferred |
| anniversary_at | audit.retention_item.anniversary_at | timestamptz(6) | C: computable anniversary | COL-01, COND-01, TIME-01; deferred |
| live_expiry_at | audit.retention_item.live_expiry_at | timestamptz(6) | C: approved expiry computable | COL-01, COND-01, TIME-01; deferred |
| purge_eligible_at | audit.retention_item.purge_eligible_at | timestamptz(6) | C: eligibility date computable | COL-01, COND-01, TIME-01; deferred |
| last_dependent_decision_at | audit.retention_item.last_dependent_decision_at | timestamptz(6) | C: configuration/audit dependency | COL-01, COND-01, TIME-01; deferred |
| lifecycle_state | audit.retention_item.lifecycle_state | varchar(50) | R | COL-01; deferred |

### provenance_envelope

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| envelope_id | audit.provenance_envelope.envelope_id | varchar(128) | R | PK-01; deferred |
| record_token | audit.provenance_envelope.record_token | varchar(128) | R | COL-01; deferred |
| source_namespace | audit.provenance_envelope.source_namespace | varchar(50) | C: source-derived record | COL-01, COND-01; deferred |
| entity_name | audit.provenance_envelope.entity_name | varchar(50) | R | COL-01; deferred |
| business_date | audit.provenance_envelope.business_date | date | C: business payload | COL-01, COND-01; deferred |
| revision | audit.provenance_envelope.revision | integer | C: revisioned payload | COL-01, COND-01; deferred |
| version_id | audit.provenance_envelope.version_id | varchar(128) | C: versioned record | COL-01, COND-01; deferred |
| digest | audit.provenance_envelope.digest | varchar(128) | C: valid content digest available | COL-01, COND-01; deferred |
| disposition | audit.provenance_envelope.disposition | varchar(50) | R | COL-01; deferred |
| expiry_at | audit.provenance_envelope.expiry_at | timestamptz(6) | C: expired payload | COL-01, COND-01, TIME-01; deferred |
| deletion_evidence_id | audit.provenance_envelope.deletion_evidence_id | varchar(128) | C: disposed payload | COL-01, REF-01, COND-01; deferred |

### lifecycle_reference

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| reference_id | audit.lifecycle_reference.reference_id | varchar(128) | R | PK-01; deferred |
| owner_envelope_id | audit.lifecycle_reference.owner_envelope_id | varchar(128) | R | COL-01, REF-01; deferred |
| target_envelope_id | audit.lifecycle_reference.target_envelope_id | varchar(128) | R | COL-01, REF-01; deferred |
| relationship_code | audit.lifecycle_reference.relationship_code | varchar(50) | R | COL-01; deferred |
| payload_state | audit.lifecycle_reference.payload_state | varchar(50) | R | COL-01; deferred |
| live_target | audit.lifecycle_reference.live_target -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | C: payload AVAILABLE | COL-01, TR-01, COND-01; deferred |
| transition_at | audit.lifecycle_reference.transition_at | timestamptz(6) | C: payload expiry transition | COL-01, COND-01, TIME-01; deferred |

### restricted_token_mapping

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| mapping_id | security.restricted_token_mapping.mapping_id | varchar(128) | R | PK-01; deferred |
| record_token | security.restricted_token_mapping.record_token | varchar(128) | R | COL-01; deferred |
| restricted_reference | security.restricted_token_mapping.restricted_reference -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01; deferred |
| dependency_reference | security.restricted_token_mapping.dependency_reference | varchar(100) | R | COL-01; deferred |
| retention_item_id | security.restricted_token_mapping.retention_item_id | varchar(128) | R | COL-01, REF-01; deferred |

### retention_hold

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| hold_id | audit.retention_hold.hold_id | varchar(128) | R | PK-01; deferred |
| requester_id | audit.retention_hold.requester_id | varchar(128) | R | COL-01; deferred |
| reason_code | audit.retention_hold.reason_code | varchar(100) | R | COL-01; deferred |
| approval_action_id | audit.retention_hold.approval_action_id | varchar(100) | C: approved hold | COL-01, REF-01, COND-01; deferred |
| legal_required | audit.retention_hold.legal_required | boolean | R | COL-01; deferred |
| effective_at | audit.retention_hold.effective_at | timestamptz(6) | C: approved effective hold | COL-01, COND-01, TIME-01; deferred |
| next_review_at | audit.retention_hold.next_review_at | timestamptz(6) | C: active hold | COL-01, COND-01, TIME-01; deferred |
| state | audit.retention_hold.state | varchar(50) | R | COL-01; deferred |
| release_action_id | audit.retention_hold.release_action_id | varchar(100) | C: released hold | COL-01, REF-01, COND-01; deferred |
| released_at | audit.retention_hold.released_at | timestamptz(6) | C: released hold | COL-01, COND-01, TIME-01; deferred |

### hold_scope

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| hold_id | audit.hold_scope.hold_id | varchar(128) | R | PK-01, REF-01; deferred |
| member_number | audit.hold_scope.member_number | bigint | R | PK-01; deferred |
| scope_type | audit.hold_scope.scope_type | varchar(50) | R | COL-01; deferred |
| scope_reference | audit.hold_scope.scope_reference -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01; deferred |
| from_date | audit.hold_scope.from_date | date | C: date-range scope | COL-01, COND-01; deferred |
| through_date | audit.hold_scope.through_date | date | C: date-range scope | COL-01, COND-01; deferred |
| evidence_reference | audit.hold_scope.evidence_reference | varchar(100) | R | COL-01; deferred |

### hold_review

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| hold_id | audit.hold_review.hold_id | varchar(128) | R | PK-01, REF-01; deferred |
| review_number | audit.hold_review.review_number | bigint | R | PK-01; deferred |
| action_id | audit.hold_review.action_id | varchar(100) | R | COL-01, REF-01; deferred |
| reviewed_at | audit.hold_review.reviewed_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| outcome | audit.hold_review.outcome | varchar(50) | R | COL-01; deferred |
| evidence_reference | audit.hold_review.evidence_reference | varchar(100) | R | COL-01; deferred |

### disposal_batch

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| batch_id | audit.disposal_batch.batch_id | varchar(128) | R | PK-01; deferred |
| approval_action_id | audit.disposal_batch.approval_action_id | varchar(100) | C: approved batch | COL-01, REF-01, COND-01; deferred |
| decision_at | audit.disposal_batch.decision_at | timestamptz(6) | C: disposal decision recorded | COL-01, COND-01, TIME-01; deferred |
| schedule_version | audit.disposal_batch.schedule_version | varchar(128) | R | COL-01; deferred |
| scope_digest | audit.disposal_batch.scope_digest | varchar(128) | C: scope fixed | COL-01, COND-01; deferred |
| status | audit.disposal_batch.status | varchar(50) | R | COL-01; deferred |

### disposal_scope

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| batch_id | audit.disposal_scope.batch_id | varchar(128) | R | PK-01, REF-01; deferred |
| item_id | audit.disposal_scope.item_id | varchar(128) | R | PK-01, REF-01; deferred |
| category_code | audit.disposal_scope.category_code | varchar(50) | R | COL-01; deferred |
| approval_evidence_reference | audit.disposal_scope.approval_evidence_reference | varchar(100) | R | COL-01; deferred |

### disposal_job

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| job_id | audit.disposal_job.job_id | varchar(128) | R | PK-01; deferred |
| batch_id | audit.disposal_job.batch_id | varchar(128) | R | COL-01, REF-01; deferred |
| executor_id | audit.disposal_job.executor_id | varchar(128) | R | COL-01; deferred |
| ruleset_version | audit.disposal_job.ruleset_version | varchar(128) | R | COL-01; deferred |
| started_at | audit.disposal_job.started_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| ended_at | audit.disposal_job.ended_at | timestamptz(6) | C: terminal job | COL-01, COND-01, TIME-01; deferred |
| eligible_count | audit.disposal_job.eligible_count | bigint | C: measured | COL-01, COND-01; deferred |
| deleted_count | audit.disposal_job.deleted_count | bigint | C: measured | COL-01, COND-01; deferred |
| skipped_count | audit.disposal_job.skipped_count | bigint | C: measured | COL-01, COND-01; deferred |
| failed_count | audit.disposal_job.failed_count | bigint | C: measured | COL-01, COND-01; deferred |
| verification_state | audit.disposal_job.verification_state | varchar(50) | R | COL-01; deferred |
| verification_reference | audit.disposal_job.verification_reference | varchar(100) | C: verification performed | COL-01, COND-01; deferred |

### disposal_item

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| result_id | audit.disposal_item.result_id | varchar(128) | R | PK-01; deferred |
| job_id | audit.disposal_item.job_id | varchar(128) | R | COL-01, REF-01; deferred |
| item_id | audit.disposal_item.item_id | varchar(128) | R | COL-01, REF-01; deferred |
| checked_at | audit.disposal_item.checked_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| expired | audit.disposal_item.expired | boolean | R | COL-01; deferred |
| unheld | audit.disposal_item.unheld | boolean | R | COL-01; deferred |
| dependency_cleared | audit.disposal_item.dependency_cleared | boolean | R | COL-01; deferred |
| scope_matches | audit.disposal_item.scope_matches | boolean | R | COL-01; deferred |
| outcome | audit.disposal_item.outcome | varchar(50) | R | COL-01; deferred |
| reason_code | audit.disposal_item.reason_code | varchar(100) | C: skip/failure or exclusion | COL-01, COND-01; deferred |
| deleted_at | audit.disposal_item.deleted_at | timestamptz(6) | C: deleted | COL-01, COND-01, TIME-01; deferred |
| backup_deadline_at | audit.disposal_item.backup_deadline_at | timestamptz(6) | C: backup obligation | COL-01, COND-01, TIME-01; deferred |
| verification_reference | audit.disposal_item.verification_reference | varchar(100) | C: verified | COL-01, COND-01; deferred |

### disposal_category_total

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| job_id | audit.disposal_category_total.job_id | varchar(128) | R | PK-01, REF-01; deferred |
| category_code | audit.disposal_category_total.category_code | varchar(50) | R | PK-01; deferred |
| eligible_count | audit.disposal_category_total.eligible_count | bigint | R | COL-01; deferred |
| deleted_count | audit.disposal_category_total.deleted_count | bigint | R | COL-01; deferred |
| skipped_count | audit.disposal_category_total.skipped_count | bigint | R | COL-01; deferred |
| failed_count | audit.disposal_category_total.failed_count | bigint | R | COL-01; deferred |
| hold_exclusions | audit.disposal_category_total.hold_exclusions | bigint | R | COL-01; deferred |
| dependency_exclusions | audit.disposal_category_total.dependency_exclusions | bigint | R | COL-01; deferred |

### backup_copy

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| backup_id | audit.backup_copy.backup_id | varchar(128) | R | PK-01; deferred |
| copy_type | audit.backup_copy.copy_type | varchar(50) | R | COL-01; deferred |
| created_at | audit.backup_copy.created_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| encrypted | audit.backup_copy.encrypted | boolean | R | COL-01; deferred |
| expires_at | audit.backup_copy.expires_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| scope_reference | audit.backup_copy.scope_reference | varchar(100) | R | COL-01; deferred |
| disposal_evidence_reference | audit.backup_copy.disposal_evidence_reference | varchar(100) | C: expired copy disposed | COL-01, COND-01; deferred |

### restore_validation

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| restore_id | audit.restore_validation.restore_id | varchar(128) | R | PK-01; deferred |
| backup_id | audit.restore_validation.backup_id | varchar(128) | R | COL-01, REF-01; deferred |
| started_at | audit.restore_validation.started_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| validated_at | audit.restore_validation.validated_at | timestamptz(6) | C: validation performed | COL-01, COND-01, TIME-01; deferred |
| deletion_reapplied | audit.restore_validation.deletion_reapplied | boolean | C: checked | COL-01, COND-01; deferred |
| revocations_reapplied | audit.restore_validation.revocations_reapplied | boolean | C: checked | COL-01, COND-01; deferred |
| holds_reapplied | audit.restore_validation.holds_reapplied | boolean | C: checked | COL-01, COND-01; deferred |
| result | audit.restore_validation.result | varchar(50) | R | COL-01; deferred |
| evidence_reference | audit.restore_validation.evidence_reference | varchar(100) | C: validation performed | COL-01, COND-01; deferred |
| temporary_copy_deadline | audit.restore_validation.temporary_copy_deadline | timestamptz(6) | C: validated restore | COL-01, COND-01, TIME-01; deferred |
| copy_disposal_reference | audit.restore_validation.copy_disposal_reference | varchar(100) | C: recovery copies removed | COL-01, COND-01; deferred |

### access_attempt

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| attempt_id | audit.access_attempt.attempt_id | varchar(128) | R | PK-01; deferred |
| actor_id | audit.access_attempt.actor_id | varchar(128) | C: known actor | COL-01, COND-01; deferred |
| active_role | audit.access_attempt.active_role | varchar(50) | C: supplied selected role | COL-01, COND-01; deferred |
| surface | audit.access_attempt.surface | varchar(50) | R | COL-01; deferred |
| decided_at | audit.access_attempt.decided_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| decision | audit.access_attempt.decision | varchar(50) | R | COL-01; deferred |
| reason_code | audit.access_attempt.reason_code | varchar(100) | R | COL-01; deferred |
| policy_version | audit.access_attempt.policy_version | varchar(128) | C: evaluable policy | COL-01, REF-01, COND-01; deferred |

### loan_schedule

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| schedule_version | curated.loan_schedule.schedule_version | varchar(128) | R | PK-01; deferred |
| source_system | curated.loan_schedule.source_system | varchar(50) | R | COL-01; deferred |
| source_schedule_id | curated.loan_schedule.source_schedule_id | varchar(128) | R | COL-01; deferred |
| loan_key | curated.loan_schedule.loan_key | bigint | R | COL-01, REF-01; deferred |
| currency | curated.loan_schedule.currency | char(3) | R | COL-01; deferred |
| effective_from | curated.loan_schedule.effective_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| effective_to | curated.loan_schedule.effective_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_date | curated.loan_schedule.original_effective_date | date | R | COL-01; deferred |
| supersedes_schedule_version | curated.loan_schedule.supersedes_schedule_version | varchar(128) | O: first version | COL-01, REF-01; deferred |
| source_version | curated.loan_schedule.source_version | varchar(128) | R | COL-01; deferred |
| batch_revision | curated.loan_schedule.batch_revision | integer | R | COL-01; deferred |
| correction_reference | curated.loan_schedule.correction_reference | varchar(100) | C: corrected version | COL-01, COND-01; deferred |

### loan_obligation

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| obligation_version | curated.loan_obligation.obligation_version | varchar(128) | R | PK-01; deferred |
| source_system | curated.loan_obligation.source_system | varchar(50) | R | COL-01; deferred |
| source_obligation_id | curated.loan_obligation.source_obligation_id | varchar(128) | R | COL-01; deferred |
| schedule_version | curated.loan_obligation.schedule_version | varchar(128) | R | COL-01, REF-01; deferred |
| loan_key | curated.loan_obligation.loan_key | bigint | R | COL-01, REF-01; deferred |
| due_date | curated.loan_obligation.due_date | date | R | COL-01; deferred |
| original_obligation_date | curated.loan_obligation.original_obligation_date | date | R | COL-01; deferred |
| scheduled_amount | curated.loan_obligation.scheduled_amount | numeric(20,4) | R | COL-01, NUM-01; deferred |
| currency | curated.loan_obligation.currency | char(3) | R | COL-01; deferred |
| effective_from | curated.loan_obligation.effective_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| effective_to | curated.loan_obligation.effective_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| supersedes_obligation_version | curated.loan_obligation.supersedes_obligation_version | varchar(128) | O: first version | COL-01, REF-01; deferred |
| source_version | curated.loan_obligation.source_version | varchar(128) | R | COL-01; deferred |
| batch_revision | curated.loan_obligation.batch_revision | integer | R | COL-01; deferred |
| correction_reference | curated.loan_obligation.correction_reference | varchar(100) | C: corrected version | COL-01, COND-01; deferred |

### payment_allocation

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| allocation_version | curated.payment_allocation.allocation_version | varchar(128) | R | PK-01; deferred |
| source_system | curated.payment_allocation.source_system | varchar(50) | R | COL-01; deferred |
| source_allocation_id | curated.payment_allocation.source_allocation_id | varchar(128) | R | COL-01; deferred |
| payment_key | curated.payment_allocation.payment_key | bigint | R | COL-01, REF-01; deferred |
| obligation_version | curated.payment_allocation.obligation_version | varchar(128) | R | COL-01, REF-01; deferred |
| component | curated.payment_allocation.component | varchar(50) | R | COL-01; deferred |
| amount | curated.payment_allocation.amount | numeric(20,4) | R | COL-01, NUM-01; deferred |
| currency | curated.payment_allocation.currency | char(3) | R | COL-01; deferred |
| effective_from | curated.payment_allocation.effective_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| effective_to | curated.payment_allocation.effective_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_date | curated.payment_allocation.original_effective_date | date | R | COL-01; deferred |
| supersedes_allocation_version | curated.payment_allocation.supersedes_allocation_version | varchar(128) | O: first version | COL-01, REF-01; deferred |
| source_version | curated.payment_allocation.source_version | varchar(128) | R | COL-01; deferred |
| batch_revision | curated.payment_allocation.batch_revision | integer | R | COL-01; deferred |
| correction_reference | curated.payment_allocation.correction_reference | varchar(100) | C: corrected version | COL-01, COND-01; deferred |

### payment_unapplied

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| unapplied_version | curated.payment_unapplied.unapplied_version | varchar(128) | R | PK-01; deferred |
| payment_key | curated.payment_unapplied.payment_key | bigint | R | COL-01, REF-01; deferred |
| amount | curated.payment_unapplied.amount | numeric(20,4) | R | COL-01, NUM-01; deferred |
| currency | curated.payment_unapplied.currency | char(3) | R | COL-01; deferred |
| effective_from | curated.payment_unapplied.effective_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| effective_to | curated.payment_unapplied.effective_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_date | curated.payment_unapplied.original_effective_date | date | R | COL-01; deferred |
| supersedes_unapplied_version | curated.payment_unapplied.supersedes_unapplied_version | varchar(128) | O: first version | COL-01, REF-01; deferred |
| source_version | curated.payment_unapplied.source_version | varchar(128) | R | COL-01; deferred |
| batch_revision | curated.payment_unapplied.batch_revision | integer | R | COL-01; deferred |
| correction_reference | curated.payment_unapplied.correction_reference | varchar(100) | C: corrected version | COL-01, COND-01; deferred |

### payment_adjustment

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| adjustment_key | curated.payment_adjustment.adjustment_key | bigint | R | PK-01; deferred |
| source_system | curated.payment_adjustment.source_system | varchar(50) | R | COL-01; deferred |
| source_adjustment_id | curated.payment_adjustment.source_adjustment_id | varchar(128) | R | COL-01; deferred |
| original_payment_key | curated.payment_adjustment.original_payment_key | bigint | R | COL-01, REF-01; deferred |
| adjustment_type | curated.payment_adjustment.adjustment_type | varchar(50) | R | COL-01; deferred |
| amount | curated.payment_adjustment.amount | numeric(20,4) | R | COL-01, NUM-01; deferred |
| currency | curated.payment_adjustment.currency | char(3) | R | COL-01; deferred |
| occurred_at | curated.payment_adjustment.occurred_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| business_date | curated.payment_adjustment.business_date | date | R | COL-01; deferred |
| application_reference | curated.payment_adjustment.application_reference | varchar(100) | R | COL-01; deferred |
| supersedes_event_key | curated.payment_adjustment.supersedes_event_key | bigint | O: first version | COL-01, REF-01; deferred |
| source_version | curated.payment_adjustment.source_version | varchar(128) | R | COL-01; deferred |
| batch_revision | curated.payment_adjustment.batch_revision | integer | R | COL-01; deferred |
| correction_reference | curated.payment_adjustment.correction_reference | varchar(100) | C: corrected version | COL-01, COND-01; deferred |

### loan_account

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| loan_account_version | curated.loan_account.loan_account_version | varchar(128) | R | PK-01; deferred |
| source_system | curated.loan_account.source_system | varchar(50) | R | COL-01; deferred |
| source_relationship_id | curated.loan_account.source_relationship_id | varchar(128) | R | COL-01; deferred |
| loan_key | curated.loan_account.loan_key | bigint | R | COL-01, REF-01; deferred |
| account_key | curated.loan_account.account_key | bigint | R | COL-01, REF-01; deferred |
| relationship_role | curated.loan_account.relationship_role | varchar(50) | R | COL-01; deferred |
| valid_from | curated.loan_account.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.loan_account.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_date | curated.loan_account.original_effective_date | date | R | COL-01; deferred |
| supersedes_relationship_version | curated.loan_account.supersedes_relationship_version | varchar(128) | O: first version | COL-01, REF-01; deferred |
| review_reference | curated.loan_account.review_reference | varchar(100) | R | COL-01; deferred |
| source_version | curated.loan_account.source_version | varchar(128) | R | COL-01; deferred |
| batch_revision | curated.loan_account.batch_revision | integer | R | COL-01; deferred |
| correction_reference | curated.loan_account.correction_reference | varchar(100) | C: corrected version | COL-01, COND-01; deferred |

### payment_transaction_link

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| link_version | curated.payment_transaction_link.link_version | varchar(128) | R | PK-01; deferred |
| payment_key | curated.payment_transaction_link.payment_key | bigint | R | COL-01, REF-01; deferred |
| transaction_key | curated.payment_transaction_link.transaction_key | bigint | R | COL-01, REF-01; deferred |
| evidence_basis | curated.payment_transaction_link.evidence_basis | varchar(50) | R | COL-01; deferred |
| evidence_reference | curated.payment_transaction_link.evidence_reference | varchar(100) | R | COL-01; deferred |
| review_action_id | curated.payment_transaction_link.review_action_id | varchar(100) | C: independently reviewed linkage | COL-01, REF-01, COND-01; deferred |
| valid_from | curated.payment_transaction_link.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.payment_transaction_link.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_date | curated.payment_transaction_link.original_effective_date | date | R | COL-01; deferred |
| supersedes_link_version | curated.payment_transaction_link.supersedes_link_version | varchar(128) | O: first version | COL-01, REF-01; deferred |

### loan_contract_publication

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| publication_version | curated.loan_contract_publication.publication_version | varchar(128) | R | PK-01, REF-01; deferred |
| entity_name | curated.loan_contract_publication.entity_name | varchar(50) | R | PK-01; deferred |
| natural_identity | curated.loan_contract_publication.natural_identity -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | PK-01, TR-01; deferred |
| selected_version | curated.loan_contract_publication.selected_version -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01; deferred |
| business_date | curated.loan_contract_publication.business_date | date | R | COL-01; deferred |

### organizational_unit

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| organization_key | curated.organizational_unit.organization_key | varchar(128) | R | PK-01; deferred |
| source_system | curated.organizational_unit.source_system | varchar(50) | R | COL-01; deferred |
| unit_type | curated.organizational_unit.unit_type | varchar(50) | R | COL-01; deferred |
| source_id | curated.organizational_unit.source_id | varchar(128) | R | COL-01; deferred |

### region

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| region_version | curated.region.region_version | varchar(128) | R | PK-01; deferred |
| organization_key | curated.region.organization_key | varchar(128) | R | COL-01, REF-01; deferred |
| source_system | curated.region.source_system | varchar(50) | R | COL-01; deferred |
| region_id | curated.region.region_id | varchar(128) | R | COL-01; deferred |
| region_name | curated.region.region_name | varchar(200) | R | COL-01; deferred |
| valid_from | curated.region.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.region.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_end | curated.region.original_effective_end | timestamptz(6) | C: ended interval | COL-01, COND-01, TIME-01; deferred |
| source_version | curated.region.source_version | varchar(128) | R | COL-01; deferred |
| supersedes_version | curated.region.supersedes_version | varchar(128) | C: correction | COL-01, REF-01, COND-01; deferred |
| correction_reason | curated.region.correction_reason | varchar(200) | C: correction | COL-01, COND-01; deferred |
| affected_from | curated.region.affected_from | timestamptz(6) | C: correction | COL-01, COND-01, TIME-01; deferred |
| affected_to | curated.region.affected_to | timestamptz(6) | O: open-ended or not correction | COL-01, TIME-01; deferred |
| approval_action_id | curated.region.approval_action_id | varchar(128) | R | COL-01, REF-01; deferred |

### organizational_successor

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| successor_version | curated.organizational_successor.successor_version | varchar(128) | R | PK-01; deferred |
| predecessor_key | curated.organizational_successor.predecessor_key | varchar(128) | R | COL-01, REF-01; deferred |
| successor_key | curated.organizational_successor.successor_key | varchar(128) | R | COL-01, REF-01; deferred |
| source_system | curated.organizational_successor.source_system | varchar(50) | R | COL-01; deferred |
| valid_from | curated.organizational_successor.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.organizational_successor.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_end | curated.organizational_successor.original_effective_end | timestamptz(6) | C: ended interval | COL-01, COND-01, TIME-01; deferred |
| source_version | curated.organizational_successor.source_version | varchar(128) | R | COL-01; deferred |
| supersedes_version | curated.organizational_successor.supersedes_version | varchar(128) | C: correction | COL-01, REF-01, COND-01; deferred |
| correction_reason | curated.organizational_successor.correction_reason | varchar(200) | C: correction | COL-01, COND-01; deferred |
| affected_from | curated.organizational_successor.affected_from | timestamptz(6) | C: correction | COL-01, COND-01, TIME-01; deferred |
| affected_to | curated.organizational_successor.affected_to | timestamptz(6) | O: open-ended or not correction | COL-01, TIME-01; deferred |
| approval_action_id | curated.organizational_successor.approval_action_id | varchar(128) | R | COL-01, REF-01; deferred |

### account_branch_assignment

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| assignment_version | curated.account_branch_assignment.assignment_version | varchar(128) | R | PK-01; deferred |
| source_system | curated.account_branch_assignment.source_system | varchar(50) | R | COL-01; deferred |
| source_assignment_id | curated.account_branch_assignment.source_assignment_id | varchar(128) | R | COL-01; deferred |
| account_key | curated.account_branch_assignment.account_key | bigint | R | COL-01, REF-01; deferred |
| branch_key | curated.account_branch_assignment.branch_key | bigint | R | COL-01, REF-01; deferred |
| assignment_role | curated.account_branch_assignment.assignment_role | varchar(50) | R | COL-01; deferred |
| valid_from | curated.account_branch_assignment.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.account_branch_assignment.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_end | curated.account_branch_assignment.original_effective_end | timestamptz(6) | C: ended interval | COL-01, COND-01, TIME-01; deferred |
| source_version | curated.account_branch_assignment.source_version | varchar(128) | R | COL-01; deferred |
| supersedes_version | curated.account_branch_assignment.supersedes_version | varchar(128) | C: correction | COL-01, REF-01, COND-01; deferred |
| correction_reason | curated.account_branch_assignment.correction_reason | varchar(200) | C: correction | COL-01, COND-01; deferred |
| affected_from | curated.account_branch_assignment.affected_from | timestamptz(6) | C: correction | COL-01, COND-01, TIME-01; deferred |
| affected_to | curated.account_branch_assignment.affected_to | timestamptz(6) | O: open-ended or not correction | COL-01, TIME-01; deferred |
| approval_action_id | curated.account_branch_assignment.approval_action_id | varchar(128) | R | COL-01, REF-01; deferred |

### loan_branch_assignment

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| assignment_version | curated.loan_branch_assignment.assignment_version | varchar(128) | R | PK-01; deferred |
| source_system | curated.loan_branch_assignment.source_system | varchar(50) | R | COL-01; deferred |
| source_assignment_id | curated.loan_branch_assignment.source_assignment_id | varchar(128) | R | COL-01; deferred |
| loan_key | curated.loan_branch_assignment.loan_key | bigint | R | COL-01, REF-01; deferred |
| branch_key | curated.loan_branch_assignment.branch_key | bigint | R | COL-01, REF-01; deferred |
| assignment_role | curated.loan_branch_assignment.assignment_role | varchar(50) | R | COL-01; deferred |
| valid_from | curated.loan_branch_assignment.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.loan_branch_assignment.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_end | curated.loan_branch_assignment.original_effective_end | timestamptz(6) | C: ended interval | COL-01, COND-01, TIME-01; deferred |
| source_version | curated.loan_branch_assignment.source_version | varchar(128) | R | COL-01; deferred |
| supersedes_version | curated.loan_branch_assignment.supersedes_version | varchar(128) | C: correction | COL-01, REF-01, COND-01; deferred |
| correction_reason | curated.loan_branch_assignment.correction_reason | varchar(200) | C: correction | COL-01, COND-01; deferred |
| affected_from | curated.loan_branch_assignment.affected_from | timestamptz(6) | C: correction | COL-01, COND-01, TIME-01; deferred |
| affected_to | curated.loan_branch_assignment.affected_to | timestamptz(6) | O: open-ended or not correction | COL-01, TIME-01; deferred |
| approval_action_id | curated.loan_branch_assignment.approval_action_id | varchar(128) | R | COL-01, REF-01; deferred |

### complaint_branch_assignment

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| assignment_version | curated.complaint_branch_assignment.assignment_version | varchar(128) | R | PK-01; deferred |
| source_system | curated.complaint_branch_assignment.source_system | varchar(50) | R | COL-01; deferred |
| source_assignment_id | curated.complaint_branch_assignment.source_assignment_id | varchar(128) | R | COL-01; deferred |
| complaint_key | curated.complaint_branch_assignment.complaint_key | bigint | R | COL-01, REF-01; deferred |
| branch_key | curated.complaint_branch_assignment.branch_key | bigint | R | COL-01, REF-01; deferred |
| assignment_role | curated.complaint_branch_assignment.assignment_role | varchar(50) | R | COL-01; deferred |
| valid_from | curated.complaint_branch_assignment.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | curated.complaint_branch_assignment.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| original_effective_end | curated.complaint_branch_assignment.original_effective_end | timestamptz(6) | C: ended interval | COL-01, COND-01, TIME-01; deferred |
| source_version | curated.complaint_branch_assignment.source_version | varchar(128) | R | COL-01; deferred |
| supersedes_version | curated.complaint_branch_assignment.supersedes_version | varchar(128) | C: correction | COL-01, REF-01, COND-01; deferred |
| correction_reason | curated.complaint_branch_assignment.correction_reason | varchar(200) | C: correction | COL-01, COND-01; deferred |
| affected_from | curated.complaint_branch_assignment.affected_from | timestamptz(6) | C: correction | COL-01, COND-01, TIME-01; deferred |
| affected_to | curated.complaint_branch_assignment.affected_to | timestamptz(6) | O: open-ended or not correction | COL-01, TIME-01; deferred |
| approval_action_id | curated.complaint_branch_assignment.approval_action_id | varchar(128) | R | COL-01, REF-01; deferred |

### branch_attribution

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| attribution_key | curated.branch_attribution.attribution_key | varchar(128) | R | PK-01; deferred |
| owner_entity | curated.branch_attribution.owner_entity | varchar(50) | R | COL-01; deferred |
| owner_version_key | curated.branch_attribution.owner_version_key -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01; deferred |
| purpose | curated.branch_attribution.purpose | varchar(50) | R | COL-01; deferred |
| observation_id | curated.branch_attribution.observation_id | varchar(128) | R | COL-01; deferred |
| publication_version | curated.branch_attribution.publication_version | varchar(128) | R | COL-01, REF-01; deferred |
| attribution_at | curated.branch_attribution.attribution_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| branch_key | curated.branch_attribution.branch_key | bigint | C: Available | COL-01, REF-01, COND-01; deferred |
| region_version | curated.branch_attribution.region_version | varchar(128) | C: Available | COL-01, REF-01, COND-01; deferred |
| basis | curated.branch_attribution.basis | varchar(50) | R | COL-01; deferred |
| assignment_entity | curated.branch_attribution.assignment_entity | varchar(50) | C: assignment/home basis or validation | COL-01, COND-01; deferred |
| assignment_version | curated.branch_attribution.assignment_version -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | C: assignment/home basis or validation | COL-01, TR-01, COND-01; deferred |
| source_reference_key | curated.branch_attribution.source_reference_key | bigint | C: supplied branch | COL-01, REF-01, COND-01; deferred |
| basis_attribution_key | curated.branch_attribution.basis_attribution_key | varchar(128) | C: inherited attribution | COL-01, REF-01, COND-01; deferred |
| availability | curated.branch_attribution.availability | varchar(50) | R | COL-01; deferred |
| missing_reason | curated.branch_attribution.missing_reason | varchar(100) | C: Unavailable | COL-01, COND-01; deferred |
| supplied_branch_key | curated.branch_attribution.supplied_branch_key | bigint | C: supplied branch | COL-01, REF-01, COND-01; deferred |
| supplied_role | curated.branch_attribution.supplied_role | varchar(50) | C: supplied branch | COL-01, COND-01; deferred |
| supplied_effective_at | curated.branch_attribution.supplied_effective_at | timestamptz(6) | C: supplied branch | COL-01, COND-01, TIME-01; deferred |
| validation_state | curated.branch_attribution.validation_state | varchar(50) | R | COL-01; deferred |
| review_action_id | curated.branch_attribution.review_action_id | varchar(128) | C: reviewed mismatch or supplied alert approval | COL-01, REF-01, COND-01; deferred |

### organization_publication

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| publication_version | curated.organization_publication.publication_version | varchar(128) | R | PK-01, REF-01; deferred |
| entity_name | curated.organization_publication.entity_name | varchar(50) | R | PK-01; deferred |
| natural_identity | curated.organization_publication.natural_identity -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | PK-01, TR-01, TIME-01; deferred |
| selected_version | curated.organization_publication.selected_version -> security.reference_binding + target-specific child | bigint reference binding; target-specific full-key child | R | COL-01, TR-01, TIME-01; deferred |

### successor_scope_mapping

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| scope_mapping_version | security.successor_scope_mapping.scope_mapping_version | varchar(128) | R | PK-01; deferred |
| current_branch_key | security.successor_scope_mapping.current_branch_key | varchar(128) | R | COL-01, REF-01; deferred |
| historical_branch_key | security.successor_scope_mapping.historical_branch_key | varchar(128) | R | COL-01, REF-01; deferred |
| valid_from | security.successor_scope_mapping.valid_from | timestamptz(6) | R | COL-01, TIME-01; deferred |
| valid_to | security.successor_scope_mapping.valid_to | timestamptz(6) | O: open-ended | COL-01, TIME-01; deferred |
| revoked_at | security.successor_scope_mapping.revoked_at | timestamptz(6) | C: revoked | COL-01, COND-01, TIME-01; deferred |
| approval_action_id | security.successor_scope_mapping.approval_action_id | varchar(128) | R | COL-01, REF-01; deferred |
| supersedes_version | security.successor_scope_mapping.supersedes_version | varchar(128) | C: corrected mapping | COL-01, REF-01, COND-01; deferred |

### scope_resolution

| Logical field | Proposed physical column/representation | PostgreSQL type | Requiredness | Enforcement plan |
| --- | --- | --- | --- | --- |
| resolution_key | audit.scope_resolution.resolution_key | varchar(128) | R | PK-01; deferred |
| access_attempt_id | audit.scope_resolution.access_attempt_id | varchar(128) | C: query | COL-01, REF-01, COND-01; deferred |
| export_event_key | audit.scope_resolution.export_event_key | bigint | C: export | COL-01, REF-01, COND-01; deferred |
| entitlement_id | audit.scope_resolution.entitlement_id | varchar(128) | C: applicable entitlement | COL-01, REF-01, COND-01; deferred |
| checked_at | audit.scope_resolution.checked_at | timestamptz(6) | R | COL-01, TIME-01; deferred |
| branch_identity | audit.scope_resolution.branch_identity | varchar(128) | C: resolved member | COL-01, REF-01, COND-01; deferred |
| current_branch_version | audit.scope_resolution.current_branch_version | bigint | C: region expansion | COL-01, REF-01, COND-01; deferred |
| scope_mapping_version | audit.scope_resolution.scope_mapping_version | varchar(128) | C: successor scope | COL-01, REF-01, COND-01; deferred |
| decision | audit.scope_resolution.decision | varchar(50) | R | COL-01; deferred |
| reason | audit.scope_resolution.reason | varchar(100) | R | COL-01; deferred |
