import os

svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1680 1440" width="100%" height="100%" style="background-color: #F8F9FA; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <filter id="shadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="2" dy="4" stdDeviation="4" flood-color="#000000" flood-opacity="0.08" />
    </filter>
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
  <rect x="40" y="25" width="1600" height="80" rx="16" fill="#FFFFFF" stroke="#DFE6E9" stroke-width="1.5" filter="url(#shadow)" />
  <text x="70" y="64" font-size="23" font-weight="800" fill="#2D3436">Robosen Tangible Coding Block System — Run Chain Execution Flow</text>
  <text x="70" y="89" font-size="14" font-weight="500" fill="#636E72">Verified against firmware/esp32_master/esp32_master.ino, ch32v003_action_block/main.c &amp; ch32v003_end_block/main.c</text>

  <rect x="1395" y="45" width="215" height="40" rx="20" fill="#6C5CE7" />
  <text x="1502" y="70" font-size="13.5" font-weight="700" fill="#FFFFFF" text-anchor="middle">0xAA / 0xBB / 0xFF (CRC-8)</text>

  <!-- Column Headers -->
  <rect x="65" y="118" width="370" height="26" rx="8" fill="#EEF2FF" stroke="#C7D2FE" stroke-width="1" />
  <text x="250" y="136" font-size="12" font-weight="800" fill="#4338CA" text-anchor="middle">PHASE 1: DISCOVERY &amp; COMPILATION (0xAA)</text>

  <rect x="615" y="118" width="410" height="26" rx="8" fill="#E0F2FE" stroke="#BAE6FD" stroke-width="1" />
  <text x="820" y="136" font-size="12" font-weight="800" fill="#0369A1" text-anchor="middle">PHASE 2: STEP TRACKING (0xBB) &amp; BLE DISPATCH</text>

  <rect x="1215" y="118" width="380" height="26" rx="8" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1" />
  <text x="1405" y="136" font-size="12" font-weight="800" fill="#047857" text-anchor="middle">PHASE 3: VICTORY / EMERGENCY HALT &amp; IDLE</text>

  <!-- ==================== COLUMN 1: DISCOVERY & COMPILATION (PHASE 1) ==================== -->

  <!-- 1. START -->
  <g id="node-start" filter="url(#shadow)">
    <rect x="75" y="156" width="350" height="90" rx="20" fill="#FFD32A" stroke="#2D3436" stroke-width="2.5" />
    <text x="250" y="186" font-size="17" font-weight="800" fill="#2D3436" text-anchor="middle">START RUN CHAIN (MODE 1B)</text>
    <text x="250" y="209" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Chain detected on J2 (pollRunChainPort @ 800ms)</text>
    <text x="250" y="229" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Config Port empty -> User clicks Green Start (GPIO 14)</text>
  </g>

  <path d="M 250 246 L 250 284" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 2. Master Emits Seed -->
  <g id="node-seed" filter="url(#shadow)">
    <rect x="65" y="284" width="370" height="110" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="250" y="311" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (ESP32-S3 UART2 @ 115200)</text>
    <text x="250" y="335" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Emit Phase 1 Discovery Seed</text>
    <text x="250" y="359" font-size="12" font-weight="700" fill="#1E293B" text-anchor="middle">Pin 3 CHAIN_TX (GPIO 15): [0xAA, 0x00, 0x00, 0x00, 0x55]</text>
    <text x="250" y="379" font-size="11.5" font-weight="500" fill="#2D3436" text-anchor="middle">Flushes UART2 RX &amp; awaits return rail (350ms timeout)</text>
  </g>

  <path d="M 250 394 L 250 432" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 3. Action Block Processing -->
  <g id="node-block-proc" filter="url(#shadow)">
    <rect x="60" y="432" width="380" height="145" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="250" y="458" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">ACTION BLOCK (CH32V003 @ 24MHz)</text>
    <text x="250" y="482" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Assign Index, Append Token &amp; Forward</text>
    <text x="250" y="505" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">1. Rx 0xAA on PD6 (IN Pin 3); g_my_index = Count + 1</text>
    <text x="250" y="525" font-size="11.5" font-weight="600" fill="#2D3436" text-anchor="middle">2. Appends [g_action_id, g_param_val] from Flash 0x08003FC0</text>
    <text x="250" y="545" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">3. Len += 2, Count++, recomputes CRC-8 (Poly 0x07)</text>
    <text x="250" y="565" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">4. Tx on PD5 (OUT Pin 3); pings WS2812B amber (50ms)</text>
  </g>

  <path d="M 250 577 L 250 612" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 4. Next Block Check -->
  <g id="node-is-next-block" filter="url(#shadow)">
    <polygon points="250,612 365,687 250,762 135,687" fill="#74B9FF" stroke="#2D3436" stroke-width="2.5" />
    <text x="250" y="670" font-size="11" font-weight="800" fill="#2D3436" text-anchor="middle">PIN 3 DAISY CHAIN</text>
    <text x="250" y="692" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">More Action</text>
    <text x="250" y="712" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">Blocks?</text>
  </g>

  <!-- Next Block? YES Loop -->
  <path d="M 135 687 L 25 687 L 25 504 L 60 504" fill="none" stroke="#2D3436" stroke-width="2" marker-end="url(#arrow)" />
  <rect x="28" y="582" width="52" height="24" rx="6" fill="#FFFFFF" stroke="#2D3436" stroke-width="1.5" />
  <text x="54" y="599" font-size="12" font-weight="800" fill="#0984E3" text-anchor="middle">YES</text>

  <!-- Next Block? NO -> End Block -->
  <path d="M 250 762 L 250 802" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />
  <rect x="260" y="770" width="46" height="24" rx="6" fill="#FFFFFF" stroke="#2D3436" stroke-width="1.5" />
  <text x="283" y="787" font-size="12" font-weight="800" fill="#2D3436" text-anchor="middle">NO</text>

  <!-- 5. End Block Terminator -->
  <g id="node-endblock" filter="url(#shadow)">
    <rect x="60" y="802" width="380" height="125" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="250" y="828" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">SMART END BLOCK (0xEE or PD0=LOW)</text>
    <text x="250" y="852" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Validate CRC-8 &amp; Loopback Return</text>
    <text x="250" y="875" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Verifies CRC-8 of [Len, Count, Payload...] &amp; 0x55</text>
    <text x="250" y="895" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Drives verified 0xAA frame onto Pin 4 RETURN_BUS</text>
    <text x="250" y="914" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">(PD0 bit-bang in unified FW; PD5 in end FW; glows green)</text>
  </g>

  <path d="M 250 927 L 250 965" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 6. Master Return & CRC Valid Check -->
  <g id="node-crc-check" filter="url(#shadow)">
    <polygon points="250,965 375,1045 250,1125 125,1045" fill="#74B9FF" stroke="#2D3436" stroke-width="2.5" />
    <text x="250" y="1024" font-size="11" font-weight="800" fill="#2D3436" text-anchor="middle">GPIO 16 CHAIN_RX</text>
    <text x="250" y="1046" font-size="14.5" font-weight="700" fill="#2D3436" text-anchor="middle">Return Frame</text>
    <text x="250" y="1066" font-size="14.5" font-weight="700" fill="#2D3436" text-anchor="middle">&amp; CRC-8 OK?</text>
  </g>

  <!-- Return Check? FAIL -->
  <path d="M 125 1045 L 25 1045 L 25 1218 L 65 1218" fill="none" stroke="#D63031" stroke-width="2" marker-end="url(#arrow-red)" />
  <rect x="28" y="1120" width="52" height="24" rx="6" fill="#FFFFFF" stroke="#D63031" stroke-width="1.5" />
  <text x="54" y="1137" font-size="12" font-weight="800" fill="#D63031" text-anchor="middle">FAIL</text>

  <!-- Error Node -->
  <g id="node-error" filter="url(#shadow)">
    <rect x="65" y="1168" width="370" height="100" rx="16" fill="#FF7675" stroke="#2D3436" stroke-width="2.5" />
    <text x="250" y="1194" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (ESP32-S3)</text>
    <text x="250" y="1218" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Open Circuit / CRC / Length Fault</text>
    <text x="250" y="1240" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Master RGB (GPIO 48) Red (50,0,0) for 500ms</text>
    <text x="250" y="1258" font-size="11.5" font-weight="600" fill="#2D3436" text-anchor="middle">E-Ink: "START: NO CHAIN BLOCKS!" -> Restore Mode</text>
  </g>

  <!-- Return Check? VALID -> Column 2 -->
  <path d="M 375 1045 L 540 1045 L 540 206 L 615 206" fill="none" stroke="#00B894" stroke-width="2.5" marker-end="url(#arrow-green)" />
  <rect x="425" y="1025" width="70" height="24" rx="6" fill="#FFFFFF" stroke="#00B894" stroke-width="1.5" />
  <text x="460" y="1042" font-size="12" font-weight="800" fill="#00B894" text-anchor="middle">VALID</text>

  <!-- ==================== COLUMN 2: EXECUTION & STEP TRACKING (PHASE 2) ==================== -->

  <!-- 7. Master Compiles Queue -->
  <g id="node-master-compile" filter="url(#shadow)">
    <rect x="615" y="156" width="410" height="102" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="820" y="183" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (ESP32-S3)</text>
    <text x="820" y="207" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Compile Sequence (Steps 1..N)</text>
    <text x="820" y="229" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Strips any trailing 0xEE, verifies Count &gt; 0 &amp; Len == 2*N</text>
    <text x="820" y="247" font-size="11.5" font-weight="500" fill="#2D3436" text-anchor="middle">Maps [Token, Param] -> RobosenAction; 400ms abortableDelay</text>
  </g>

  <path d="M 820 258 L 820 295" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 8. Broadcast Active Step on Pin 3 -->
  <g id="node-broadcast-step" filter="url(#shadow)">
    <rect x="615" y="295" width="410" height="110" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="820" y="322" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER -&gt; PIN 3 CHAIN_TX (GPIO 15)</text>
    <text x="820" y="346" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Phase 2: Broadcast Active Step (0xBB)</text>
    <text x="820" y="370" font-size="12" font-weight="700" fill="#1E293B" text-anchor="middle">Tx [0xBB, ActiveStep = s, TotalSteps = N, CRC8, 0x55]</text>
    <text x="820" y="390" font-size="11.5" font-weight="500" fill="#2D3436" text-anchor="middle">Action blocks Rx on PD6 &amp; forward downstream on PD5 (OUT Pin 3)</text>
  </g>

  <path d="M 820 405 L 820 442" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 9. Visual Step Sync & E-Ink -->
  <g id="node-led-sync" filter="url(#shadow)">
    <rect x="615" y="442" width="410" height="112" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="820" y="469" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">ALL BLOCKS (WS2812B PA2) &amp; MASTER E-INK (CORE 0)</text>
    <text x="820" y="493" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Real-Time Step LED &amp; E-Ink Update</text>
    <text x="820" y="517" font-size="12.5" font-weight="700" fill="#00897B" text-anchor="middle">Block (g_my_index == s) -&gt; Bright Green (0, 255, 0)</text>
    <text x="820" y="537" font-size="11.5" font-weight="600" fill="#2D3436" text-anchor="middle">Others show idle action color; E-Ink shows "STEP s/N" + action</text>
  </g>

  <path d="M 820 554 L 820 591" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 10. Send BLE Command -->
  <g id="node-send-ble" filter="url(#shadow)">
    <rect x="615" y="591" width="410" height="110" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="820" y="618" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLE CENTRAL (Service 0xFFE0 / Char 0xFFE1)</text>
    <text x="820" y="642" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Dispatch Robosen K1 BLE Packet</text>
    <text x="820" y="666" font-size="12" font-weight="700" fill="#1E293B" text-anchor="middle">[0xFF, 0xFF, NumBytes, Opcode, Payload..., Checksum]</text>
    <text x="820" y="686" font-size="11.5" font-weight="500" fill="#2D3436" text-anchor="middle">Walk/Turn: 0x01/05/08/02/07/03  |  Predefined Stunts: 0x17</text>
  </g>

  <path d="M 820 701 L 820 738" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 11. Robot Motion & Timing -->
  <g id="node-robot-exec" filter="url(#shadow)">
    <rect x="615" y="738" width="410" height="125" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="820" y="764" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">ROBOSEN K1 (17 SERVOS) + MASTER TIMING ENGINE</text>
    <text x="820" y="788" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Physical Motion &amp; Abortable Wait</text>
    <text x="820" y="811" font-size="11.5" font-weight="600" fill="#2D3436" text-anchor="middle">• Turn (0x08/02): 1600ms/90° L, 3200ms/90° R -> Stop (0x0C) + 1.0s</text>
    <text x="820" y="830" font-size="11.5" font-weight="600" fill="#2D3436" text-anchor="middle">• Walk/Side: Steps x 1400ms -> BLE Stop (0x0C) + 1.2s settle</text>
    <text x="820" y="849" font-size="11.5" font-weight="600" fill="#2D3436" text-anchor="middle">• Action (0x17): Duration lookup (2.5s-55s) x Reps (+0.4s pause)</text>
  </g>

  <path d="M 820 863 L 820 902" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 12. Red Stop Button / BLE Fail Check -->
  <g id="node-stop-check" filter="url(#shadow)">
    <polygon points="820,902 945,980 820,1058 695,980" fill="#74B9FF" stroke="#2D3436" stroke-width="2.5" />
    <text x="820" y="960" font-size="11" font-weight="800" fill="#2D3436" text-anchor="middle">SW5 (GPIO 2) / BLE</text>
    <text x="820" y="982" font-size="14.5" font-weight="700" fill="#2D3436" text-anchor="middle">Red Stop or</text>
    <text x="820" y="1002" font-size="14.5" font-weight="700" fill="#2D3436" text-anchor="middle">BLE Error?</text>
  </g>

  <!-- Abort Branch -> Col 3 Emergency Halt -->
  <path d="M 945 980 L 1185 980" fill="none" stroke="#D63031" stroke-width="2.5" marker-end="url(#arrow-red)" />
  <rect x="1030" y="960" width="75" height="24" rx="6" fill="#FFFFFF" stroke="#D63031" stroke-width="1.5" />
  <text x="1067" y="977" font-size="12" font-weight="800" fill="#D63031" text-anchor="middle">ABORT</text>

  <!-- Step OK -> More Steps Check -->
  <path d="M 820 1058 L 820 1102" fill="none" stroke="#00B894" stroke-width="2.5" marker-end="url(#arrow-green)" />
  <rect x="830" y="1068" width="60" height="24" rx="6" fill="#FFFFFF" stroke="#00B894" stroke-width="1.5" />
  <text x="860" y="1085" font-size="12" font-weight="800" fill="#00B894" text-anchor="middle">DONE</text>

  <!-- 13. More Steps Check -->
  <g id="node-more-steps" filter="url(#shadow)">
    <polygon points="820,1102 945,1180 820,1258 695,1180" fill="#74B9FF" stroke="#2D3436" stroke-width="2.5" />
    <text x="820" y="1160" font-size="11" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER QUEUE</text>
    <text x="820" y="1182" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">More Steps</text>
    <text x="820" y="1202" font-size="15" font-weight="700" fill="#2D3436" text-anchor="middle">(s &lt; N)?</text>
  </g>

  <!-- More Steps? YES -> Loop back to Broadcast Step -->
  <path d="M 695 1180 L 568 1180 L 568 350 L 615 350" fill="none" stroke="#0984E3" stroke-width="2.5" marker-end="url(#arrow-blue)" />
  <rect x="526" y="750" width="84" height="36" rx="6" fill="#FFFFFF" stroke="#0984E3" stroke-width="1.5" />
  <text x="568" y="766" font-size="11.5" font-weight="800" fill="#0984E3" text-anchor="middle">YES (s++)</text>
  <text x="568" y="781" font-size="10" font-weight="600" fill="#636E72" text-anchor="middle">500ms delay</text>

  <!-- More Steps? NO -> Column 3 Phase 3 -->
  <path d="M 945 1180 L 1115 1180 L 1115 211 L 1185 211" fill="none" stroke="#00B894" stroke-width="2.5" marker-end="url(#arrow-green)" />
  <rect x="995" y="1160" width="88" height="24" rx="6" fill="#FFFFFF" stroke="#00B894" stroke-width="1.5" />
  <text x="1039" y="1177" font-size="12" font-weight="800" fill="#00B894" text-anchor="middle">ALL DONE</text>

  <!-- ==================== COLUMN 3: PHASE 3 COMPLETION, HALT & IDLE ==================== -->

  <!-- 14. Phase 3 Complete Broadcast (0xBB 0xFF) -->
  <g id="node-phase3-complete" filter="url(#shadow)">
    <rect x="1185" y="156" width="420" height="110" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="1395" y="183" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER -&gt; PIN 3 CHAIN_TX (GPIO 15)</text>
    <text x="1395" y="207" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Phase 3: Broadcast Complete (0xFF)</text>
    <text x="1395" y="231" font-size="12" font-weight="700" fill="#1E293B" text-anchor="middle">Tx [0xBB, 0xFF, TotalSteps = N, CRC8, 0x55]</text>
    <text x="1395" y="250" font-size="11.5" font-weight="500" fill="#2D3436" text-anchor="middle">Forwarded PD6 -&gt; PD5 across all Action &amp; End blocks</text>
  </g>

  <path d="M 1395 266 L 1395 304" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 15. Rainbow Victory Sparkle & E-Ink Update -->
  <g id="node-mission-complete" filter="url(#shadow)">
    <rect x="1185" y="304" width="420" height="120" rx="16" fill="#55E6C1" stroke="#2D3436" stroke-width="2.5" />
    <text x="1395" y="331" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">BLOCKS (WS2812B) + MASTER (E-INK &amp; RGB)</text>
    <text x="1395" y="355" font-size="15.5" font-weight="700" fill="#00695C" text-anchor="middle">Rainbow Victory Sparkle &amp; UI Done</text>
    <text x="1395" y="378" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">All blocks &amp; Master RGB (GPIO 48) play 3x Rainbow cycle</text>
    <text x="1395" y="398" font-size="12" font-weight="700" fill="#1E293B" text-anchor="middle">E-Ink: "RUNNING CHAIN" / "ALL STEPS DONE! [OK]"</text>
    <text x="1395" y="415" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">Blocks return to idle color; K1 holds neutral standing pose</text>
  </g>

  <path d="M 1395 424 L 1395 462" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 16. Restore Post-Run Mode -->
  <g id="node-restore" filter="url(#shadow)">
    <rect x="1185" y="462" width="420" height="110" rx="16" fill="#A29BFE" stroke="#2D3436" stroke-width="2.5" />
    <text x="1395" y="489" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">MASTER BLOCK (restorePostRunMode)</text>
    <text x="1395" y="513" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Clear RX Buffers &amp; Restore Mode</text>
    <text x="1395" y="536" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">Waits 1200ms, resets chain/cfg RX indices &amp; redraws E-Ink</text>
    <text x="1395" y="555" font-size="11.5" font-weight="500" fill="#2D3436" text-anchor="middle">Returns to Mode 1B (Run UI) or Mode 2 (RC if unplugged)</text>
  </g>

  <path d="M 1395 572 L 1395 612" fill="none" stroke="#2D3436" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- 17. END -->
  <g id="node-end" filter="url(#shadow)">
    <rect x="1230" y="612" width="330" height="90" rx="20" fill="#FFD32A" stroke="#2D3436" stroke-width="2.5" />
    <text x="1395" y="647" font-size="17" font-weight="800" fill="#2D3436" text-anchor="middle">READY FOR NEXT RUN</text>
    <text x="1395" y="670" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">BLE Link Kept Active; Screenless Tangible Loop</text>
    <text x="1395" y="688" font-size="11" font-weight="500" fill="#2D3436" text-anchor="middle">(Python k1_ble_daemon.py also supports 0x64 100% ACK)</text>
  </g>

  <!-- 18. Emergency Halt Node -->
  <g id="node-abort" filter="url(#shadow)">
    <rect x="1185" y="905" width="420" height="150" rx="16" fill="#FF7675" stroke="#2D3436" stroke-width="2.5" />
    <text x="1395" y="932" font-size="12.5" font-weight="800" fill="#2D3436" text-anchor="middle">EMERGENCY HALT (triggerChainAbort)</text>
    <text x="1395" y="956" font-size="15.5" font-weight="700" fill="#2D3436" text-anchor="middle">Red Stop Button (SW5) / BLE Abort</text>
    <text x="1395" y="979" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">1. Pin 3 Tx: [0xBB, 0x00, N, CRC8, 0x55] (Blocks idle)</text>
    <text x="1395" y="999" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">2. BLE Stop: [0xFF, 0xFF, 0x02, 0x0C, 0x0E] -&gt; K1 Stand</text>
    <text x="1395" y="1019" font-size="12" font-weight="600" fill="#2D3436" text-anchor="middle">3. Master LED Red (120,0,0); E-Ink: "HALT / EMERGENCY STOP"</text>
    <text x="1395" y="1039" font-size="11.5" font-weight="500" fill="#2D3436" text-anchor="middle">4. Waits 1500ms -&gt; Calls restorePostRunMode(true)</text>
  </g>

  <!-- Emergency Halt -> Restore Mode -->
  <path d="M 1605 980 L 1635 980 L 1635 517 L 1605 517" fill="none" stroke="#D63031" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow-red)" />

  <!-- Footer Legend Bar -->
  <g transform="translate(40, 1345)">
    <rect x="0" y="0" width="1600" height="65" rx="12" fill="#FFFFFF" stroke="#DFE6E9" stroke-width="1.5" />
    <text x="30" y="38" font-size="14" font-weight="700" fill="#2D3436">LEGEND:</text>

    <rect x="115" y="23" width="20" height="20" rx="6" fill="#FFD32A" stroke="#2D3436" stroke-width="1.5" />
    <text x="145" y="38" font-size="13" font-weight="600" fill="#636E72">Terminal (Start / End)</text>

    <rect x="330" y="23" width="20" height="20" rx="6" fill="#A29BFE" stroke="#2D3436" stroke-width="1.5" />
    <text x="360" y="38" font-size="13" font-weight="600" fill="#636E72">Process &amp; Hardware Action</text>

    <polygon points="595,23 605,33 595,43 585,33" fill="#74B9FF" stroke="#2D3436" stroke-width="1.5" />
    <text x="615" y="38" font-size="13" font-weight="600" fill="#636E72">Conditional Check / CRC-8</text>

    <rect x="845" y="23" width="20" height="20" rx="6" fill="#FF7675" stroke="#2D3436" stroke-width="1.5" />
    <text x="875" y="38" font-size="13" font-weight="600" fill="#636E72">Fault / Emergency Halt</text>

    <rect x="1085" y="23" width="20" height="20" rx="6" fill="#55E6C1" stroke="#2D3436" stroke-width="1.5" />
    <text x="1115" y="38" font-size="13" font-weight="600" fill="#636E72">Victory Celebration / E-Ink Done</text>
  </g>
</svg>
'''

repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out_dir = os.path.join(repo_root, 'docs', 'diagrams')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'robosen_coding_data_flow.svg')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(svg_content)
print(f'SVG successfully generated at: {out_path}')
