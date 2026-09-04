# JARVIS AT SCALE — DISASTER RECOVERY & RELIABILITY PLAN

## 1. Service Level Objectives

* **Recovery Point Objective (RPO)**: $\le 15$ minutes (Maximum acceptable data loss window)
* **Recovery Time Objective (RTO)**: $\le 30$ minutes (Maximum acceptable downtime window)
* **Availability Target**: $99.9\%$ Uptime

---

## 2. Failure Matrix & Degradation Behavior

| Failure Mode | Impact | Automated Resilience / Fallback |
| :--- | :--- | :--- |
| **Redis Offline** | Caching unavailable | `HybridCacheProvider` switches to `MemoryFallbackCache`. Requests proceed normally. |
| **Web Provider Offline** | Web search fails | `web_search` returns graceful error message. Agent relies on vector RAG context. |
| **Primary LLM Offline** | Anthropic Claude error | `LLMClient` falls back to HuggingFace / secondary LLM provider. |
| **Background Worker Crash** | Worker task stops | `JobManager` detects stale jobs on startup and resets state to `pending`. |
| **Database Failure** | DB writes fail | `/ready` health check reports `degraded`. Retries write transactions. |

---

## 3. Disaster Recovery Procedures

### 1. Database Restore Procedure:
```bash
# 1. Stop API and worker services
docker-compose stop api

# 2. Restore PostgreSQL database from latest backup snapshot
cat backup_latest.sql | docker exec -i jarvis-postgres psql -U jarvis_user -d jarvis_db

# 3. Restart API service
docker-compose start api
```

### 2. Stale Job Recovery:
When the API server starts, `init_db()` and `JobManager` clean up crashed or interrupted background jobs:
```sql
UPDATE background_jobs SET status = 'failed', error = 'Worker process terminated unexpectedly' WHERE status = 'running';
```
