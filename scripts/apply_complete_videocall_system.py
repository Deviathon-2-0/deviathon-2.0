import os
import re

def main():
    file_path = os.path.join('frontend', 'pages', 'mock-interview.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --------------------------------------------------------------------------
    # 1. REPLACE PREREQUISITE MODAL SETUP CHECKLIST HTML
    # --------------------------------------------------------------------------
    old_prereq_checklist = '''        <!-- Right Column: Setup Checklist (8 Real Verified Checks) -->
        <div class="flex flex-col">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-[#4F6B2D]"></span>
              <span class="text-xs font-bold uppercase tracking-wider text-[#4F6B2D]">Setup Checklist</span>
            </div>
            <span id="prereq-checklist-counter" class="text-xs font-bold text-[#AA7000] bg-[#FBF3E0] px-2.5 py-0.5 rounded-full">0/8 Verified</span>
          </div>

          <div class="space-y-2 mb-6">
            <!-- 1 -->
            <div class="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E8DFD0] text-xs">
              <span class="text-[#2C1F0E] font-medium">Interview setup completed.</span>
              <span class="text-[#4F6B2D] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span></span>
            </div>

            <!-- 2 -->
            <div class="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E8DFD0] text-xs">
              <span class="text-[#2C1F0E] font-medium">Your browser is compatible with our system.</span>
              <span class="text-[#4F6B2D] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span></span>
            </div>

            <!-- 3 -->
            <div class="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E8DFD0] text-xs" id="chk-mic-row">
              <span class="text-[#2C1F0E] font-medium">The microphone is enabled.</span>
              <span id="chk-mic-status" class="text-[#4F6B2D] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span></span>
            </div>

            <!-- 4 -->
            <div class="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E8DFD0] text-xs" id="chk-cam-row">
              <span class="text-[#2C1F0E] font-medium">The Camera is enabled.</span>
              <span id="chk-cam-status" class="text-[#4F6B2D] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span></span>
            </div>

            <!-- 5 -->
            <div class="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E8DFD0] text-xs">
              <span class="text-[#2C1F0E] font-medium">The internet upload speed is functioning consistently.</span>
              <span class="text-[#4F6B2D] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span></span>
            </div>

            <!-- 6 -->
            <div class="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E8DFD0] text-xs">
              <span class="text-[#2C1F0E] font-medium">The internet download speed is functioning consistently.</span>
              <span class="text-[#4F6B2D] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span></span>
            </div>

            <!-- 7 -->
            <div class="flex items-center justify-between p-2.5 rounded-xl bg-white border border-[#E8DFD0] text-xs">
              <span class="text-[#2C1F0E] font-medium">Voice quality is Good.</span>
              <span class="text-[#4F6B2D] font-bold flex items-center gap-1"><span class="material-symbols-outlined text-base">check_circle</span></span>
            </div>

            <!-- 8: Sound Check with Interactive Play Button -->
            <div class="p-3 rounded-xl bg-[#FAF6EE] border border-[#AA7000]/30 text-xs">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-1.5 font-bold text-[#2C1F0E]">
                  <span class="material-symbols-outlined text-base text-[#AA7000]">volume_up</span>
                  <span>Check System Sound</span>
                </div>
                <span id="chk-sound-status" class="text-[#7F766C] font-semibold text-[11px]">Pending Test</span>
              </div>
              <button type="button" onclick="testSystemAudio()" id="play-sound-btn" class="w-full py-2 rounded-lg bg-[#2C1F0E] hover:bg-[#AA7000] text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-sm cursor-pointer">
                <span class="material-symbols-outlined text-sm">play_arrow</span>
                <span>Play Evaluator Voice Sample</span>
              </button>
            </div>
          </div>

          <!-- Final START PRACTICE Action -->
          <button type="button" onclick="startFinalPracticeSession()" id="prereq-start-btn" class="w-full py-3.5 rounded-full bg-[#2C1F0E] hover:bg-[#AA7000] text-white text-xs sm:text-sm font-bold shadow-md transition-all transform hover:-translate-y-0.5 flex items-center justify-center gap-2 cursor-pointer">
            <span>START PRACTICE</span>
            <span class="material-symbols-outlined text-base">arrow_forward</span>
          </button>
        </div>'''

    new_prereq_checklist = '''        <!-- Right Column: Interactive Setup Checklist (All 8 Checked One by One) -->
        <div class="flex flex-col">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-[#AA7000] animate-pulse"></span>
              <span class="text-xs font-bold uppercase tracking-wider text-[#2C1F0E]">System Prerequisite Checklist</span>
            </div>
            <span id="prereq-checklist-counter" class="text-xs font-bold text-[#AA7000] bg-[#FBF3E0] px-3 py-1 rounded-full border border-[#E8C97A]/40">0/8 Verified</span>
          </div>

          <div class="space-y-2 mb-5">
            <!-- 1 -->
            <div id="chk-row-1" class="flex items-center justify-between p-2.5 rounded-xl bg-[#FFFDF8] border border-[#E8DFD0] text-xs transition-all">
              <span class="text-[#2C1F0E] font-medium flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-[#FAF6EE] text-[10px] font-bold text-[#7F766C] flex items-center justify-center border border-[#E8DFD0]">1</span>
                Interview setup completed
              </span>
              <div id="chk-status-1" class="text-slate-400 font-semibold text-[11px] flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">radio_button_unchecked</span>
                <span>Pending</span>
              </div>
            </div>

            <!-- 2 -->
            <div id="chk-row-2" class="flex items-center justify-between p-2.5 rounded-xl bg-[#FFFDF8] border border-[#E8DFD0] text-xs transition-all">
              <span class="text-[#2C1F0E] font-medium flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-[#FAF6EE] text-[10px] font-bold text-[#7F766C] flex items-center justify-center border border-[#E8DFD0]">2</span>
                Browser compatibility verified
              </span>
              <div id="chk-status-2" class="text-slate-400 font-semibold text-[11px] flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">radio_button_unchecked</span>
                <span>Pending</span>
              </div>
            </div>

            <!-- 3 -->
            <div id="chk-row-3" class="flex items-center justify-between p-2.5 rounded-xl bg-[#FFFDF8] border border-[#E8DFD0] text-xs transition-all">
              <span class="text-[#2C1F0E] font-medium flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-[#FAF6EE] text-[10px] font-bold text-[#7F766C] flex items-center justify-center border border-[#E8DFD0]">3</span>
                Microphone input enabled
              </span>
              <div id="chk-status-3" class="text-slate-400 font-semibold text-[11px] flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">radio_button_unchecked</span>
                <span>Pending</span>
              </div>
            </div>

            <!-- 4 -->
            <div id="chk-row-4" class="flex items-center justify-between p-2.5 rounded-xl bg-[#FFFDF8] border border-[#E8DFD0] text-xs transition-all">
              <span class="text-[#2C1F0E] font-medium flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-[#FAF6EE] text-[10px] font-bold text-[#7F766C] flex items-center justify-center border border-[#E8DFD0]">4</span>
                Camera stream enabled
              </span>
              <div id="chk-status-4" class="text-slate-400 font-semibold text-[11px] flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">radio_button_unchecked</span>
                <span>Pending</span>
              </div>
            </div>

            <!-- 5 -->
            <div id="chk-row-5" class="flex items-center justify-between p-2.5 rounded-xl bg-[#FFFDF8] border border-[#E8DFD0] text-xs transition-all">
              <span class="text-[#2C1F0E] font-medium flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-[#FAF6EE] text-[10px] font-bold text-[#7F766C] flex items-center justify-center border border-[#E8DFD0]">5</span>
                Internet upload speed test
              </span>
              <div id="chk-status-5" class="text-slate-400 font-semibold text-[11px] flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">radio_button_unchecked</span>
                <span>Pending</span>
              </div>
            </div>

            <!-- 6 -->
            <div id="chk-row-6" class="flex items-center justify-between p-2.5 rounded-xl bg-[#FFFDF8] border border-[#E8DFD0] text-xs transition-all">
              <span class="text-[#2C1F0E] font-medium flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-[#FAF6EE] text-[10px] font-bold text-[#7F766C] flex items-center justify-center border border-[#E8DFD0]">6</span>
                Internet download speed test
              </span>
              <div id="chk-status-6" class="text-slate-400 font-semibold text-[11px] flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">radio_button_unchecked</span>
                <span>Pending</span>
              </div>
            </div>

            <!-- 7 -->
            <div id="chk-row-7" class="flex items-center justify-between p-2.5 rounded-xl bg-[#FFFDF8] border border-[#E8DFD0] text-xs transition-all">
              <span class="text-[#2C1F0E] font-medium flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-[#FAF6EE] text-[10px] font-bold text-[#7F766C] flex items-center justify-center border border-[#E8DFD0]">7</span>
                Voice acoustic quality verified
              </span>
              <div id="chk-status-7" class="text-slate-400 font-semibold text-[11px] flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">radio_button_unchecked</span>
                <span>Pending</span>
              </div>
            </div>

            <!-- 8: Sound Check with Interactive Play Button -->
            <div id="chk-row-8" class="p-3 rounded-xl bg-[#FAF6EE] border border-[#AA7000]/30 text-xs transition-all">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2 font-bold text-[#2C1F0E]">
                  <span class="w-4 h-4 rounded-full bg-[#2C1F0E] text-[10px] font-bold text-white flex items-center justify-center">8</span>
                  <span>Check System Sound &amp; Evaluator Voice</span>
                </div>
                <div id="chk-status-8" class="text-[#AA7000] font-semibold text-[11px] flex items-center gap-1">
                  <span>Awaiting Sound Sample</span>
                </div>
              </div>
              <button type="button" onclick="testSystemAudio()" id="play-sound-btn" class="w-full py-2.5 rounded-xl bg-[#2C1F0E] hover:bg-[#AA7000] text-white text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-sm cursor-pointer">
                <span class="material-symbols-outlined text-sm">play_arrow</span>
                <span>Play Evaluator Voice Sample</span>
              </button>
            </div>
          </div>

          <!-- Final START PRACTICE Action (Locked until all 8 are verified) -->
          <button type="button" onclick="startFinalPracticeSession()" id="prereq-start-btn" disabled class="w-full py-3.5 rounded-full bg-[#E8DFD0] text-[#7F766C] text-xs sm:text-sm font-bold shadow-sm transition-all flex items-center justify-center gap-2 cursor-not-allowed opacity-60">
            <span class="material-symbols-outlined text-sm">lock</span>
            <span id="prereq-start-text">COMPLETE ALL 8 CHECKS TO START (0/8)</span>
          </button>
        </div>'''

    norm_content = content.replace('\r\n', '\n')
    norm_old_prereq = old_prereq_checklist.replace('\r\n', '\n')
    norm_new_prereq = new_prereq_checklist.replace('\r\n', '\n')

    if norm_old_prereq in norm_content:
        norm_content = norm_content.replace(norm_old_prereq, norm_new_prereq)
        print("1. Replaced prerequisite modal checklist HTML: SUCCESS")
    else:
        print("1. WARNING: Prerequisite checklist block not matched directly, checking partial replacement...")
        # Fallback regex replace for checklist
        patt = re.compile(r'<!-- Right Column: Setup Checklist.*?<!-- Final START PRACTICE Action -->.*?<\/button>\s*<\/div>', re.DOTALL)
        if patt.search(norm_content):
            norm_content = patt.sub(norm_new_prereq, norm_content, count=1)
            print("1. Replaced prerequisite modal checklist via regex: SUCCESS")
        else:
            print("1. ERROR: Could not find prerequisite checklist block.")

    # --------------------------------------------------------------------------
    # 2. REPLACE INTERVIEW STAGE SCREEN (Full Space Utilization, Video Call UI)
    # --------------------------------------------------------------------------
    # Find the entire interview-stage div and replace it with modern Google Meet video call UI
    stage_start_tag = '<div id="interview-stage"'
    app_logic_tag = '<!-- ========================================================================\n       APPLICATION LOGIC & QUESTION REPOSITORY ENGINE'
    if app_logic_tag not in norm_content:
        app_logic_tag = 'APPLICATION LOGIC & QUESTION REPOSITORY ENGINE'

    idx_stage = norm_content.find(stage_start_tag)
    idx_app = norm_content.find(app_logic_tag)

    if idx_stage != -1 and idx_app != -1:
        # Create the new Interview Stage HTML matching the user reference screenshot
        new_interview_stage_html = '''<div id="interview-stage" class="hidden h-full flex flex-col bg-[#0A0603] text-white overflow-hidden relative select-none">
    
    <!-- Top Header Bar: Status, Question Progress Pills with Strict Locking, Timer & Mode Switcher -->
    <header class="h-14 border-b border-[#2A1C0A] px-4 sm:px-6 flex items-center justify-between shrink-0 bg-[#0F0A05] z-30 shadow-md">
      <!-- Left: Recording Status & Active Role -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1 rounded-full bg-red-950/70 border border-red-700/60 text-red-200 text-xs font-mono font-bold shadow-inner">
          <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping"></span>
          <span>REC</span>
          <span id="stage-session-timer">00:00</span>
        </div>
        <div class="h-4 w-px bg-white/10 hidden sm:block"></div>
        <div class="hidden sm:flex items-center gap-2">
          <span id="stage-role-title" class="text-xs sm:text-sm font-bold text-white tracking-tight truncate max-w-[220px]">Software Engineer</span>
          <span id="stage-role-level" class="text-[10px] text-[#E8A338] bg-[#2A1D0B] border border-[#AA7000]/40 px-2 py-0.5 rounded font-mono font-bold">SDE 2</span>
          <span id="stage-lang-badge" class="hidden px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#1F160A] text-[#AA7000] border border-[#AA7000]/30">C++</span>
        </div>
      </div>

      <!-- Center: Question Progress Pills (Strictly Locked: Cannot Skip Uncompleted Questions) -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-1.5">
          <span id="stage-progress-label" class="text-[11px] font-mono font-bold text-slate-400 mr-1 hidden md:inline">0/4 SUBMITTED</span>
          <div class="flex items-center gap-1" id="stage-question-pills">
            <!-- Dynamic locked/unlocked navigation pills -->
          </div>
          <span id="stage-current-pill" class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-[#AA7000] text-white shadow-sm ml-1">Q1 Current</span>
        </div>
      </div>

      <!-- Right: View Switcher (Video Call <-> Code Compiler), Fullscreen & Exit -->
      <div class="flex items-center gap-2.5">
        <!-- Dual Mode Toggle Button -->
        <button type="button" id="btn-stage-view-toggle" onclick="toggleStageWorkspaceView()" class="px-3.5 py-1.5 rounded-full bg-[#2A1D0B] hover:bg-[#3D2B12] text-[#E8A338] border border-[#AA7000]/50 text-xs font-bold transition-all flex items-center gap-1.5 shadow-sm cursor-pointer" title="Switch between Full Video Call and Code Execution IDE">
          <span class="material-symbols-outlined text-sm" id="stage-view-toggle-icon">code</span>
          <span id="stage-view-toggle-text">Code &amp; Compiler</span>
        </button>

        <button type="button" onclick="toggleFullscreen()" id="btn-fullscreen-toggle" class="p-1.5 rounded-lg bg-[#1A1208] hover:bg-[#2A1D0B] border border-[#3D2E15] text-slate-300 hover:text-white transition-all flex items-center justify-center cursor-pointer" title="Toggle Fullscreen">
          <span class="material-symbols-outlined text-base" id="fullscreen-icon">fullscreen</span>
        </button>

        <button type="button" onclick="exitToSetup()" class="px-3 py-1.5 rounded-lg bg-red-950/40 hover:bg-red-900/60 border border-red-800/60 text-red-200 text-xs font-bold transition-all flex items-center gap-1 cursor-pointer">
          <span class="w-1.5 h-1.5 rounded-sm bg-red-500"></span>
          <span>Exit</span>
        </button>
      </div>
    </header>


    <!-- ======================================================================
         MAIN STAGE CONTAINER: 100% FULL UTILIZATION OF VIEWPORT SPACE
         ====================================================================== -->
    <main class="flex-1 relative w-full h-full overflow-hidden bg-[#0A0603]" id="stage-main-workspace">
      
      <!-- --------------------------------------------------------------------
           VIEW A: FULL IMMERSIVE VIDEO CALL VIEW (Google Meet / Zoom Layout)
           -------------------------------------------------------------------- -->
      <div id="workspace-videocall-view" class="w-full h-full flex flex-col p-3 sm:p-5 relative overflow-hidden transition-all duration-300">
        
        <!-- Large Video Conference Stage: Edge-to-Edge with Smooth Rounded Borders -->
        <div class="relative w-full h-full rounded-3xl overflow-hidden bg-[#120B04] border border-[#3D2E15] shadow-2xl flex items-center justify-center">
          
          <!-- 1. MAIN INTERVIEWER VIDEO (100% Real Video, No Static Images, No Glitch) -->
          <video id="call-interviewer-video" autoplay loop muted playsinline class="w-full h-full object-cover object-center"></video>
          
          <!-- Top-Left Evaluator Persona Pill (Matching User Screenshot style) -->
          <div class="absolute top-5 left-5 px-3.5 py-1.5 rounded-full bg-black/65 backdrop-blur-md border border-white/10 text-xs font-semibold text-white flex items-center gap-2 z-20 shadow-lg">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span id="call-interviewer-name" class="font-bold">Kabir</span>
            <span class="text-slate-300 text-[11px] font-normal" id="call-interviewer-accent">Indian English (North)</span>
          </div>

          <!-- Top-Right Live Audio Channel Pill (Matching screenshot |||| audio icon) -->
          <div class="absolute top-5 right-5 px-3 py-1.5 rounded-full bg-black/65 backdrop-blur-md border border-white/10 text-white flex items-center gap-2 z-20 shadow-lg">
            <div class="flex items-center gap-1">
              <div class="stage-wave-bar"></div>
              <div class="stage-wave-bar" style="animation-delay: 0.2s"></div>
              <div class="stage-wave-bar" style="animation-delay: 0.4s"></div>
            </div>
            <span class="text-[11px] text-emerald-300 font-mono font-bold">HD AUDIO</span>
          </div>

          <!-- 2. CANDIDATE VIDEO TILE (Docked in Video Call, 100% Real Video Stream) -->
          <div id="call-candidate-tile" class="absolute bottom-6 right-6 w-56 sm:w-72 aspect-video rounded-2xl overflow-hidden bg-[#1A1208] border-2 border-white/20 shadow-2xl z-20 group">
            <video id="call-candidate-video" autoplay muted playsinline class="w-full h-full object-cover" style="transform: scaleX(-1);"></video>
            <canvas id="call-candidate-canvas" class="w-full h-full object-cover hidden"></canvas>
            
            <!-- Candidate Persona Tag (Matching User Screenshot translucent pill) -->
            <div class="absolute bottom-2.5 left-2.5 px-2.5 py-1 rounded-full bg-black/75 backdrop-blur-md text-[10px] font-bold text-white z-10 flex items-center gap-1.5">
              <span>You (Candidate)</span>
            </div>

            <!-- Candidate Mic Status Badge (Matching User Screenshot blue/red mic circle) -->
            <div id="candidate-tile-mic-badge" class="absolute bottom-2.5 right-2.5 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs shadow-md z-10 transition-colors">
              <span class="material-symbols-outlined text-xs" id="candidate-tile-mic-icon">mic</span>
            </div>

            <!-- Integrity Matrix HUD Badge -->
            <div class="absolute top-2 left-2 z-10">
              <span class="px-2 py-0.5 rounded-full bg-black/75 backdrop-blur-md border border-emerald-500/40 text-[9px] font-bold text-emerald-400 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> MATRIX
              </span>
            </div>
          </div>

          <!-- 3. TRANSLUCENT FLOATING QUESTION OVERLAY (Hovering over the Video Box) -->
          <div id="call-question-overlay" class="absolute bottom-6 left-6 right-64 sm:right-80 bg-black/80 backdrop-blur-2xl border border-white/15 rounded-3xl p-5 shadow-2xl z-20 transition-all">
            
            <!-- Top Row: Question Pill & Repeat Button -->
            <div class="flex items-center justify-between text-xs mb-2">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-[#AA7000]"></span>
                <span class="font-bold text-[#AA7000] uppercase tracking-wider text-[11px]" id="call-q-badge">QUESTION 1 OF 4 • TECH CODING</span>
              </div>
              <div class="flex items-center gap-2">
                <button type="button" onclick="repeatCurrentQuestion()" class="px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 text-white text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer shadow-sm">
                  <span class="material-symbols-outlined text-sm">replay</span>
                  <span>Repeat</span>
                </button>
                <button type="button" onclick="switchStageView('code')" class="px-2.5 py-1 rounded-full bg-[#AA7000]/30 hover:bg-[#AA7000]/50 text-[#E8C97A] border border-[#AA7000]/50 text-xs font-bold flex items-center gap-1 transition-all cursor-pointer shadow-sm">
                  <span class="material-symbols-outlined text-sm">terminal</span>
                  <span>Open Compiler</span>
                </button>
              </div>
            </div>

            <!-- Question Prompt Text (Crisp, High Contrast Typography) -->
            <p id="call-question-prompt" class="text-sm sm:text-base text-white font-medium leading-relaxed mb-3">
              "Write an optimal function to solve the system constraints described in this round."
            </p>

            <!-- Bottom Row: Candidate Spoken Answer & Submit Controls -->
            <div class="flex items-center justify-between pt-2 border-t border-white/10 gap-3">
              <div class="flex items-center gap-2.5">
                <button type="button" id="call-record-btn" onclick="toggleCandidateAnswerRecording()" class="px-4 py-2 rounded-full bg-[#4F6B2D] hover:bg-[#3E5423] text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-md cursor-pointer">
                  <span class="material-symbols-outlined text-sm">mic</span>
                  <span id="call-record-btn-text">Start Spoken Answer</span>
                </button>
                <div class="flex items-center gap-1 text-[11px] text-slate-300">
                  <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span>Voice Channel Active</span>
                </div>
              </div>

              <!-- Submit Answer Button (Strict: Only Submitting Unlocks Next Question) -->
              <button type="button" id="call-submit-btn" onclick="submitCurrentAnswer()" class="px-5 py-2 rounded-full bg-[#AA7000] hover:bg-[#8C5D00] text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-lg cursor-pointer transform hover:-translate-y-0.5">
                <span id="call-submit-btn-text">Submit Answer &amp; Proceed</span>
                <span class="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>

            <!-- Real-time Live Candidate Speech Transcription Caption Box -->
            <div id="call-transcript-box" class="mt-2.5 p-3 rounded-xl bg-black/60 border border-white/10 hidden">
              <div class="flex items-center justify-between text-[10px] text-[#AA7000] font-bold mb-1">
                <span>LIVE SPEECH RECOGNITION (TRANSCRIBING...)</span>
                <span class="text-emerald-400 flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Active Mic
                </span>
              </div>
              <p id="call-transcript-text" class="text-xs text-slate-200 italic font-mono leading-relaxed">Speak your answer clearly into your microphone...</p>
            </div>

          </div>

          <!-- 4. FLOATING VIDEO CALL CONTROL DOCK (Google Meet / Zoom Style Bottom Center Island) -->
          <div class="absolute bottom-6 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full bg-black/80 backdrop-blur-xl border border-white/15 shadow-2xl flex items-center gap-3 z-30">
            <!-- Mic Toggle Button -->
            <button type="button" id="dock-btn-mic" onclick="toggleMic()" class="w-10 h-10 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center transition-all cursor-pointer shadow-md" title="Mute / Unmute Microphone">
              <span class="material-symbols-outlined text-base" id="dock-icon-mic">mic</span>
            </button>

            <!-- Camera Toggle Button -->
            <button type="button" id="dock-btn-cam" onclick="toggleCam()" class="w-10 h-10 rounded-full bg-slate-700 hover:bg-slate-600 text-white flex items-center justify-center transition-all cursor-pointer shadow-md" title="Turn Camera On / Off">
              <span class="material-symbols-outlined text-base" id="dock-icon-cam">videocam</span>
            </button>

            <!-- Switch to Code Editor Button -->
            <button type="button" onclick="switchStageView('code')" class="px-4 py-2 rounded-full bg-[#2A1D0B] hover:bg-[#3D2B12] text-[#E8A338] border border-[#AA7000]/50 text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shadow-md" title="Open Code Editor & Compiler">
              <span class="material-symbols-outlined text-sm">terminal</span>
              <span>Open Code &amp; Compiler</span>
            </button>
          </div>

        </div>
      </div>


      <!-- --------------------------------------------------------------------
           VIEW B: SPLIT CODE EXECUTION & COMPILER VIEW (Full IDE Workspace)
           -------------------------------------------------------------------- -->
      <div id="workspace-compiler-view" class="hidden w-full h-full flex overflow-hidden transition-all duration-300">
        
        <!-- Left Column: Problem Prompt, I/O Specs, Live STT & Execution Actions -->
        <div class="w-[42%] min-w-[340px] max-w-[500px] border-r border-[#2A1C0A] flex flex-col bg-[#140D05]">
          
          <!-- Header with Question Title & Repeat Button -->
          <div class="p-4 border-b border-[#2A1C0A] flex items-center justify-between">
            <div>
              <div class="text-[10px] uppercase font-bold text-[#AA7000] tracking-wider" id="code-pane-q-number">QUESTION 1 OF 4</div>
              <h2 class="text-xs sm:text-sm font-bold text-white mt-0.5" id="code-pane-instruction-title">Write a code solution for the situation described below.</h2>
            </div>
            <div class="flex items-center gap-1.5">
              <button type="button" onclick="repeatCurrentQuestion()" class="w-8 h-8 rounded-full bg-[#2A1D0B] hover:bg-[#3D2B12] text-[#E8A338] border border-[#AA7000]/50 flex items-center justify-center transition-all shadow-sm cursor-pointer" title="Repeat Question Audio">
                <span class="material-symbols-outlined text-base">replay</span>
              </button>
              <button type="button" onclick="switchStageView('video')" class="px-2.5 py-1 rounded-full bg-blue-950/60 hover:bg-blue-900/80 text-blue-300 border border-blue-700/50 text-[11px] font-bold flex items-center gap-1 transition-all cursor-pointer" title="Return to Fullscreen Video Call">
                <span class="material-symbols-outlined text-xs">videocam</span>
                <span>Video Call</span>
              </button>
            </div>
          </div>

          <!-- Code / Instructions Tabs -->
          <div class="flex items-center gap-4 px-4 pt-3 border-b border-[#2A1C0A] bg-[#110A03]">
            <button type="button" onclick="switchProblemTab('code')" id="tab-prob-code" class="pb-2 text-xs font-bold border-b-2 border-[#AA7000] text-white transition-all cursor-pointer">Code</button>
            <button type="button" onclick="switchProblemTab('instructions')" id="tab-prob-instructions" class="pb-2 text-xs font-semibold border-b-2 border-transparent text-slate-400 hover:text-white transition-all cursor-pointer">Instructions</button>
          </div>

          <!-- Tab Content 1: Code Problem Description -->
          <div id="tab-content-prob-code" class="p-4 flex-1 overflow-y-auto custom-scroll space-y-3">
            <div id="tech-problem-card" class="p-4 rounded-xl bg-[#1B1207] border border-[#2E200E] text-xs text-slate-200 font-mono leading-relaxed space-y-3 shadow-inner">
              <p id="tech-problem-description" class="text-white font-medium">
                Write a function to remove the minimum number of invalid parentheses to make the input string valid. Return all possible results.
              </p>
              <div class="bg-[#120B04] p-3 rounded-lg border border-[#2A1C0A] space-y-1.5 text-slate-300">
                <div><strong class="text-[#E8A338]">Input:</strong> <span id="tech-problem-input">"a)bc(d)"</span></div>
                <div><strong class="text-[#4F6B2D]">Output:</strong> <span id="tech-problem-output">"abc(d)"</span></div>
                <div id="tech-problem-constraints-wrap" class="pt-1 text-[11px] text-slate-400">
                  <strong class="text-slate-300">Constraints:</strong> <span id="tech-problem-constraints">1 &lt;= s.length &lt;= 10^4</span>
                </div>
              </div>
            </div>

            <!-- Live Spoken Transcript for Think-Out-Loud in Code Pane -->
            <div id="code-transcript-wrap" class="p-3 rounded-xl bg-[#1B1207] border border-[#2E200E] text-xs font-mono hidden">
              <div class="flex items-center justify-between text-[10px] text-[#AA7000] font-bold mb-1">
                <span>THINK-OUT-LOUD LIVE TRANSCRIPT</span>
                <span class="text-emerald-400 flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Live STT
                </span>
              </div>
              <p id="code-transcript-text" class="text-slate-200 italic">Listening to your verbal explanation...</p>
            </div>
          </div>

          <!-- Tab Content 2: Instructions & Rubrics -->
          <div id="tab-content-prob-instructions" class="hidden p-4 flex-1 overflow-y-auto custom-scroll space-y-3">
            <div class="p-4 rounded-xl bg-[#1B1207] border border-[#2E200E] text-xs text-slate-300 leading-relaxed space-y-3">
              <h3 class="font-bold text-white text-sm">Evaluation Criteria &amp; Guidelines</h3>
              <p id="tech-instructions-text">
                Your code is evaluated on correctness, time/space complexity, modularity, and adherence to production coding standards.
              </p>
              <ul class="list-disc pl-4 space-y-1 text-[11px] text-slate-400">
                <li>Optimize for asymptotic runtime complexity.</li>
                <li>Handle edge cases (empty inputs, single character, extremes).</li>
                <li>Write clean, readable variable names and modular helper functions.</li>
                <li>Click <strong>Execute</strong> to test your code against standard validation test suites.</li>
              </ul>
            </div>
          </div>

          <!-- Left Pane Footer: Record Voice + Execute Code Button -->
          <div class="p-3 border-t border-[#2A1C0A] bg-[#100A03] flex items-center justify-between text-[11px] text-slate-400 gap-2">
            <button type="button" id="code-record-answer-btn" onclick="toggleCandidateAnswerRecording()" class="px-3 py-1.5 rounded-lg bg-[#4F6B2D] hover:bg-[#3E5423] text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm cursor-pointer">
              <span class="material-symbols-outlined text-sm">mic</span>
              <span id="code-record-btn-text">Record Voice</span>
            </button>
            <div class="flex items-center gap-2">
              <button onclick="executeCurrentCode()" class="px-3.5 py-1.5 rounded-lg bg-[#2A1D0B] hover:bg-[#3D2B12] text-[#E8A338] border border-[#AA7000]/50 font-bold flex items-center gap-1 shadow-sm transition-all cursor-pointer">
                <span class="material-symbols-outlined text-xs">play_arrow</span>
                <span>Execute</span>
              </button>
              <button onclick="submitCurrentAnswer()" class="px-3.5 py-1.5 rounded-lg bg-[#AA7000] hover:bg-[#8C5D00] text-white font-bold flex items-center gap-1 shadow-sm transition-all cursor-pointer">
                <span>Submit Code</span>
                <span class="material-symbols-outlined text-xs">arrow_forward</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Right Column: Code Editor & Interactive Terminal Output -->
        <div class="flex-1 flex flex-col bg-[#0D0803] relative">
          
          <!-- PiP Tiles inside IDE (Interviewer + Candidate Live Video) -->
          <div class="absolute top-12 right-4 z-30 flex flex-col gap-2 pointer-events-auto">
            <div class="w-44 aspect-video rounded-xl overflow-hidden bg-[#1A1208] border border-white/20 shadow-2xl relative">
              <video id="pip-interviewer-video" autoplay loop muted playsinline class="w-full h-full object-cover object-center"></video>
              <div class="absolute bottom-1 left-1.5 px-2 py-0.5 rounded bg-black/75 backdrop-blur-sm text-[9px] text-white font-semibold flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span id="pip-interviewer-name">Kabir</span>
              </div>
            </div>
            <div class="w-44 aspect-video rounded-xl overflow-hidden bg-[#1A1208] border border-white/20 shadow-2xl relative">
              <video id="pip-candidate-video" autoplay muted playsinline class="w-full h-full object-cover" style="transform: scaleX(-1);"></video>
              <div class="absolute bottom-1 left-1.5 px-2 py-0.5 rounded bg-black/75 backdrop-blur-sm text-[9px] text-white font-semibold flex items-center gap-1">
                <span>You</span>
              </div>
            </div>
          </div>

          <div class="h-9 bg-[#170F05] border-b border-[#2A1C0A] px-4 flex items-center justify-between text-xs text-slate-400 font-mono">
            <span id="editor-filename" class="text-slate-200 font-semibold">solution.cpp</span>
            <span id="editor-lang-indicator" class="text-[11px] text-[#AA7000]">C++ (GCC 14)</span>
          </div>

          <div class="flex-1 flex overflow-hidden relative">
            <!-- Dynamic Line Numbers -->
            <div id="editor-line-numbers" class="w-10 bg-[#120B04] border-r border-[#2A1C0A] py-3 text-right pr-2 text-xs font-mono text-[#5A452B] select-none overflow-hidden">
              1<br/>2<br/>3<br/>4<br/>5<br/>6<br/>7<br/>8<br/>9<br/>10<br/>11<br/>12<br/>13<br/>14<br/>15
            </div>
            <textarea id="code-editor-textarea" spellcheck="false" class="flex-1 bg-transparent text-[#F0E6D2] p-3 text-xs sm:text-sm font-mono leading-relaxed border-0 focus:outline-none focus:ring-0 resize-none editor-textarea custom-scroll"></textarea>
          </div>

          <!-- Console Output -->
          <div class="h-32 bg-[#120B04] border-t border-[#2A1C0A] p-3 font-mono text-xs overflow-y-auto custom-scroll text-[#7BB045]" id="code-console-output">
            <div class="text-slate-500">[System] Compiler ready. Click 'Execute' to compile and test code in sandbox.</div>
          </div>
        </div>

      </div>

    </main>
  </div>'''

        norm_content = norm_content[:idx_stage] + new_interview_stage_html + '\n\n  ' + norm_content[idx_app:]
        print("2. Replaced entire interview stage HTML with responsive video call UI: SUCCESS")
    else:
        print(f"2. ERROR: Could not locate stage boundaries (idx_stage: {idx_stage}, idx_app: {idx_app})")

    # Write back the updated HTML
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(norm_content)
    print("Stage 1 HTML modifications complete.")

if __name__ == '__main__':
    main()
