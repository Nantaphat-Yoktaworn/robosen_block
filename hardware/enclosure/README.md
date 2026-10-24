# 📦 Robosen Block - Master Block 3D Enclosure Specification

> **Project:** Tangible Modular Physical Block Coding System for Robosen K1 Robot  
> **Component:** Master Controller Block Enclosure (Box with Lid, Knobs & Buttons)  
> **Native CAD File:** [`master_block_enclosure.FCStd`](master_block_enclosure.FCStd)  
> **Generation Script:** [`generate_enclosure.py`](generate_enclosure.py)  
> **CAD Environment:** FreeCAD 1.1+ (Python OpenCASCADE BREP Solid Modeling)  
> **Status:** **COMPLETE & VERIFIED 100% VALID SOLID BREP GEOMETRY**

---

## 1. Overview & 4-Part Architecture

The Master Block enclosure is designed as a rugged, child-friendly 2-piece split enclosure (Case + Lid) plus 2 user-interface parts (Knob + Button), producing **4 unique CAD parts** in FreeCAD:

| # | FreeCAD Object Name | Display Label | Description & Role | Print Qty |
| :---: | :--- | :--- | :--- | :---: |
| **1** | `Case` | `Case (Bottom Box)` | Deep bottom tub housing the 18650 battery underneath, 4× M3 PCB standoffs, side U-notches for Pogo docks and USB-C, and rear 20mm power switch cutout. | 1× |
| **2** | `Lid` | `Lid (Top Cover)` | Top cover with centered 2.13" E-Paper display window, dual rotary encoder holes, dual captive button sockets, and 4 corner screw counterbores. | 1× |
| **3** | `Knob` | `Knob (18mm D-Shaft Dial)` | 18mm diameter knurled rotary encoder dial with tactile indicator dot and keyed 6.0mm D-shaft socket. | 2× |
| **4** | `Button` | `Button (Captive Cap)` | Ergonomic captive push-button cap with bottom retention flange (cannot fall out when flipped) and finger depression dish. | 2× |

---

## 2. Dimensional & Geometric Specifications

```
                     ◄─────────────────── 129.0 mm ───────────────────►
        ┌────────────────────────────────────────────────────────────────────────┐ ▲
        │ ⊕ [Lid Screw]                  [20mm Power Switch]        [Lid Screw] ⊕│ │
        │                                                                        │ │
     ▲  │ ┌───────────────┐        ┌─────────────────────────┐ ┌───────────────┐ │ │
     │  │ │ Knob 1 (KY040)│        │     E-Paper Display     │ │ Knob 2 (KY040)│ │ │ 72.0 mm
     │  │ └───────────────┘        │ [Symmetrically Centered]│ └───────────────┘ │ │
     │  │                          └─────────────────────────┘                   │ │
     │  │ ┌───────────────┐                                    ┌───────────────┐ │ │
     ▼  │ │Button 1 (SW5) │        [18650 Battery Cavity]      │ Button 2 (SW3)│ │ │
        │ └───────────────┘                                    └───────────────┘ │ │
        │ ⊕ [Lid Screw]                  [USB-C Charging]           [Lid Screw] ⊕│ │
        └────────────────────────────────────────────────────────────────────────┘ ▼
```

### 2.1 Overall Enclosure Envelope
* **External Dimensions:** $129.0\text{ mm}\ (W) \times 72.0\text{ mm}\ (D) \times 42.4\text{ mm}\ (H)$
* **Wall Thickness:** $2.4\text{ mm}$ heavy-duty perimeter walls (6 perimeters with 0.4mm nozzle).
* **Corner Fillets:** $R = 4.0\text{ mm}$ rounded vertical corners for drop protection and tactile comfort.
* **Base Split Line:** Mates horizontally at $Z = 26.0\text{ mm}$ (PCB deck level) with U-notches for drop-in PCB installation.
* **Bottom Feet:** 4× circular recesses ($\varnothing 8.0\text{ mm} \times 0.8\text{ mm}$ depth) at $X = \pm 52.0\text{ mm}, Y = \pm 25.0\text{ mm}$ for non-slip silicone rubber bumper feet.

### 2.2 PCB Mounting & Battery Clearance (Bottom Case)
* **Internal Cavity:** $117.5\text{ mm}\ (W) \times 64.0\text{ mm}\ (D) \times 37.6\text{ mm}\ (H)$ (providing $1.0\text{ mm}$ clearance around the $115.5 \times 62.0\text{ mm}$ PCB).
* **PCB Standoff Height:** $22.0\text{ mm}$ tall bosses (from $Z = 2.4\text{ mm}$ floor to $Z = 24.4\text{ mm}$) to easily clear the onboard 18650 battery holder ($21.0\text{ mm}$ height) below the PCB.
* **PCB Mounting Holes (H1–H4):**
  * `H1`: $(-48.00\text{ mm}, +1.00\text{ mm})$
  * `H2`: $(+48.00\text{ mm}, +1.00\text{ mm})$
  * `H3`: $(-52.75\text{ mm}, -27.50\text{ mm})$
  * `H4`: $(+52.75\text{ mm}, -27.50\text{ mm})$
  * **Boss Size:** $\varnothing 7.0\text{ mm}$ outer diameter with $\varnothing 4.2\text{ mm} \times 5.5\text{ mm}$ pilot hole for M3 brass heat-set threaded inserts.

### 2.3 Lid Fastening & Corner Pillars
* **4 Outer Corner Pillars:** Centered at $X = \pm 60.5\text{ mm}, Y = \pm 31.0\text{ mm}$ (completely outside the PCB perimeter, allowing the PCB to drop in and be fastened independently).
* **Case Corner Pilot Holes:** $\varnothing 4.2\text{ mm} \times 6.0\text{ mm}$ pilot holes for M3 heat-set threaded inserts.
* **Lid Corner Holes:** $\varnothing 3.4\text{ mm}$ clearance through-holes with $\varnothing 6.2\text{ mm} \times 2.5\text{ mm}$ counterbores for flush M3 socket-head screws.

### 2.4 Ports & Cutouts
1. **Left Magnetic Pogo Dock (`J1`):** Sized for Guang Chen 4-pin magnetic connector (19.54 mm body width, no ears). Wall cutout $20.2\text{ mm} \times 4.2\text{ mm}$ with a $1.0\text{ mm}$ lead-in alignment chamfer to guide mating action blocks and absorb magnetic pull strain.
2. **Right Magnetic Pogo Dock (`J2`):** Symmetrical to J1 at $X = +64.5\text{ mm}, Y = +1.00\text{ mm}$.
3. **USB-C Charging Port:** Front wall ($Y = -36.0\text{ mm}$), centered at $X = -18.00\text{ mm}$, opening $12.0\text{ mm} \times 6.5\text{ mm}$ with rounded lead-in edges.
4. **Power Switch Hole:** Rear wall ($Y = +36.0\text{ mm}$), **$20.0\text{ mm}$ ($2\text{ cm}$) diameter** circular cutout centered at $X = 0.0\text{ mm}$.
5. **E-Paper Screen Window:** Symmetrically centered at $X = 0.0\text{ mm}, Y = +15.5\text{ mm}$. Active viewing window $48.0\text{ mm} \times 23.5\text{ mm}$ with a stepped interior framing bezel ($50.5\text{ mm} \times 26.0\text{ mm}$, depth $1.2\text{ mm}$) to secure the screen edges.
6. **Rotary Encoder Openings:** $\varnothing 9.0\text{ mm}$ clearance holes at $X = -47.75\text{ mm}$ (Knob 1) and $X = +48.13\text{ mm}$ (Knob 2), $Y = +17.50\text{ mm}$.
7. **Button Openings:** $\varnothing 8.6\text{ mm}$ through-holes at $X = -42.00\text{ mm}$ (Button 1) and $X = +40.00\text{ mm}$ (Button 2), $Y = -13.00\text{ mm}$, with $\varnothing 12.0\text{ mm} \times 2.0\text{ mm}$ captive retention pockets underneath the lid.

---

## 3. Fastener Bill of Materials (BOM)

| Item | Specification | Quantity | Usage |
| :--- | :--- | :---: | :--- |
| **M3 Heat-Set Brass Inserts** | $\text{M3} \times 4.0\text{ mm}$ or $5.0\text{ mm}$ (OD $4.6\text{ mm}$, for $\varnothing 4.2\text{ mm}$ hole) | **8×** | 4× for PCB standoffs + 4× for Lid corner pillars |
| **PCB Mounting Screws** | $\text{M3} \times 6.0\text{ mm}$ Button Head / Pan Head | **4×** | Securing PCB onto standoffs (H1–H4) |
| **Lid Corner Screws** | $\text{M3} \times 16.0\text{ mm}$ Socket Head Cap Screws | **4×** | Clamping Lid into Case corner inserts |
| **Rubber Bumper Feet** | $\varnothing 8.0\text{ mm} \times 1.5\text{–}2.0\text{ mm}$ adhesive silicone pads | **4×** | Bottom case base pockets |

---

## 4. 3D Printing Recommendations

| Parameter | Recommended Setting | Notes |
| :--- | :--- | :--- |
| **Material** | **PLA+** or **PETG** | PETG recommended for impact resistance in classrooms |
| **Nozzle Diameter** | $0.4\text{ mm}$ | Compatible with $0.6\text{ mm}$ nozzles |
| **Layer Height** | $0.20\text{ mm}$ (Quality) | $0.16\text{ mm}$ recommended for Knob knurling and Button dish |
| **Perimeters / Walls** | **4 to 6 perimeters** | Solid perimeter rings around M3 heat-set insert holes |
| **Infill Density** | **20% to 30%** (Gyroid or Grid) | Provides high torsional rigidity |
| **Supports** | Minimal / None | Case and Lid print flat on their mating rims or outer faces |
| **Print Orientations** | | |
| - `Case` | Bottom floor flat on print bed ($Z = 0$ down) | No supports needed for standoffs |
| - `Lid` | Top face flat on print bed ($Z = 42.4$ down) | Produces smooth, glass-like top finish on PEI sheet |
| - `Knob` | Flat bottom skirt on print bed ($Z = 0$ down) | No supports needed for internal D-shaft socket |
| - `Button` | Bottom flange flat on print bed ($Z = 0$ down) | Cleanest print for the top finger dish |

---

## 5. FreeCAD Regeneration Instructions

To regenerate or programmatically modify the enclosure geometry at any time:
```powershell
& "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe" -c "import runpy; runpy.run_path(r'C:\Users\nnnn\Projects\robosen_block\hardware\enclosure\generate_enclosure.py', run_name='__main__')"
```
This recomputes all OpenCASCADE BREP solids and updates [`master_block_enclosure.FCStd`](master_block_enclosure.FCStd).
