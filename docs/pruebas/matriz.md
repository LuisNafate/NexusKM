# Matriz de pruebas ejecutadas

Cada fila corresponde a un caso del JUnit real, no a una declaración manual de éxito. El test de fechas usa parametrización y produce dos casos. Los cuerpos, fixtures y limpieza están en tests/.

| ID | Prueba pytest | Área | Resultado | Segundos |
| --- | --- | --- | --- | --- |
| P01 | test_connectivity_to_three_real_databases | Integración / dominio | Aprobada | 0.077 |
| P02 | test_authentication_required | Autorización | Aprobada | 0.004 |
| P03 | test_wrong_password_rejected | Autorización | Aprobada | 0.048 |
| P04 | test_tampered_token_rejected | Autorización | Aprobada | 0.000 |
| P05 | test_expired_token_rejected | Autorización | Aprobada | 0.000 |
| P06 | test_catalog_has_reused_identifiers | Integración / dominio | Aprobada | 0.314 |
| P07 | test_impact_combines_graph_catalog_and_document | Grafo | Aprobada | 0.040 |
| P08 | test_unknown_api_returns_404 | Integración / dominio | Aprobada | 0.017 |
| P09 | test_api_without_service_consumers_returns_empty_projects | Integración / dominio | Aprobada | 0.036 |
| P10 | test_restricted_document_denies_leader | Autorización | Aprobada | 0.021 |
| P11 | test_document_list_filters_restricted_content | Autorización | Aprobada | 0.023 |
| P12 | test_technical_reviewer_can_read_restricted_document | Autorización | Aprobada | 0.030 |
| P13 | test_postgres_rejects_missing_reference | SQL | Aprobada | 0.009 |
| P14 | test_postgres_rejects_second_current_version | SQL | Aprobada | 0.008 |
| P15 | test_postgres_rolls_back_partial_transaction | SQL | Aprobada | 0.015 |
| P16 | test_mongodb_rejects_invalid_document | Mongo / contenido | Aprobada | 0.001 |
| P17 | test_mongodb_rejects_wrong_nested_type | Mongo / contenido | Aprobada | 0.001 |
| P18 | test_neo4j_rejects_duplicate_identifier | Grafo | Aprobada | 0.005 |
| P19 | test_graph_tests_and_positive_coverage | Grafo | Aprobada | 0.036 |
| P20 | test_q2_only_returns_published_current_versions | Grafo | Aprobada | 0.006 |
| P21 | test_historical_owner_approval_is_corrected | Grafo | Aprobada | 0.004 |
| P22 | test_idempotent_create_and_conflicting_reuse | Integración / dominio | Aprobada | 0.158 |
| P23 | test_create_rename_content_and_soft_delete | Integración / dominio | Aprobada | 0.364 |
| P24 | test_non_owner_cannot_rename | Autorización | Aprobada | 0.024 |
| P25 | test_stale_revision_rejected | Integración / dominio | Aprobada | 0.177 |
| P26 | test_concurrent_updates_have_one_winner | Integración / dominio | Aprobada | 0.154 |
| P27 | test_content_validation_before_enqueue | Mongo / contenido | Aprobada | 0.021 |
| P28 | test_invalid_expiration[2020-01-01T00:00:00+00:00] | Integración / dominio | Aprobada | 0.021 |
| P29 | test_invalid_expiration[2027-01-01] | Integración / dominio | Aprobada | 0.013 |
| P30 | test_published_content_is_immutable | Integración / dominio | Aprobada | 0.025 |
| P31 | test_duplicate_version_number_rejected | Integración / dominio | Aprobada | 0.098 |
| P32 | test_self_technical_approval_rejected | Integración / dominio | Aprobada | 0.246 |
| P33 | test_wrong_role_and_wrong_owner_approvals_rejected | Autorización | Aprobada | 0.207 |
| P34 | test_full_approval_and_publication_flow | Integración / dominio | Aprobada | 0.743 |
| P35 | test_restricted_publication_requires_security | Autorización | Aprobada | 0.603 |
| P36 | test_partial_write_is_recoverable | Integración / dominio | Aprobada | 0.161 |
| P37 | test_sync_retry_requires_admin | Integración / dominio | Aprobada | 0.014 |
| P38 | test_audit_is_recorded_and_scoped | Integración / dominio | Aprobada | 0.097 |
| P39 | test_sql_input_is_parameterized | SQL | Aprobada | 0.057 |

Las pruebas de conectividad, repositorio y flujo se ejecutan sobre PostgreSQL, MongoDB y Neo4j reales. El caso de recuperación inyecta una excepción del repositorio de grafo para controlar el punto de fallo. No se presenta como una desconexión física de red.
