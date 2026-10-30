with open('frontend/pages/mock-interview.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update interviewers list with local 16:9 images, talking/listening videos, and neural audio
old_interviewers = '''    const interviewers = [
      {
        id: "kabir",
        name: "Kabir",
        gender: "male",
        region: "India",
        regionFlag: "🇮🇳",
        accentLabel: "Indian English (North)",
        subLabel: "Senior Systems Architect",
        bcp47: "en-IN",
        pitch: 0.90,
        rate: 1.0,
        sampleIntro: "Hello! I am Kabir. Let's delve into your technical architecture and problem-solving strategy.",
        avatar: "https://images.unsplash.com/photo-1566492031773-4f4e44671857?w=400&auto=format&fit=crop&q=80"
      },
      {
        id: "payal",
        name: "Payal",
        gender: "female",
        region: "India",
        regionFlag: "🇮🇳",
        accentLabel: "Indian English (Standard)",
        subLabel: "VP of Engineering",
        bcp47: "en-IN",
        pitch: 1.18,
        rate: 1.02,
        sampleIntro: "Hi there! I am Payal. I look forward to exploring your distributed systems and algorithmic trade-offs.",
        avatar: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=80"
      },
      {
        id: "charlotte",
        name: "Charlotte",
        gender: "female",
        region: "UK & Europe",
        regionFlag: "🇬🇧",
        accentLabel: "British English (London RP)",
        subLabel: "Principal Systems Lead",
        bcp47: "en-GB",
        pitch: 1.14,
        rate: 0.98,
        sampleIntro: "Good day. I am Charlotte. We shall be exploring system constraints, latency guarantees, and failure modes.",
        avatar: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&auto=format&fit=crop&q=80"
      },
      {
        id: "john",
        name: "John",
        gender: "male",
        region: "North America",
        regionFlag: "🇺🇸",
        accentLabel: "US English (West Coast)",
        subLabel: "Silicon Valley Tech Lead",
        bcp47: "en-US",
        pitch: 0.92,
        rate: 1.04,
        sampleIntro: "Hey there! I am John. Excited to chat through your approach and see how you tackle scaling bottlenecks.",
        avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&auto=format&fit=crop&q=80"
      },
      {
        id: "sarah",
        name: "Sarah",
        gender: "female",
        region: "North America",
        regionFlag: "🇺🇸",
        accentLabel: "US English (Standard)",
        subLabel: "Engineering Director",
        bcp47: "en-US",
        pitch: 1.16,
        rate: 1.00,
        sampleIntro: "Welcome! I am Sarah. We will examine your architectural tradeoffs, data structures, and edge case mitigation.",
        avatar: "https://images.unsplash.com/photo-1573496799652-408c2ac9fe98?w=400&auto=format&fit=crop&q=80"
      },
      {
        id: "kenji",
        name: "Kenji",
        gender: "male",
        region: "East & SE Asia",
        regionFlag: "🇯🇵",
        accentLabel: "Japanese English (Tokyo)",
        subLabel: "Robotics & Backend Lead",
        bcp47: "ja-JP",
        pitch: 0.88,
        rate: 0.95,
        sampleIntro: "Konnichiwa. I am Kenji. Please walk through your architectural assumptions step-by-step with clarity.",
        avatar: "https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?w=400&auto=format&fit=crop&q=80"
      }
    ];'''

new_interviewers = '''    const interviewers = [
      {
        id: "kabir",
        name: "Kabir",
        gender: "male",
        region: "India",
        regionFlag: "🇮🇳",
        accentLabel: "Indian English (North)",
        subLabel: "Senior Systems Architect",
        bcp47: "en-IN",
        pitch: 0.90,
        rate: 1.0,
        sampleIntro: "Hello! I am Kabir. Let's delve into your technical architecture and problem-solving strategy.",
        avatar: "../assets/interviewers/kabir.jpg",
        videoListening: "../assets/interviewers/kabir_listening.mp4",
        videoTalking: "../assets/interviewers/kabir_talking.mp4",
        introAudio: "../assets/interviewers/kabir_intro.mp3"
      },
      {
        id: "payal",
        name: "Payal",
        gender: "female",
        region: "India",
        regionFlag: "🇮🇳",
        accentLabel: "Indian English (Standard)",
        subLabel: "VP of Engineering",
        bcp47: "en-IN",
        pitch: 1.18,
        rate: 1.02,
        sampleIntro: "Hi there! I am Payal. I look forward to exploring your distributed systems and algorithmic trade-offs.",
        avatar: "../assets/interviewers/payal.jpg",
        videoListening: "../assets/interviewers/payal_listening.mp4",
        videoTalking: "../assets/interviewers/payal_talking.mp4",
        introAudio: "../assets/interviewers/payal_intro.mp3"
      },
      {
        id: "charlotte",
        name: "Charlotte",
        gender: "female",
        region: "UK & Europe",
        regionFlag: "🇬🇧",
        accentLabel: "British English (London RP)",
        subLabel: "Principal Systems Lead",
        bcp47: "en-GB",
        pitch: 1.14,
        rate: 0.98,
        sampleIntro: "Good day. I am Charlotte. We shall explore system constraints, latency guarantees, and failure modes.",
        avatar: "../assets/interviewers/charlotte.jpg",
        videoListening: "../assets/interviewers/charlotte_listening.mp4",
        videoTalking: "../assets/interviewers/charlotte_talking.mp4",
        introAudio: "../assets/interviewers/charlotte_intro.mp3"
      },
      {
        id: "john",
        name: "John",
        gender: "male",
        region: "North America",
        regionFlag: "🇺🇸",
        accentLabel: "US English (West Coast)",
        subLabel: "Silicon Valley Tech Lead",
        bcp47: "en-US",
        pitch: 0.92,
        rate: 1.04,
        sampleIntro: "Hey there! I am John. Excited to chat through your approach and see how you tackle scaling bottlenecks.",
        avatar: "../assets/interviewers/john.jpg",
        videoListening: "../assets/interviewers/john_listening.mp4",
        videoTalking: "../assets/interviewers/john_talking.mp4",
        introAudio: "../assets/interviewers/john_intro.mp3"
      },
      {
        id: "sarah",
        name: "Sarah",
        gender: "female",
        region: "North America",
        regionFlag: "🇺🇸",
        accentLabel: "US English (Standard)",
        subLabel: "Engineering Director",
        bcp47: "en-US",
        pitch: 1.16,
        rate: 1.00,
        sampleIntro: "Welcome. I am Sarah. Let's walk through your engineering background and architectural decisions.",
        avatar: "../assets/interviewers/sarah.jpg",
        videoListening: "../assets/interviewers/sarah_listening.mp4",
        videoTalking: "../assets/interviewers/sarah_talking.mp4",
        introAudio: "../assets/interviewers/sarah_intro.mp3"
      },
      {
        id: "kenji",
        name: "Kenji",
        gender: "male",
        region: "East & SE Asia",
        regionFlag: "🇯🇵",
        accentLabel: "Japanese English (Tokyo)",
        subLabel: "Robotics & Backend Lead",
        bcp47: "en-US",
        pitch: 0.88,
        rate: 0.98,
        sampleIntro: "Hello, I am Kenji. We will focus on data consensus, partitioning, and resilience today.",
        avatar: "../assets/interviewers/kenji.jpg",
        videoListening: "../assets/interviewers/kenji_listening.mp4",
        videoTalking: "../assets/interviewers/kenji_talking.mp4",
        introAudio: "../assets/interviewers/kenji_intro.mp3"
      }
    ];'''

if old_interviewers in content:
    content = content.replace(old_interviewers, new_interviewers)
    print("1. Replaced interviewers array: SUCCESS")
else:
    print("1. Old interviewers block not found")

# 2. Update Prerequisite Modal Video Card
old_prereq_card = '''          <!-- Interviewer Card: Authentic Image of Selected Evaluator -->
          <div class="relative w-full h-56 rounded-2xl overflow-hidden bg-[#1E293B] border border-[#E8DFD0] shadow-md mb-4 flex items-center justify-center group">
            <img id="prereq-interviewer-img" src="" alt="Selected Evaluator" class="w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20 pointer-events-none"></div>
            
            <!-- Persona Tag -->
            <div class="absolute top-3 left-3 px-3 py-1 rounded-full bg-black/60 backdrop-blur-md text-white text-xs font-bold flex items-center gap-2 border border-white/10 z-10">
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span id="prereq-interviewer-name">Kabir</span>
              <span class="text-slate-300 text-[10px] font-normal" id="prereq-interviewer-sublabel">IN English (North)</span>
            </div>

            <!-- Start Answer Floating Pill (Matching User Screenshot) -->
            <div class="absolute bottom-3.5 px-4 py-1.5 rounded-full bg-[#4F6B2D] text-white text-xs font-bold flex items-center gap-1.5 shadow-lg z-10 pointer-events-none">
              <span class="material-symbols-outlined text-sm">mic</span>
              <span>START ANSWER</span>
            </div>
          </div>'''

new_prereq_card = '''          <!-- Interviewer Card: 16:9 Properly Framed AI Video of Selected Evaluator -->
          <div class="relative w-full aspect-video rounded-2xl overflow-hidden bg-[#120B04] border border-[#E8DFD0] shadow-md mb-4 flex items-center justify-center group">
            <video id="prereq-interviewer-video" autoplay loop muted playsinline class="w-full h-full object-cover object-center"></video>
            <img id="prereq-interviewer-img" src="" alt="Selected Evaluator" class="w-full h-full object-cover object-center hidden" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20 pointer-events-none"></div>
            
            <!-- Persona Tag -->
            <div class="absolute top-3 left-3 px-3.5 py-1.5 rounded-full bg-black/65 backdrop-blur-md text-white text-xs font-bold flex items-center gap-2 border border-white/10 z-10">
              <span id="prereq-status-dot" class="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span id="prereq-interviewer-name" class="font-bold">Kabir</span>
              <span class="text-slate-300 text-[11px] font-normal" id="prereq-interviewer-sublabel">Senior Systems Architect • Indian English (North)</span>
            </div>

            <!-- Start Answer Floating Pill (Matching User Screenshot) -->
            <div id="prereq-mic-pill" class="absolute bottom-3.5 px-4 py-1.5 rounded-full bg-[#4F6B2D] text-white text-xs font-bold flex items-center gap-1.5 shadow-lg z-10 pointer-events-none">
              <span class="material-symbols-outlined text-sm">mic</span>
              <span>START ANSWER</span>
            </div>

            <!-- Realtime Evaluator Voiceover & Lip-Sync Subtitles Overlay -->
            <div id="prereq-speech-indicator" class="hidden absolute bottom-3 left-3 right-3 bg-black/85 backdrop-blur-md border border-white/15 rounded-xl p-2.5 z-20 flex items-center gap-3">
              <div class="flex items-center gap-1 shrink-0">
                <div class="stage-wave-bar"></div>
                <div class="stage-wave-bar" style="animation-delay: 0.2s"></div>
                <div class="stage-wave-bar" style="animation-delay: 0.4s"></div>
              </div>
              <p id="prereq-subtitle-text" class="text-xs text-emerald-300 font-medium italic truncate flex-1"></p>
            </div>
          </div>'''

if old_prereq_card in content:
    content = content.replace(old_prereq_card, new_prereq_card)
    print("2. Replaced Prerequisite Modal Video Card: SUCCESS")
else:
    print("2. Old prerequisite card not found")

# 3. Update Spotlight Video Container in Stage
old_spotlight = '''        <!-- Video Container: Takes maximum comfortable viewport space -->
        <div id="spotlight-frame-container" class="relative w-full max-w-5xl h-full max-h-[82vh] rounded-3xl overflow-hidden bg-[#1A1208] border border-[#3D2E15] shadow-2xl flex items-center justify-center">
          
          <img id="spotlight-img" src="" alt="Spotlight" class="w-full h-full object-cover object-top natural-face-anim" />
          <video id="spotlight-video" autoplay muted playsinline class="w-full h-full object-cover hidden"></video>'''

new_spotlight = '''        <!-- Video Container: Takes maximum comfortable viewport space with 16:9 Proper Framing -->
        <div id="spotlight-frame-container" class="relative w-full max-w-5xl h-full max-h-[82vh] rounded-3xl overflow-hidden bg-[#1A1208] border border-[#3D2E15] shadow-2xl flex items-center justify-center">
          
          <video id="spotlight-interviewer-video" autoplay loop muted playsinline class="w-full h-full object-cover object-center"></video>
          <img id="spotlight-img" src="" alt="Spotlight" class="w-full h-full object-cover object-center hidden" />
          <video id="spotlight-video" autoplay muted playsinline class="w-full h-full object-cover object-center hidden"></video>'''

if old_spotlight in content:
    content = content.replace(old_spotlight, new_spotlight)
    print("3. Replaced Spotlight Video: SUCCESS")
else:
    print("3. Old spotlight block not found")

# 4. Update Dock Interviewer Video
old_dock = '''        <img id="dock-interviewer-img" src="" alt="Interviewer" class="w-full h-full object-cover object-top natural-face-anim pointer-events-none" />'''

new_dock = '''        <video id="dock-interviewer-video" autoplay loop muted playsinline class="w-full h-full object-cover object-center pointer-events-none"></video>
        <img id="dock-interviewer-img" src="" alt="Interviewer" class="w-full h-full object-cover object-center hidden pointer-events-none" />'''

if old_dock in content:
    content = content.replace(old_dock, new_dock)
    print("4. Replaced Dock Interviewer Video: SUCCESS")
else:
    print("4. Old dock block not found")

with open('frontend/pages/mock-interview.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved stage 1 patches successfully.")
