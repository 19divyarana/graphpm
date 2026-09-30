# GraphPM — Dynamic Enterprise Project Intelligence

GraphPM is a working MVP based on the supplied research paper. It turns project-management data into a Neo4j Knowledge Graph, computes graph-derived risk features, predicts task risk, and gives explainable recommendations.

## What changed from the paper prototype

- **No static CSV-only workflow:** project managers can create/update projects, developers, tasks, dependencies and defects from the UI.
- **Real-data ingestion:** import a CSV exported from Jira or use the included adapter for public Jira-style datasets.
- **Neo4j graph:** Task, Developer, Project, Defect and Module nodes with ASSIGNED_TO, DEPENDS_ON, HAS_DEFECT and WORKS_ON relationships.
- **Risk model:** Random Forest when enough labelled historical records exist; deterministic fallback when there is not enough training data.
- **Recommendations:** explainable recommendations are generated from the actual risk factors and graph context. An optional LLM provider can be added later.
- **API-first:** FastAPI backend + React frontend.

The research paper describes heterogeneous data from project-management platforms, version control and issue trackers, graph construction in Neo4j, graph-derived features, Random Forest prediction and an Agentic AI recommendation layer. This repository implements that flow as an extensible MVP.

## Stack

- Backend: Python, FastAPI, SQLModel/SQLite, pandas, scikit-learn, Neo4j
- Frontend: React + Vite
- Graph: Neo4j 5
- ML: Random Forest; optional XGBoost dependency
- Deployment: Docker Compose

## 1. Run with Docker

```bash
docker compose up --build
```

Open:
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Neo4j: http://localhost:7474

## 2. Run locally

Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## 3. Load demo data

The repo includes a small **demo dataset only for bootstrapping the UI**. It is not claimed to be a real-world dataset.

```bash
python scripts/seed_demo.py
```

Then click **Sync Graph** in the dashboard.

## 4. Import real Jira data

The backend accepts normalized CSV files. See `data/README.md` and `scripts/normalize_jira_csv.py`.

For research-scale data, the Public Jira Dataset is available from Zenodo. The 2025 release contains anonymized public Jira repositories and is much too large to commit into this repository, so download a subset and normalize it locally.

Dataset: https://zenodo.org/records/15719919

## Normalized schema

### projects.csv
`project_id,name,manager,start_date,end_date,status`

### developers.csv
`developer_id,name,role,capacity_hours_per_week`

### tasks.csv
`task_id,project_id,title,status,priority,developer_id,module_id,created_at,due_date,completed_at,story_points,estimated_hours,actual_hours,defect_count,risk_label`

`risk_label` is optional. Use `1` for high-risk and `0` for low-risk historical tasks when a trusted outcome label exists.

### dependencies.csv
`source_task_id,target_task_id,type`

### defects.csv
`defect_id,task_id,severity,status,created_at,resolved_at`

## PM workflow

1. PM creates a project.
2. PM adds developers and tasks.
3. PM assigns tasks, due dates, estimates and priorities.
4. PM creates dependencies and defects.
5. PM clicks **Sync Graph**.
6. Backend computes graph features such as degree, betweenness and dependency depth.
7. Backend predicts risk for tasks.
8. Dashboard shows risk factors and recommendations.
9. Historical labelled data can be imported later and the model retrained.

## Important research note

Do not claim that a model is "92% accurate" merely because the paper reports that figure. The supplied paper reports 80% for Graph PM + Random Forest and 92% for a Graph PM + XGBoost configuration, but this repository is designed to recompute metrics on the actual dataset used for evaluation. Your final paper should report the measured result, dataset version, split strategy and class distribution.
