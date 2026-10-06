# Payments API HTTP 500 Runbook

## Service
payments-api

## Symptoms
- HTTP 500 responses
- Customer checkout failures
- Increased API latency

## Investigation Steps
1. Check payments-api service health.
2. Review recent application logs.
3. Check database connectivity.
4. Check database connection pool utilization.
5. Search previous incidents for similar errors.

## Common Causes
- Database connection pool exhaustion
- Database connectivity failure
- Invalid application configuration
- Downstream payment provider failure

## DatabaseConnectionPoolTimeout
If logs contain `DatabaseConnectionPoolTimeout`:

1. Check active database connections.
2. Check connection pool utilization.
3. Compare utilization against configured capacity.
4. Review recent transaction traffic.

## Safety
Do not automatically restart a production service.
Production service restart requires engineer approval.