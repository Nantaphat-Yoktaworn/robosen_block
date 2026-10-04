"""Read-only audit. Run with KiCad bundled Python from repository root."""
import wx
app=wx.App(False)
import pcbnew as k
import json,hashlib,collections
from pathlib import Path
OUT=Path('hardware/preorder_audit_evidence')
mm=lambda v:v/1e6
xy=lambda v:[mm(v.x),mm(v.y)]
def poly(item,layer):
 p=k.SHAPE_POLY_SET();item.TransformShapeToPolygon(p,layer,0,1000,k.ERROR_OUTSIDE);return p
def overlap(a,b):
 p=k.SHAPE_POLY_SET(a);p.BooleanIntersection(b);return p.Area()/1e12
def zp(b):
 return [dict(layer=b.GetLayerName(z.GetLayer()),net=z.GetNetname(),area_mm2=z.GetFilledPolysList(z.GetLayer()).Area()/1e12,polygons=z.GetFilledPolysList(z.GetLayer()).OutlineCount(),clearance=mm(z.GetLocalClearance()),thermal_gap=mm(z.GetThermalReliefGap()),thermal_spoke=mm(z.GetThermalReliefSpokeWidth()),pad_connection=z.GetPadConnection(),island_removal=z.GetIslandRemovalMode()) for z in b.Zones() if not z.GetIsRuleArea()]
for name,src in [('action','hardware/action_block/action_block.kicad_pcb'),('master','hardware/master_block/robosen_master_block.kicad_pcb')]:
 path=Path(src);sha=hashlib.sha256(path.read_bytes()).hexdigest();b=k.LoadBoard(src)
 pads=list(b.GetPads());tracks=[t for t in b.GetTracks() if t.Type()!=k.PCB_VIA_T];vias=[t for t in b.GetTracks() if t.Type()==k.PCB_VIA_T]
 d=dict(source=src,sha256=sha,thickness=mm(b.GetDesignSettings().GetBoardThickness()),layers=b.GetCopperLayerCount(),tracks=len(tracks),vias=len(vias),footprints=[],edges=[],nets={},zones_stored=zp(b))
 for f in b.GetFootprints():
  d['footprints'].append(dict(ref=f.GetReference(),value=f.GetValue(),footprint=str(f.GetFPID().GetLibItemName()),layer=f.GetLayerName(),origin=xy(f.GetPosition()),angle=f.GetOrientationDegrees(),pads=[dict(number=p.GetNumber(),net=p.GetNetname(),pos=xy(p.GetPosition()),size=xy(p.GetSize()),drill=xy(p.GetDrillSize()),zone_connection=p.GetLocalZoneConnection()) for p in f.Pads()]))
 for s in b.GetDrawings():
  if s.GetLayer()==k.Edge_Cuts:d['edges'].append(dict(shape=s.GetShapeStr(),start=xy(s.GetStart()),end=xy(s.GetEnd()),width=mm(s.GetWidth())))
 for n in sorted(set(t.GetNetname() for t in tracks)|{'GND'}):
  ts=[t for t in tracks if t.GetNetname()==n]
  d['nets'][n]=dict(pads=[p.GetParentFootprint().GetReference()+':'+p.GetNumber() for p in pads if p.GetNetname()==n],widths=dict(collections.Counter(str(mm(t.GetWidth())) for t in ts)),length=sum(mm(t.GetLength()) for t in ts),segments=[dict(start=xy(t.GetStart()),end=xy(t.GetEnd()),layer=t.GetLayerName(),width=mm(t.GetWidth())) for t in ts])
 b.BuildConnectivity();k.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();d['zones_refilled']=zp(b)
 if name=='master':
  d['battery_ground_clearance']={}
  for layer in [k.F_Cu,k.B_Cu]:
   ground=k.SHAPE_POLY_SET();battery=k.SHAPE_POLY_SET()
   for z in b.Zones():
    if z.IsOnLayer(layer) and z.GetNetname()=='GND':ground.BooleanAdd(z.GetFilledPolysList(layer))
   for item in pads+tracks+vias:
    if item.IsOnLayer(layer):
     if item.GetNetname()=='GND':ground.BooleanAdd(poly(item,layer))
     if item.GetNetname()=='/VBAT_GND':battery.BooleanAdd(poly(item,layer))
   lo,hi=0,1000000
   while hi-lo>1000:
    mid=(lo+hi)//2
    if ground.Collide(battery,mid):hi=mid
    else:lo=mid
   d['battery_ground_clearance'][b.GetLayerName(layer)]=dict(lower=mm(lo),upper=mm(hi),overlap_mm2=overlap(ground,battery))
  keeps=[z for f in b.GetFootprints() for z in f.Zones() if z.GetIsRuleArea()]
  d['keepouts']=[]
  for z in keeps:
   p=z.Outline();kd=dict(outline=[xy(p.COutline(0).CPoint(i)) for i in range(p.COutline(0).PointCount())],copper_overlap={})
   for layer in [k.F_Cu,k.B_Cu]:
    kd['copper_overlap'][b.GetLayerName(layer)]=sum(overlap(poly(t,layer),p) for t in pads+tracks+vias if t.IsOnLayer(layer))+sum(overlap(zz.GetFilledPolysList(layer),p) for zz in b.Zones() if zz.IsOnLayer(layer) and not zz.GetIsRuleArea())
   d['keepouts'].append(kd)
 d['source_unchanged']=hashlib.sha256(path.read_bytes()).hexdigest()==sha
 (OUT/(name+'_geometry.json')).write_text(json.dumps(d,indent=2))
 print(name,json.dumps({key:d[key] for key in ['sha256','layers','thickness','tracks','vias','edges','zones_stored','zones_refilled','source_unchanged']},indent=2))
 print('NETS',json.dumps({n:{key:v for key,v in data.items() if key!='segments'} for n,data in d['nets'].items()},indent=2))
 if name=='master': print('ISOLATION',d['battery_ground_clearance'],'KEEPOUT',d['keepouts'])
