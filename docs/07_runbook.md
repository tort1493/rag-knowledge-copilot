# Runbook

## When an alert fires
1. Confirm scope (which metric, which segment, when)
2. Check recent changes (data, prompt, model version)
3. Apply mitigation (throttle, rollback, disable feature)
4. Communicate status
5. Postmortem and corrective actions

## Common alerts
- Data schema drift
- Latency spike
- KPI drop
- Increased refusal / decreased citation coverage (LLM)

## Rollback procedure
- Steps to revert to last known good model/prompt/config.
