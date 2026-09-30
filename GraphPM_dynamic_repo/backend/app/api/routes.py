from pathlib import Path
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import Project, Developer, Task, Dependency, Defect
from app.schemas import ProjectIn, DeveloperIn, TaskIn, DependencyIn, DefectIn
from app.services.graph import GraphService
from app.services.importer import import_csvs
from app.ml.risk import RiskEngine
from app.core.config import settings

router=APIRouter()

def upsert(session, model, payload):
    obj=model(**payload.model_dump())
    obj=session.merge(obj); session.commit(); session.refresh(obj); return obj

@router.get('/health')
def health(): return {'status':'ok'}

@router.get('/projects')
def projects(session:Session=Depends(get_session)): return session.exec(select(Project)).all()
@router.post('/projects')
def create_project(p:ProjectIn, session:Session=Depends(get_session)): return upsert(session,Project,p)
@router.get('/developers')
def developers(session:Session=Depends(get_session)): return session.exec(select(Developer)).all()
@router.post('/developers')
def create_developer(p:DeveloperIn, session:Session=Depends(get_session)): return upsert(session,Developer,p)
@router.get('/tasks')
def tasks(session:Session=Depends(get_session)): return session.exec(select(Task)).all()
@router.post('/tasks')
def create_task(p:TaskIn, session:Session=Depends(get_session)): return upsert(session,Task,p)
@router.get('/dependencies')
def dependencies(session:Session=Depends(get_session)): return session.exec(select(Dependency)).all()
@router.post('/dependencies')
def create_dependency(p:DependencyIn, session:Session=Depends(get_session)):
    obj=Dependency(**p.model_dump()); session.add(obj); session.commit(); session.refresh(obj); return obj
@router.get('/defects')
def defects(session:Session=Depends(get_session)): return session.exec(select(Defect)).all()
@router.post('/defects')
def create_defect(p:DefectIn, session:Session=Depends(get_session)): return upsert(session,Defect,p)

@router.post('/sync-graph')
def sync_graph(session:Session=Depends(get_session)):
    gs=GraphService()
    try:
        ps=session.exec(select(Project)).all(); ds=session.exec(select(Developer)).all(); ts=session.exec(select(Task)).all(); deps=session.exec(select(Dependency)).all(); fs=session.exec(select(Defect)).all()
        return gs.sync([{'id':p.project_id,'name':p.name,'manager':p.manager,'status':p.status} for p in ps], [{'id':d.developer_id,'name':d.name,'role':d.role,'capacity':d.capacity_hours_per_week} for d in ds], [{'id':t.task_id,'title':t.title,'status':t.status,'priority':t.priority,'project_id':t.project_id,'developer_id':t.developer_id,'module_id':t.module_id,'due_date':str(t.due_date) if t.due_date else None,'story_points':t.story_points,'estimated_hours':t.estimated_hours,'actual_hours':t.actual_hours,'defect_count':t.defect_count,'risk_label':t.risk_label} for t in ts], [{'source':d.source_task_id,'target':d.target_task_id,'type':d.type} for d in deps], [{'id':f.defect_id,'task_id':f.task_id,'severity':f.severity,'status':f.status} for f in fs])
    finally: gs.close()

@router.get('/risk')
def risk(session:Session=Depends(get_session)):
    gs=GraphService()
    try:
        engine=RiskEngine(settings.model_path)
        df=engine.frame(gs.features(),gs.paths())
        return {'results':engine.predict(df),'model_loaded':engine.model is not None,'count':len(df)}
    finally: gs.close()

@router.post('/train')
def train(session:Session=Depends(get_session)):
    gs=GraphService()
    try:
        engine=RiskEngine(settings.model_path); df=engine.frame(gs.features(),gs.paths()); return engine.train(df)
    finally: gs.close()

@router.post('/import-csv')
async def import_csv(projects:UploadFile|None=File(None),developers:UploadFile|None=File(None),tasks:UploadFile|None=File(None),dependencies:UploadFile|None=File(None),defects:UploadFile|None=File(None),session:Session=Depends(get_session)):
    files={}; uploads={'projects':projects,'developers':developers,'tasks':tasks,'dependencies':dependencies,'defects':defects}
    with tempfile.TemporaryDirectory() as td:
        for name,up in uploads.items():
            if up:
                p=Path(td)/f'{name}.csv'; p.write_bytes(await up.read()); files[name]=str(p)
        if not files: raise HTTPException(400,'Upload at least one CSV')
        return {'imported':import_csvs(session,files)}
