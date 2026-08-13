# Advanced DAX Patterns

Use variables to make measures readable and avoid repeated expressions. Prefer `CALCULATE` for filter-context changes, `DIVIDE` for safe ratios, and iterators such as `AVERAGEX` when the business definition requires evaluation over a date set. Keep dimensions as filter axes and facts as aggregation tables; avoid bidirectional relationships unless a specific business case requires them.

For role-playing warehouse relationships, use `USERELATIONSHIP` in measures instead of duplicating dimensions. For scenario analysis, isolate parameters in a disconnected `Scenario` table and use `SELECTEDVALUE` to apply the parameter without altering the base fact data.
