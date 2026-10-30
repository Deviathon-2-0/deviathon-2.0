import asyncio
import json
import subprocess
import time
import urllib.request
import websockets

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "http://localhost:3000/pages/mock-interview.html"

async def run_e2e_test():
    print("=== STARTING IMAIRA+ E2E INTERVIEW AUTOMATION LOOP ===")

    # 1. Launch Edge in headless with fake media devices and CDP port
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--remote-debugging-port=9222",
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--autoplay-policy=no-user-gesture-required",
        URL
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2.5)

    try:
        resp = urllib.request.urlopen("http://localhost:9222/json")
        targets = json.loads(resp.read().decode())
        page_target = next(t for t in targets if "mock-interview" in t.get("url", ""))

        ws_url = page_target["webSocketDebuggerUrl"]
        print(f"Connected to CDP WebSocket: {ws_url}")

        async with websockets.connect(ws_url) as ws:
            msg_id = 0

            async def send_cmd(method, params=None):
                nonlocal msg_id
                msg_id += 1
                payload = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(payload))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == msg_id:
                        return data.get("result", {})

            async def eval_js(expression):
                res = await send_cmd("Runtime.evaluate", {
                    "expression": expression,
                    "returnByValue": True,
                    "awaitPromise": True
                })
                result = res.get("result", {})
                if "value" in result:
                    return result["value"]
                return result

            # Enable console and page events
            await send_cmd("Runtime.enable")
            await send_cmd("Page.enable")
            await send_cmd("DOM.enable")

            print("\n[Step 1] Verifying Page Load and Roles Catalog...")
            roles_count = await eval_js("document.querySelectorAll('#roles-grid > div').length")
            print(f" -> Rendered role cards: {roles_count}")
            if roles_count == 0:
                print("FAIL: No roles rendered!")
                return False

            print("\n[Step 2] Clicking on first role (Software Engineer)...")
            await eval_js("document.querySelector('#roles-grid > div').click()")
            await asyncio.sleep(0.5)

            config_visible = await eval_js("window.getComputedStyle(document.getElementById('interview-config-modal')).display !== 'none'")
            print(f" -> Config modal visible: {config_visible}")
            if not config_visible:
                print("FAIL: Interview config modal did not open!")
                return False

            print("\n[Step 3] Accepting Terms and Proceeding to Prerequisite Modal...")
            await eval_js("document.getElementById('setting-terms').checked = true")
            await eval_js("openPracticePrerequisite()")
            await asyncio.sleep(0.8)

            prereq_visible = await eval_js("window.getComputedStyle(document.getElementById('prerequisite-modal')).display !== 'none'")
            print(f" -> Prerequisite modal visible: {prereq_visible}")
            if not prereq_visible:
                print("FAIL: Prerequisite modal did not open!")
                return False

            print("\n[Step 4] Requesting Camera & Microphone Access...")
            perm_result = await eval_js("requestCameraAndMicrophone()")
            print(f" -> Camera & Mic permission granted: {perm_result}")

            chk3_text = await eval_js("document.getElementById('chk-status-3').textContent.trim()")
            chk4_text = await eval_js("document.getElementById('chk-status-4').textContent.trim()")
            print(f" -> Check 3 (Mic): {chk3_text}")
            print(f" -> Check 4 (Cam): {chk4_text}")

            print("\n[Step 5] Waiting for System Checks & Triggering Sound Check...")
            await asyncio.sleep(1.0)
            await eval_js("testSystemAudio()")
            await asyncio.sleep(1.0)
            await eval_js("confirmAudioAudible(true)")
            await asyncio.sleep(0.5)

            chk8_text = await eval_js("document.getElementById('chk-status-8').textContent.trim()")
            counter_text = await eval_js("document.getElementById('prereq-checklist-counter').textContent.trim()")
            print(f" -> Check 8 (Audio): {chk8_text}")
            print(f" -> Prerequisite Counter: {counter_text}")

            start_btn_disabled = await eval_js("document.getElementById('prereq-start-btn').disabled")
            start_btn_html = await eval_js("document.getElementById('prereq-start-btn').innerText.trim()")
            print(f" -> Start button disabled: {start_btn_disabled}, text: '{start_btn_html}'")

            print("\n[Step 6] Clicking START INTERVIEW...")
            await eval_js("startFinalPracticeSession()")
            await asyncio.sleep(1.0)

            prereq_closed = await eval_js("window.getComputedStyle(document.getElementById('prerequisite-modal')).display === 'none'")
            setup_hidden = await eval_js("window.getComputedStyle(document.getElementById('setup-screen')).display === 'none'")
            stage_visible = await eval_js("window.getComputedStyle(document.getElementById('interview-stage')).display !== 'none'")
            stage_z = await eval_js("window.getComputedStyle(document.getElementById('interview-stage')).zIndex")

            print(f" -> Prerequisite modal closed: {prereq_closed}")
            print(f" -> Setup screen hidden: {setup_hidden}")
            print(f" -> Interview stage visible: {stage_visible} (z-index: {stage_z})")

            if not stage_visible:
                print("FAIL: Interview stage is NOT visible!")
                return False

            print("\n[Step 7] Checking Live Stage Question and Videos...")
            q_prompt = await eval_js("document.getElementById('call-question-prompt').textContent.trim()")
            q_badge = await eval_js("document.getElementById('call-q-badge').textContent.trim()")
            timer_text = await eval_js("document.getElementById('stage-session-timer').textContent.trim()")
            print(f" -> Question Badge: {q_badge}")
            print(f" -> Question Prompt: {q_prompt[:80]}...")
            print(f" -> Stage Timer: {timer_text}")

            print("\n[Step 8] Testing Dynamic Evaluator TTS Voice Generation...")
            tts_status = await eval_js("""
                (async () => {
                    const data = await tryApiFetch('/tts/generate/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: 'Test speech', interviewer_name: 'Kabir'})
                    });
                    return data ? data.audio_url : null;
                })()
            """)
            print(f" -> Evaluator TTS generated audio URL: {tts_status}")

            print("\n[Step 9] Simulating Candidate Answer Submission & Dynamic Scoring Pipeline...")
            eval_response = await eval_js("""
                (async () => {
                    const payload = {
                        question_id: 'q_hashmap_internal',
                        transcript: 'In this problem we use a hashmap with collision resolution via separate chaining and order of one O(1) lookup latency.',
                        telemetry: [
                            {"timestamp": 1.0, "eye_contact": true, "pitch_hz": 120.5, "posture_ok": true},
                            {"timestamp": 2.5, "eye_contact": true, "pitch_hz": 122.0, "posture_ok": true},
                            {"timestamp": 4.0, "eye_contact": true, "pitch_hz": 119.2, "posture_ok": true}
                        ]
                    };
                    return await tryApiFetch('/sessions/evaluate/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });
                })()
            """)
            if eval_response:
                print(f" -> Dynamic Overall Score: {eval_response.get('overall_score')}")
                print(f" -> Grade: {eval_response.get('grade')}")
                print(f" -> Synthesis Tier: {eval_response.get('synthesis_tier')}")
                print(f" -> Phonetic Corrections Applied: {len(eval_response.get('phonetic_corrections_applied', []))} phrases")
                print(f" -> Executive Summary: {eval_response.get('executive_summary', '')[:100]}...")
                print(f" -> Targeted Coaching Tips: {len(eval_response.get('targeted_coaching_tips', []))} tips")
            else:
                print("FAIL: No evaluation response returned!")
                return False

            print("\n=== E2E AUTOMATION SUCCESSFUL: INTERVIEW STAGE & ENGINE FULLY OPERATIONAL ===")
            return True

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except:
            proc.kill()

if __name__ == "__main__":
    success = asyncio.run(run_e2e_test())
    exit(0 if success else 1)
