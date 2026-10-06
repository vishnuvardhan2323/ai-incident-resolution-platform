# Incident INC-2026-001

## Service
payments-api

## Impact
Customers experienced checkout failures.

## Symptoms
The payments API returned HTTP 500 errors.

## Error
DatabaseConnectionPoolTimeout

## Root Cause
The application's database connection pool reached
its configured capacity during increased transaction
traffic.

## Resolution
Connection pool capacity was increased after
engineering review and affected application workers
were restarted.

## Prevention
- Monitor connection pool utilization.
- Alert when utilization exceeds 80 percent.
- Review connection pool sizing during traffic growth.

## Safety
Production restart requires engineer approval.