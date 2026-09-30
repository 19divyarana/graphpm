# GraphPM architecture

```text
                    Project Manager
                          |
                          v
                 React Project UI
                          |
                          v
                     FastAPI API
                 /        |        \
                v         v         v
             SQLite     Neo4j      CSV/Jira
             state       KG        importer
                |         |
                +----+----+
                     |
              graph feature engine
                     |
             Random Forest / XGBoost
                     |
                risk predictions
                     |
          explainable recommendation layer
                     |
                 React dashboard
```

## Graph model

- `(Project)` contains tasks.
- `(Task)-[:ASSIGNED_TO]->(Developer)`
- `(Task)-[:DEPENDS_ON]->(Task)`
- `(Task)-[:HAS_DEFECT]->(Defect)`
- `(Task)-[:PART_OF]->(Project)`

## Dynamic data principle

The UI is the source of truth for current project state. The graph is rebuilt from the current relational state by **Sync Graph**. Historical labelled tasks are used for supervised training.

## Production evolution

For a larger deployment, replace SQLite with PostgreSQL, add authentication/RBAC, use a background queue for graph synchronization and model training, and connect Jira/GitHub webhooks for near-real-time ingestion.
