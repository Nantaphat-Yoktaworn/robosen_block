import wx
app=wx.App(False)
import pcbnew as k
import json
b=k.LoadBoard('hardware/action_block/action_block.kicad_pcb')
results=[]
for f in b.GetFootprints():
 if f.GetReference()=='MCU':
  print('MCU graphics',[(g.GetLayerName(),str(g.GetStart()),str(g.GetEnd())) for g in f.GraphicalItems() if isinstance(g,k.PCB_SHAPE)])
 for pad in f.Pads():
  if pad.GetNetname()!='GND':continue
  row={'pad':f.GetReference()+':'+pad.GetNumber(),'local_connection':pad.GetLocalZoneConnection(),'fill_contact_area_mm2':{}}
  for z in b.Zones():
   layer=z.GetLayer();p=k.SHAPE_POLY_SET();pad.TransformShapeToPolygon(p,layer,0,1000,k.ERROR_OUTSIDE);p.BooleanIntersection(z.GetFilledPolysList(layer))
   row['fill_contact_area_mm2'][b.GetLayerName(layer)]=p.Area()/1e12
  results.append(row)
open('hardware/preorder_audit_evidence/action_ground_contacts.json','w').write(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
