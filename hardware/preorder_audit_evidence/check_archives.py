import json,zipfile,hashlib,re
from pathlib import Path
out={}
def normalize(s):
 return '\n'.join(l for l in s.splitlines() if not any(x in l for x in ['TF.CreationDate','G04 Created by KiCad','; DRILL file KiCad','"CreationDate":']))
for name,folder in [('action','action_block'),('master','master_block')]:
 p=next(Path('hardware',folder).glob('*.zip'));z=zipfile.ZipFile(p)
 d={'archive':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'crc_bad_member':z.testzip(),'members':[]}
 for i in z.infolist():
  s=z.read(i.filename).decode();f=Path('hardware/preorder_audit_evidence',name+'_export',i.filename).read_text()
  entry=dict(name=i.filename,bytes=i.file_size,normalized_matches_fresh=normalize(s)==normalize(f))
  if i.filename.endswith('.drl'):
   entry['tool_diameters_mm']=re.findall(r'T\d+C([\d.]+)',s);entry['hits']=len(re.findall(r'^X',s,re.M))
  d['members'].append(entry)
 out[name]=d
Path('hardware/preorder_audit_evidence/archive_integrity.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
