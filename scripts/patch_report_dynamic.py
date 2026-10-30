import os

def patch_report():
    file_path = os.path.join('frontend', 'pages', 'report.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    newline = '\r\n' if '\r\n' in html else '\n'
    html = html.replace('\r\n', '\n')

    # Add IDs to the metric cards in HTML
    old_header = '''        <div>
          <div class="flex items-center gap-2 mb-2">
            <span class="px-3 py-1 rounded-full bg-[#FBF3E0] text-[#AA7000] text-[11px] font-bold border border-[#E8C97A]">
              System Design &amp; Distributed Consensus
            </span>
            <span class="text-xs text-[#7F766C]">• Session ID: #SES-9821</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#2C1F0E]">
            Staff Backend Architect Evaluation
          </h1>
          <p class="text-xs text-[#8C7B6B] mt-1">
            Conducted on October 28, 2026 • 28 minutes duration • 5 core questions evaluated
          </p>
        </div>

        <div class="flex items-center gap-4 bg-[#FAF6EE] p-4 rounded-2xl border border-[#E8DFD0] shrink-0">
          <div>
            <div class="text-[11px] font-bold uppercase tracking-wider text-[#7F766C]">Composite Grade</div>
            <div class="text-3xl font-black text-[#2C1F0E]">91.6 <span class="text-sm font-semibold text-[#7F766C]">/ 100</span></div>
          </div>
          <div class="w-12 h-12 rounded-2xl bg-[#EFF4E8] text-[#4F6B2D] font-black text-xl flex items-center justify-center border border-[#4F6B2D]/30">
            A
          </div>
        </div>'''

    new_header = '''        <div>
          <div class="flex items-center gap-2 mb-2">
            <span id="report-track-badge" class="px-3 py-1 rounded-full bg-[#FBF3E0] text-[#AA7000] text-[11px] font-bold border border-[#E8C97A]">
              System Design &amp; Distributed Consensus
            </span>
            <span id="report-session-id" class="text-xs text-[#7F766C]">• Session ID: #SES-9821</span>
          </div>
          <h1 id="report-role-title" class="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#2C1F0E]">
            Staff Backend Architect Evaluation
          </h1>
          <p id="report-meta-text" class="text-xs text-[#8C7B6B] mt-1">
            Conducted on October 28, 2026 • 28 minutes duration • 4 core questions evaluated
          </p>
        </div>

        <div class="flex items-center gap-4 bg-[#FAF6EE] p-4 rounded-2xl border border-[#E8DFD0] shrink-0">
          <div>
            <div class="text-[11px] font-bold uppercase tracking-wider text-[#7F766C]">Composite Grade</div>
            <div class="text-3xl font-black text-[#2C1F0E]"><span id="report-overall-score">91.6</span> <span class="text-sm font-semibold text-[#7F766C]">/ 100</span></div>
          </div>
          <div id="report-grade-badge" class="w-12 h-12 rounded-2xl bg-[#EFF4E8] text-[#4F6B2D] font-black text-xl flex items-center justify-center border border-[#4F6B2D]/30">
            A
          </div>
        </div>'''

    if old_header in html:
        html = html.replace(old_header, new_header)
        print("Header IDs patched.")

    # Body Language card
    old_body = '''            <div class="flex items-baseline gap-2 mb-3">
              <span class="text-4xl font-black text-[#2C1F0E]">78</span>
              <span class="text-sm font-semibold text-[#7F766C]">/ 100</span>
              <span class="ml-auto text-[11px] font-bold text-[#AA7000] bg-[#FBF3E0] px-2.5 py-0.5 rounded-full">Good Presence</span>
            </div>
            <div class="w-full bg-[#FAF6EE] h-2 rounded-full overflow-hidden mb-4 border border-[#E8DFD0]">
              <div class="bg-[#AA7000] h-full rounded-full" style="width: 78%"></div>
            </div>'''

    new_body = '''            <div class="flex items-baseline gap-2 mb-3">
              <span id="report-score-body" class="text-4xl font-black text-[#2C1F0E]">78</span>
              <span class="text-sm font-semibold text-[#7F766C]">/ 100</span>
              <span id="report-badge-body" class="ml-auto text-[11px] font-bold text-[#AA7000] bg-[#FBF3E0] px-2.5 py-0.5 rounded-full">Good Presence</span>
            </div>
            <div class="w-full bg-[#FAF6EE] h-2 rounded-full overflow-hidden mb-4 border border-[#E8DFD0]">
              <div id="report-bar-body" class="bg-[#AA7000] h-full rounded-full" style="width: 78%"></div>
            </div>'''

    if old_body in html:
        html = html.replace(old_body, new_body)
        print("Body card patched.")

    # Tech depth card
    old_tech = '''            <div class="flex items-baseline gap-2 mb-3">
              <span class="text-4xl font-black text-[#2C1F0E]">92</span>
              <span class="text-sm font-semibold text-[#7F766C]">/ 100</span>
              <span class="ml-auto text-[11px] font-bold text-[#4F6B2D] bg-[#EFF4E8] px-2.5 py-0.5 rounded-full">Staff Level</span>
            </div>
            <div class="w-full bg-[#FAF6EE] h-2 rounded-full overflow-hidden mb-4 border border-[#E8DFD0]">
              <div class="bg-[#2C1F0E] h-full rounded-full" style="width: 92%"></div>
            </div>'''

    new_tech = '''            <div class="flex items-baseline gap-2 mb-3">
              <span id="report-score-tech" class="text-4xl font-black text-[#2C1F0E]">92</span>
              <span class="text-sm font-semibold text-[#7F766C]">/ 100</span>
              <span id="report-badge-tech" class="ml-auto text-[11px] font-bold text-[#4F6B2D] bg-[#EFF4E8] px-2.5 py-0.5 rounded-full">Staff Level</span>
            </div>
            <div class="w-full bg-[#FAF6EE] h-2 rounded-full overflow-hidden mb-4 border border-[#E8DFD0]">
              <div id="report-bar-tech" class="bg-[#2C1F0E] h-full rounded-full" style="width: 92%"></div>
            </div>'''

    if old_tech in html:
        html = html.replace(old_tech, new_tech)
        print("Tech card patched.")

    # Speech clarity card
    old_speech = '''            <div class="flex items-baseline gap-2 mb-3">
              <span class="text-4xl font-black text-[#2C1F0E]">95</span>
              <span class="text-sm font-semibold text-[#7F766C]">/ 100</span>
              <span class="ml-auto text-[11px] font-bold text-[#4F6B2D] bg-[#EFF4E8] px-2.5 py-0.5 rounded-full">Exemplary</span>
            </div>
            <div class="w-full bg-[#FAF6EE] h-2 rounded-full overflow-hidden mb-4 border border-[#E8DFD0]">
              <div class="bg-[#4F6B2D] h-full rounded-full" style="width: 95%"></div>
            </div>'''

    new_speech = '''            <div class="flex items-baseline gap-2 mb-3">
              <span id="report-score-speech" class="text-4xl font-black text-[#2C1F0E]">95</span>
              <span class="text-sm font-semibold text-[#7F766C]">/ 100</span>
              <span id="report-badge-speech" class="ml-auto text-[11px] font-bold text-[#4F6B2D] bg-[#EFF4E8] px-2.5 py-0.5 rounded-full">Exemplary</span>
            </div>
            <div class="w-full bg-[#FAF6EE] h-2 rounded-full overflow-hidden mb-4 border border-[#E8DFD0]">
              <div id="report-bar-speech" class="bg-[#4F6B2D] h-full rounded-full" style="width: 95%"></div>
            </div>'''

    if old_speech in html:
        html = html.replace(old_speech, new_speech)
        print("Speech card patched.")

    # Dynamic hydration script
    script_to_add = '''
    // Populate session report from live Django backend evaluation
    try {
      const storedReport = localStorage.getItem('imaira_session_report');
      if (storedReport) {
        const rep = JSON.parse(storedReport);
        if (rep) {
          if (rep.session_id) {
            const sidEl = document.getElementById('report-session-id');
            if (sidEl) sidEl.textContent = `• Session ID: #${rep.session_id.substring(0, 8).toUpperCase()}`;
          }
          if (rep.overall_score) {
            const sc = parseFloat(rep.overall_score).toFixed(1);
            const scEl = document.getElementById('report-overall-score');
            if (scEl) scEl.textContent = sc;

            const gradeEl = document.getElementById('report-grade-badge');
            if (gradeEl) {
              const num = parseFloat(sc);
              gradeEl.textContent = num >= 90 ? 'A' : (num >= 80 ? 'B' : (num >= 70 ? 'C' : 'D'));
            }
          }
          if (rep.score_technical_depth) {
            const val = Math.round(rep.score_technical_depth);
            const valEl = document.getElementById('report-score-tech');
            const barEl = document.getElementById('report-bar-tech');
            if (valEl) valEl.textContent = val;
            if (barEl) barEl.style.width = `${val}%`;
          }
          if (rep.score_speech_clarity) {
            const val = Math.round(rep.score_speech_clarity);
            const valEl = document.getElementById('report-score-speech');
            const barEl = document.getElementById('report-bar-speech');
            if (valEl) valEl.textContent = val;
            if (barEl) barEl.style.width = `${val}%`;
          }
          if (rep.score_body_language) {
            const val = Math.round(rep.score_body_language);
            const valEl = document.getElementById('report-score-body');
            const barEl = document.getElementById('report-bar-body');
            if (valEl) valEl.textContent = val;
            if (barEl) barEl.style.width = `${val}%`;
          }
        }
      }
    } catch (e) {
      console.log("Report hydration notice:", e);
    }
'''

    if 'function switchTab' in html:
        html = html.replace('    function switchTab', script_to_add + '\n    function switchTab')
        print("Script hydration injected.")

    if newline == '\r\n':
        html = html.replace('\n', '\r\n')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("report.html patched successfully.")

if __name__ == '__main__':
    patch_report()

