"""Triage pending planning decisions with TypeSafe Jev.

Usage: python3 scripts/kanban.py --json > board.json; TYPESAFE_API_KEY=... python3 scripts/jev-triage.py board.json out.json
The key is read from the environment only; never commit it.
"""
import sys,json,os,urllib.request,concurrent.futures as cf
key=os.environ.get("TYPESAFE_API_KEY") or os.environ["JEV_KEY"]
d=json.load(open(sys.argv[1]))
its=[i for i in d['open_items'] if i['kind']=='decision' and i['status'] in('open','in_progress','blocked') and not i.get('same_as') and i['owner'].startswith('负责人')]
Q={
 "money_or_attr":{"type":"noul","instructions":"这条待确认事项的决定，会不会改变用户拿到的钱、订单或邀请关系归到谁名下、平台的资金口径或资金安全控制？","criteria":{"true":"会影响金额、资金口径、资金操作的安全控制，或订单/邀请人的归属","false":"只影响界面文案、显示方式、远期功能约束或内部技术细节"}},
 "account_or_risk":{"type":"noul","instructions":"这条事项是否涉及用户账号安全与授权、个人信息处理、对外承诺，或可能招致平台封禁、监管、商店审核风险？"},
 "has_default":{"type":"noul","instructions":"`default` 字段是否给出了一个明确可执行的默认做法（而不是写「未定」「没有默认」「不自拟」）？"},
}
def run(i):
    f=dict(i['fields']); dv=f.get('默认') or f.get('已按默认写回的做法') or f.get('现在怎么处理') or f.get('默认值') or f.get('保守默认') or ''
    state={"item":i['title'],"default":dv[:1200],"context":' '.join(t for _,t in i['fields'])[:1500]}
    body=json.dumps({"state":state,"model":"jev-latest","questions":Q}).encode()
    r=urllib.request.Request("https://api.typesafe.ai/v1/systemone",body,{"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    a=json.load(urllib.request.urlopen(r,timeout=60))
    return i['id'],i['title'],a
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(run,its))
json.dump(res,open(sys.argv[2] if len(sys.argv)>2 else '/tmp/jev_out.json','w'),ensure_ascii=False)
print(len(res)); print(json.dumps(res[0][2],ensure_ascii=False)[:600])
