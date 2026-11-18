import os
import shutil
import subprocess
import tempfile

svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1680 1040" width="1680" height="1040" style="background-color: #F8F9FA; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <filter id="shadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="4" stdDeviation="4" flood-color="#000000" flood-opacity="0.08" />
    </filter>
    <marker id="arrow-dark" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2D3436" />
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0984E3" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#00B894" />
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6C5CE7" />
    </marker>
    <marker id="arrow-power" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#E17055" />
    </marker>
  </defs>

  <!-- Title Header Bar -->
  <rect x="40" y="20" width="1600" height="76" rx="16" fill="#FFFFFF" stroke="#DFE6E9" stroke-width="1.5" filter="url(#shadow)" />
  <text x="68" y="56" font-size="22" font-weight="800" fill="#2D3436">Robosen Tangible Coding Block System — Hardware &amp; Protocol System Block Diagram</text>
  <text x="68" y="80" font-size="13.5" font-weight="500" fill="#636E72">Verified against hardware/master_block (Proto #1-1), hardware/action_block (32x32mm) &amp; firmware/</text>
  <rect x="1355" y="38" width="258" height="40" rx="20" fill="#2D3436" />
  <text x="1484" y="63" font-size="13" font-weight="700" fill="#FFFFFF" text-anchor="middle">ESP32-S3 + CH32V003 + K1 BLE</text>

  <!-- Overhead Wireless BLE Bridge (Master -> Robosen K1) -->
  <path d="M 255 175 L 255 136 L 1455 136 L 1455 175" fill="none" stroke="#0984E3" stroke-width="3" stroke-dasharray="8,5" marker-end="url(#arrow-blue)" />
  <rect x="575" y="116" width="530" height="38" rx="19" fill="#E0F2FE" stroke="#0284C7" stroke-width="2" filter="url(#shadow)" />
  <text x="840" y="140" font-size="13" font-weight="800" fill="#0369A1" text-anchor="middle">BLE 5.0 Central (NimBLE) -&gt; GATT Service 0xFFE0 / Char 0xFFE1</text>

  <!-- ==================== LEFT: MASTER CONTROLLER BLOCK ==================== -->
  <g id="master-block" filter="url(#shadow)">
    <rect x="40" y="175" width="430" height="775" rx="18" fill="#FFFFFF" stroke="#2D3436" stroke-width="2.5" />
    <rect x="40" y="175" width="430" height="46" rx="18" fill="#6C5CE7" />
    <rect x="40" y="203" width="430" height="18" fill="#6C5CE7" />
    <text x="255" y="198" font-size="15.5" font-weight="800" fill="#FFFFFF" text-anchor="middle">MASTER CONTROLLER BLOCK (Proto #1-1)</text>
    <text x="255" y="214" font-size="11" font-weight="600" fill="#EDE9FE" text-anchor="middle">hardware/master_block/robosen_master_block.kicad_pcb</text>

    <!-- 1. MCU Core -->
    <rect x="58" y="232" width="394" height="106" rx="12" fill="#EEF2FF" stroke="#4F46E5" stroke-width="1.8" />
    <text x="255" y="253" font-size="13" font-weight="800" fill="#312E81" text-anchor="middle">U1: ESP32-S3-DevKitC-1 Dual-Core MCU</text>
    <text x="74" y="274" font-size="11.5" font-weight="600" fill="#1E293B">• Core 1: 3-Mode FSM (1A/1B/2/3), Chain Engine, UART1/2</text>
    <text x="74" y="294" font-size="11.5" font-weight="600" fill="#1E293B">• Core 0: einkDisplayTask + bleReconnectTask + bleMutex</text>
    <text x="74" y="314" font-size="11.5" font-weight="600" fill="#1E293B">• Status: RGB_BUILTIN (GPIO 48) | Serial Log @ 115200</text>

    <!-- 2. J2 Run Chain Port -->
    <rect x="58" y="350" width="394" height="148" rx="12" fill="#FFFBEB" stroke="#D97706" stroke-width="2" />
    <text x="255" y="371" font-size="13" font-weight="800" fill="#92400E" text-anchor="middle">J2: RUN CHAIN MAGNETIC POGO PORT (4-Pin)</text>
    <text x="74" y="393" font-size="11.5" font-weight="700" fill="#C2410C">Pin 1: +3V3  |  Pin 2: GND (Shared Chain Bus Power)</text>
    <text x="74" y="423" font-size="11.5" font-weight="700" fill="#0369A1">Pin 3: CHAIN_TX (GPIO 15 + R1 10k PU) -&gt; 0xAA / 0xBB</text>
    <text x="74" y="468" font-size="11.5" font-weight="700" fill="#047857">Pin 4: CHAIN_RX (GPIO 16 + R2 10k PU) &lt;- 0xAA Return</text>
    <text x="74" y="488" font-size="10.5" font-weight="500" fill="#78350F">pollRunChainPort() @ 800ms detects chain -&gt; Mode 1B</text>

    <!-- 3. UI Peripherals & E-Ink -->
    <rect x="58" y="510" width="394" height="140" rx="12" fill="#F8FAFC" stroke="#64748B" stroke-width="1.8" />
    <text x="255" y="531" font-size="13" font-weight="800" fill="#1E293B" text-anchor="middle">UI Peripherals: E-Ink, Knobs &amp; Pushbuttons</text>
    <text x="74" y="553" font-size="11.2" font-weight="600" fill="#334155">• DISP1: 2.13" E-Paper SPI (BUSY=4, RES=5, DC=6, CS=7,</text>
    <text x="84" y="570" font-size="11.2" font-weight="600" fill="#334155">SCL=21, SDA=38); 210x122 bezel (280ms + 350ms settle)</text>
    <text x="74" y="592" font-size="11.2" font-weight="600" fill="#334155">• SW1 KY-040 Knob 1 (CLK=8, DT=9, SW=10)</text>
    <text x="74" y="611" font-size="11.2" font-weight="600" fill="#334155">• SW2 KY-040 Knob 2 (CLK=11, DT=12, SW=13)</text>
    <text x="74" y="630" font-size="11.2" font-weight="600" fill="#334155">• SW3 Green Start (GPIO 14) | SW5 Red Stop (GPIO 2)</text>

    <!-- 4. Power Tree -->
    <rect x="58" y="662" width="394" height="114" rx="12" fill="#FEF2F2" stroke="#EF4444" stroke-width="1.8" />
    <text x="255" y="683" font-size="13" font-weight="800" fill="#991B1B" text-anchor="middle">Power Subsystem (18650 Li-Ion -&gt; +3V3)</text>
    <text x="74" y="705" font-size="11.2" font-weight="600" fill="#1E293B">• BT1 18650 Cell -&gt; U2 TP4056 (USB-C Charger)</text>
    <text x="74" y="725" font-size="11.2" font-weight="600" fill="#1E293B">• SW4 Slide Switch -&gt; U3 TPS63020 (+3V3 Buck-Boost)</text>
    <text x="74" y="745" font-size="11.2" font-weight="600" fill="#1E293B">• R3 / R4 / C1 BATSENSE Divider -&gt; GPIO 1 (ADC Monitor)</text>

    <!-- 5. J1 Config Dock Port -->
    <rect x="58" y="788" width="394" height="146" rx="12" fill="#F3E8FF" stroke="#7C3AED" stroke-width="2" />
    <text x="255" y="809" font-size="13" font-weight="800" fill="#5B21B6" text-anchor="middle">J1: CONFIG DOCK POGO PORT (4-Pin)</text>
    <text x="74" y="835" font-size="11.5" font-weight="700" fill="#C2410C">Pin 1: +3V3  |  Pin 2: GND (Dock Block Power)</text>
    <text x="74" y="870" font-size="11.5" font-weight="700" fill="#6D28D9">Pin 3: CFG_RX (GPIO 18) | Pin 4: CFG_TX (GPIO 17)</text>
    <text x="74" y="896" font-size="10.8" font-weight="600" fill="#4C1D95">• Auto-alternates UART1 TX/RX (17&lt;-&gt;18) to match orientation</text>
    <text x="74" y="914" font-size="10.8" font-weight="600" fill="#4C1D95">• pollConfigDock() @ 250ms locks Mode 1A (1200ms timeout)</text>
  </g>

  <!-- ==================== CENTER UPPER: PHYSICAL RUN CHAIN (J2) ==================== -->
  <g id="run-chain-region">
    <rect x="520" y="175" width="710" height="368" rx="18" fill="#FFFFFF" stroke="#BAE6FD" stroke-width="2" filter="url(#shadow)" />
    <rect x="520" y="175" width="710" height="36" rx="18" fill="#E0F2FE" />
    <rect x="520" y="195" width="710" height="16" fill="#E0F2FE" />
    <text x="875" y="199" font-size="13" font-weight="800" fill="#0369A1" text-anchor="middle">PHYSICAL RUN CHAIN (J2 DAISY CHAIN — UART2 @ 115200, CRC-8 Poly 0x07)</text>

    <!-- J2 Wires from Master (x=452) to Action Block #1 (x=545) -->
    <path d="M 452 388 L 545 388" fill="none" stroke="#E17055" stroke-width="2.5" marker-end="url(#arrow-power)" />
    <rect x="478" y="369" width="56" height="15" rx="4" fill="#FFFFFF" />
    <text x="506" y="380" font-size="9.5" font-weight="700" fill="#C2410C" text-anchor="middle">+3V3/GND</text>
    <path d="M 452 419 L 545 419" fill="none" stroke="#0984E3" stroke-width="2.8" marker-end="url(#arrow-blue)" />
    <rect x="477" y="400" width="58" height="15" rx="4" fill="#FFFFFF" />
    <text x="506" y="411" font-size="9.5" font-weight="700" fill="#0369A1" text-anchor="middle">0xAA / 0xBB</text>
    <path d="M 545 464 L 452 464" fill="none" stroke="#00B894" stroke-width="2.8" marker-end="url(#arrow-green)" />
    <rect x="478" y="445" width="56" height="15" rx="4" fill="#FFFFFF" />
    <text x="506" y="456" font-size="9.5" font-weight="700" fill="#047857" text-anchor="middle">0xAA Loop</text>

    <!-- Action Block #1..#N -->
    <g id="action-block-node" filter="url(#shadow)">
      <rect x="545" y="226" width="300" height="296" rx="14" fill="#F5F3FF" stroke="#5B21B6" stroke-width="2.2" />
      <rect x="545" y="226" width="300" height="42" rx="14" fill="#A29BFE" />
      <rect x="545" y="252" width="300" height="16" fill="#A29BFE" />
      <text x="695" y="246" font-size="13.5" font-weight="800" fill="#1E293B" text-anchor="middle">ACTION BLOCK #1 .. #N</text>
      <text x="695" y="262" font-size="10.5" font-weight="600" fill="#312E81" text-anchor="middle">32x32mm Unified PCB (CH32V003F4P6 @ 24MHz)</text>

      <text x="558" y="286" font-size="10.8" font-weight="600" fill="#1E293B">• IN (PD6 RX) -&gt; Append [Act, Par] -&gt; OUT (PD5 TX)</text>
      <text x="558" y="305" font-size="10.8" font-weight="600" fill="#1E293B">• NVMEM Flash 0x08003FC0 (64B Action+Param)</text>
      <text x="558" y="324" font-size="10.8" font-weight="600" fill="#1E293B">• PA2 -&gt; WS2812B RGB (Amber / Green / Rainbow)</text>
      <text x="558" y="343" font-size="10.8" font-weight="600" fill="#1E293B">• PD4/PC0 Heartbeat | PROG (GND/3V3/SWIO PD1)</text>
      <text x="558" y="362" font-size="10.8" font-weight="600" fill="#1E293B">• Forwards 0xBB step/complete PD6 -&gt; PD5</text>

      <line x1="560" y1="373" x2="830" y2="373" stroke="#DDD6FE" stroke-width="1.5" />
      <line x1="545" y1="388" x2="845" y2="388" stroke="#E17055" stroke-width="2" stroke-dasharray="4,3" />
      <text x="695" y="384" font-size="10" font-weight="700" fill="#C2410C" text-anchor="middle">Pin 1 (+3V3) &amp; Pin 2 (GND) Pass-Through</text>

      <line x1="545" y1="419" x2="635" y2="419" stroke="#0984E3" stroke-width="2" />
      <line x1="755" y1="419" x2="845" y2="419" stroke="#0984E3" stroke-width="2" />
      <rect x="635" y="404" width="120" height="30" rx="6" fill="#DBEAFE" stroke="#0284C7" stroke-width="1.5" />
      <text x="695" y="423" font-size="10.5" font-weight="800" fill="#0369A1" text-anchor="middle">PD6 -&gt; MCU -&gt; PD5</text>

      <line x1="545" y1="464" x2="845" y2="464" stroke="#00B894" stroke-width="2.8" />
      <rect x="605" y="472" width="180" height="38" rx="6" fill="#ECFDF5" stroke="#059669" stroke-width="1.2" />
      <text x="695" y="488" font-size="10" font-weight="800" fill="#047857" text-anchor="middle">Pin 4 RETURN_BUS (PD0 Hi-Z)</text>
      <text x="695" y="502" font-size="9.5" font-weight="600" fill="#065F46" text-anchor="middle">Straight-Through Return Rail</text>
    </g>

    <!-- Daisy Chain Wires Between Action Block and Smart End Block -->
    <path d="M 845 388 L 920 388" fill="none" stroke="#E17055" stroke-width="2.5" marker-end="url(#arrow-power)" />
    <text x="882" y="381" font-size="10" font-weight="700" fill="#C2410C" text-anchor="middle">+3V3/GND</text>
    <path d="M 845 419 L 920 419" fill="none" stroke="#0984E3" stroke-width="2.8" marker-end="url(#arrow-blue)" />
    <text x="882" y="411" font-size="10" font-weight="700" fill="#0369A1" text-anchor="middle">0xAA+2N</text>
    <path d="M 920 464 L 845 464" fill="none" stroke="#00B894" stroke-width="2.8" marker-end="url(#arrow-green)" />
    <text x="882" y="456" font-size="10" font-weight="700" fill="#047857" text-anchor="middle">Return Bus</text>

    <!-- Smart End Block -->
    <g id="end-block-node" filter="url(#shadow)">
      <rect x="920" y="226" width="290" height="296" rx="14" fill="#ECFDF5" stroke="#059669" stroke-width="2.2" />
      <rect x="920" y="226" width="290" height="42" rx="14" fill="#55E6C1" />
      <rect x="920" y="252" width="290" height="16" fill="#55E6C1" />
      <text x="1065" y="246" font-size="13.5" font-weight="800" fill="#064E3B" text-anchor="middle">SMART END BLOCK (0xEE)</text>
      <text x="1065" y="262" font-size="10.5" font-weight="600" fill="#065F46" text-anchor="middle">Same 32x32mm PCB or ch32v003_end_block</text>

      <text x="934" y="288" font-size="11" font-weight="600" fill="#1E293B">• Receives final 0xAA frame on PD6 (IN Pin 3)</text>
      <text x="934" y="308" font-size="11" font-weight="600" fill="#1E293B">• Validates CRC-8 (Poly 0x07) &amp; 0x55 footer</text>
      <text x="934" y="328" font-size="11" font-weight="600" fill="#1E293B">• Bridges 0xAA onto Pin 4 RETURN_BUS:</text>
      <text x="944" y="346" font-size="10.5" font-weight="600" fill="#047857">PD0 SW TX (Unified FW) / PD5 (End FW)</text>
      <text x="934" y="366" font-size="11" font-weight="600" fill="#1E293B">• Glows green; mirrors 0xBB rainbow end</text>

      <line x1="934" y1="376" x2="1196" y2="376" stroke="#A7F3D0" stroke-width="1.5" />
      <path d="M 920 419 L 1065 419 L 1065 464 L 920 464" fill="none" stroke="#00B894" stroke-width="3" marker-end="url(#arrow-green)" />
      <rect x="975" y="427" width="185" height="30" rx="6" fill="#FFFFFF" stroke="#059669" stroke-width="1.5" />
      <text x="1067" y="446" font-size="10.5" font-weight="800" fill="#047857" text-anchor="middle">Verify CRC-8 &amp; Loopback</text>
      <text x="1065" y="492" font-size="10.5" font-weight="700" fill="#065F46" text-anchor="middle">No manual terminator cap needed</text>
      <text x="1065" y="507" font-size="10" font-weight="500" fill="#065F46" text-anchor="middle">(Configured via 0xEE in Config Dock)</text>
    </g>
  </g>

  <!-- ==================== CENTER LOWER: CONFIG DOCK MODE (J1) ==================== -->
  <g id="config-dock-region">
    <rect x="520" y="562" width="710" height="388" rx="18" fill="#FFFFFF" stroke="#DDD6FE" stroke-width="2" filter="url(#shadow)" />
    <rect x="520" y="562" width="710" height="36" rx="18" fill="#F3E8FF" />
    <rect x="520" y="582" width="710" height="16" fill="#F3E8FF" />
    <text x="875" y="586" font-size="13" font-weight="800" fill="#5B21B6" text-anchor="middle">CONFIG DOCK MODE (J1 PORT — AUTO-DIRECTIONAL 0xCF PROTOCOL @ 115200)</text>

    <!-- J1 Wires from Master (x=452) to Docked Block (x=570) -->
    <path d="M 452 831 L 570 831" fill="none" stroke="#E17055" stroke-width="2.5" marker-end="url(#arrow-power)" />
    <rect x="491" y="812" width="58" height="15" rx="4" fill="#FFFFFF" />
    <text x="520" y="823" font-size="9.5" font-weight="700" fill="#C2410C" text-anchor="middle">+3V3/GND</text>
    <path d="M 452 866 L 570 866" fill="none" stroke="#6C5CE7" stroke-width="2.8" marker-start="url(#arrow-purple)" marker-end="url(#arrow-purple)" />
    <rect x="485" y="846" width="70" height="15" rx="4" fill="#FFFFFF" />
    <text x="520" y="857" font-size="9.5" font-weight="700" fill="#5B21B6" text-anchor="middle">0xCF (Bi-Dir)</text>

    <!-- Single Docked Action or End Block -->
    <g id="docked-block-node" filter="url(#shadow)">
      <rect x="570" y="616" width="635" height="314" rx="16" fill="#FAF5FF" stroke="#6D28D9" stroke-width="2.2" />
      <rect x="570" y="616" width="635" height="40" rx="16" fill="#6C5CE7" />
      <rect x="570" y="640" width="635" height="16" fill="#6C5CE7" />
      <text x="887" y="642" font-size="14" font-weight="800" fill="#FFFFFF" text-anchor="middle">SINGLE DOCKED ACTION OR END BLOCK (Unified CH32V003F4P6)</text>

      <!-- Left Panel inside Docked Block -->
      <rect x="590" y="672" width="288" height="140" rx="10" fill="#FFFFFF" stroke="#C4B5FD" stroke-width="1.5" />
      <text x="734" y="694" font-size="12.5" font-weight="800" fill="#4C1D95" text-anchor="middle">Auto-Direction &amp; Read-Sync</text>
      <text x="604" y="716" font-size="11" font-weight="600" fill="#1E293B">• probeConfigDockElectrical() @ 250ms</text>
      <text x="604" y="736" font-size="11" font-weight="600" fill="#1E293B">• Query: [0xCF, 0x01, 0x07, 0x55]</text>
      <text x="604" y="756" font-size="11" font-weight="600" fill="#1E293B">• Reply: [0xCF, 0x81, Act, Par, CRC, 0x55]</text>
      <text x="604" y="776" font-size="11" font-weight="600" fill="#1E293B">• Works plugged via IN (PD6/PD5) OR</text>
      <text x="612" y="794" font-size="11" font-weight="600" fill="#1E293B">OUT (PD0 SW bit-bang UART)</text>

      <!-- Right Panel inside Docked Block -->
      <rect x="898" y="672" width="287" height="140" rx="10" fill="#FFFFFF" stroke="#C4B5FD" stroke-width="1.5" />
      <text x="1041" y="694" font-size="12.5" font-weight="800" fill="#4C1D95" text-anchor="middle">Write, Flash &amp; Verify ACK</text>
      <text x="912" y="716" font-size="11" font-weight="600" fill="#1E293B">• Start (SW3): [0xCF, 0x02, Act, Par, CRC, 0x55]</text>
      <text x="912" y="736" font-size="11" font-weight="600" fill="#1E293B">• Erases &amp; writes 64B Page 0x08003FC0</text>
      <text x="912" y="756" font-size="11" font-weight="600" fill="#1E293B">• PA2 WS2812B Emerald (0,255,40) 400ms</text>
      <text x="912" y="776" font-size="11" font-weight="600" fill="#1E293B">• 4B ACK: [0xCF, 0x06, CRC=0x12, 0x55]</text>
      <text x="912" y="794" font-size="11" font-weight="600" fill="#5B21B6">• Act=0xEE marks block as Smart End</text>

      <!-- Bottom Dock Interface Strip -->
      <rect x="590" y="824" width="595" height="90" rx="10" fill="#EDE9FE" stroke="#8B5CF6" stroke-width="1.5" />
      <text x="887" y="846" font-size="12" font-weight="800" fill="#4C1D95" text-anchor="middle">Physical Dock Mapping: GPIO 17 / GPIO 18 &lt;-&gt; Block PD6 (UART1) or PD0 (SW UART)</text>
      <text x="887" y="868" font-size="11" font-weight="600" fill="#312E81" text-anchor="middle">Bad CRC-8 or 0x55 footer is silently dropped; Master verifies save with immediate 0xCF 0x01 readback</text>
      <text x="887" y="890" font-size="11" font-weight="600" fill="#312E81" text-anchor="middle">Knob 2 SW (GPIO 13) resets param to min; Red Stop (SW5, GPIO 2) reverts unsaved edit to docked value</text>
    </g>
  </g>

  <!-- ==================== RIGHT: ROBOSEN K1 ROBOT & HOST SOFTWARE ==================== -->
  <!-- 1. Robosen K1 Robot -->
  <g id="robosen-k1" filter="url(#shadow)">
    <rect x="1270" y="175" width="370" height="430" rx="18" fill="#FFFFFF" stroke="#059669" stroke-width="2.5" />
    <rect x="1270" y="175" width="370" height="46" rx="18" fill="#00B894" />
    <rect x="1270" y="203" width="370" height="18" fill="#00B894" />
    <text x="1455" y="198" font-size="15.5" font-weight="800" fill="#FFFFFF" text-anchor="middle">ROBOSEN K1 ROBOT (BLE Peripheral)</text>
    <text x="1455" y="214" font-size="11" font-weight="600" fill="#D1FAE5" text-anchor="middle">17 Smart Servos, IMU &amp; Integrated Audio</text>

    <rect x="1288" y="234" width="334" height="72" rx="10" fill="#ECFDF5" stroke="#10B981" stroke-width="1.5" />
    <text x="1455" y="255" font-size="12" font-weight="800" fill="#065F46" text-anchor="middle">BLE GATT Wire Protocol (0xFFE0 / 0xFFE1)</text>
    <text x="1455" y="275" font-size="11" font-weight="700" fill="#047857" text-anchor="middle">[0xFF, 0xFF, Len, Opcode, Payload..., Sum]</text>
    <text x="1455" y="294" font-size="10.5" font-weight="500" fill="#064E3B" text-anchor="middle">Packetized BLE Write TX &amp; Notify RX Stream</text>

    <rect x="1288" y="320" width="334" height="156" rx="10" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.5" />
    <text x="1455" y="341" font-size="12" font-weight="800" fill="#1E293B" text-anchor="middle">Hardware Motion &amp; Opcodes</text>
    <text x="1302" y="363" font-size="11" font-weight="600" fill="#334155">• Walk / Turn: 0x01 / 0x05 / 0x08 / 0x02 / 0x07 / 0x03</text>
    <text x="1302" y="383" font-size="11" font-weight="600" fill="#334155">• Predefined Stunts: Opcode 0x17 (10 Stunt Strings)</text>
    <text x="1302" y="403" font-size="11" font-weight="600" fill="#334155">• Emergency Stop: 0x0C ([FF FF 02 0C 0E])</text>
    <text x="1302" y="423" font-size="11" font-weight="600" fill="#334155">• 17-Joint Direct Servo Angles (ALL_JOINTS)</text>
    <text x="1302" y="443" font-size="11" font-weight="600" fill="#334155">• Joint Angle Read/Move (0xE9/0xE8) &amp; Lock Ctrl</text>
    <text x="1302" y="463" font-size="11" font-weight="600" fill="#334155">• Power-on BLE Auto-Discovery + NVS MAC Cache</text>

    <rect x="1288" y="490" width="334" height="98" rx="10" fill="#FEF3C7" stroke="#F59E0B" stroke-width="1.5" />
    <text x="1455" y="511" font-size="12" font-weight="800" fill="#92400E" text-anchor="middle">ESP32-S3 Direct Robot Modes</text>
    <text x="1302" y="532" font-size="11" font-weight="600" fill="#78350F">• Mode 1B: Tangible Physical Block Chain Runner</text>
    <text x="1302" y="551" font-size="11" font-weight="600" fill="#78350F">• Mode 2: Dual-Pedal RC Drive &amp; 10-Stunt Control</text>
    <text x="1302" y="570" font-size="11" font-weight="600" fill="#78350F">• Mode 3: Individual 17-Joint Servo Adjuster</text>
  </g>

  <!-- 2. Host Tools, SDK & SWIO Programmers -->
  <g id="host-tools" filter="url(#shadow)">
    <rect x="1270" y="625" width="370" height="325" rx="18" fill="#FFFFFF" stroke="#64748B" stroke-width="2" />
    <rect x="1270" y="625" width="370" height="40" rx="18" fill="#334155" />
    <rect x="1270" y="649" width="370" height="16" fill="#334155" />
    <text x="1455" y="651" font-size="14" font-weight="800" fill="#FFFFFF" text-anchor="middle">HOST BLE TOOLS, SDK &amp; PROGRAMMERS</text>

    <text x="1288" y="688" font-size="12" font-weight="800" fill="#0369A1">1. Python BLE Suite (scripts/, Bleak)</text>
    <text x="1296" y="707" font-size="11" font-weight="600" fill="#334155">• k1_ble_daemon.py (0x64 100% ACK &amp; 0xE9 telemetry)</text>
    <text x="1296" y="725" font-size="11" font-weight="600" fill="#334155">• k1_action.py, k1_joint_controller.py, k1_ble_tester.py</text>

    <line x1="1288" y1="740" x2="1622" y2="740" stroke="#E2E8F0" stroke-width="1.5" />
    <text x="1288" y="762" font-size="12" font-weight="800" fill="#4F46E5">2. Node.js RobosenJS SDK (src/, bin/)</text>
    <text x="1296" y="781" font-size="11" font-weight="600" fill="#334155">• src/Robot.js, src/K1.js (BLE action, joint &amp; LLM API)</text>
    <text x="1296" y="799" font-size="11" font-weight="600" fill="#334155">• bin/k1.js CLI (repl, control, run, prompt, voice)</text>

    <line x1="1288" y1="814" x2="1622" y2="814" stroke="#E2E8F0" stroke-width="1.5" />
    <text x="1288" y="836" font-size="11.5" font-weight="800" fill="#047857">3. CH32V003 SWIO Tools (firmware/tools_programmer/)</text>
    <text x="1296" y="855" font-size="11" font-weight="600" fill="#334155">• esp32_ch32v003_programmer (SWIO -&gt; PD1)</text>
    <text x="1296" y="873" font-size="11" font-weight="600" fill="#334155">• arduino_uno_ch32v003_programmer (SWIO -&gt; PD1)</text>
    <text x="1296" y="895" font-size="10.5" font-weight="500" fill="#64748B">Flashes unified Action/End firmware via 3-pin PROG</text>
    <text x="1296" y="913" font-size="10.5" font-weight="500" fill="#64748B">header (GND, +3V3, SWIO PD1) &amp; resets NVMEM</text>
  </g>

  <!-- ==================== FOOTER LEGEND BAR ==================== -->
  <g transform="translate(40, 968)">
    <rect x="0" y="0" width="1600" height="52" rx="12" fill="#FFFFFF" stroke="#DFE6E9" stroke-width="1.5" />
    <text x="28" y="31" font-size="13.5" font-weight="800" fill="#2D3436">BUSES:</text>

    <line x1="105" y1="26" x2="145" y2="26" stroke="#E17055" stroke-width="3" />
    <text x="155" y="31" font-size="12.5" font-weight="600" fill="#475569">+3V3 / GND Pogo Power</text>

    <line x1="340" y1="26" x2="380" y2="26" stroke="#0984E3" stroke-width="3" />
    <text x="390" y="31" font-size="12.5" font-weight="600" fill="#475569">Pin 3 Forward TX (0xAA / 0xBB)</text>

    <line x1="635" y1="26" x2="675" y2="26" stroke="#00B894" stroke-width="3" />
    <text x="685" y="31" font-size="12.5" font-weight="600" fill="#475569">Pin 4 Return Bus (End -&gt; Master 0xAA)</text>

    <line x1="970" y1="26" x2="1010" y2="26" stroke="#6C5CE7" stroke-width="3" />
    <text x="1020" y="31" font-size="12.5" font-weight="600" fill="#475569">J1 Config Dock (0xCF Bi-Dir)</text>

    <line x1="1255" y1="26" x2="1295" y2="26" stroke="#0984E3" stroke-width="3" stroke-dasharray="7,4" />
    <text x="1305" y="31" font-size="12.5" font-weight="600" fill="#475569">BLE 5.0 Wireless (0xFFE0/0xFFE1)</text>
  </g>
</svg>
'''


def find_browser():
    for candidate in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ):
        if candidate and os.path.exists(candidate):
            return candidate
    raise RuntimeError("No headless Chromium/Chrome/Edge browser found")


repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out_dir = os.path.join(repo_root, 'docs', 'diagrams')
os.makedirs(out_dir, exist_ok=True)
png_path = os.path.join(out_dir, 'robosen_system_block_diagram.png')

with tempfile.NamedTemporaryFile('w', suffix='.svg', encoding='utf-8', delete=False) as tmp:
    tmp.write(svg_content)
    tmp_svg = tmp.name

try:
    browser = find_browser()
    subprocess.run(
        [
            browser,
            '--headless',
            '--disable-gpu',
            '--window-size=1680,1040',
            f'--screenshot={png_path}',
            f'file://{tmp_svg}',
        ],
        check=True,
    )
    print(f'PNG successfully generated at: {png_path}')
finally:
    if os.path.exists(tmp_svg):
        os.remove(tmp_svg)
