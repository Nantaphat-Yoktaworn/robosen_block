import re,json
from pathlib import Path
text=Path('hardware/action_block/action_block.net').read_text()
tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text);pos=0
def parse():
 global pos
 token=tokens[pos];pos+=1
 if token!='(':return json.loads(token) if token.startswith('"') else token
 a=[]
 while tokens[pos]!=')':a.append(parse())
 pos+=1;return a
root=parse()
def child(a,n):return next(x for x in a if isinstance(x,list) and x[0]==n)
def value(a,n):return child(a,n)[1]
nets=child(root,'nets')[1:]
expected={value(n,'name'):sorted(value(x,'ref')+':'+value(x,'pin') for x in n if isinstance(x,list) and x[0]=='node') for n in nets}
b=json.loads(Path('hardware/preorder_audit_evidence/action_geometry.json').read_text());actual={}
for f in b['footprints']:
 for p in f['pads']:actual.setdefault(p['net'],[]).append(f['ref']+':'+p['number'])
actual={n:sorted(v) for n,v in actual.items()}
result=dict(all_21_nets_exactly_match=expected==actual,schematic=expected,pcb=actual)
Path('hardware/preorder_audit_evidence/action_netlist_comparison.json').write_text(json.dumps(result,indent=2));print('Action schematic/PCB: all 21 nets exactly match:',expected==actual)
