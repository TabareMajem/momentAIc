---
description: VPS Deployment Safety Protocol - MUST follow before any deployment
---

# VPS DEPLOYMENT SAFETY PROTOCOL
# VPS Deployment Safety Protocol

**CRITICAL RULE: NO DIRECT DEPLOYMENTS**. All code changes must pass through the **STAGING GATE** before the VPS is touched.

## 1. The Staging Gate
Before proposing any deployment to the VPS, the following must be done in an isolated local environment:
- [ ] **Full Container Rebuild**: Ensure the `Dockerfile` and `docker-compose.yml` build from scratch without cache.
- [ ] **4-Hour Burn-In Test**: The services must run in isolation for at least 4 hours with ZERO restarts.
- [ ] **Resource Monitoring Audit**: 
    - CPU usage must remain stable (no upward trends).
    - Memory usage must show no leaks (verified by `docker stats`).
- [ ] **Startup Verification**: All services (`api`, `worker`, `beat`) must reach `healthy` status.
- [ ] **Integration Smoke Test**: Run `curl` against the health endpoint AND at least one representative API endpoint (e.g., `/api/v1/agents/list`).
- [ ] **Log Audit**: Zero "Error" or "Traceback" lines in the logs for all services.

## 2. Pre-Deployment Stability Audit
For every deployment, a `stability_audit.md` must be created and shared with the user containing:
- **Change Summary**: Exactly what files were touched and why.
- **Risk Assessment**: Potential impact on database, networking, or AI model costs.
- **Evidence of Staging Success**: 
    - Raw output of health checks.
    - Snapshot of `docker stats` after hours of uptime.
    - Tail of 1000 lines of logs to prove zero errors.

## 3. Deployment Checklist (VPS)
Only after the user approves the `stability_audit.md`, proceed with:
1. `bash /root/momentaic/scripts/validate_before_deploy.sh`
2. `bash /root/momentaic/scripts/deploy_verified_updates.sh`
3. **Live Health Check**: Immediate verification of `docker ps` on the VPS.

## 4. Rollback Command
If any issue occurs on the VPS:
```bash
# Emergency Rollback to last backup
bash /root/momentaic/scripts/rollback_vps.sh
```

## 5. Dangerous Files (Extra Caution)
- `app/core/database.py` (Schema breaking)
- `app/models/*.py` (Migration requirements)
- `app/core/config.py` (Env Var dependencies)
- `docker-compose.yml` (Network/Isolation changes)
- `app/main.py` (Application entry point)
- `.env` / `.env.production` (Secrets)
- `ecosystem.config.js` (PM2 config)
- `docker-compose*.yml` (Docker config)
