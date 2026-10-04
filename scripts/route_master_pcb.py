"""Two-layer grid router for the placed Robosen carrier, using KiCad's pcbnew.

Run with KiCad 10's Python. Refuses to overwrite an already routed board.
Final acceptance must use kicad-cli pcb drc; the grid is only a routing aid.
"""
from pathlib import Path
import heapq
import math
import pcbnew as pcb
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / 'hardware/master_block/robosen_master_block.kicad_pcb'
STEP = 0.125
X0, Y0, X1, Y1 = 86.5, 62., 202., 124.
NX, NY = round((X1-X0)/STEP)+1, round((Y1-Y0)/STEP)+1
LAYERS = [pcb.F_Cu, pcb.B_Cu]
CLEARANCE = 0.22
MARGIN = 0.035
POWER = {'+3V3', '/VBAT_SW', '/VBAT_PROT', '/VBAT_RAW', '/VBAT_GND'}

def mm(v):
    return v / 1e6

def point(x, y):
    return pcb.VECTOR2I(round(x*1e6), round(y*1e6))

def xy(node):
    return X0+node[0]*STEP, Y0+node[1]*STEP

def node(x, y, layer):
    return round((x-X0)/STEP), round((y-Y0)/STEP), layer

class Router:
    def __init__(self, board):
        self.b = board
        self.pads = list(board.GetPads())
        self.copper = []  # net, layer, start, end, radius
        self.keepouts = []
        for f in board.GetFootprints():
            for z in f.Zones():
                if z.GetIsRuleArea():
                    c = z.Outline().COutline(0)
                    pts = [(mm(c.CPoint(i).x), mm(c.CPoint(i).y)) for i in range(c.PointCount())]
                    self.keepouts.append((min(x for x,y in pts), min(y for x,y in pts), max(x for x,y in pts), max(y for x,y in pts)))

    def stamp(self, a, bounds, predicate, layers=(0,1)):
        x0,y0,x1,y1 = bounds
        ix0,iy0 = max(0,math.floor((x0-X0)/STEP)),max(0,math.floor((y0-Y0)/STEP))
        ix1,iy1 = min(NX-1,math.ceil((x1-X0)/STEP)),min(NY-1,math.ceil((y1-Y0)/STEP))
        if ix0>ix1 or iy0>iy1:
            return
        xx = X0+np.arange(ix0,ix1+1)[None,:]*STEP
        yy = Y0+np.arange(iy0,iy1+1)[:,None]*STEP
        mask = predicate(xx,yy)
        for layer in layers:
            a[layer,iy0:iy1+1,ix0:ix1+1] |= mask

    def obstacles(self, net, radius):
        a = np.zeros((2,NY,NX),dtype=bool)
        edge = radius+0.5
        xx = X0+np.arange(NX)*STEP
        yy = Y0+np.arange(NY)*STEP
        a |= ((xx < X0+edge)|(xx > X1-edge))[None,None,:]
        a |= ((yy < Y0+edge)|(yy > Y1-edge))[None,:,None]
        gap = radius+CLEARANCE+MARGIN
        for p in self.pads:
            if p.GetNetCode()==net and net:
                continue
            parent = p.GetParentFootprint()
            ref = parent.GetReference() if parent else ""
            x,y = mm(p.GetPosition().x),mm(p.GetPosition().y)
            if ref in ('H1', 'H2', 'H3', 'H4'):
                r = 3.4 + gap
                self.stamp(a,(x-r,y-r,x+r,y+r),lambda xx,yy:(xx-x)**2+(yy-y)**2<=r*r)
                continue
            sx,sy = mm(p.GetSize().x)/2,mm(p.GetSize().y)/2
            if round(p.GetOrientationDegrees()) % 180 == 90:
                sx,sy=sy,sx
            if p.GetShape()==pcb.PAD_SHAPE_CIRCLE:
                r=max(sx,sy)+gap
                self.stamp(a,(x-r,y-r,x+r,y+r),lambda xx,yy:(xx-x)**2+(yy-y)**2<=r*r)
            else:
                # Rounded expansion of a conservative rectangular pad envelope.
                self.stamp(a,(x-sx-gap,y-sy-gap,x+sx+gap,y+sy+gap),lambda xx,yy:np.maximum(abs(xx-x)-sx,0)**2+np.maximum(abs(yy-y)-sy,0)**2<=gap*gap)
        for x0,y0,x1,y1 in self.keepouts:
            self.stamp(a,(x0-gap,y0-gap,x1+gap,y1+gap),lambda xx,yy:(xx>=x0-gap)&(xx<=x1+gap)&(yy>=y0-gap)&(yy<=y1+gap))
        for code,layer,(x,y),(ex,ey),r0 in self.copper:
            if code==net:
                continue
            r=r0+gap
            dx,dy=ex-x,ey-y
            def capsule(xx,yy):
                t=np.clip(((xx-x)*dx+(yy-y)*dy)/(dx*dx+dy*dy or 1),0,1)
                return (xx-x-t*dx)**2+(yy-y-t*dy)**2<=r*r
            self.stamp(a,(min(x,ex)-r,min(y,ey)-r,max(x,ex)+r,max(y,ey)+r),capsule,(layer,))
        return a

    def search(self, starts, targets, blocked, via_blocked):
        target_set=set(targets)
        tx0,tx1=min(t[0] for t in targets),max(t[0] for t in targets)
        ty0,ty1=min(t[1] for t in targets),max(t[1] for t in targets)
        def h(x,y):
            dx=max(tx0-x,0,x-tx1); dy=max(ty0-y,0,y-ty1)
            return max(dx,dy)+0.41421356*min(dx,dy)
        queue=[]; dist={}; parent={}
        for s in starts:
            if not blocked[s[2],s[1],s[0]]:
                dist[s]=0; heapq.heappush(queue,(h(s[0],s[1]),0,s))
        moves=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.41421356),(1,-1,1.41421356),(-1,1,1.41421356),(-1,-1,1.41421356)]
        while queue:
            _,g,s=heapq.heappop(queue)
            if g!=dist[s]: continue
            if s in target_set:
                path=[s]
                while s in parent:
                    s=parent[s]; path.append(s)
                return path[::-1]
            x,y,l=s
            for dx,dy,cost in moves:
                xx,yy=x+dx,y+dy
                if not (0<=xx<NX and 0<=yy<NY) or blocked[l,yy,xx]: continue
                if dx and dy and (blocked[l,y,xx] or blocked[l,yy,x]): continue
                t=(xx,yy,l)
                ng=g+cost*(1 if l==0 else 1.035)
                if ng<dist.get(t,float('inf')):
                    dist[t]=ng; parent[t]=s; heapq.heappush(queue,(ng+h(xx,yy),ng,t))
            if not via_blocked[:,y,x].any():
                t=(x,y,1-l); ng=g+32
                if ng<dist.get(t,float('inf')):
                    dist[t]=ng;parent[t]=s;heapq.heappush(queue,(ng+h(x,y),ng,t))
        return None

    def track(self, a, b, layer, net, width):
        if a==b: return
        t=pcb.PCB_TRACK(self.b); t.SetStart(point(*a)); t.SetEnd(point(*b))
        t.SetWidth(pcb.FromMM(width));t.SetLayer(LAYERS[layer]);t.SetNetCode(net);self.b.Add(t)
        self.copper.append((net,layer,a,b,width/2))

    def route(self, name, pads):
        net=pads[0].GetNetCode(); width=0.8 if name in POWER else 0.25
        via_size,via_drill=(1.0,0.5) if name in POWER else (0.6,0.3)
        blocked=self.obstacles(net,width/2)
        via_blocked=self.obstacles(net,via_size/2)
        connected=[pads[0]]; remaining=pads[1:]
        tree=set()
        for l in range(2): tree.add(node(mm(pads[0].GetPosition().x),mm(pads[0].GetPosition().y),l))
        while remaining:
            p=min(remaining,key=lambda p:min((p.GetPosition().x-q.GetPosition().x)**2+(p.GetPosition().y-q.GetPosition().y)**2 for q in connected))
            pos=(mm(p.GetPosition().x),mm(p.GetPosition().y))
            starts=[node(*pos,l) for l in range(2)]
            path=self.search(starts,tree,blocked,via_blocked)
            if path is None:
                print('FAILED',name,flush=True);return False
            self.track(pos,xy(path[0]),path[0][2],net,width)
            # Snap target pad to its grid node on the actual arrival layer.
            for q in connected:
                qp=(mm(q.GetPosition().x),mm(q.GetPosition().y))
                if node(*qp,path[-1][2])==path[-1]:
                    self.track(qp,xy(path[-1]),path[-1][2],net,width)
            start=path[0]; prev=path[0]; direction=None
            for cur in path[1:]:
                d=(cur[0]-prev[0],cur[1]-prev[1],cur[2]-prev[2])
                if cur[2]!=prev[2]:
                    self.track(xy(start),xy(prev),prev[2],net,width)
                    v=pcb.PCB_VIA(self.b);v.SetPosition(point(*xy(prev)));v.SetWidth(pcb.FromMM(via_size));v.SetDrill(pcb.FromMM(via_drill));v.SetViaType(pcb.VIATYPE_THROUGH);v.SetLayerPair(*LAYERS);v.SetNetCode(net);self.b.Add(v)
                    for l in range(2):self.copper.append((net,l,xy(prev),xy(prev),via_size/2))
                    start=cur;direction=None
                elif direction is not None and d!=direction:
                    self.track(xy(start),xy(prev),prev[2],net,width);start=prev
                direction=d if cur[2]==prev[2] else None
                prev=cur
            self.track(xy(start),xy(prev),prev[2],net,width)
            tree.update(path)
            # All pads are plated through holes, so both copper layers are reachable.
            tree.update(starts);connected.append(p);remaining.remove(p)
        print('ROUTED',name,len(pads),'pads',flush=True)
        return True

def main():
    b=pcb.LoadBoard(str(BOARD))
    if len(b.GetTracks()): raise SystemExit('Board already has tracks; use an unrouted input.')
    router=Router(b)
    # Reserve straight escapes into the open interior of the ESP32 socket.
    # This prevents early long routes from enclosing still-unrouted header pads.
    for f in b.GetFootprints():
        if f.GetReference()=='U1':
            for p in f.Pads():
                if p.GetNetname() in POWER or p.GetNetname()=='GND' or p.GetNetname().startswith('unconnected-'):
                    continue
                x,y=mm(p.GetPosition().x),mm(p.GetPosition().y)
                router.copper.append((p.GetNetCode(),0,(x,y),(x,86.0 if y>80 else 72.0),0.125))
    nets={}
    for p in b.GetPads():
        if p.GetNetCode() and not p.GetNetname().startswith('unconnected-'):
            nets.setdefault(p.GetNetname(),[]).append(p)
    priority = ['/K1_SW', '/K2_CLK', '/K2_SW', '/K1_DT', '/K2_DT', '/K1_CLK']
    names=sorted((n for n in nets if n!='GND'),key=lambda n:(n not in POWER, n not in priority, -len(nets[n]),n))
    failed=[]
    for name in names:
        if not router.route(name,nets[name]):failed.append(name)
    for layer in LAYERS:
        z=pcb.ZONE(b);z.SetLayer(layer);z.SetNetCode(nets['GND'][0].GetNetCode());z.SetZoneName('GND plane '+b.GetLayerName(layer))
        z.SetLocalClearance(pcb.FromMM(0.25));z.SetPadConnection(pcb.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(pcb.FromMM(0.3));z.SetThermalReliefSpokeWidth(pcb.FromMM(0.4))
        z.SetMinThickness(pcb.FromMM(0.2));z.SetIslandRemovalMode(pcb.ISLAND_REMOVAL_MODE_ALWAYS)
        poly=z.Outline();poly.NewOutline()
        for x,y in [(85,60),(203.5,60),(203.5,125.5),(85,125.5)]:poly.Append(round(x*1e6),round(y*1e6))
        b.Add(z)
    b.BuildConnectivity();pcb.ZONE_FILLER(b).Fill(b.Zones());pcb.SaveBoard(str(BOARD),b)
    print('Saved',BOARD,'failed nets:',failed,flush=True)

if __name__=='__main__':main()
