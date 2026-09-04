# ION AT SCALE — FINAL MASTER SYSTEM ARCHITECTURE (ION 5.0 RELEASE)

---

## 1. Complete System Architecture Overview

```text
                      ION 5.0 Intelligent Platform Integration
                                        │
                       Unified Request Lifecycle Engine (18 Stages)
           (Auth -> Tenant -> Context -> Intent -> Capability -> Strategy -> Plan -> 
            Agent -> Security -> Budget -> Approval -> Execute -> Verify -> Replanning -> 
            Evidence Gate -> Response -> Persist -> Learn)
                                        │
                      Unified Capability Lifecycle Engine (11 Stages)
           (DISCOVER -> DESCRIBE -> VALIDATE -> AUTHORIZE -> BUDGET -> EXECUTE -> 
            VERIFY -> OBSERVE -> EVALUATE -> UPDATE -> ROLLBACK)
                                        │
                    Global Scale & Multi-Region Architecture
           (RegionRouter, Data Residency Enforcer, Global LLM Router, Global Job Router, 
            Distributed Scheduler Safety, WebSocket Reconnect Manager, Failover Engine)
                                        │
                  Advanced Multimodal Interaction & Unified Context
           (InteractionRequest, 9 Context Streams, Modality Router, Cross-Modal Evidence 
            Tree, Voice Multimodal Pipeline, Context Budget Manager, Privacy Tracker)
                                        │
                          Enterprise ION Platform 2.0
           (EnterprisePolicyManager, Roles, Multi-Tier Budget Inheritance, Resource 
            Ownership Matrix, Capability Governance, Enterprise Audit Logger)
                                        │
              Massive Evaluation, Benchmarking & Quality Intelligence
           (BenchmarkSuite, 8 Eval Categories, Capability x Model Matrix, Baseline vs 
            Candidate Regression Engine, Continuous Evaluation Gates)
                                        │
                        ION IoT & Smart Environment Platform
           (DeviceRegistry, EnvironmentManager, EdgeRuntime, DeviceSecurityPolicy)
                                        │
                           ION 4.2 Advanced Intelligence
           (LongHorizonPlanner, CausalGraph, ScenarioSimulator, WhatIfDecisionMatrix)
                                        │
                        Controlled Self-Improvement Pipeline
           (Observe -> Measure -> Candidate -> Offline Eval -> Admin Approval -> Deploy -> Rollback)
                                        │
                          Developer SDK 2.0 & Connector Platform
           (IonClient, PublicAPIGateway, UniversalConnectors, Marketplace)
                                        │
                          Clients / SDK / Webhooks / Frontend UI
                                        │
                      API Layer (FastAPI v5.0) / WebSocket Gateway
                                        │
                      LangGraph Multi-Agent Orchestrator
                                        │
                    PostgreSQL / SQLAlchemy Database Models
```

---

## 2. Module Ownership & Architecture Matrix

| Phase | Subsystem / Feature Area | Primary Modules | Security & Isolation Boundaries |
| :--- | :--- | :--- | :--- |
| **91** | Global Scale & Multi-Region | [`orchestrator/platform/global_routing.py`](file:///c:/Users/tanis/Projects/jarvis/orchestrator/platform/global_routing.py) | Data Residency Enforcer, Distributed Leases, Failover Guard |
| **92** | Advanced Multimodal Context | [`orchestrator/multimodal/unified_context.py`](file:///c:/Users/tanis/Projects/jarvis/orchestrator/multimodal/unified_context.py) | Modality Router, Token & Image Budgeting, Privacy Tracker |
| **93** | Enterprise Platform 2.0 | [`orchestrator/auth/enterprise_policy.py`](file:///c:/Users/tanis/Projects/jarvis/orchestrator/auth/enterprise_policy.py) | Role Hierarchy (`ORG_OWNER`..`VIEWER`), Multi-Tier Budget Inheritance, Tenant Isolation |
| **94** | Massive Evaluation & Benchmarking | [`orchestrator/evaluation/benchmark_suite.py`](file:///c:/Users/tanis/Projects/jarvis/orchestrator/evaluation/benchmark_suite.py) | Baseline vs Candidate Regression Gates, 8 Eval Categories |
| **95–100** | ION 5.0 Platform Integration | [`orchestrator/platform/unified_runtime.py`](file:///c:/Users/tanis/Projects/jarvis/orchestrator/platform/unified_runtime.py), [`api/routes_v5_0.py`](file:///c:/Users/tanis/Projects/jarvis/api/routes_v5_0.py) | 18-Stage Request Lifecycle, 11-Stage Capability Lifecycle, 8-Layer Security Boundary |
| **86–90** | IoT, Devices & Smart Environment | `orchestrator/devices/*`, `orchestrator/platform/edge.py` | RBAC Permissions, Risk Classifier, Secret Redaction, `LOCAL_ONLY` Mode |

---

## 3. Database Schema Reference (SQLAlchemy ORM)

The PostgreSQL relational database schema includes:
- `users`: Core user accounts and credentials
- `organizations`: Organization tenant entities
- `workspaces`: Workspace entities bound to organizations
- `org_policies`: Enterprise policy matrices and budgets
- `enterprise_audit_events`: Structural enterprise audit event trail
- `eval_datasets`: Versioned evaluation datasets
- `eval_runs`: Candidate evaluation run metrics and gate results
- `devices`: Registered IoT device metadata and status
- `environments`: Smart environment rooms/zones and state policies
- `scenes`: Multi-device declarative automation scenes
- `device_audit_events`: IoT device audit logs with credential redaction
