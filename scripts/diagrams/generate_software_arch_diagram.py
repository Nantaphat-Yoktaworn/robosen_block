import os

svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1680 1180" width="100%" height="100%" style="background-color: #F8F9FA; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
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
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6C5CE7" />
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#00B894" />
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D97706" />
    </marker>
  </defs>

  <!-- Header Banner -->
  <rect x="40" y="20" width="1600" height="76" rx="16" fill="#FFFFFF" stroke="#DFE6E9" stroke-width="1.5" filter="url(#shadow)" />
  <text x="68" y="55" font-size="22" font-weight="800" fill="#2D3436">Robosen Tangible Coding Block System — Firmware &amp; Software Architecture</text>
  <text x="68" y="80" font-size="13.5" font-weight="500" fill="#636E72">Complete code architecture across ESP32-S3 Master (FreeRTOS), CH32V003 RISC-V Blocks, SWIO Tools, Python BLE Suite &amp; Node.js SDK</text>
  <rect x="1355" y="38" width="258" height="40" rx="20" fill="#4338CA" />
  <text x="1484" y="63" font-size="13" font-weight="700" fill="#FFFFFF" text-anchor="middle">Dual-Core + Multi-Target Stack</text>

  <!-- ==================== TIER 1: ESP32-S3 MASTER FIRMWARE ==================== -->
  <g id="tier-esp32" filter="url(#shadow)">
    <rect x="40" y="114" width="1600" height="398" rx="18" fill="#FFFFFF" stroke="#4F46E5" stroke-width="2.2" />
    <rect x="40" y="114" width="1600" height="42" rx="18" fill="#4F46E5" />
    <rect x="40" y="140" width="1600" height="16" fill="#4F46E5" />
    <text x="68" y="141" font-size="15" font-weight="800" fill="#FFFFFF">TIER 1: MASTER CONTROLLER FIRMWARE (firmware/esp32_master/esp32_master.ino — ESP32-S3 Dual-Core FreeRTOS)</text>

    <!-- Core 0 Async Tasks -->
    <rect x="60" y="172" width="445" height="320" rx="14" fill="#EEF2FF" stroke="#818CF8" stroke-width="1.8" />
    <text x="282" y="196" font-size="13.5" font-weight="800" fill="#312E81" text-anchor="middle">CORE 0: ASYNC I/O &amp; BLE RTOS TASKS</text>

    <rect x="76" y="210" width="413" height="96" rx="10" fill="#FFFFFF" stroke="#A5B4FC" stroke-width="1.5" />
    <text x="90" y="231" font-size="12" font-weight="800" fill="#4338CA">einkDisplayTask (DISP1 2.13" E-Paper SPI @ 4MHz)</text>
    <text x="90" y="250" font-size="11" font-weight="600" fill="#1E293B">• Pins: BUSY=4, RES=5, DC=6, CS=7, SCL=21, SDA=38</text>
    <text x="90" y="268" font-size="11" font-weight="600" fill="#1E293B">• Partial window (40,24,210,96), 210x122 visible bezel</text>
    <text x="90" y="286" font-size="11" font-weight="600" fill="#1E293B">• LUT_FAST_280MS + 350ms settle pass (LUT_STD_727MS)</text>

    <rect x="76" y="318" width="413" height="54" rx="10" fill="#DBEAFE" stroke="#3B82F6" stroke-width="1.5" />
    <text x="282" y="340" font-size="12" font-weight="800" fill="#1E3A8A" text-anchor="middle">Shared Synchronization: bleMutex</text>
    <text x="282" y="358" font-size="10.8" font-weight="600" fill="#1E40AF" text-anchor="middle">Guards BLE writes between Core 1 FSM &amp; Core 0 reconnect task</text>

    <rect x="76" y="384" width="413" height="96" rx="10" fill="#FFFFFF" stroke="#A5B4FC" stroke-width="1.5" />
    <text x="90" y="405" font-size="12" font-weight="800" fill="#0369A1">bleReconnectTask (NimBLE Central Client)</text>
    <text x="90" y="424" font-size="11" font-weight="600" fill="#1E293B">• Handles STATE_BLE_SCANNING &amp; PAIRING (1s scan, 2s retry)</text>
    <text x="90" y="442" font-size="11" font-weight="600" fill="#1E293B">• NVS Namespace "robosen_cfg" caches paired K1 MAC</text>
    <text x="90" y="460" font-size="11" font-weight="600" fill="#1E293B">• Attaches to GATT Service 0xFFE0 / Char 0xFFE1</text>

    <!-- Core 1 <-> bleMutex Sync Arrow -->
    <path d="M 548 345 L 491 345" fill="none" stroke="#0984E3" stroke-width="2.5" marker-start="url(#arrow-blue)" marker-end="url(#arrow-blue)" />

    <!-- Core 1 State Machine & Engines -->
    <rect x="548" y="172" width="1072" height="320" rx="14" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.8" />
    <text x="1084" y="196" font-size="13.5" font-weight="800" fill="#1E293B" text-anchor="middle">CORE 1: PORT-DRIVEN STATE MACHINE, TANGIBLE ENGINES &amp; INPUTS</text>

    <!-- Port Hardware Arbiter Strip -->
    <rect x="568" y="210" width="1032" height="62" rx="10" fill="#FEF3C7" stroke="#D97706" stroke-width="1.8" />
    <text x="584" y="232" font-size="12" font-weight="800" fill="#92400E">enforcePortModeLock() — Automatic Hardware Arbiter (Priority: J1 Config Dock &gt; J2 Run Chain &gt; Knob-Switched Modes)</text>
    <text x="584" y="253" font-size="11" font-weight="600" fill="#78350F">• pollConfigDock() @ 250ms (1200ms timeout, GPIO 17/18 probe)  |  pollRunChainPort() @ 800ms (GPIO 16 pull-up check)  |  SW1/SW2 (8..13), SW3 (14), SW5 (2)</text>

    <path d="M 755 272 L 755 294" fill="none" stroke="#D97706" stroke-width="2" marker-end="url(#arrow-amber)" />
    <path d="M 1090 272 L 1090 294" fill="none" stroke="#D97706" stroke-width="2" marker-end="url(#arrow-amber)" />
    <path d="M 1425 272 L 1425 294" fill="none" stroke="#D97706" stroke-width="2" marker-end="url(#arrow-amber)" />

    <!-- Mode 1A & 1B -->
    <rect x="568" y="294" width="380" height="184" rx="12" fill="#F3E8FF" stroke="#7C3AED" stroke-width="2" />
    <text x="758" y="317" font-size="12.5" font-weight="800" fill="#5B21B6" text-anchor="middle">MODE 1: STATE_ACTION_MENU (J1 / J2 Locked)</text>
    <text x="582" y="340" font-size="11" font-weight="700" fill="#4C1D95">1A Config Dock (when J1 occupied):</text>
    <text x="590" y="357" font-size="10.8" font-weight="600" fill="#1E293B">• Auto UART1 (17&lt;-&gt;18): 0xCF 0x01 read / 0x02 write</text>
    <text x="590" y="374" font-size="10.8" font-weight="600" fill="#1E293B">• Knob 1 edits ACTIONS[8]; SW3 writes; SW5 reverts</text>
    <text x="582" y="399" font-size="11" font-weight="700" fill="#0369A1">1B Run Chain (when J1 empty &amp; J2 chain detected):</text>
    <text x="590" y="416" font-size="10.8" font-weight="600" fill="#1E293B">• executeRunChain() emits 0xAA seed on UART2 (GPIO 15)</text>
    <text x="590" y="433" font-size="10.8" font-weight="600" fill="#1E293B">• Reads GPIO 16 return, steps 0xBB, abortableDelay()</text>
    <text x="590" y="450" font-size="10.8" font-weight="600" fill="#1E293B">• SW5 Red Stop calls triggerChainAbort() + BLE 0x0C</text>
    <text x="590" y="467" font-size="10.5" font-weight="500" fill="#5B21B6">• Knob 1 click disabled while locked in Mode 1</text>

    <!-- Mode 2 Remote Control -->
    <rect x="964" y="294" width="316" height="184" rx="12" fill="#E0F2FE" stroke="#0284C7" stroke-width="2" />
    <text x="1122" y="317" font-size="12.5" font-weight="800" fill="#0369A1" text-anchor="middle">MODE 2: STATE_REMOTE_CONTROL</text>
    <text x="978" y="342" font-size="11" font-weight="600" fill="#1E293B">• Active when J1 &amp; J2 are empty</text>
    <text x="978" y="362" font-size="11" font-weight="600" fill="#1E293B">• Knob 1 click cycles Mode 2 &lt;-&gt; Mode 3</text>
    <text x="978" y="384" font-size="11" font-weight="700" fill="#0369A1">• updateRemoteControlEngine():</text>
    <text x="986" y="403" font-size="10.8" font-weight="600" fill="#1E293B">- Dual-knob walk/turn &amp; stunt dispatch</text>
    <text x="986" y="421" font-size="10.8" font-weight="600" fill="#1E293B">- Calls sendRobosenPacket() via bleMutex</text>
    <text x="978" y="443" font-size="11" font-weight="600" fill="#1E293B">• Supports 16 tokens in getActionObjByToken()</text>
    <text x="978" y="463" font-size="10.8" font-weight="600" fill="#1E293B">• SW5 / Knob SW triggers BLE Stop (0x0C)</text>

    <!-- Mode 3 Joint Control -->
    <rect x="1296" y="294" width="304" height="184" rx="12" fill="#ECFDF5" stroke="#059669" stroke-width="2" />
    <text x="1448" y="317" font-size="12.5" font-weight="800" fill="#047857" text-anchor="middle">MODE 3: STATE_JOINT_CONTROL</text>
    <text x="1310" y="342" font-size="11" font-weight="600" fill="#1E293B">• Direct servo control over ALL_JOINTS (17)</text>
    <text x="1310" y="362" font-size="11" font-weight="600" fill="#1E293B">• Knob 1 selects target servo joint index</text>
    <text x="1310" y="382" font-size="11" font-weight="600" fill="#1E293B">• Knob 2 adjusts angle setpoint in real time</text>
    <text x="1310" y="404" font-size="11" font-weight="700" fill="#047857">• Sends joint command via sendRobosenPacket()</text>
    <text x="1310" y="426" font-size="11" font-weight="600" fill="#1E293B">• E-Ink shows joint label &amp; angle live</text>
    <text x="1310" y="448" font-size="11" font-weight="600" fill="#1E293B">• Plugging block into J1/J2 immediately</text>
    <text x="1318" y="466" font-size="10.8" font-weight="600" fill="#1E293B">preempts into locked Mode 1A/1B</text>
  </g>

  <!-- ==================== TIER 2 LEFT: CH32V003 BLOCK FIRMWARE & SWIO ==================== -->
  <g id="tier-ch32" filter="url(#shadow)">
    <rect x="40" y="534" width="785" height="360" rx="18" fill="#FFFFFF" stroke="#7C3AED" stroke-width="2.2" />
    <rect x="40" y="534" width="785" height="40" rx="18" fill="#6C5CE7" />
    <rect x="40" y="558" width="785" height="16" fill="#6C5CE7" />
    <text x="432" y="560" font-size="14.5" font-weight="800" fill="#FFFFFF" text-anchor="middle">TIER 2A: CH32V003 RISC-V FIRMWARE &amp; SWIO PROGRAMMERS (24MHz, No External XTAL)</text>

    <!-- Unified Action Block FW -->
    <rect x="58" y="588" width="424" height="172" rx="12" fill="#F5F3FF" stroke="#8B5CF6" stroke-width="1.6" />
    <text x="270" y="610" font-size="12.2" font-weight="800" fill="#4C1D95" text-anchor="middle">ch32v003_action_block/main.c (Unified FW)</text>
    <text x="70" y="631" font-size="10.5" font-weight="600" fill="#1E293B">• USART1 @ 115200: PD6 (IN Pin 3 RX), PD5 (OUT Pin 3 TX)</text>
    <text x="70" y="649" font-size="10.5" font-weight="600" fill="#1E293B">• PD0 RETURN_BUS: Hi-Z in Action Run; SW 0xCF RX (handle_pd0_rx)</text>
    <text x="70" y="667" font-size="10.5" font-weight="600" fill="#1E293B">• If g_action_id == 0xEE: PD0 loops verified 0xAA to Master</text>
    <text x="70" y="685" font-size="10.5" font-weight="600" fill="#1E293B">• NVMEM 0x08003FC0 (64B page, CFG_MAGIC 0xA55A0002)</text>
    <text x="70" y="703" font-size="10.5" font-weight="600" fill="#1E293B">• 0xCF write -> [0xCF, 0x06, 0x12, 0x55]; silent drop on bad CRC</text>
    <text x="70" y="721" font-size="10.5" font-weight="600" fill="#1E293B">• PA2 WS2812B (Green 400ms / Step / Rainbow); PD4/PC0 500ms HB</text>
    <text x="70" y="739" font-size="10.5" font-weight="600" fill="#1E293B">• 0xBB step &amp; 0xFF complete forwarded downstream PD6 -&gt; PD5</text>

    <!-- Dedicated End Block FW -->
    <rect x="496" y="588" width="311" height="172" rx="12" fill="#ECFDF5" stroke="#10B981" stroke-width="1.6" />
    <text x="651" y="610" font-size="12.2" font-weight="800" fill="#065F46" text-anchor="middle">ch32v003_end_block/main.c</text>
    <text x="508" y="633" font-size="10.5" font-weight="600" fill="#1E293B">• Fixed role: END_BLOCK_TOKEN 0xEE</text>
    <text x="508" y="653" font-size="10.5" font-weight="600" fill="#1E293B">• PD6 RX_IN receives finished 0xAA frame</text>
    <text x="508" y="673" font-size="10.5" font-weight="600" fill="#1E293B">• Validates CRC-8 (Poly 0x07) &amp; 0x55</text>
    <text x="508" y="693" font-size="10.5" font-weight="600" fill="#1E293B">• Transmits verified 0xAA loopback (PD5)</text>
    <text x="508" y="713" font-size="10.5" font-weight="600" fill="#1E293B">• Answers 0xCF dock identity queries</text>
    <text x="508" y="733" font-size="10.5" font-weight="600" fill="#1E293B">• PA2 RGB idle green &amp; 0xFF rainbow</text>

    <!-- SWIO Programmers Bar -->
    <rect x="58" y="774" width="749" height="104" rx="12" fill="#FFFBEB" stroke="#F59E0B" stroke-width="1.6" />
    <text x="432" y="797" font-size="12.5" font-weight="800" fill="#92400E" text-anchor="middle">SWIO FLASHING TOOLS (firmware/tools_programmer/ -&gt; 3-Pin PROG Header: GND, 3V3, SWIO PD1)</text>
    <text x="74" y="821" font-size="11.2" font-weight="700" fill="#1E293B">• esp32_ch32v003_programmer</text>
    <text x="330" y="821" font-size="11" font-weight="500" fill="#475569">Single-wire SWIO flasher hosted on ESP32 -&gt; PD1</text>
    <text x="74" y="843" font-size="11.2" font-weight="700" fill="#1E293B">• arduino_uno_ch32v003_programmer</text>
    <text x="330" y="843" font-size="11" font-weight="500" fill="#475569">Single-wire SWIO flasher hosted on Arduino Uno -&gt; PD1</text>
    <text x="74" y="865" font-size="10.5" font-weight="600" fill="#78350F">Note: Action &amp; End PCB hardware is identical (32x32mm); role is selected via 0xCF Config Dock (0xEE) or SWIO FW.</text>
  </g>

  <!-- ==================== TIER 2 RIGHT: HOST PYTHON & NODE.JS SDK ==================== -->
  <g id="tier-host" filter="url(#shadow)">
    <rect x="855" y="534" width="785" height="360" rx="18" fill="#FFFFFF" stroke="#0284C7" stroke-width="2.2" />
    <rect x="855" y="534" width="785" height="40" rx="18" fill="#0369A1" />
    <rect x="855" y="558" width="785" height="16" fill="#0369A1" />
    <text x="1247" y="560" font-size="14.5" font-weight="800" fill="#FFFFFF" text-anchor="middle">TIER 2B: HOST SOFTWARE, PYTHON BLE DAEMON &amp; NODE.JS SDK (Direct BLE Control)</text>

    <!-- Python BLE Suite -->
    <rect x="875" y="588" width="368" height="290" rx="12" fill="#F0F9FF" stroke="#38BDF8" stroke-width="1.6" />
    <text x="1059" y="611" font-size="12.5" font-weight="800" fill="#0369A1" text-anchor="middle">Python BLE Automation Suite (scripts/)</text>
    <text x="890" y="636" font-size="11.2" font-weight="700" fill="#0C4A6E">• k1_ble_daemon.py (Bleak Daemon):</text>
    <text x="900" y="654" font-size="10.8" font-weight="600" fill="#1E293B">- Persistent K1 GATT connection &amp; queue</text>
    <text x="900" y="672" font-size="10.8" font-weight="600" fill="#1E293B">- Waits on 0x64 100% progress ACK packets</text>
    <text x="900" y="690" font-size="10.8" font-weight="600" fill="#1E293B">- Reads live servo telemetry via 0xE9 opcode</text>
    <text x="890" y="716" font-size="11.2" font-weight="700" fill="#0C4A6E">• k1_action.py:</text>
    <text x="900" y="734" font-size="10.8" font-weight="600" fill="#1E293B">- Scripted action sequence CLI runner</text>
    <text x="890" y="758" font-size="11.2" font-weight="700" fill="#0C4A6E">• k1_joint_controller.py:</text>
    <text x="900" y="776" font-size="10.8" font-weight="600" fill="#1E293B">- Direct 17-joint pose &amp; angle controller</text>
    <text x="890" y="800" font-size="11.2" font-weight="700" fill="#0C4A6E">• Diagnostics &amp; Firmware Tools:</text>
    <text x="900" y="818" font-size="10.8" font-weight="600" fill="#1E293B">- k1_ble_tester.py &amp; k1_deep_explorer.py</text>
    <text x="900" y="836" font-size="10.8" font-weight="600" fill="#1E293B">- k1_live_super_test.py &amp; robot_live_dumper.py</text>
    <text x="900" y="854" font-size="10.8" font-weight="600" fill="#1E293B">- update_firmware_nonblocking.py</text>

    <!-- Node.js RobosenJS SDK -->
    <rect x="1259" y="588" width="363" height="290" rx="12" fill="#EEF2FF" stroke="#818CF8" stroke-width="1.6" />
    <text x="1440" y="611" font-size="12.5" font-weight="800" fill="#312E81" text-anchor="middle">Node.js RobosenJS SDK (src/, bin/)</text>
    <text x="1274" y="636" font-size="11.2" font-weight="700" fill="#3730A3">• src/Robot.js &amp; Robot.d.ts:</text>
    <text x="1284" y="654" font-size="10.8" font-weight="600" fill="#1E293B">- Low-level K1 BLE packet builder &amp; parser</text>
    <text x="1284" y="672" font-size="10.8" font-weight="600" fill="#1E293B">- Opcodes: 0x01..0x0C, 0x17, 0xE8/E9, 0xF4..0xFA</text>
    <text x="1284" y="690" font-size="10.8" font-weight="600" fill="#1E293B">- PacketKind: data, progress, completed, stop</text>
    <text x="1274" y="716" font-size="11.2" font-weight="700" fill="#3730A3">• src/K1.js, K1.d.ts &amp; src/K1/:</text>
    <text x="1284" y="734" font-size="10.8" font-weight="600" fill="#1E293B">- High-level K1 action wrappers (kungFu(),</text>
    <text x="1292" y="751" font-size="10.8" font-weight="600" fill="#1E293B">pushUps(), waveHands(), backFlip(), etc.)</text>
    <text x="1274" y="777" font-size="11.2" font-weight="700" fill="#3730A3">• bin/k1.js (CLI Entrypoints):</text>
    <text x="1284" y="795" font-size="10.8" font-weight="600" fill="#1E293B">- Commands: repl, control, run, prompt, voice</text>
    <text x="1274" y="821" font-size="11.2" font-weight="700" fill="#3730A3">• scripts/*.js Automation Examples:</text>
    <text x="1284" y="839" font-size="10.8" font-weight="600" fill="#1E293B">- repl.js, control.js, program.js, main.js,</text>
    <text x="1292" y="856" font-size="10.8" font-weight="600" fill="#1E293B">prompt.js (promptRepl), voice.js</text>
  </g>

  <!-- ==================== TIER 3: SHARED PROTOCOLS & TARGET ROBOT ==================== -->
  <!-- Wire Protocol Bus -->
  <g id="tier-protocols" filter="url(#shadow)">
    <rect x="40" y="936" width="785" height="162" rx="16" fill="#FFFFFF" stroke="#64748B" stroke-width="2" />
    <rect x="40" y="936" width="785" height="34" rx="16" fill="#334155" />
    <rect x="40" y="954" width="785" height="16" fill="#334155" />
    <text x="432" y="958" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="middle">INTER-BLOCK POGO BUS PROTOCOLS (115200 bps, CRC-8 Poly 0x07, Footer 0x55)</text>

    <text x="60" y="994" font-size="11.5" font-weight="700" fill="#5B21B6">• 0xCF Config Dock (UART1 on J1):</text>
    <text x="275" y="994" font-size="11.2" font-weight="600" fill="#1E293B">0x01 Query -&gt; 0x81 Reply  |  0x02 Write -&gt; 0x06 4-Byte ACK</text>

    <text x="60" y="1020" font-size="11.5" font-weight="700" fill="#0369A1">• 0xAA Chain Discovery (UART2 J2):</text>
    <text x="275" y="1020" font-size="11.2" font-weight="600" fill="#1E293B">Seed (5B) -&gt; +2B/Block on Pin 3 -&gt; Smart End loops via Pin 4 RETURN_BUS</text>

    <text x="60" y="1046" font-size="11.5" font-weight="700" fill="#047857">• 0xBB Live Telemetry (Pin 3 TX):</text>
    <text x="275" y="1046" font-size="11.2" font-weight="600" fill="#1E293B">Active Step 1..N (Green LED)  |  0x00 Abort  |  0xFF Victory Rainbow</text>

    <text x="60" y="1076" font-size="10.8" font-weight="600" fill="#64748B">Hardware Isolation: J1 &amp; J2 are independent 4-pin magnetic ports; Action Blocks accept PD6 (UART1) or PD0 (SW UART) seamlessly.</text>
  </g>

  <!-- Robosen K1 BLE Target -->
  <g id="tier-k1" filter="url(#shadow)">
    <rect x="855" y="936" width="785" height="162" rx="16" fill="#ECFDF5" stroke="#059669" stroke-width="2.2" />
    <rect x="855" y="936" width="785" height="34" rx="16" fill="#00B894" />
    <rect x="855" y="954" width="785" height="16" fill="#00B894" />
    <text x="1247" y="958" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="middle">ROBOSEN K1 HUMANOID TARGET (BLE Service 0xFFE0 / Characteristic 0xFFE1)</text>

    <text x="875" y="994" font-size="11.5" font-weight="700" fill="#065F46">• Wire Framing:</text>
    <text x="990" y="994" font-size="11.2" font-weight="600" fill="#1E293B">[0xFF, 0xFF, NumBytes, Opcode, Payload..., Checksum] (Shared across ESP32, Python &amp; Node.js)</text>

    <text x="875" y="1020" font-size="11.5" font-weight="700" fill="#065F46">• Control Paths:</text>
    <text x="990" y="1020" font-size="11.2" font-weight="600" fill="#1E293B">ESP32-S3 Master uses abortableDelay() + 0x0C Stop; Python daemon additionally parses 0x64 100% ACK</text>

    <text x="875" y="1046" font-size="11.5" font-weight="700" fill="#065F46">• K1 Actuators:</text>
    <text x="990" y="1046" font-size="11.2" font-weight="600" fill="#1E293B">17 Smart Servos (ALL_JOINTS), Predefined Stunts (0x17), Locomotion (0x01..0x08), Emergency Stop (0x0C)</text>

    <text x="875" y="1076" font-size="10.8" font-weight="600" fill="#047857">Field Operation: ESP32-S3 Master -&gt; K1 (screenless standalone). Host PC Mode: Python / RobosenJS -&gt; K1 directly via macOS/OS BLE.</text>
  </g>

  <!-- ==================== CROSS-TIER ARROWS ==================== -->
  <path d="M 432 512 L 432 534" fill="none" stroke="#6C5CE7" stroke-width="2.5" marker-start="url(#arrow-purple)" marker-end="url(#arrow-purple)" />
  <path d="M 432 894 L 432 936" fill="none" stroke="#2D3436" stroke-width="2.5" marker-start="url(#arrow-dark)" marker-end="url(#arrow-dark)" />
  <path d="M 1247 894 L 1247 936" fill="none" stroke="#0984E3" stroke-width="2.5" marker-start="url(#arrow-blue)" marker-end="url(#arrow-blue)" />
  <path d="M 489 432 L 522 432 L 522 520 L 840 520 L 840 1005 L 855 1005" fill="none" stroke="#00B894" stroke-width="2.5" stroke-dasharray="6,4" marker-end="url(#arrow-green)" />

  <!-- Footer Summary Pill Bar -->
  <g transform="translate(40, 1114)">
    <rect x="0" y="0" width="1600" height="46" rx="12" fill="#FFFFFF" stroke="#DFE6E9" stroke-width="1.5" />
    <text x="28" y="28" font-size="12.5" font-weight="800" fill="#2D3436">FLOWS:</text>

    <line x1="100" y1="24" x2="140" y2="24" stroke="#6C5CE7" stroke-width="2.5" />
    <text x="150" y="28" font-size="12" font-weight="600" fill="#475569">Master &lt;-&gt; CH32V003 Pogo Serial (0xCF / 0xAA / 0xBB)</text>

    <line x1="535" y1="24" x2="575" y2="24" stroke="#00B894" stroke-width="2.5" stroke-dasharray="6,4" />
    <text x="585" y="28" font-size="12" font-weight="600" fill="#475569">ESP32-S3 Standalone BLE Central -&gt; K1</text>

    <line x1="895" y1="24" x2="935" y2="24" stroke="#0984E3" stroke-width="2.5" />
    <text x="945" y="28" font-size="12" font-weight="600" fill="#475569">Host Python / Node.js Direct BLE &lt;-&gt; K1</text>

    <line x1="1265" y1="24" x2="1305" y2="24" stroke="#D97706" stroke-width="2.5" />
    <text x="1315" y="28" font-size="12" font-weight="600" fill="#475569">Hardware Lock Arbiter (J1 &gt; J2)</text>
  </g>
</svg>
'''

repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out_dir = os.path.join(repo_root, 'docs', 'diagrams')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'robosen_system_software_architecture.svg')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(svg_content)
print(f'SVG successfully generated at: {out_path}')
