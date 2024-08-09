# To do

### fastf1-predictions

- [ ] Update `environment.yml` to reflect the new llama env along with `poetry`

### multi-agents-analysis

- [x] Add poetry as a package manager https://python-poetry.org/docs/basic-usage/
- [ ] Create a toy db with formula 1 data
- [x] Drop `laps.db` columns:
  - DriverNumber
  - Team
  - LapStartDate
  - TrackStatus
  - Position
  - Deleted
  - DeletedReason
  - FastF1Generated
  - IsAccurate
  - index
- [ ] Connect `NLSQLRetriever` and `RetrieverQueryEngine` on this toy db
