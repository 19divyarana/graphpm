"""Normalize a Jira CSV export into GraphPM tasks.csv.
Usage: python normalize_jira_csv.py input.csv output.csv
Adjust COLUMN_MAP for the exact export you downloaded.
"""
import sys
import pandas as pd

COLUMN_MAP={
    'Issue key':'task_id','Issue Type':'issue_type','Summary':'title','Status':'status','Priority':'priority',
    'Assignee':'developer_id','Project key':'project_id','Created':'created_at','Due Date':'due_date',
    'Story Points':'story_points','Original Estimate':'estimated_hours','Time Spent':'actual_hours',
}
if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('python normalize_jira_csv.py input.csv output.csv')
    df=pd.read_csv(sys.argv[1])
    df=df.rename(columns=COLUMN_MAP)
    required=['task_id','project_id','title']
    missing=[x for x in required if x not in df]
    if missing: raise SystemExit(f'Missing columns: {missing}. Update COLUMN_MAP for your Jira export.')
    for c in ['status','priority','developer_id','module_id','created_at','due_date','completed_at','story_points','estimated_hours','actual_hours','defect_count','risk_label']:
        if c not in df: df[c]=None
    df.to_csv(sys.argv[2],index=False)
    print(f'Wrote {len(df)} rows to {sys.argv[2]}')
