"""Route the fixed Action Block placement with KiCad 10's Python.

Requires an unrouted input board. Use --return-detour to route RETURN_BUS
below the MCU: a straight line shorts pads 4/15 and 0.4 mm copper cannot
fit between its 1.8 mm pads at the project's 0.2 mm clearance.
"""
from pathlib import Path
import argparse
import pcbnew as pcb

BOARD = Path(__file__).with_name('action_block.kicad_pcb')

def point(x, y):
    return pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(y))

def placement(board):
    return sorted((f.GetReference(), f.GetPosition().x, f.GetPosition().y,
                   f.GetOrientationDegrees(),
                   tuple(sorted((p.GetNumber(), p.GetPosition().x,
                                 p.GetPosition().y, p.GetNetname()) for p in f.Pads())))
                  for f in board.GetFootprints())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--return-detour', action='store_true')
    args = parser.parse_args()
    board = pcb.LoadBoard(str(BOARD))
    if len(board.GetTracks()) or len(board.Zones()):
        raise SystemExit('Input must be unrouted; refusing to replace existing copper.')
    original = placement(board)
    nets = board.GetNetsByName()

    def route(net, layer, width, points):
        for start, end in zip(points, points[1:]):
            t = pcb.PCB_TRACK(board)
            t.SetStart(point(*start)); t.SetEnd(point(*end))
            t.SetWidth(pcb.FromMM(width)); t.SetLayer(layer)
            t.SetNetCode(nets[net].GetNetCode()); board.Add(t)

    route('/LED_DIN', pcb.F_Cu, .3, [(84,65.04),(86.5,67.54),(86.5,70.44),(88.76,72.7)])
    route('/RX_IN', pcb.B_Cu, .3, [(83.5,73.77),(85.4,71.87),(85.4,68.9),(86.68,67.62),(88.76,67.62)])
    route('/TX_OUT', pcb.B_Cu, .3, [(88.76,65.08),(91,65.08),(92.27,66.35),(104.9,66.35),(107,68.45),(107,71.27),(109.5,73.77)])
    route('/SWIO', pcb.F_Cu, .3, [(104,75.24),(106,77.24),(106,83),(109.5,86.5)])
    route('+3V3', pcb.F_Cu, .6, [(84,62.5),(81.8,64.7),(81.8,66.99),(83.5,68.69)])
    route('+3V3', pcb.B_Cu, .6, [(84,62.5),(88.72,62.5),(88.76,62.54)])
    route('+3V3', pcb.F_Cu, .6, [(88.76,62.54),(104,62.54),(105.58,60.96),(109.5,60.96)])
    route('+3V3', pcb.F_Cu, .6, [(105.58,60.96),(106.5,61.88),(106.5,65.69),(109.5,68.69)])
    route('+3V3', pcb.F_Cu, .6, [(109.5,68.69),(111.4,70.59),(111.4,82.06),(109.5,83.96)])
    if args.return_detour:
        route('/RETURN_BUS', pcb.B_Cu, .4, [(83.5,76.31),(86,78.81),(86,85.25),(88,87.25),(104.9,87.25),(106.5,85.65),(106.5,79.31),(109.5,76.31)])

    for layer in (pcb.F_Cu, pcb.B_Cu):
        z = pcb.ZONE(board)
        z.SetLayer(layer); z.SetNetCode(nets['GND'].GetNetCode())
        z.SetZoneName('GND plane ' + board.GetLayerName(layer))
        z.SetLocalClearance(pcb.FromMM(.25))
        z.SetPadConnection(pcb.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(pcb.FromMM(.3))
        z.SetThermalReliefSpokeWidth(pcb.FromMM(.4))
        z.SetMinThickness(pcb.FromMM(.2))
        z.SetIslandRemovalMode(pcb.ISLAND_REMOVAL_MODE_ALWAYS)
        poly = z.Outline(); poly.NewOutline()
        for x, y in [(80.5,56.5),(112.5,56.5),(112.5,88.5),(80.5,88.5)]:
            poly.Append(pcb.FromMM(x), pcb.FromMM(y))
        board.Add(z)
    assert placement(board) == original, 'Placement changed'
    board.BuildConnectivity()
    pcb.ZONE_FILLER(board).Fill(board.Zones())
    pcb.SaveBoard(str(BOARD), board)
    assert placement(pcb.LoadBoard(str(BOARD))) == original
    print('Saved routes and filled thermal GND planes; placement unchanged.')

if __name__ == '__main__':
    main()
