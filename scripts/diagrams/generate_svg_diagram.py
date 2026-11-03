import os

svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1620 1380" width="100%" height="100%" style="background-color: #F8F9FA; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Shadow Filter -->
    <filter id="shadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="4" stdDeviation="4" flood-color="#000000" flood-opacity="0.08" />
    </filter>
    <filter id="shadow-hover" x="-15%" y="-15%" width="135%" height="135%">
      <feDropShadow dx="3" dy="6" stdDeviation="6" flood-color="#000000" flood-opacity="0.12" />
    </filter>
    
    <!-- Arrowhead Marker -->
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2D3436" />
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0984E3" />
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D63031" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#00B894" />
    </marker>
  </defs>

  <!-- Title Header Bar -->
  <rect x="40" y="30" width="1540" height="80" rx="16" fill="#FFFFFF" stroke="#DFE6E9" stroke-width="1.5" filter="url(#shadow)" />
  <text x="70" y="78" font-size="24" font-weight="800" fill="#2D3436">Robosen Tangible Coding Block System</text>
  <text x="560" y="78" font-size="18" font-weight="500" fill="#636E72">|  Data Flow, Hardware Devices &amp; Protocol Communication</text>
  
  <rect x="1380" y="50" width="170" height="40" rx="20" fill="#6C5CE7" />
  <text x="1465" y="76" font-size="14" font-weight="700" fill="#FFFFFF" text-anchor="middle">2-Phase CRC-8</text>

  <!-- ==================== COLUMN 1: DISCOVERY & COMPILATION (PHASE 1) ==================== -->
  
  <!-- 1. START (Gold/Yellow) -->
  <g id="node-start" filter="url(#shadow)">
    <rect x="70" y="160" width="300" height="85" rx="20" fill="#FFD32A" stroke="#2D3436" stroke-width="2.5" />
    <text x="220" y="198" font-size="18" font-weight="800" fill="#2D3436" text-anchor="middle">START CODING</text>
    <text x="220" y="224" font-size="13" font-weight="600" fill="#2D3436" text-anchor="middle">Child Snaps Blocks &amp; Hits Start Button</text>
  </g>

  <!-- Path Start -> Emit Seed -->
  <path d="M 220 245 L 220 295" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 2. Master Emits Seed (Lavender) -->
  <g id="node-seed" filter="url(#shadow)">
    <rect x="60" y="295" width="320" height="105" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="220" y="325" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (ESP32-S3)</text>
    <text x="220" y="350" font-size="16" font-weight="700" fill="#2D3436" text-anchor="middle">Emits Phase 1 Discovery Seed</text>
    <text x="220" y="373" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Pin 3 TX: [0xAA, Len=0, Count=0, 0x55]</text>
    <text x="220" y="391" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">Starts cascading discovery wave</text>
  </g>

  <!-- Path Emit Seed -> Block Loop -->
  <path d="M 220 400 L 220 440" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 3. Action Block Processing (Lavender) -->
  <g id="node-block-proc" filter="url(#shadow)">
    <rect x="50" y="440" width="340" height="135" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="220" y="470" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">ACTION BLOCK (CH32V003)</text>
    <text x="220" y="495" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Append Action &amp; Increment Index</text>
    <text x="220" y="520" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">1. Sets MyIndex = Count + 1</text>
    <text x="220" y="540" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">2. Reads [ActionID, Param] from Flash</text>
    <text x="220" y="560" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">3. Appends 2B, Updates Count &amp; CRC-8</text>
  </g>

  <!-- Path Block Processing -> Next Block Check -->
  <path d="M 220 575 L 220 615" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 4. Next Block Check (Diamond - Sky Blue) -->
  <g id="node-is-next-block" filter="url(#shadow)">
    <polygon points="220,615 325,690 220,765 115,690" fill="#74B9FF" stroke="#2D3436" stroke-width="2.5" />
    <text x="220" y="675" font-size="11" font-weight="800" fill="#2D3436" text-anchor="middle">PIN 3 TX/RX BUS</text>
    <text x="220" y="695" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">More Action</text>
    <text x="220" y="715" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Blocks?</text>
  </g>

  <!-- Path Next Block? YES (Loopback left) -->
  <path d="M 115 690 L 25 690 L 25 507 L 50 507" fill="none" stroke="#2D3436" stroke-width="2" marker-end="url(#arrow)" />
  <rect x="30" y="590" width="55" height="24" rx="6" fill="#FFFFFF" stroke="#2D3436" stroke-width="1.5" />
  <text x="57" y="607" font-size="12" font-weight="800" fill="#0984E3" text-anchor="middle">YES</text>

  <!-- Path Next Block? NO (To End Block) -->
  <path d="M 220 765 L 220 810" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />
  <rect x="230" y="777" width="50" height="24" rx="6" fill="#FFFFFF" stroke="#2D3436" stroke-width="1.5" />
  <text x="255" y="794" font-size="12" font-weight="800" fill="#2D3436" text-anchor="middle">NO</text>

  <!-- 5. End Block Terminator (Lavender) -->
  <g id="node-endblock" filter="url(#shadow)">
    <rect x="50" y="810" width="340" height="115" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="220" y="840" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">SMART END BLOCK (CH32V003)</text>
    <text x="220" y="865" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Validate CRC-8 &amp; Loopback</text>
    <text x="220" y="890" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Calculates cumulative polynomial checksum</text>
    <text x="220" y="910" font-size="12" font-weight="500" fill="#2D3436" text-anchor="middle">Loops verified data to Pin 4 Return Rail</text>
  </g>

  <!-- Path End Block -> CRC Valid Diamond -->
  <path d="M 220 925 L 220 965" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 6. CRC-8 Valid Check (Diamond - Sky Blue) -->
  <g id="node-crc-check" filter="url(#shadow)">
    <polygon points="220,965 330,1040 220,1115 110,1040" fill="#74B9FF" stroke="#2D3436" stroke-width="2.5" />
    <text x="220" y="1025" font-size="11" font-weight="800" fill="#2D3436" text-anchor="middle">CHECKSUM</text>
    <text x="220" y="1045" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">CRC-8</text>
    <text x="220" y="1065" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Valid?</text>
  </g>

  <!-- Path CRC Valid? NO (Error State) -->
  <path d="M 110 1040 L 25 1040 L 25 1205 L 60 1205" fill="none" stroke="#D63031" stroke-width="2" marker-end="url(#arrow-red)" />
  <rect x="30" y="1110" width="55" height="24" rx="6" fill="#FFFFFF" stroke="#D63031" stroke-width="1.5" />
  <text x="57" y="1127" font-size="12" font-weight="800" fill="#D63031" text-anchor="middle">FAIL</text>

  <!-- Error Node (Soft Pink) -->
  <g id="node-error" filter="url(#shadow)">
    <rect x="60" y="1165" width="320" height="85" rx="16" fill="#FF7675" stroke="#2D3436" stroke-width="2.5" />
    <text x="220" y="1195" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER &amp; ACTION BLOCKS</text>
    <text x="220" y="1220" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Hardware Error / Broken Chain</text>
    <text x="220" y="1240" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Double Red Flash / Check Contacts</text>
  </g>

  <!-- Path CRC Valid? YES -> Master Compilation (Column 2) -->
  <path d="M 330 1040 L 560 1040 L 560 207 L 620 207" fill="none" stroke="#00B894" stroke-width="2.5" marker-end="url(#arrow-green)" />
  <rect x="415" y="1020" width="65" height="24" rx="6" fill="#FFFFFF" stroke="#00B894" stroke-width="1.5" />
  <text x="447" y="1037" font-size="12" font-weight="800" fill="#00B894" text-anchor="middle">VALID</text>


  <!-- ==================== COLUMN 2: EXECUTION & STEP TRACKING (PHASE 2) ==================== -->

  <!-- 7. Master Compiles Queue (Lavender) -->
  <g id="node-master-compile" filter="url(#shadow)">
    <rect x="620" y="160" width="340" height="95" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="790" y="190" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (ESP32-S3)</text>
    <text x="790" y="215" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Compile Sequence Queue</text>
    <text x="790" y="238" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Receives payload via Pin 4 Return Bus</text>
    <text x="790" y="254" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">Builds Non-Blocking Plan (Steps 1..N)</text>
  </g>

  <!-- Path Master Compile -> Step Loop Start -->
  <path d="M 790 255 L 790 295" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 8. Broadcast Active Step (Lavender) -->
  <g id="node-broadcast-step" filter="url(#shadow)">
    <rect x="610" y="295" width="360" height="105" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="790" y="325" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (ESP32-S3)</text>
    <text x="790" y="350" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Phase 2: Broadcast Active Step</text>
    <text x="790" y="373" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Pin 4 Bus: [0xBB, ActiveStep = i, Total = N, CRC]</text>
    <text x="790" y="391" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">All blocks listen concurrently in High-Z mode</text>
  </g>

  <!-- Path Broadcast Step -> LED Sync -->
  <path d="M 790 400 L 790 440" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 9. Visual Step Sync (Lavender) -->
  <g id="node-led-sync" filter="url(#shadow)">
    <rect x="610" y="440" width="360" height="105" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="790" y="470" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">ALL ACTION BLOCKS (WS2812B)</text>
    <text x="790" y="495" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Real-Time LED Step Tracking</text>
    <text x="790" y="520" font-size="13" font-weight="700" fill="#00B894" text-anchor="middle">Block (MyIndex == i) -&gt; PULSING GREEN (100%)</text>
    <text x="790" y="538" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">Other blocks remain dim in action mode color</text>
  </g>

  <!-- Path LED Sync -> BLE Command -->
  <path d="M 790 545 L 790 585" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 10. Send BLE Command (Lavender) -->
  <g id="node-send-ble" filter="url(#shadow)">
    <rect x="610" y="585" width="360" height="105" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="790" y="615" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (ESP32-S3 BLE)</text>
    <text x="790" y="640" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Dispatch Wireless BLE Command</text>
    <text x="790" y="663" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">BLE Char 0xFFE1 (Service 0xFFE0)</text>
    <text x="790" y="681" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">• Locomotion (0x01..0x08)  • Actions (0x17)</text>
  </g>

  <!-- Path Send BLE -> Robot Movement Exec -->
  <path d="M 790 690 L 790 730" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 11. Robot Motion Execution (Lavender) -->
  <g id="node-robot-exec" filter="url(#shadow)">
    <rect x="610" y="730" width="360" height="105" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="790" y="760" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">ROBOSEN K1 ROBOT (17 SERVOS)</text>
    <text x="790" y="785" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Physical Motion Execution</text>
    <text x="790" y="808" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">17 High-Precision Servos execute motion</text>
    <text x="790" y="826" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">Streams real-time action progress bytes</text>
  </g>

  <!-- Path Robot Exec -> ACK Check -->
  <path d="M 790 835 L 790 875" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 12. 100% Progress ACK Check (Diamond - Sky Blue) -->
  <g id="node-ack-check" filter="url(#shadow)">
    <polygon points="790,875 905,950 790,1025 675,950" fill="#74B9FF" stroke="#2D3436" stroke-width="2.5" />
    <text x="790" y="935" font-size="11" font-weight="800" fill="#2D3436" text-anchor="middle">BLE TELEMETRY</text>
    <text x="790" y="955" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">100% ACK</text>
    <text x="790" y="975" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">(0x64)?</text>
  </g>

  <!-- Path ACK Check? NO (Wait / Stream) -->
  <path d="M 675 950 L 590 950 L 590 782 L 610 782" fill="none" stroke="#2D3436" stroke-width="2" marker-end="url(#arrow)" />
  <rect x="595" y="855" width="65" height="24" rx="6" fill="#FFFFFF" stroke="#2D3436" stroke-width="1.5" />
  <text x="627" y="872" font-size="11" font-weight="700" fill="#636E72" text-anchor="middle">RUNNING</text>

  <!-- Path ACK Check? YES -> More Steps Check -->
  <path d="M 790 1025 L 790 1070" fill="none" stroke="#00B894" stroke-width="2.5" marker-end="url(#arrow-green)" />
  <rect x="800" y="1037" width="55" height="24" rx="6" fill="#FFFFFF" stroke="#00B894" stroke-width="1.5" />
  <text x="827" y="1054" font-size="12" font-weight="800" fill="#00B894" text-anchor="middle">DONE</text>

  <!-- 13. More Steps in Queue Check (Diamond - Sky Blue) -->
  <g id="node-more-steps" filter="url(#shadow)">
    <polygon points="790,1070 905,1145 790,1220 675,1145" fill="#74B9FF" stroke="#2D3436" stroke-width="2.5" />
    <text x="790" y="1130" font-size="11" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER QUEUE</text>
    <text x="790" y="1150" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">More Steps</text>
    <text x="790" y="1170" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">(i &lt; N)?</text>
  </g>

  <!-- Path More Steps? YES (Loop back to Step i+1) -->
  <path d="M 675 1145 L 530 1145 L 530 347 L 610 347" fill="none" stroke="#0984E3" stroke-width="2.5" marker-end="url(#arrow-blue)" />
  <rect x="535" y="730" width="65" height="24" rx="6" fill="#FFFFFF" stroke="#0984E3" stroke-width="1.5" />
  <text x="567" y="747" font-size="12" font-weight="800" fill="#0984E3" text-anchor="middle">YES (i++)</text>

  <!-- Path More Steps? NO -> Victory Column (Column 3) -->
  <path d="M 905 1145 L 1150 1145 L 1150 207 L 1210 207" fill="none" stroke="#00B894" stroke-width="2.5" marker-end="url(#arrow-green)" />
  <rect x="1005" y="1125" width="85" height="24" rx="6" fill="#FFFFFF" stroke="#00B894" stroke-width="1.5" />
  <text x="1047" y="1142" font-size="12" font-weight="800" fill="#00B894" text-anchor="middle">ALL DONE</text>


  <!-- ==================== COLUMN 3: MISSION COMPLETE & IDLE ==================== -->

  <!-- 14. Mission Complete & UI Update (Lavender) -->
  <g id="node-mission-complete" filter="url(#shadow)">
    <rect x="1210" y="160" width="340" height="105" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="1380" y="190" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (E-INK)</text>
    <text x="1380" y="215" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Sequence Completed</text>
    <text x="1380" y="238" font-size="13" font-weight="700" fill="#6C5CE7" text-anchor="middle">Master E-Ink: 'MISSION COMPLETE 🎉'</text>
    <text x="1380" y="256" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">All execution queue steps verified</text>
  </g>

  <!-- Path Mission Complete -> Robot Safe Stand -->
  <path d="M 1380 265 L 1380 305" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 15. Robot Safe Stand (Lavender) -->
  <g id="node-safe-stand" filter="url(#shadow)">
    <rect x="1210" y="305" width="340" height="105" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="1380" y="335" font-size="13" font-weight="800" fill="#2D3436" text-anchor="middle">ROBOSEN K1 ROBOT (IMU)</text>
    <text x="1380" y="360" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Safe Standing Posture &amp; Idle</text>
    <text x="1380" y="383" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Master sends Stop (0x0C) / Auto-Balance</text>
    <text x="1380" y="401" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">Robot holds stable standing posture</text>
  </g>

  <!-- Path Stand -> END -->
  <path d="M 1380 410 L 1380 455" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 16. END (Gold/Yellow) -->
  <g id="node-end" filter="url(#shadow)">
    <rect x="1240" y="455" width="280" height="85" rx="20" fill="#FFD32A" stroke="#2D3436" stroke-width="2.5" />
    <text x="1380" y="495" font-size="18" font-weight="800" fill="#2D3436" text-anchor="middle">READY FOR NEXT RUN</text>
    <text x="1380" y="520" font-size="13" font-weight="600" fill="#2D3436" text-anchor="middle">Screenless Tangible Coding Loop</text>
  </g>

  <!-- Footer Legend Bar -->
  <g transform="translate(40, 1280)">
    <rect x="0" y="0" width="1540" height="60" rx="12" fill="#FFFFFF" stroke="#DFE6E9" stroke-width="1.5" />
    <text x="30" y="35" font-size="14" font-weight="700" fill="#2D3436">LEGEND:</text>
    
    <rect x="110" y="20" width="20" height="20" rx="6" fill="#FFD32A" stroke="#2D3436" stroke-width="1.5" />
    <text x="140" y="35" font-size="13" font-weight="600" fill="#636E72">Terminal (Start / End)</text>
    
    <rect x="330" y="20" width="20" height="20" rx="6" fill="#A29BFE" stroke="#2D3436" stroke-width="1.5" />
    <text x="360" y="35" font-size="13" font-weight="600" fill="#636E72">Process &amp; Hardware Action</text>
    
    <polygon points="590,20 600,30 590,40 580,30" fill="#74B9FF" stroke="#2D3436" stroke-width="1.5" />
    <text x="610" y="35" font-size="13" font-weight="600" fill="#636E72">Conditional Logic / Checksum</text>

    <rect x="860" y="20" width="20" height="20" rx="6" fill="#FF7675" stroke="#2D3436" stroke-width="1.5" />
    <text x="890" y="35" font-size="13" font-weight="600" fill="#636E72">Fault / Error Branch</text>
  </g>
</svg>'''

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(base_dir, 'docs', 'diagrams')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'robosen_coding_data_flow.svg')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(svg_content)
print(f'SVG successfully generated at: {out_path}')
