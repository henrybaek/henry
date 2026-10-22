#!/usr/bin/env python3
"""build/ 폴더의 데이터로 저장소 루트의 index.html을 다시 만든다.
사용: python3 build/build.py  (저장소 루트에서 실행)"""
import json, os, sys
B=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(B)
p=lambda f:os.path.join(B,f)
lines=lambda f:[l.rstrip('\n') for l in open(p(f),encoding='utf-8') if l.strip() and not l.startswith('#')]
roles=dict(l.split('|') for l in lines('roles.txt'))
removed=[dict(zip('ngvd',l.split('|'))) for l in lines('removed.txt')]
REM={r['n'] for r in removed}
sp=lambda x:[a.strip() for a in x.split(',') if a.strip() and a.strip() not in REM]
warn=[]
rows=[]
for l in lines('data.txt'):
    f=l.split('|')
    if len(f)!=9: warn.append('형식 오류: '+l); continue
    cid,n,t,w,pr,go,si,it,bo=f
    if cid not in roles: warn.append('역할 없음: '+cid)
    rows.append(dict(id=cid,n=n,t=t,w=float(w.rstrip('%')),r=roles.get(cid,'전사'),p=sp(pr),g=sp(go),s=sp(si),i=sp(it),b=bo))
meta={}
for i,l in enumerate(lines('aug_meta.txt')):
    n,g,t,pk=l.split('|'); meta[n]=dict(g=g,t=t,p=float(pk))
raw={}
for l in lines('aug_raw.txt'):
    n,d,c=l.split('|'); raw[n]=dict(d=d,c=[x.strip() for x in c.split(',')])
easy={}
for l in lines('aug_easy.txt'):
    n,e,fit=l.split('|'); easy[n]=dict(e=e,f=fit)
aug=[]
for i,(n,m) in enumerate(meta.items()):
    if n not in raw or n not in easy: warn.append('증강 설명 누락: '+n); continue
    aug.append(dict(i=i,n=n,**m,**raw[n],**easy[n]))
names={a['n'] for a in aug}
for r in rows:
    for a in r['p']+r['g']+r['s']:
        if a not in names: warn.append(f'사전에 없는 증강: {a} ({r["n"]})')
m=json.load(open(p('meta.json'),encoding='utf-8'))
ch=json.load(open(p('changes.json'),encoding='utf-8'))
bal=json.load(open(p('balance.json'),encoding='utf-8')) if os.path.exists(p('balance.json')) else {}
j=lambda o:json.dumps(o,ensure_ascii=False,separators=(',',':'))
h=open(p('template.html'),encoding='utf-8').read()
for k,v in {'/*__DATA__*/[]':j(rows),'/*__AUG__*/[]':j(aug),'/*__REMOVED__*/[]':j(removed),'/*__CHANGES__*/[]':j(ch),'/*__BAL__*/{}':j(bal),'__STATS__':m.get('stats',m['patch']),'__PATCH__':m['patch'],'__DATE__':m['collected']}.items():
    h=h.replace(k,v)
open(os.path.join(R,'index.html'),'w',encoding='utf-8').write(h)
print(f'챔피언 {len(rows)} · 증강 {len(aug)} · 경고 {len(warn)}')
for w in sorted(set(warn)): print(' -',w)
sys.exit(1 if any(w.startswith(('형식','증강 설명')) for w in warn) else 0)
