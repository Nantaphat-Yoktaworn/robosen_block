"""Read-only geometry audit using KiCad 10 pcbnew; never saves the source PCB."""
import collections
import hashlib
import json
import math
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'hardware/kicad/robosen_master_block.kicad_pcb'
OUT = ROOT / 'hardware/kicad/reports'
b = k.LoadBoard(str(SOURCE))
mm = lambda v: v / 1e6
xy = lambda p: [mm(p.x), mm(p.y)]
tracks = [t for t in b.GetTracks() if t.Type() != k.PCB_VIA_T]
vias = [t for t in b.GetTracks() if t.Type() == k.PCB_VIA_T]
pads = [p for p in b.GetPads() if p.GetAttribute() != k.PAD_ATTRIB_NPTH]
holes = {f.GetReference(): xy(f.GetPosition()) for f in b.GetFootprints() if f.GetReference() in ('H1','H2','H3','H4')}
def poly(item, layer):
    p = k.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(p, layer, 0, 1000, k.ERROR_OUTSIDE)
    return p
def rect(x0,y0,x1,y1):
    p=k.SHAPE_POLY_SET();p.NewOutline()
    for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:p.Append(round(x*1e6),round(y*1e6))
    return p
def area_overlap(a,c):
    p=k.SHAPE_POLY_SET(a);p.BooleanIntersection(c)
    return p.Area()/1e12
def desc(t):
    if isinstance(t,k.PAD):
        return dict(kind='pad',ref=t.GetParentFootprint().GetReference(),pad=t.GetNumber(),net=t.GetNetname(),position=xy(t.GetPosition()))
    return dict(kind='via' if t.Type()==k.PCB_VIA_T else 'track',net=t.GetNetname(),layer=t.GetLayerName(),start=xy(t.GetStart()),end=xy(t.GetEnd()),width=mm(t.GetWidth(k.F_Cu) if t.Type()==k.PCB_VIA_T else t.GetWidth()))
def segdist(p,a,c):
    dx,dy=c[0]-a[0],c[1]-a[1];l=dx*dx+dy*dy
    u=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/l)) if l else 0
    return math.hypot(p[0]-a[0]-u*dx,p[1]-a[1]-u*dy)
def radius(t,p):return segdist(p,xy(t.GetStart()),xy(t.GetEnd()))-mm(t.GetWidth(k.F_Cu) if t.Type()==k.PCB_VIA_T else t.GetWidth())/2
data=dict(source=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),kicad=k.GetBuildVersion(),tracks=len(tracks),vias=len(vias),footprint_count=len(list(b.GetFootprints())),track_types=dict(collections.Counter(t.GetClass() for t in tracks)),holes={},power={},zones={},antenna={},footprints=[])
for f in b.GetFootprints():
    data['footprints'].append(dict(ref=f.GetReference(),layer=f.GetLayerName(),position=xy(f.GetPosition()),pads=[dict(number=p.GetNumber(),net=p.GetNetname(),position=xy(p.GetPosition()),size=xy(p.GetSize()),drill=xy(p.GetDrillSize()),shape=int(p.GetShape()),attribute=int(p.GetAttribute())) for p in f.Pads()],graphics=[dict(layer=g.GetLayerName(),start=xy(g.GetStart()),end=xy(g.GetEnd()),shape=int(g.GetShape())) for g in f.GraphicalItems() if isinstance(g,k.PCB_SHAPE)]))
for n in ['+3V3','/VBAT_SW','/VBAT_PROT','/VBAT_RAW','/VBAT_GND','GND']:
    ts=[t for t in tracks if t.GetNetname()==n];vs=[v for v in vias if v.GetNetname()==n]
    data['power'][n]=dict(segments=len(ts),widths=dict(collections.Counter(str(mm(t.GetWidth(k.F_Cu) if t.Type()==k.PCB_VIA_T else t.GetWidth())) for t in ts)),length_mm=sum(mm(t.GetLength()) for t in ts),layer_lengths={b.GetLayerName(l):sum(mm(t.GetLength()) for t in ts if t.GetLayer()==l) for l in [k.F_Cu,k.B_Cu]},vias=[dict(position=xy(v.GetPosition()),diameter=mm(v.GetWidth(k.F_Cu)),drill=mm(v.GetDrill())) for v in vs],pads=[desc(p) for p in pads if p.GetNetname()==n])
for name,pos in holes.items():
    q=k.VECTOR2I(round(pos[0]*1e6),round(pos[1]*1e6))
    near={}
    for label,items in [('tracks',tracks),('vias',vias)]:
        ordered=sorted(items,key=lambda t:radius(t,pos))
        near[label]=[dict(radius_mm=radius(t,pos),**desc(t)) for t in ordered[:5]]
    pp=sorted([(mm(poly(p,k.F_Cu).Distance(q)),desc(p)) for p in pads],key=lambda x:x[0])
    near['pads']=[dict(radius_mm=d,**v) for d,v in pp[:3]]
    near['position']=pos
    data['holes'][name]=near
keep=[z for f in b.GetFootprints() for z in f.Zones() if z.GetIsRuleArea()]
kp=keep[0].Outline()
data['antenna']['outline']=[xy(kp.COutline(0).CPoint(i)) for i in range(kp.COutline(0).PointCount())]
data['antenna']['copper_intrusions']=[]
for layer in [k.F_Cu,k.B_Cu]:
    for item in tracks+vias+pads:
        if item.IsOnLayer(layer):
            a=area_overlap(poly(item,layer),kp)
            if a>0:data['antenna']['copper_intrusions'].append(dict(layer=b.GetLayerName(layer),area_mm2=a,item=desc(item)))
def zones(state):
    result=[]
    for z in b.Zones():
        layer=z.GetLayer();p=z.GetFilledPolysList(layer)
        result.append(dict(name=z.GetZoneName(),net=z.GetNetname(),layer=b.GetLayerName(layer),area_mm2=p.Area()/1e12,polygons=p.OutlineCount(),antenna_overlap_mm2=area_overlap(p,kp),clearance_mm=mm(z.GetLocalClearance()),thermal_gap_mm=mm(z.GetThermalReliefGap()),thermal_spoke_mm=mm(z.GetThermalReliefSpokeWidth()),island_removal=int(z.GetIslandRemovalMode()),hole_radius_mm={name:mm(p.Distance(k.VECTOR2I(round(pos[0]*1e6),round(pos[1]*1e6)))) for name,pos in holes.items()}))
    data['zones'][state]=result
zones('stored')
b.BuildConnectivity()
k.ZONE_FILLER(b).Fill(b.Zones())
zones('refilled')
data['battery_ground_clearance']={}
for layer in [k.F_Cu,k.B_Cu]:
    ground=k.SHAPE_POLY_SET();battery=k.SHAPE_POLY_SET()
    for z in b.Zones():
        if z.IsOnLayer(layer) and z.GetNetname()=='GND':ground.BooleanAdd(z.GetFilledPolysList(layer))
    for item in tracks+vias+pads:
        if item.IsOnLayer(layer):
            if item.GetNetname()=='GND':ground.BooleanAdd(poly(item,layer))
            if item.GetNetname()=='/VBAT_GND':battery.BooleanAdd(poly(item,layer))
    lo,hi=0,1000000
    while hi-lo>1000:
        mid=(lo+hi)//2
        if ground.Collide(battery,mid):hi=mid
        else:lo=mid
    data['battery_ground_clearance'][b.GetLayerName(layer)]={'lower_mm':mm(lo),'upper_mm':mm(hi),'overlap_mm2':area_overlap(ground,battery)}
data['source_unchanged']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()==data['sha256']
OUT.mkdir(exist_ok=True)
(OUT/'independent_audit_geometry.json').write_text(json.dumps(data,indent=2))
# Standalone copper views, both shown in PCB coordinates (bottom is not mirrored).
for layer in [k.F_Cu,k.B_Cu]:
    s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="83 57 123 74" width="1476" height="888">','<rect x="83" y="57" width="123" height="74" fill="white"/>']
    def drawpoly(p,color,opacity):
        paths=[]
        for i in range(p.OutlineCount()):
            for c in [p.COutline(i)]+[p.CHole(i,j) for j in range(p.HoleCount(i))]:
                points=[xy(c.CPoint(j)) for j in range(c.PointCount())]
                paths.append('M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in points)+' Z')
        s.append(f'<path d="{" ".join(paths)}" fill="{color}" opacity="{opacity}" fill-rule="evenodd"/>')
    for z in b.Zones():
        if z.IsOnLayer(layer):drawpoly(z.GetFilledPolysList(layer),'#a6caa7',1)
    for t in tracks+vias+pads:
        if t.IsOnLayer(layer):drawpoly(poly(t,layer),'#a74b18' if t.GetNetname()!='/VBAT_GND' else '#b000db',1)
    s.append('<rect x="86.5" y="62" width="115.5" height="62" fill="none" stroke="black" stroke-width="0.12"/>')
    drawpoly(kp,'#e22222',0.25)
    for x,y,w,h,label in [(104.75,95.55,77.5,20.5,'BT1 body, back'),(108,63,71,30,'DISP1 body, front')]:
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#164ca0" stroke-width="0.15" stroke-dasharray="1,0.5"/><text x="{x+2}" y="{y+2}" font-size="1.4" fill="#164ca0">{label}</text>')
    for name,(x,y) in holes.items():
        for r,color in [(1.6,'black'),(2.85,'#ff8a00'),(3.5,'#c00000')]:s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{color}" stroke-width="0.15"/>')
        s.append(f'<text x="{x+3.8}" y="{y}" font-size="1.5">{name}</text>')
    for f in b.GetFootprints():
        x,y=xy(f.GetPosition());s.append(f'<text x="{x}" y="{y}" font-size="1.25" fill="#003366">{f.GetReference()}</text>')
    s.append(f'<text x="86" y="59.5" font-size="1.7">{b.GetLayerName(layer)}: copper / orange R2.85 screw / red R3.5 boss / purple battery negative</text></svg>')
    (OUT/f'independent_audit_{b.GetLayerName(layer).replace(".","_")}.svg').write_text('\n'.join(s))
print(json.dumps({key:data[key] for key in ['sha256','tracks','vias','track_types','holes','zones','antenna','source_unchanged']},indent=2))
print('POWER',json.dumps(data['power'],indent=2))



