# Time Intelligence

```dax
OTIF % YTD = TOTALYTD([OTIF %], dim_date[date])
OTIF % PY = CALCULATE([OTIF %], SAMEPERIODLASTYEAR(dim_date[date]))
OTIF % YoY = DIVIDE([OTIF % YTD] - [OTIF % PY], [OTIF % PY], 0)
Fill Rate 3M Avg = AVERAGEX(DATESINPERIOD(dim_date[date], LASTDATE(dim_date[date]), -3, MONTH), [Fill Rate %])
Cost to Serve MoM = VAR current = [Cost to Serve] VAR prior = CALCULATE([Cost to Serve], DATEADD(dim_date[date], -1, MONTH)) RETURN DIVIDE(current - prior, prior, 0)
```
