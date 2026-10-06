# High CPU Utilization Runbook

## Symptoms
- CPU utilization above 90 percent
- Increased application latency
- Slow API responses
- Request timeouts

## Investigation Steps
1. Check current CPU utilization.
2. Identify high CPU processes.
3. Review application traffic.
4. Check recent deployments.
5. Review application logs.
6. Compare against historical utilization.

## Common Causes
- Traffic spike
- Expensive application queries
- Infinite processing loop
- Resource undersizing
- Recent deployment regression

## Safety
Restarting or scaling production services requires approval.