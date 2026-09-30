from datetime import date
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

FEATURES = ["story_points","estimated_hours","actual_hours","defect_count","incoming","outgoing","dependency_depth","deadline_days","workload_ratio"]

class RiskEngine:
    def __init__(self, model_path="./artifacts/risk_model.joblib"):
        self.model_path=Path(model_path)
        self.model=None
        if self.model_path.exists(): self.model=joblib.load(self.model_path)

    def frame(self, rows, paths):
        df=pd.DataFrame(rows)
        if df.empty: return df
        edges=[(x['source'],x['target']) for x in paths]
        depth={}
        def calc(n,seen=None):
            seen=set() if seen is None else seen
            if n in depth:return depth[n]
            if n in seen:return 0
            seen.add(n)
            parents=[a for a,b in edges if a==n]
            depth[n]=0 if not parents else 1+max(calc(p,seen.copy()) for p in parents)
            return depth[n]
        df['dependency_depth']=df['task_id'].map(calc).fillna(0)
        today=pd.Timestamp(date.today())
        df['deadline_days']=(pd.to_datetime(df['due_date'], errors='coerce')-today).dt.days.fillna(30).clip(-365,365)
        df['workload_ratio']=(df['actual_hours'].fillna(0)+df['estimated_hours'].fillna(0))/(df['capacity'].replace(0,np.nan).fillna(40))
        return df

    def train(self, df):
        labelled=df.dropna(subset=['risk_label']).copy()
        if len(labelled)<8 or labelled['risk_label'].nunique()<2:
            return {"trained":False,"reason":"Need at least 8 labelled tasks containing both classes (0 and 1)."}
        X=labelled[FEATURES].fillna(0); y=labelled['risk_label'].astype(int)
        model=RandomForestClassifier(n_estimators=250,random_state=42,class_weight='balanced')
        model.fit(X,y); self.model=model
        self.model_path.parent.mkdir(parents=True,exist_ok=True); joblib.dump(model,self.model_path)
        pred=model.predict(X)
        return {"trained":True,"samples":len(labelled),"accuracy":accuracy_score(y,pred),"precision":precision_score(y,pred,zero_division=0),"recall":recall_score(y,pred,zero_division=0),"f1":f1_score(y,pred,zero_division=0)}

    def predict(self, df):
        if df.empty:return []
        if self.model is not None:
            probs=self.model.predict_proba(df[FEATURES].fillna(0))[:,1]
        else:
            x=df
            probs=(0.22*(x['priority'].eq('HIGH'))+0.20*(x['status'].isin(['BLOCKED','IN_PROGRESS']))+0.16*(x['deadline_days']<7)+0.16*(x['workload_ratio']>1)+0.12*(x['dependency_depth']>=2)+0.14*(x['defect_count']>0)+0.10*(x['outgoing']>1)).clip(0,1).astype(float).values
        result=[]
        for row,p in zip(df.to_dict('records'),probs):
            factors=[]
            if row['priority']=='HIGH': factors.append('high priority')
            if row['status']=='BLOCKED': factors.append('blocked status')
            if row['deadline_days']<7: factors.append('deadline is close')
            if row['workload_ratio']>1: factors.append('developer workload is high')
            if row['dependency_depth']>=2: factors.append('deep dependency chain')
            if row['defect_count']>0: factors.append('open defects')
            if row['outgoing']>1: factors.append('multiple downstream dependencies')
            level='HIGH' if p>=0.65 else 'MEDIUM' if p>=0.35 else 'LOW'
            rec=self.recommend(level,factors,row)
            result.append({"task_id":row['task_id'],"title":row['title'],"risk_probability":round(float(p),3),"risk_level":level,"factors":factors,"recommendation":rec})
        return result

    def recommend(self,level,factors,row):
        if level=='HIGH':
            actions=[]
            if 'developer workload is high' in factors: actions.append('reallocate part of the task to another available developer')
            if 'deep dependency chain' in factors or 'multiple downstream dependencies' in factors: actions.append('review and unblock the dependency chain before the next sprint commitment')
            if 'open defects' in factors: actions.append('reserve QA capacity and triage open defects')
            if not actions: actions.append('review scope and deadline during sprint planning')
            return 'High-risk task: ' + '; '.join(actions) + '.'
        if level=='MEDIUM': return 'Monitor this task in the next stand-up and review its deadline, dependencies and workload.'
        return 'No immediate intervention suggested; continue normal sprint monitoring.'
