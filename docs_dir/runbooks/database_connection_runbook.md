# Database Connectivity Runbook

## Symptoms
- Database connection timeout
- Application HTTP 500 errors
- Connection refused errors
- Increased database latency

## Investigation Steps
1. Check database service health.
2. Verify network connectivity.
3. Check active database connections.
4. Check connection pool utilization.
5. Review database error logs.
6. Check recent configuration changes.

## Common Causes
- Connection pool exhaustion
- Database unavailable
- Network connectivity issue
- Incorrect credentials
- Maximum connection limit reached

## Safety
Database configuration changes require engineer approval.