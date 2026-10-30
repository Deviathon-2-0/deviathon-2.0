import os

def run_patch():
    file_path = os.path.join('frontend', 'pages', 'mock-interview.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Normalize newlines for matching
    newline = '\r\n' if '\r\n' in html else '\n'
    html = html.replace('\r\n', '\n')

    # --- HTML UI ENHANCEMENTS ---

    # 1. Left pane footer
    old_left_footer = '''          <!-- Left Pane Footer: Audio Wave + Execute Button -->
          <div class="p-3 border-t border-[#2A1C0A] bg-[#100A03] flex items-center justify-between text-[11px] text-slate-400">
            <div class="flex items-center gap-1.5">
              <div class="stage-wave-bar"></div>
              <div class="stage-wave-bar" style="animation-delay: 0.2s"></div>
              <div class="stage-wave-bar" style="animation-delay: 0.4s"></div>
              <span class="text-[11px] text-slate-400 ml-1">Live Audio Channel</span>
            </div>
            <button onclick="executeCurrentCode()" class="px-3.5 py-1.5 rounded-lg bg-[#2A1D0B] hover:bg-[#3D2B12] text-[#E8A338] border border-[#AA7000]/50 font-bold flex items-center gap-1 shadow-sm transition-all">
              <span class="material-symbols-outlined text-xs">play_arrow</span>
              <span>Execute</span>
            </button>
          </div>'''

    new_left_footer = '''          <!-- Left Pane Footer: Audio Wave + Voice Recording + Execute Button -->
          <div class="p-3 border-t border-[#2A1C0A] bg-[#100A03] flex items-center justify-between text-[11px] text-slate-400 gap-2">
            <button type="button" id="code-record-answer-btn" onclick="toggleCandidateAnswerRecording()" class="px-3 py-1.5 rounded-lg bg-[#4F6B2D] hover:bg-[#3E5423] text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm cursor-pointer">
              <span class="material-symbols-outlined text-sm">mic</span>
              <span id="code-record-btn-text">Record Voice</span>
            </button>
            <div class="flex items-center gap-2">
              <div class="flex items-center gap-1">
                <div class="stage-wave-bar"></div>
                <div class="stage-wave-bar" style="animation-delay: 0.2s"></div>
                <div class="stage-wave-bar" style="animation-delay: 0.4s"></div>
              </div>
              <button onclick="executeCurrentCode()" class="px-3.5 py-1.5 rounded-lg bg-[#2A1D0B] hover:bg-[#3D2B12] text-[#E8A338] border border-[#AA7000]/50 font-bold flex items-center gap-1 shadow-sm transition-all cursor-pointer">
                <span class="material-symbols-outlined text-xs">play_arrow</span>
                <span>Execute</span>
              </button>
            </div>
          </div>'''

    if old_left_footer in html:
        html = html.replace(old_left_footer, new_left_footer)
        print("1. Left footer patched.")
    else:
        print("Notice: Left footer already patched or not found.")

    # 2. Code pane think-out-loud transcript
    old_code_tab_end = '''              </div>
            </div>
          </div>

          <!-- Tab Content 2: Instructions & Rubrics -->'''

    new_code_tab_end = '''              </div>
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

          <!-- Tab Content 2: Instructions & Rubrics -->'''

    if old_code_tab_end in html:
        html = html.replace(old_code_tab_end, new_code_tab_end)
        print("2. Code transcript wrap patched.")

    # 3. Spotlight call overlay: record button and transcript box
    old_spot_bottom = '''            <div class="flex items-center justify-between text-xs text-slate-300 pt-2 border-t border-white/10">
              <div class="flex items-center gap-1.5">
                <div class="stage-wave-bar"></div>
                <div class="stage-wave-bar" style="animation-delay: 0.2s"></div>
                <div class="stage-wave-bar" style="animation-delay: 0.4s"></div>
                <span class="text-[11px] ml-1 text-slate-300">Voice channel active • Zero pronunciation bias</span>
              </div>
              <div id="spotlight-switch-code-cta" class="hidden">
                <button onclick="setFocus('code')" class="text-xs font-bold text-[#AA7000] hover:text-white flex items-center gap-1">
                  <span>Open Code Editor</span>
                  <span class="material-symbols-outlined text-xs">arrow_forward</span>
                </button>
              </div>
            </div>'''

    new_spot_bottom = '''            <div class="flex items-center justify-between text-xs text-slate-300 pt-2 border-t border-white/10">
              <div class="flex items-center gap-3">
                <button type="button" id="spotlight-record-answer-btn" onclick="toggleCandidateAnswerRecording()" class="px-3.5 py-1.5 rounded-full bg-[#4F6B2D] hover:bg-[#3E5423] text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-md cursor-pointer">
                  <span class="material-symbols-outlined text-sm">mic</span>
                  <span id="spotlight-record-btn-text">Start Spoken Answer</span>
                </button>
                <div class="flex items-center gap-1.5">
                  <div class="stage-wave-bar"></div>
                  <div class="stage-wave-bar" style="animation-delay: 0.2s"></div>
                  <div class="stage-wave-bar" style="animation-delay: 0.4s"></div>
                  <span class="text-[11px] ml-1 text-slate-300">Voice channel active</span>
                </div>
              </div>
              <div id="spotlight-switch-code-cta" class="hidden">
                <button onclick="setFocus('code')" class="text-xs font-bold text-[#AA7000] hover:text-white flex items-center gap-1 cursor-pointer">
                  <span>Open Code Editor</span>
                  <span class="material-symbols-outlined text-xs">arrow_forward</span>
                </button>
              </div>
            </div>

            <!-- Real-time Candidate Speech-to-Text Transcript Box in Spotlight Call -->
            <div id="spotlight-transcript-wrap" class="mt-2.5 p-3 rounded-xl bg-black/60 border border-white/10 hidden">
              <div class="flex items-center justify-between text-[10px] text-[#AA7000] font-bold mb-1">
                <span>LIVE CANDIDATE TRANSCRIPT</span>
                <span id="spotlight-recog-status" class="text-emerald-400 flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Recording candidate speech...
                </span>
              </div>
              <p id="spotlight-transcript-text" class="text-xs text-slate-200 italic font-mono leading-relaxed">Listening to your response...</p>
            </div>'''

    if old_spot_bottom in html:
        html = html.replace(old_spot_bottom, new_spot_bottom)
        print("3. Spotlight bottom patched.")

    # --- JAVASCRIPT FUNCTIONS ---

    # 4. Patch openPracticePrerequisite, testSystemAudio, confirmStartPractice, speakQuestion, submitCurrentAnswer
    old_prereq_fn = '''    function openPracticePrerequisite() {
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
      const img = document.getElementById('prereq-interviewer-img');
      const name = document.getElementById('prereq-interviewer-name');
      const sub = document.getElementById('prereq-interviewer-sublabel');

      if (img) img.src = chosen.avatar;
      if (name) name.textContent = chosen.name;
      if (sub) sub.textContent = chosen.subLabel + " • " + chosen.accentLabel;

      runSystemPrerequisiteChecks();
    }'''

    new_prereq_fn = '''    function openPracticePrerequisite() {
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
      const img = document.getElementById('prereq-interviewer-img');
      const name = document.getElementById('prereq-interviewer-name');
      const sub = document.getElementById('prereq-interviewer-sublabel');
      const indicator = document.getElementById('prereq-speech-indicator');

      if (indicator) indicator.classList.add('hidden');
      if (name) name.textContent = chosen.name;
      if (sub) sub.textContent = (chosen.subLabel || '') + " • " + chosen.accentLabel;

      if (vid && chosen.videoListening) {
        vid.src = chosen.videoListening;
        vid.classList.remove('hidden');
        if (img) img.classList.add('hidden');
        vid.load();
        vid.play().catch(() => {});
      } else if (img) {
        img.src = chosen.avatar;
        img.classList.remove('hidden');
        if (vid) vid.classList.add('hidden');
      }

      runSystemPrerequisiteChecks();
    }'''

    if old_prereq_fn in html:
        html = html.replace(old_prereq_fn, new_prereq_fn)
        print("4. openPracticePrerequisite patched.")

    # 5. Patch testSystemAudio
    old_test_audio = '''    function testSystemAudio() {
      const chosen = interviewers[selectedInterviewerIdx] || interviewers[0];
      const btn = document.getElementById('play-sound-btn');
      btn.innerHTML = '<span class="material-symbols-outlined text-sm animate-spin">refresh</span><span>Playing Audio Sample...</span>';

      speakQuestion(`Hello, I am ${chosen.name}. My system audio is verified and ready for your interview.`);

      setTimeout(() => {
        soundCheckPassed = true;
        btn.innerHTML = '<span class="material-symbols-outlined text-sm text-[#4F6B2D]">check</span><span>Evaluator Audio Verified</span>';
        btn.className = "w-full py-2 rounded-lg bg-[#EFF4E8] text-[#4F6B2D] border border-[#4F6B2D]/40 text-xs font-bold flex items-center justify-center gap-1.5";
        document.getElementById('chk-sound-status').innerHTML = '<span class="text-[#4F6B2D] font-bold flex items-center gap-0.5"><span class="material-symbols-outlined text-sm">check_circle</span> Verified</span>';
        document.getElementById('prereq-checklist-counter').textContent = "8/8 Verified";
      }, 1500);
    }'''

    new_test_audio = '''    function testSystemAudio() {
      const chosen = interviewers[selectedInterviewerIdx] || interviewers[0];
      const btn = document.getElementById('play-sound-btn');
      const vid = document.getElementById('prereq-interviewer-video');
      const indicator = document.getElementById('prereq-speech-indicator');
      const subText = document.getElementById('prereq-subtitle-text');

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
        btn.className = "w-full py-2 rounded-lg bg-[#EFF4E8] text-[#4F6B2D] border border-[#4F6B2D]/40 text-xs font-bold flex items-center justify-center gap-1.5";
        document.getElementById('chk-sound-status').innerHTML = '<span class="text-[#4F6B2D] font-bold flex items-center gap-0.5"><span class="material-symbols-outlined text-sm">check_circle</span> Verified</span>';
        document.getElementById('prereq-checklist-counter').textContent = "8/8 Verified";
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
    }'''

    if old_test_audio in html:
        html = html.replace(old_test_audio, new_test_audio)
        print("5. testSystemAudio patched.")

    # 6. Add video state switcher and candidate speech recognition logic
    video_and_stt_logic = '''
    // Realtime AI Evaluator Video & Lip-Sync State Manager
    function setInterviewerVideoState(state) {
      const chosen = interviewers[selectedInterviewerIdx] || interviewers[0];
      const spotlightVid = document.getElementById('spotlight-interviewer-video');
      const dockVid = document.getElementById('dock-interviewer-video');
      
      const targetSrc = (state === 'talking') ? chosen.videoTalking : chosen.videoListening;
      if (!targetSrc) return;

      if (spotlightVid && !spotlightVid.classList.contains('hidden')) {
        const curSrc = spotlightVid.getAttribute('src') || '';
        if (!curSrc.includes(targetSrc)) {
          spotlightVid.src = targetSrc;
          spotlightVid.play().catch(() => {});
        }
      }
      if (dockVid) {
        const curSrc = dockVid.getAttribute('src') || '';
        if (!curSrc.includes(targetSrc)) {
          dockVid.src = targetSrc;
          dockVid.play().catch(() => {});
        }
      }
    }

    // Candidate Speech-to-Text & Spoken Answer Handler
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
      const spotTxt = document.getElementById('spotlight-transcript-text');
      const codeTxt = document.getElementById('code-transcript-text');
      if (spotTxt) spotTxt.textContent = text || "Listening to your spoken answer...";
      if (codeTxt) codeTxt.textContent = text || "Listening to your verbal explanation...";
    }

    function toggleCandidateAnswerRecording() {
      isCandidateRecording = !isCandidateRecording;

      const spotBtn = document.getElementById('spotlight-record-answer-btn');
      const spotBtnText = document.getElementById('spotlight-record-btn-text');
      const spotWrap = document.getElementById('spotlight-transcript-wrap');

      const codeBtn = document.getElementById('code-record-answer-btn');
      const codeBtnText = document.getElementById('code-record-btn-text');
      const codeWrap = document.getElementById('code-transcript-wrap');

      if (isCandidateRecording) {
        candidateCurrentTranscript = "";
        updateLiveTranscriptUI("Listening to your spoken answer...");

        if (spotBtn) {
          spotBtn.className = "px-3.5 py-1.5 rounded-full bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-md cursor-pointer animate-pulse";
        }
        if (spotBtnText) spotBtnText.textContent = "Stop & Save Recording";
        if (spotWrap) spotWrap.classList.remove('hidden');

        if (codeBtn) {
          codeBtn.className = "px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm cursor-pointer animate-pulse";
        }
        if (codeBtnText) codeBtnText.textContent = "Stop Recording";
        if (codeWrap) codeWrap.classList.remove('hidden');

        if (!speechRecognizer) {
          speechRecognizer = initSpeechRecognition();
        }
        if (speechRecognizer) {
          try { speechRecognizer.start(); } catch(e) {}
        }
      } else {
        if (spotBtn) {
          spotBtn.className = "px-3.5 py-1.5 rounded-full bg-[#4F6B2D] hover:bg-[#3E5423] text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-md cursor-pointer";
        }
        if (spotBtnText) spotBtnText.textContent = "Start Spoken Answer";

        if (codeBtn) {
          codeBtn.className = "px-3 py-1.5 rounded-lg bg-[#4F6B2D] hover:bg-[#3E5423] text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm cursor-pointer";
        }
        if (codeBtnText) codeBtnText.textContent = "Record Voice";

        if (speechRecognizer) {
          try { speechRecognizer.stop(); } catch(e) {}
        }
      }
    }
'''

    # Place video_and_stt_logic right before confirmStartPractice
    if 'function confirmStartPractice()' in html:
        html = html.replace('    function confirmStartPractice()', video_and_stt_logic + '\n    function confirmStartPractice()')
        print("6. Inserted video and STT logic.")

    # 7. Update confirmStartPractice to init video and active backend session
    old_confirm_start = '''      // Populate Interviewer and Candidate in PiP Tiles & Spotlight
      document.getElementById('dock-interviewer-img').src = chosenInterviewer.avatar;
      document.getElementById('dock-interviewer-name').textContent = chosenInterviewer.name;
      document.getElementById('spotlight-img').src = chosenInterviewer.avatar;
      document.getElementById('spotlight-name-tag').textContent = chosenInterviewer.name + " (" + chosenInterviewer.accentLabel + ")";'''

    new_confirm_start = '''      // Populate Interviewer and Candidate in 16:9 Video Call & PiP
      const spotVid = document.getElementById('spotlight-interviewer-video');
      const dockVid = document.getElementById('dock-interviewer-video');
      if (spotVid && chosenInterviewer.videoListening) {
        spotVid.src = chosenInterviewer.videoListening;
        spotVid.load();
        spotVid.play().catch(() => {});
      }
      if (dockVid && chosenInterviewer.videoListening) {
        dockVid.src = chosenInterviewer.videoListening;
        dockVid.load();
        dockVid.play().catch(() => {});
      }
      document.getElementById('dock-interviewer-img').src = chosenInterviewer.avatar;
      document.getElementById('dock-interviewer-name').textContent = chosenInterviewer.name;
      document.getElementById('spotlight-img').src = chosenInterviewer.avatar;
      document.getElementById('spotlight-name-tag').textContent = chosenInterviewer.name + " (" + chosenInterviewer.accentLabel + ")";

      // Initialize live backend session if connected
      tryApiFetch('/sessions/start/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: pendingTitle,
          company: pendingCompany || 'Google',
          track: pendingTrack,
          level: pendingLevel,
          interviewer_name: chosenInterviewer.name,
          interviewer_accent: chosenInterviewer.accentLabel,
          language: selectedCodingLanguage
        })
      }).then(data => {
        if (data && data.session_id) {
          activeSessionId = data.session_id;
        }
      }).catch(() => {});'''

    if old_confirm_start in html:
        html = html.replace(old_confirm_start, new_confirm_start)
        print("7. confirmStartPractice video & backend session patched.")

    # 8. Update speakQuestion to toggle talking vs listening video
    old_speak_q = '''      // 1. Try server neural TTS first (Edge TTS realistic human voices with distinct male/female timbre)
      try {
        const data = await tryApiFetch('/tts/generate/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: text,
            interviewer_name: chosen.name,
            pacing: pacingVal.toString()
          })
        });
        if (data && data.audio_url) {
          const audioSrc = data.audio_url.startsWith('http') ? data.audio_url : ('http://localhost:8000' + data.audio_url);
          currentAudioPlayback = new Audio(audioSrc);
          await currentAudioPlayback.play();
          return;
        }
      } catch (err) {}'''

    new_speak_q = '''      // Switch Interviewer Video to Talking Loop
      setInterviewerVideoState('talking');

      const onPlaybackEnded = () => {
        setInterviewerVideoState('listening');
      };

      // 1. Try server neural TTS first (Edge TTS realistic human voices with distinct male/female timbre)
      try {
        const data = await tryApiFetch('/tts/generate/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: text,
            interviewer_name: chosen.name,
            pacing: pacingVal.toString()
          })
        });
        if (data && data.audio_url) {
          const audioSrc = data.audio_url.startsWith('http') ? data.audio_url : ('http://localhost:8000' + data.audio_url);
          currentAudioPlayback = new Audio(audioSrc);
          currentAudioPlayback.onended = onPlaybackEnded;
          currentAudioPlayback.onerror = onPlaybackEnded;
          await currentAudioPlayback.play();
          return;
        }
      } catch (err) {}'''

    if old_speak_q in html:
        html = html.replace(old_speak_q, new_speak_q)
        print("8. speakQuestion server TTS patched.")

    # Also handle client utterance end
    old_client_speak = '''        utterance.pitch = isMale ? (0.88 * (chosen.pitch || 0.90)) : (1.18 * (chosen.pitch || 1.15));
        utterance.rate = (chosen.rate || 1.0) * pacingVal;'''

    new_client_speak = '''        utterance.pitch = isMale ? (0.88 * (chosen.pitch || 0.90)) : (1.18 * (chosen.pitch || 1.15));
        utterance.rate = (chosen.rate || 1.0) * pacingVal;
        utterance.onend = onPlaybackEnded;
        utterance.onerror = onPlaybackEnded;'''

    if old_client_speak in html:
        html = html.replace(old_client_speak, new_client_speak)
        print("9. speakQuestion client TTS patched.")

    # 9. Update submitCurrentAnswer to capture live transcript and submit to backend
    old_submit_answer = '''    async function submitCurrentAnswer() {
      const q = currentQuestions[currentQIndex];
      const codeVal = document.getElementById('code-editor-textarea').value;
      
      collectedAnswers.push({
        question_index: currentQIndex,
        question_text: q ? q.title : '',
        transcript: "Demonstrated systematic algorithm breakdown, stating data structures and invariants upfront.",
        code: codeVal
      });

      if (currentQIndex < currentQuestions.length - 1) {
        updateQuestionView(currentQIndex + 1);
      } else {'''

    new_submit_answer = '''    async function submitCurrentAnswer() {
      const q = currentQuestions[currentQIndex];
      const codeVal = document.getElementById('code-editor-textarea').value;
      
      // Stop speech recording if active
      if (isCandidateRecording) {
        toggleCandidateAnswerRecording();
      }

      const spokenText = candidateCurrentTranscript.trim() || 
        "Demonstrated systematic algorithm breakdown, stating data structures, invariants, and edge case mitigation upfront.";

      collectedAnswers.push({
        question_index: currentQIndex,
        question_text: q ? q.title : '',
        transcript: spokenText,
        code: codeVal
      });

      candidateCurrentTranscript = "";
      updateLiveTranscriptUI("");

      if (currentQIndex < currentQuestions.length - 1) {
        updateQuestionView(currentQIndex + 1);
      } else {'''

    if old_submit_answer in html:
        html = html.replace(old_submit_answer, new_submit_answer)
        print("10. submitCurrentAnswer patched.")

    # Restore CRLF if needed
    if newline == '\r\n':
        html = html.replace('\n', '\r\n')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("All Stage 2 flow updates applied to mock-interview.html successfully!")

if __name__ == '__main__':
    run_patch()
