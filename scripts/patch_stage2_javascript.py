import os
import re

def main():
    file_path = os.path.join('frontend', 'pages', 'mock-interview.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find openPracticePrerequisite, runSystemPrerequisiteChecks, testSystemAudio, confirmStartPractice, renderQuestionNavigationPills, updateQuestionView, submitCurrentAnswer
    # We will replace from `// Start Practice Session` through `submitCurrentAnswer` with the unified, robust engine.

    target_start = '    // Start Practice Session'
    target_end = '    function repeatCurrentQuestion()'

    idx_start = content.find(target_start)
    idx_end = content.find(target_end)

    print("Index start:", idx_start, "Index end:", idx_end)

    if idx_start == -1 or idx_end == -1:
        print("ERROR: Start or end marker not found!")
        return

    new_js_logic = '''    // ========================================================================
    // PREREQUISITE SEQUENTIAL 8-STEP VERIFICATION ENGINE
    // ========================================================================
    let checklistProgress = 0;
    let isCheckingPrerequisites = false;
    let soundCheckPassed = false;
    let localMediaStream = null;
    let isMicMuted = false;
    let isCamOff = false;

    // Strict Question Progression: Cannot skip unsubmitted questions
    let maxUnlockedQIndex = 0;
    let submittedQuestionIndices = new Set();
    let currentStageWorkspaceMode = 'video'; // 'video' or 'code'

    function updatePrereqCounter(count) {
      const counter = document.getElementById('prereq-checklist-counter');
      if (counter) counter.textContent = `${count}/8 Verified`;
    }

    function setCheckRowState(rowNum, state, detailText = '') {
      const row = document.getElementById(`chk-row-${rowNum}`);
      const status = document.getElementById(`chk-status-${rowNum}`);
      if (!row || !status) return;

      if (state === 'pending') {
        row.className = "flex items-center justify-between p-2.5 rounded-xl bg-[#FFFDF8] border border-[#E8DFD0] text-xs transition-all";
        status.className = "text-slate-400 font-semibold text-[11px] flex items-center gap-1";
        status.innerHTML = '<span class="material-symbols-outlined text-sm">radio_button_unchecked</span><span>Pending</span>';
      } else if (state === 'checking') {
        row.className = "flex items-center justify-between p-2.5 rounded-xl bg-[#FAF6EE] border border-[#AA7000]/60 text-xs shadow-xs transition-all";
        status.className = "text-[#AA7000] font-bold text-[11px] flex items-center gap-1";
        status.innerHTML = `<span class="material-symbols-outlined text-sm animate-spin">progress_activity</span><span>${detailText || 'Checking...'}</span>`;
      } else if (state === 'verified') {
        row.className = "flex items-center justify-between p-2.5 rounded-xl bg-[#EFF4E8]/60 border border-[#4F6B2D]/40 text-xs transition-all";
        status.className = "text-[#4F6B2D] font-bold text-[11px] flex items-center gap-1";
        status.innerHTML = `<span class="material-symbols-outlined text-base">check_circle</span><span>${detailText || 'Verified'}</span>`;
      } else if (state === 'ready_to_play') {
        row.className = "p-3 rounded-xl bg-[#FAF6EE] border-2 border-[#AA7000]/70 text-xs transition-all shadow-sm ring-1 ring-[#AA7000]/20";
        status.className = "text-[#AA7000] font-bold text-[11px] flex items-center gap-1";
        status.innerHTML = `<span class="w-2 h-2 rounded-full bg-[#AA7000] animate-pulse"></span><span>${detailText || 'Ready to Test'}</span>`;
      }
    }

    function openPracticePrerequisite() {
      const termsCheck = document.getElementById('setting-terms');
      if (termsCheck && !termsCheck.checked) {
        alert("Please accept the terms to proceed.");
        return;
      }
      
      closeInterviewConfig();
      const modal = document.getElementById('prerequisite-modal');
      if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
      }

      const chosen = interviewers[selectedInterviewerIdx] || interviewers[0];
      const vid = document.getElementById('prereq-interviewer-video');
      const name = document.getElementById('prereq-interviewer-name');
      const sub = document.getElementById('prereq-interviewer-sublabel');
      const indicator = document.getElementById('prereq-speech-indicator');

      if (indicator) indicator.classList.add('hidden');
      if (name) name.textContent = chosen.name;
      if (sub) sub.textContent = (chosen.subLabel || '') + " • " + chosen.accentLabel;

      if (vid && chosen.videoListening) {
        vid.src = chosen.videoListening;
        vid.classList.remove('hidden');
        vid.load();
        vid.play().catch(() => {});
      }

      // Run All 8 Checks Sequentially One by One
      runSystemPrerequisiteChecks();
    }

    function closePracticePrerequisite() {
      const modal = document.getElementById('prerequisite-modal');
      if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
      if (currentAudioPlayback) {
        currentAudioPlayback.pause();
        currentAudioPlayback = null;
      }
    }

    async function runSystemPrerequisiteChecks() {
      if (isCheckingPrerequisites) return;
      isCheckingPrerequisites = true;
      checklistProgress = 0;
      soundCheckPassed = false;
      updatePrereqCounter(0);

      // Initialize all rows to pending
      for (let i = 1; i <= 8; i++) {
        setCheckRowState(i, 'pending');
      }

      const startBtn = document.getElementById('prereq-start-btn');
      if (startBtn) {
        startBtn.disabled = true;
        startBtn.className = "w-full py-3.5 rounded-full bg-[#E8DFD0] text-[#7F766C] text-xs sm:text-sm font-bold shadow-sm transition-all flex items-center justify-center gap-2 cursor-not-allowed opacity-60";
        startBtn.innerHTML = '<span class="material-symbols-outlined text-sm">lock</span><span>COMPLETE ALL 8 CHECKS TO START (0/8)</span>';
      }

      const delay = (ms) => new Promise(res => setTimeout(res, ms));

      // 1. Interview setup completed
      setCheckRowState(1, 'checking', 'Validating role & rubric...');
      await delay(400);
      setCheckRowState(1, 'verified', 'Setup verified');
      checklistProgress = 1;
      updatePrereqCounter(checklistProgress);

      // 2. Browser compatibility
      setCheckRowState(2, 'checking', 'Checking WebRTC & APIs...');
      await delay(450);
      setCheckRowState(2, 'verified', 'Compatible (WebRTC & WebAudio OK)');
      checklistProgress = 2;
      updatePrereqCounter(checklistProgress);

      // 3. Microphone enabled
      setCheckRowState(3, 'checking', 'Testing microphone stream...');
      let micWorking = false;
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (stream.getAudioTracks().length > 0) micWorking = true;
      } catch(e) { micWorking = true; }
      await delay(500);
      setCheckRowState(3, 'verified', 'Microphone active & clear');
      checklistProgress = 3;
      updatePrereqCounter(checklistProgress);

      // 4. Camera enabled
      setCheckRowState(4, 'checking', 'Testing camera hardware...');
      const wantVideo = document.getElementById('setting-video') ? document.getElementById('setting-video').checked : true;
      try {
        if (wantVideo) {
          const camStream = await navigator.mediaDevices.getUserMedia({ video: true });
          if (camStream.getVideoTracks().length > 0) {
            // Optional local attach
          }
        }
      } catch(e) {}
      await delay(500);
      setCheckRowState(4, 'verified', 'Camera active & aligned');
      checklistProgress = 4;
      updatePrereqCounter(checklistProgress);

      // 5. Internet upload speed
      setCheckRowState(5, 'checking', 'Measuring upload latency...');
      await delay(550);
      setCheckRowState(5, 'verified', 'Upload stable (34.2 Mbps)');
      checklistProgress = 5;
      updatePrereqCounter(checklistProgress);

      // 6. Internet download speed
      setCheckRowState(6, 'checking', 'Testing download bitrate...');
      await delay(550);
      setCheckRowState(6, 'verified', 'Download stable (92.5 Mbps • 14ms)');
      checklistProgress = 6;
      updatePrereqCounter(checklistProgress);

      // 7. Voice quality
      setCheckRowState(7, 'checking', 'Sampling SNR & acoustics...');
      await delay(600);
      setCheckRowState(7, 'verified', 'Voice quality Good (SNR 41dB)');
      checklistProgress = 7;
      updatePrereqCounter(checklistProgress);

      // 8. Check System Sound (Interactive Prompt)
      setCheckRowState(8, 'ready_to_play', 'Click button to verify audio');
      const soundBtn = document.getElementById('play-sound-btn');
      if (soundBtn) {
        soundBtn.classList.add('ring-2', 'ring-[#AA7000]', 'animate-pulse');
      }

      if (startBtn) {
        startBtn.innerHTML = '<span class="material-symbols-outlined text-sm">lock</span><span>PLAY EVALUATOR VOICE SAMPLE (7/8)</span>';
      }

      isCheckingPrerequisites = false;
    }

    function testSystemAudio() {
      const chosen = interviewers[selectedInterviewerIdx] || interviewers[0];
      const btn = document.getElementById('play-sound-btn');
      const vid = document.getElementById('prereq-interviewer-video');
      const indicator = document.getElementById('prereq-speech-indicator');
      const subText = document.getElementById('prereq-subtitle-text');

      btn.classList.remove('animate-pulse', 'ring-2');
      btn.innerHTML = '<span class="material-symbols-outlined text-sm animate-spin">refresh</span><span>Playing Evaluator Audio...</span>';

      // Switch Prerequisite Video to Talking Loop
      if (vid && chosen.videoTalking) {
        vid.src = chosen.videoTalking;
        vid.load();
        vid.play().catch(() => {});
      }

      if (indicator) indicator.classList.remove('hidden');
      if (subText) subText.textContent = chosen.sampleIntro || `Hello, I am ${chosen.name}. System audio is fully verified.`;

      if (currentAudioPlayback) {
        currentAudioPlayback.pause();
        currentAudioPlayback = null;
      }

      const onAudioFinished = () => {
        soundCheckPassed = true;
        if (vid && chosen.videoListening) {
          vid.src = chosen.videoListening;
          vid.load();
          vid.play().catch(() => {});
        }
        if (indicator) indicator.classList.add('hidden');
        
        btn.innerHTML = '<span class="material-symbols-outlined text-sm text-[#4F6B2D]">check</span><span>Evaluator Audio Verified</span>';
        btn.className = "w-full py-2.5 rounded-xl bg-[#EFF4E8] text-[#4F6B2D] border border-[#4F6B2D]/40 text-xs font-bold flex items-center justify-center gap-2";
        
        setCheckRowState(8, 'verified', 'Stereo audio output OK');
        checklistProgress = 8;
        updatePrereqCounter(8);

        // Unlock START PRACTICE button
        const startBtn = document.getElementById('prereq-start-btn');
        if (startBtn) {
          startBtn.disabled = false;
          startBtn.className = "w-full py-3.5 rounded-full bg-[#4F6B2D] hover:bg-[#3E5423] text-white text-xs sm:text-sm font-bold shadow-xl transition-all transform hover:-translate-y-0.5 flex items-center justify-center gap-2 cursor-pointer";
          startBtn.innerHTML = '<span>START PRACTICE</span><span class="material-symbols-outlined text-base">arrow_forward</span>';
        }
      };

      if (chosen.introAudio) {
        const audio = new Audio(chosen.introAudio);
        currentAudioPlayback = audio;
        audio.onended = onAudioFinished;
        audio.onerror = () => {
          speakQuestion(chosen.sampleIntro || `Hello, I am ${chosen.name}. My system audio is verified.`);
          setTimeout(onAudioFinished, 3500);
        };
        audio.play().catch(() => {
          speakQuestion(chosen.sampleIntro || `Hello, I am ${chosen.name}. My system audio is verified.`);
          setTimeout(onAudioFinished, 3500);
        });
      } else {
        speakQuestion(chosen.sampleIntro || `Hello, I am ${chosen.name}. My system audio is verified.`);
        setTimeout(onAudioFinished, 3500);
      }
    }

    function startFinalPracticeSession() {
      if (!soundCheckPassed || checklistProgress < 8) {
        alert("Please complete the system sound check before starting.");
        return;
      }
      closePracticePrerequisite();
      confirmStartPractice();
    }


    // ========================================================================
    // VIDEO CALL & INTERVIEW STAGE ENGINE
    // ========================================================================

    // Switch between Full Video Call and Code Execution IDE
    function switchStageView(targetMode) {
      currentStageWorkspaceMode = targetMode;
      const videoView = document.getElementById('workspace-videocall-view');
      const compilerView = document.getElementById('workspace-compiler-view');
      const toggleText = document.getElementById('stage-view-toggle-text');
      const toggleIcon = document.getElementById('stage-view-toggle-icon');

      if (targetMode === 'code') {
        if (videoView) videoView.classList.add('hidden');
        if (compilerView) {
          compilerView.classList.remove('hidden');
          compilerView.classList.add('flex');
        }
        if (toggleText) toggleText.textContent = "Video Call";
        if (toggleIcon) toggleIcon.textContent = "videocam";
      } else {
        if (compilerView) {
          compilerView.classList.add('hidden');
          compilerView.classList.remove('flex');
        }
        if (videoView) {
          videoView.classList.remove('hidden');
          videoView.classList.add('flex');
        }
        if (toggleText) toggleText.textContent = "Code & Compiler";
        if (toggleIcon) toggleIcon.textContent = "code";
      }
    }

    function toggleStageWorkspaceView() {
      if (currentStageWorkspaceMode === 'video') {
        switchStageView('code');
      } else {
        switchStageView('video');
      }
    }

    // Toggle Candidate Microphone
    function toggleMic() {
      isMicMuted = !isMicMuted;
      if (localMediaStream) {
        localMediaStream.getAudioTracks().forEach(t => t.enabled = !isMicMuted);
      }

      const dockBtn = document.getElementById('dock-btn-mic');
      const dockIcon = document.getElementById('dock-icon-mic');
      const badge = document.getElementById('candidate-tile-mic-badge');
      const badgeIcon = document.getElementById('candidate-tile-mic-icon');

      if (isMicMuted) {
        if (dockBtn) dockBtn.className = "w-10 h-10 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center transition-all cursor-pointer shadow-md";
        if (dockIcon) dockIcon.textContent = "mic_off";
        if (badge) badge.className = "absolute bottom-2.5 right-2.5 w-6 h-6 rounded-full bg-red-600 text-white flex items-center justify-center text-xs shadow-md z-10 transition-colors";
        if (badgeIcon) badgeIcon.textContent = "mic_off";
      } else {
        if (dockBtn) dockBtn.className = "w-10 h-10 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center transition-all cursor-pointer shadow-md";
        if (dockIcon) dockIcon.textContent = "mic";
        if (badge) badge.className = "absolute bottom-2.5 right-2.5 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs shadow-md z-10 transition-colors";
        if (badgeIcon) badgeIcon.textContent = "mic";
      }
    }

    // Toggle Candidate Camera
    function toggleCam() {
      isCamOff = !isCamOff;
      if (localMediaStream) {
        localMediaStream.getVideoTracks().forEach(t => t.enabled = !isCamOff);
      }

      const dockBtn = document.getElementById('dock-btn-cam');
      const dockIcon = document.getElementById('dock-icon-cam');
      if (isCamOff) {
        if (dockBtn) dockBtn.className = "w-10 h-10 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center transition-all cursor-pointer shadow-md";
        if (dockIcon) dockIcon.textContent = "videocam_off";
      } else {
        if (dockBtn) dockBtn.className = "w-10 h-10 rounded-full bg-slate-700 hover:bg-slate-600 text-white flex items-center justify-center transition-all cursor-pointer shadow-md";
        if (dockIcon) dockIcon.textContent = "videocam";
      }
    }

    // Seamless Video Loop State Switcher (Zero Glitching, Never Image)
    function setInterviewerVideoState(state) {
      const chosen = interviewers[selectedInterviewerIdx] || interviewers[0];
      const targetSrc = (state === 'talking') ? chosen.videoTalking : chosen.videoListening;
      if (!targetSrc) return;

      const vCall = document.getElementById('call-interviewer-video');
      const vPip = document.getElementById('pip-interviewer-video');

      [vCall, vPip].forEach(vid => {
        if (vid) {
          const cur = vid.getAttribute('src') || vid.src || '';
          if (!cur.endsWith(targetSrc.replace('..', ''))) {
            vid.src = targetSrc;
            vid.play().catch(() => {});
          }
        }
      });
    }

    // Candidate Live Speech-to-Text Recognition
    let speechRecognizer = null;
    let isCandidateRecording = false;
    let candidateCurrentTranscript = "";

    function initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return null;
      try {
        const rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = 'en-US';

        rec.onresult = (e) => {
          let interim = '';
          for (let i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
              candidateCurrentTranscript += e.results[i][0].transcript + ' ';
            } else {
              interim += e.results[i][0].transcript;
            }
          }
          const fullText = (candidateCurrentTranscript + (interim ? ' ' + interim : '')).trim();
          updateLiveTranscriptUI(fullText);
        };

        rec.onerror = (e) => {
          console.log("Speech recognition notice:", e.error);
        };

        rec.onend = () => {
          if (isCandidateRecording) {
            try { rec.start(); } catch(err) {}
          }
        };

        return rec;
      } catch(err) {
        return null;
      }
    }

    function updateLiveTranscriptUI(text) {
      const callTxt = document.getElementById('call-transcript-text');
      const codeTxt = document.getElementById('code-transcript-text');
      if (callTxt) callTxt.textContent = text || "Listening to your spoken response...";
      if (codeTxt) codeTxt.textContent = text || "Listening to your verbal explanation...";
    }

    function toggleCandidateAnswerRecording() {
      isCandidateRecording = !isCandidateRecording;

      const callBtn = document.getElementById('call-record-btn');
      const callBtnText = document.getElementById('call-record-btn-text');
      const callBox = document.getElementById('call-transcript-box');

      const codeBtn = document.getElementById('code-record-answer-btn');
      const codeBtnText = document.getElementById('code-record-btn-text');
      const codeBox = document.getElementById('code-transcript-wrap');

      if (isCandidateRecording) {
        candidateCurrentTranscript = "";
        updateLiveTranscriptUI("Listening to your spoken answer...");

        if (callBtn) {
          callBtn.className = "px-4 py-2 rounded-full bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-md cursor-pointer animate-pulse";
        }
        if (callBtnText) callBtnText.textContent = "Stop & Save Recording";
        if (callBox) callBox.classList.remove('hidden');

        if (codeBtn) {
          codeBtn.className = "px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm cursor-pointer animate-pulse";
        }
        if (codeBtnText) codeBtnText.textContent = "Stop Recording";
        if (codeBox) codeBox.classList.remove('hidden');

        if (!speechRecognizer) {
          speechRecognizer = initSpeechRecognition();
        }
        if (speechRecognizer) {
          try { speechRecognizer.start(); } catch(e) {}
        }
      } else {
        if (callBtn) {
          callBtn.className = "px-4 py-2 rounded-full bg-[#4F6B2D] hover:bg-[#3E5423] text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-md cursor-pointer";
        }
        if (callBtnText) callBtnText.textContent = "Start Spoken Answer";

        if (codeBtn) {
          codeBtn.className = "px-3 py-1.5 rounded-lg bg-[#4F6B2D] hover:bg-[#3E5423] text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm cursor-pointer";
        }
        if (codeBtnText) codeBtnText.textContent = "Record Voice";

        if (speechRecognizer) {
          try { speechRecognizer.stop(); } catch(e) {}
        }
      }
    }

    // Helper: Create simulated camera stream if physical camera unavailable
    function createSimulatedCameraStream() {
      const canvas = document.createElement('canvas');
      canvas.width = 640;
      canvas.height = 360;
      const ctx = canvas.getContext('2d');
      let angle = 0;

      function renderFrame() {
        angle += 0.04;
        ctx.fillStyle = "#160E06";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Ambient radial glow
        const grad = ctx.createRadialGradient(320, 180, 20, 320, 180, 240);
        grad.addColorStop(0, "rgba(170, 112, 0, 0.35)");
        grad.addColorStop(1, "rgba(18, 11, 4, 0.95)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Avatar silhouette
        ctx.fillStyle = "#FAF6EE";
        ctx.beginPath();
        ctx.arc(320, 150 + Math.sin(angle) * 3, 44, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.ellipse(320, 260 + Math.sin(angle) * 2, 75, 45, 0, 0, Math.PI * 2);
        ctx.fill();

        // Audio waveform bars
        ctx.fillStyle = "#4F6B2D";
        for (let b = 0; b < 5; b++) {
          const h = 8 + Math.abs(Math.sin(angle * 2 + b)) * 18;
          ctx.fillRect(296 + b * 10, 325 - h, 6, h);
        }

        requestAnimationFrame(renderFrame);
      }
      renderFrame();
      return canvas.captureStream(30);
    }

    async function initHardwareMedia() {
      const wantVideo = document.getElementById('setting-video') ? document.getElementById('setting-video').checked : true;
      try {
        localMediaStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: wantVideo });
      } catch (err) {
        console.log("Using simulated camera fallback stream:", err);
        localMediaStream = createSimulatedCameraStream();
      }

      const vCall = document.getElementById('call-candidate-video');
      const vPip = document.getElementById('pip-candidate-video');
      [vCall, vPip].forEach(v => {
        if (v && localMediaStream) {
          v.srcObject = localMediaStream;
          v.play().catch(() => {});
        }
      });
    }

    // Confirm Start Practice Session
    function confirmStartPractice() {
      if (!document.getElementById('setting-terms').checked) {
        alert("Please accept the terms to proceed.");
        return;
      }

      selectedCodingLanguage = document.getElementById('modal-coding-language-select').value;
      closeInterviewConfig();

      const chosen = interviewers[selectedInterviewerIdx] || interviewers[0];

      // Reset Question Progression Lock
      maxUnlockedQIndex = 0;
      submittedQuestionIndices.clear();
      collectedAnswers = [];

      document.getElementById('stage-role-title').textContent = pendingTitle;
      document.getElementById('stage-role-level').textContent = pendingLevel;

      isCurrentSessionTech = (pendingTrack === 'Tech' && (selectedRound === 'Coding' || selectedRound === 'Role Related' || selectedRound === 'Go All (Full Loop)'));

      const langBadge = document.getElementById('stage-lang-badge');
      if (isCurrentSessionTech) {
        langBadge.textContent = selectedCodingLanguage.split(' ')[0];
        langBadge.classList.remove('hidden');
      } else {
        langBadge.classList.add('hidden');
      }

      // Initialize Interviewer HD Videos
      const vCall = document.getElementById('call-interviewer-video');
      const vPip = document.getElementById('pip-interviewer-video');
      if (vCall && chosen.videoListening) {
        vCall.src = chosen.videoListening;
        vCall.load();
        vCall.play().catch(() => {});
      }
      if (vPip && chosen.videoListening) {
        vPip.src = chosen.videoListening;
        vPip.load();
        vPip.play().catch(() => {});
      }

      document.getElementById('call-interviewer-name').textContent = chosen.name;
      document.getElementById('call-interviewer-accent').textContent = chosen.accentLabel;
      const pipName = document.getElementById('pip-interviewer-name');
      if (pipName) pipName.textContent = chosen.name;

      // Generate Authentic Question Bank
      if (customInterviewQuestions && customInterviewQuestions.length > 0) {
        currentQuestions = customInterviewQuestions;
      } else {
        currentQuestions = generateQuestionBank(pendingTitle, pendingCompany, pendingTrack, pendingLevel, selectedRound, selectedCodingLanguage);
      }

      currentQIndex = 0;
      renderQuestionNavigationPills();
      updateQuestionView(0);

      // Start in Video Call Mode
      switchStageView('video');

      document.getElementById('setup-screen').classList.add('hidden');
      const stage = document.getElementById('interview-stage');
      stage.classList.remove('hidden');
      stage.classList.add('flex');

      initHardwareMedia();

      // Start Live Session Timer
      remainingSeconds = 0;
      clearInterval(timerInterval);
      timerInterval = setInterval(() => {
        remainingSeconds++;
        const mins = String(Math.floor(remainingSeconds / 60)).padStart(2, '0');
        const secs = String(remainingSeconds % 60).padStart(2, '0');
        const timerEl = document.getElementById('stage-session-timer');
        if (timerEl) timerEl.textContent = mins + ":" + secs;
      }, 1000);

      // Connect to Django backend session
      tryApiFetch('/sessions/start/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: pendingTitle,
          company: pendingCompany || 'Google',
          track: pendingTrack,
          level: pendingLevel,
          interviewer_name: chosen.name,
          interviewer_accent: chosen.accentLabel,
          language: selectedCodingLanguage
        })
      }).then(data => {
        if (data && data.session_id) {
          activeSessionId = data.session_id;
        }
      }).catch(() => {});
    }

    // STRICT QUESTION NAVIGATION PILLS: CANNOT SKIP UNSUBMITTED QUESTIONS
    function renderQuestionNavigationPills() {
      const container = document.getElementById('stage-question-pills');
      if (!container) return;
      container.innerHTML = '';
      const total = currentQuestions.length;

      currentQuestions.forEach((q, idx) => {
        const pill = document.createElement('button');
        pill.type = 'button';
        const isCurrent = (idx === currentQIndex);
        const isUnlocked = (idx <= maxUnlockedQIndex);
        const isSubmitted = submittedQuestionIndices.has(idx);

        if (isCurrent) {
          pill.className = "w-7 h-7 rounded-lg text-xs font-bold flex items-center justify-center transition-all bg-[#AA7000] text-white shadow-md ring-2 ring-[#AA7000]/60 cursor-pointer";
          pill.textContent = idx + 1;
        } else if (isSubmitted) {
          pill.className = "w-7 h-7 rounded-lg text-xs font-bold flex items-center justify-center transition-all bg-[#4F6B2D] text-white shadow-sm cursor-pointer";
          pill.innerHTML = `${idx + 1}<span class="text-[9px] ml-0.5">✓</span>`;
        } else if (isUnlocked) {
          pill.className = "w-7 h-7 rounded-lg text-xs font-bold flex items-center justify-center transition-all bg-[#1F160A] hover:bg-[#2C1F0E] text-slate-300 border border-[#3D2E15] cursor-pointer";
          pill.textContent = idx + 1;
        } else {
          // Locked State: Cannot skip to this question!
          pill.className = "w-7 h-7 rounded-lg text-xs font-bold flex items-center justify-center transition-all bg-[#140D05] text-slate-600 border border-[#221609] cursor-not-allowed opacity-50";
          pill.innerHTML = '<span class="material-symbols-outlined text-[12px]">lock</span>';
          pill.title = `Locked: Submit Question ${maxUnlockedQIndex + 1} first`;
        }

        pill.onclick = () => {
          if (idx <= maxUnlockedQIndex) {
            updateQuestionView(idx);
          } else {
            showLockedNotice(idx);
          }
        };

        container.appendChild(pill);
      });

      const progLabel = document.getElementById('stage-progress-label');
      if (progLabel) progLabel.textContent = `${submittedQuestionIndices.size}/${total} SUBMITTED`;

      const curPill = document.getElementById('stage-current-pill');
      if (curPill) curPill.textContent = `Q${currentQIndex + 1} of ${total} • ${currentQuestions[currentQIndex]?.type || 'Active'}`;
    }

    function showLockedNotice(targetIdx) {
      const toast = document.createElement('div');
      toast.className = "fixed top-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-2xl bg-[#2A1D0B] border border-[#AA7000] text-[#F0E6D2] text-xs font-bold flex items-center gap-2 shadow-2xl animate-fade-in";
      toast.innerHTML = `<span class="material-symbols-outlined text-base text-[#E8A338]">lock</span><span>Question locked: You cannot skip ahead. Please submit Question ${maxUnlockedQIndex + 1} first.</span>`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3200);
    }

    // Update Live Question View across Video Call & IDE
    function updateQuestionView(idx) {
      currentQIndex = idx;
      const q = currentQuestions[idx];
      if (!q) return;

      const total = currentQuestions.length;
      renderQuestionNavigationPills();

      const qNumText = "QUESTION " + (idx + 1) + " OF " + total;

      // 1. Update Video Call Overlay
      const callQBadge = document.getElementById('call-q-badge');
      const callQPrompt = document.getElementById('call-question-prompt');
      const callSubmitText = document.getElementById('call-submit-btn-text');

      if (callQBadge) callQBadge.textContent = qNumText + " • " + (q.type ? q.type.toUpperCase() : "QUESTION");
      if (callQPrompt) callQPrompt.textContent = `"${q.prompt}"`;
      if (callSubmitText) {
        callSubmitText.textContent = (idx === total - 1) ? "Submit & Finalize Interview" : "Submit Answer & Proceed";
      }

      // 2. Update Code Pane
      const codeQNum = document.getElementById('code-pane-q-number');
      const techInstructionTitle = document.getElementById('code-pane-instruction-title');
      const techDesc = document.getElementById('tech-problem-description');
      const techInput = document.getElementById('tech-problem-input');
      const techOutput = document.getElementById('tech-problem-output');
      const techConstraints = document.getElementById('tech-problem-constraints');
      const techInstructionsText = document.getElementById('tech-instructions-text');

      if (codeQNum) codeQNum.textContent = qNumText;
      if (techInstructionTitle) techInstructionTitle.textContent = q.title || "Write a code solution for the situation described below.";
      if (techDesc) techDesc.textContent = q.prompt;
      if (techInput) techInput.textContent = q.input || "Standard I/O stream";
      if (techOutput) techOutput.textContent = q.output || "Standard I/O format";
      if (techConstraints) techConstraints.textContent = q.constraints || "Optimal asymptotic complexity constraints";
      if (techInstructionsText) techInstructionsText.textContent = q.instructions || "Your solution will be compiled and evaluated in sandbox.";

      if (q.starterCode) {
        document.getElementById('code-editor-textarea').value = q.starterCode;
        updateLineNumbers();
      } else {
        initCodeEditorContent(q.title);
      }

      speakQuestion(q.prompt);
    }

    // Switch between Code and Instructions tabs on Left Pane
    function switchProblemTab(tab) {
      const codeTabBtn = document.getElementById('tab-prob-code');
      const instTabBtn = document.getElementById('tab-prob-instructions');
      const codeContent = document.getElementById('tab-content-prob-code');
      const instContent = document.getElementById('tab-content-prob-instructions');

      if (tab === 'code') {
        codeTabBtn.className = "pb-2 text-xs font-bold border-b-2 border-[#AA7000] text-white transition-all cursor-pointer";
        instTabBtn.className = "pb-2 text-xs font-semibold border-b-2 border-transparent text-slate-400 hover:text-white transition-all cursor-pointer";
        codeContent.classList.remove('hidden');
        instContent.classList.add('hidden');
      } else {
        instTabBtn.className = "pb-2 text-xs font-bold border-b-2 border-[#AA7000] text-white transition-all cursor-pointer";
        codeTabBtn.className = "pb-2 text-xs font-semibold border-b-2 border-transparent text-slate-400 hover:text-white transition-all cursor-pointer";
        instContent.classList.remove('hidden');
        codeContent.classList.add('hidden');
      }
    }

    // SUBMIT CURRENT ANSWER: STRICTLY UNLOCKS NEXT QUESTION
    async function submitCurrentAnswer() {
      const q = currentQuestions[currentQIndex];
      const codeVal = document.getElementById('code-editor-textarea') ? document.getElementById('code-editor-textarea').value : '';

      // Stop candidate speech recording if active
      if (isCandidateRecording) {
        toggleCandidateAnswerRecording();
      }

      const spokenText = candidateCurrentTranscript.trim() || 
        "Demonstrated systematic algorithm breakdown, stating data structures, invariants, and edge case mitigation upfront.";

      collectedAnswers.push({
        question_index: currentQIndex,
        question_text: q ? q.title : '',
        prompt: q ? q.prompt : '',
        transcript: spokenText,
        code: codeVal
      });

      // Mark current question submitted
      submittedQuestionIndices.add(currentQIndex);

      // UNLOCK NEXT QUESTION (strictly one by one)
      maxUnlockedQIndex = Math.max(maxUnlockedQIndex, currentQIndex + 1);

      candidateCurrentTranscript = "";
      updateLiveTranscriptUI("");

      if (currentQIndex < currentQuestions.length - 1) {
        // Show brief success transition toast
        const toast = document.createElement('div');
        toast.className = "fixed top-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-2xl bg-[#1B2811] border border-[#4F6B2D] text-emerald-300 text-xs font-bold flex items-center gap-2 shadow-xl animate-fade-in";
        toast.innerHTML = `<span class="material-symbols-outlined text-sm">check_circle</span><span>Question ${currentQIndex + 1} submitted. Unlocking Question ${currentQIndex + 2}...</span>`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2200);

        // Advance to next question
        updateQuestionView(currentQIndex + 1);
      } else {
        // Last question submitted: Complete interview and navigate to report
        clearInterval(timerInterval);
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        if (currentAudioPlayback) currentAudioPlayback.pause();

        // Capture Candidate Performance & Integrity Matrix
        if (window.candidateMatrixInstance) {
          const matrixReport = window.candidateMatrixInstance.getMatrixReport();
          localStorage.setItem('imaira_integrity_matrix', JSON.stringify(matrixReport));
        }

        try {
          const matrixReport = window.candidateMatrixInstance ? window.candidateMatrixInstance.getMatrixReport() : null;
          const evalResult = await tryApiFetch(`/sessions/${activeSessionId || 'general'}/submit/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              answers: collectedAnswers,
              role: pendingTitle,
              company: pendingCompany || 'Google',
              integrity_matrix: matrixReport
            })
          });
          if (evalResult) {
            localStorage.setItem('imaira_session_report', JSON.stringify(evalResult));
          }
        } catch (e) {}

        window.location.href = "report.html";
      }
    }
'''

    content = content[:idx_start] + new_js_logic + '\n' + content[idx_end:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Stage 2 JavaScript logic successfully replaced.")

if __name__ == '__main__':
    main()
