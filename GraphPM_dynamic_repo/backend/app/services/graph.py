from neo4j import GraphDatabase
from app.core.config import settings

class GraphService:
    def __init__(self):
        self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))

    def close(self):
        self.driver.close()

    def sync(self, projects, developers, tasks, dependencies, defects):
        with self.driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n")
            for p in projects:
                s.run("MERGE (x:Project {id:$id}) SET x.name=$name, x.manager=$manager, x.status=$status", **p)
            for d in developers:
                s.run("MERGE (x:Developer {id:$id}) SET x.name=$name, x.role=$role, x.capacity=$capacity", **d)
            for t in tasks:
                s.run("MERGE (x:Task {id:$id}) SET x.title=$title, x.status=$status, x.priority=$priority, x.project_id=$project_id, x.developer_id=$developer_id, x.module_id=$module_id, x.due_date=$due_date, x.story_points=$story_points, x.estimated_hours=$estimated_hours, x.actual_hours=$actual_hours, x.defect_count=$defect_count, x.risk_label=$risk_label", **t)
                s.run("MATCH (t:Task {id:$id}),(p:Project {id:$project_id}) MERGE (t)-[:PART_OF]->(p)", id=t['id'], project_id=t['project_id'])
                if t.get('developer_id'):
                    s.run("MATCH (t:Task {id:$id}),(d:Developer {id:$developer_id}) MERGE (t)-[:ASSIGNED_TO]->(d)", id=t['id'], developer_id=t['developer_id'])
            for dep in dependencies:
                s.run("MATCH (a:Task {id:$source}),(b:Task {id:$target}) MERGE (a)-[r:DEPENDS_ON {type:$type}]->(b)", source=dep['source'], target=dep['target'], type=dep['type'])
            for f in defects:
                s.run("MERGE (x:Defect {id:$id}) SET x.severity=$severity, x.status=$status", **f)
                s.run("MATCH (f:Defect {id:$id}),(t:Task {id:$task_id}) MERGE (t)-[:HAS_DEFECT]->(f)", id=f['id'], task_id=f['task_id'])
        return {"status":"synced", "nodes": len(projects)+len(developers)+len(tasks)+len(defects), "dependencies": len(dependencies)}

    def features(self):
        q = """
        MATCH (t:Task)
        OPTIONAL MATCH (t)-[:ASSIGNED_TO]->(d:Developer)
        OPTIONAL MATCH (t)-[:DEPENDS_ON]->(down:Task)
        OPTIONAL MATCH (up:Task)-[:DEPENDS_ON]->(t)
        OPTIONAL MATCH (t)-[:HAS_DEFECT]->(f:Defect)
        WITH t,d,count(DISTINCT down) AS outgoing,count(DISTINCT up) AS incoming,count(DISTINCT f) AS defects
        RETURN t.id AS task_id, t.title AS title, t.status AS status, t.priority AS priority,
               t.due_date AS due_date, t.story_points AS story_points,
               t.estimated_hours AS estimated_hours, t.actual_hours AS actual_hours,
               t.defect_count AS defect_count, t.risk_label AS risk_label,
outgoing, incoming, defects,
coalesce(d.capacity,40) AS capacity
        """
        with self.driver.session() as s:
            return [dict(r) for r in s.run(q)]

    def paths(self):
        q="MATCH (a:Task)-[:DEPENDS_ON]->(b:Task) RETURN a.id AS source,b.id AS target"
        with self.driver.session() as s:
            return [dict(r) for r in s.run(q)]
