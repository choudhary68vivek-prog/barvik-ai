import os
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY or API_KEY == "PASTE_YOUR_API_KEY_HERE":
    raise RuntimeError(
        "Please add your Gemini API key to the .env file."
    )

client = genai.Client(api_key=API_KEY)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#06111f">
<title>BARVIK AI Command Center</title>

<style>
:root {
    --bg: #030a14;
    --panel: rgba(8, 26, 43, .96);
    --border: #16415a;
    --cyan: #39eaff;
    --blue: #159fff;
    --green: #36f5b0;
    --text: #dceeff;
    --muted: #7f9db6;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    min-height: 100vh;
    background:
        radial-gradient(ellipse at 55% 30%, #092743 0%, transparent 50%),
        var(--bg);
    color: var(--text);
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}
button, input { font: inherit; }
button { cursor: pointer; }
.app {
    min-height: 100vh;
    padding: 12px;
    display: grid;
    grid-template-columns: 190px minmax(0, 1fr);
    gap: 12px;
}
.panel {
    background: linear-gradient(145deg, #0a1c2c, #06111e);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: inset 0 0 18px #071b2b;
}
.sidebar {
    padding: 14px 10px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.logo {
    padding: 14px 5px 22px;
    text-align: center;
    color: var(--cyan);
    font-size: 23px;
    letter-spacing: 5px;
    text-shadow: 0 0 18px #00bfff;
}
.logo small {
    display: block;
    margin-top: 8px;
    font-size: 9px;
    letter-spacing: 3px;
    color: var(--muted);
}
.nav { display: flex; flex-direction: column; gap: 5px; }
.nav button {
    text-align: left;
    color: #b9d2e5;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 12px 8px;
}
.nav button:hover, .nav button.active {
    color: var(--cyan);
    background: #0d3046;
    border-color: #17617c;
}
.side-status {
    margin-top: auto;
    padding: 14px 8px;
    text-align: center;
}
.side-status p { color: var(--muted); }
.wave {
    color: var(--cyan);
    font-size: 21px;
    letter-spacing: 2px;
    animation: pulse 1.5s infinite alternate;
}
main { min-width: 0; }
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 14px;
    margin-bottom: 12px;
}
.status { color: var(--green); letter-spacing: 1px; }
.clock { color: var(--cyan); font-size: 19px; font-weight: bold; }
.dashboard {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(220px, 270px);
    gap: 12px;
}
.left-content, .right-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: 0;
}
.section { padding: 14px; min-width: 0; }
.section-title {
    color: #92bdd5;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.hero {
    min-height: 270px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(ellipse, rgba(0, 174, 255, .15), transparent 65%),
        #061525;
}
.orb {
    width: 180px;
    height: 180px;
    border: 1px solid #31cfff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        repeating-radial-gradient(circle, transparent 0 14px, #13527755 15px 16px),
        radial-gradient(circle, #103c5d, #06111e 72%);
    box-shadow: 0 0 25px #008dff66, inset 0 0 28px #008dff55;
    animation: float 5s ease-in-out infinite;
    position: relative;
}
.orb:before, .orb:after {
    content: "";
    position: absolute;
    width: 230px;
    height: 58px;
    border: 1px solid #24cfff77;
    border-radius: 50%;
    transform: rotate(-20deg);
}
.orb:after { transform: rotate(35deg); width: 210px; }
.orb-inner {
    position: relative;
    z-index: 1;
    text-align: center;
    color: var(--cyan);
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 4px;
    text-shadow: 0 0 16px #00cfff;
}
.orb-inner small {
    display: block;
    margin-top: 12px;
    font-size: 10px;
    letter-spacing: 4px;
}
.hero-caption {
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 3px;
    margin-top: 18px;
}
.cards {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 9px;
}
.stat {
    background: #0b2031;
    border: 1px solid #17415a;
    padding: 12px 9px;
    border-radius: 7px;
    min-width: 0;
}
.stat .icon { font-size: 19px; color: var(--cyan); margin-bottom: 8px; }
.stat strong { display: block; font-size: 12px; margin-bottom: 5px; }
.stat small { color: var(--green); font-size: 10px; }
.feed-item {
    padding: 11px 0;
    border-bottom: 1px solid #173348;
    line-height: 1.5;
}
.feed-item:last-child { border-bottom: 0; }
.feed-item small { display: block; color: var(--muted); margin-top: 4px; }
.quick {
    width: 100%;
    margin: 5px 0;
    padding: 11px;
    text-align: left;
    color: #cce8fa;
    background: #0a2235;
    border: 1px solid #194660;
    border-radius: 6px;
}
.quick:hover { border-color: var(--cyan); color: var(--cyan); }
.chat-panel { margin-top: 12px; }
.chat {
    height: 210px;
    overflow-y: auto;
    padding: 10px;
    background: #040d17;
    border: 1px solid #14334a;
    border-radius: 7px;
}
.message {
    padding: 10px 12px;
    margin: 8px 0;
    border-radius: 7px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    line-height: 1.5;
}
.bot { background: #0c2334; border-left: 2px solid var(--cyan); }
.user { background: #10344a; border-left: 2px solid var(--blue); }
.composer { display: flex; gap: 8px; margin-top: 10px; }
.composer input {
    flex: 1;
    min-width: 0;
    padding: 13px;
    color: white;
    background: #061421;
    border: 1px solid #1c4c65;
    border-radius: 7px;
    outline: none;
}
.composer input:focus { border-color: var(--cyan); }
.action {
    padding: 11px 15px;
    color: #00121c;
    background: var(--cyan);
    border: 0;
    border-radius: 7px;
    font-weight: bold;
}
.action:disabled { opacity: .5; }
.bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-top: 12px;
    padding: 15px;
}
.mic {
    width: 54px;
    height: 54px;
    border-radius: 50%;
    color: var(--cyan);
    background: #09263b;
    border: 1px solid var(--cyan);
    font-size: 23px;
    box-shadow: 0 0 16px #00bfff33;
}
.mic.listening {
    background: #124b59;
    box-shadow: 0 0 25px #00eaff99;
}
.muted { color: var(--muted); }
@keyframes pulse {
    from { opacity: .45; }
    to { opacity: 1; text-shadow: 0 0 15px var(--cyan); }
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
@media (min-width: 1500px) {
    .app { max-width: 1800px; margin: auto; }
}
@media (max-width: 850px) {
    .app { grid-template-columns: 1fr; padding: 7px; }
    .sidebar { padding: 8px; }
    .logo { padding: 7px; }
    .nav { flex-direction: row; overflow-x: auto; }
    .nav button { flex-shrink: 0; padding: 9px; }
    .side-status { display: none; }
    .dashboard { grid-template-columns: 1fr; }
    .right-content { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .hero { min-height: 230px; }
    .topbar { flex-wrap: wrap; }
}
@media (max-width: 480px) {
    .right-content { grid-template-columns: 1fr; }
    .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .clock { font-size: 16px; }
    .section { padding: 10px; }
    .composer { flex-wrap: wrap; }
    .composer input { flex-basis: 100%; }
    .bottom { flex-wrap: wrap; }
}
</style>
</head>

<body>
<div class="app">
<aside class="sidebar panel">
    <div class="logo">◉ BARVIK<small>COMMAND CENTER</small></div>
    <nav class="nav">
        <button class="active" data-section="Command Center">▦ Command Center</button>
        <button data-section="AI Core">◉ AI Core</button>
        <button data-section="Agents">♙ Agents</button>
        <button data-section="Tasks">☷ Tasks</button>
        <button data-section="Memory">▤ Memory</button>
        <button data-section="Conversations">▱ Conversations</button>
        <button data-section="Knowledge Base">◇ Knowledge Base</button>
        <button data-section="Tools & Skills">⚙ Tools & Skills</button>
        <button data-section="Workflows">⌘ Workflows</button>
    </nav>
    <div class="side-status panel">
        <div class="section-title">VOICE STATUS</div>
        <div class="wave">▁▃▆█▅▂▅█▆▃</div>
        <p id="voiceStatus">Voice standby</p>
        <button class="mic" id="mic" type="button" aria-label="Voice input">🎤</button>
        <p class="muted">Tap to speak</p>
    </div>
</aside>

<main>
    <header class="topbar panel">
        <div class="status">● SYSTEM STATUS: <strong>ONLINE</strong></div>
        <div class="clock" id="clock">BARVIK AI</div>
        <div class="muted">OPERATOR ▣</div>
    </header>

    <div class="dashboard">
        <div class="left-content">
            <section class="section hero panel">
                <div class="section-title">AI CORE OVERVIEW</div>
                <div class="orb">
                    <div class="orb-inner">BARVIK<small>AI CORE</small></div>
                </div>
                <div class="hero-caption">PERSONAL INTELLIGENCE SYSTEM</div>
            </section>

            <section class="section panel">
                <div class="section-title">AI SYSTEM OVERVIEW</div>
                <div class="cards">
                    <div class="stat"><div class="icon">◉</div><strong>AI Core</strong><small>● Connected</small></div>
                    <div class="stat"><div class="icon">▤</div><strong>Memory</strong><small>● Ready</small></div>
                    <div class="stat"><div class="icon">🎤</div><strong>Voice</strong><small id="voiceCard">● Standby</small></div>
                    <div class="stat"><div class="icon">⌘</div><strong>Agents</strong><small>● Interface ready</small></div>
                    <div class="stat"><div class="icon">⌁</div><strong>Gemini AI</strong><small>● Configured</small></div>
                    <div class="stat"><div class="icon">✓</div><strong>System</strong><small>● Online</small></div>
                </div>
            </section>

            <section class="section panel">
                <div class="section-title">BARVIK AI CONSOLE</div>
                <div class="chat" id="chat" aria-live="polite">
                    <div class="message bot">BARVIK: System online. Welcome, operator. How can I help you?</div>
                </div>
                <form class="composer" id="form">
                    <input id="question" placeholder="Enter command or ask BARVIK..." autocomplete="off" required>
                    <button class="mic" id="micMobile" type="button" aria-label="Voice input">🎤</button>
                    <button class="action" id="send" type="submit">EXECUTE ↗</button>
                </form>
            </section>
        </div>

        <div class="right-content">
            <section class="section panel">
                <div class="section-title">LIVE INTELLIGENCE FEED</div>
                <div class="feed-item">🟢 BARVIK AI Core<small>Interface initialized</small></div>
                <div class="feed-item">🔵 Gemini connection<small>Ready for questions</small></div>
                <div class="feed-item">🎤 Voice interface<small>Depends on browser support and permission</small></div>
                <div class="feed-item">🛡️ Security<small>API key stays on the server</small></div>
            </section>
            <section class="section panel">
                <div class="section-title">QUICK COMMANDS</div>
                <button class="quick" data-prompt="Introduce yourself as BARVIK.">＋ Introduce BARVIK</button>
                <button class="quick" data-prompt="Explain artificial intelligence in simple words.">◈ Explain AI</button>
                <button class="quick" data-prompt="Give me three useful tasks I can do today.">☷ Suggest tasks</button>
                <button class="quick" data-prompt="Help me learn Python programming as a beginner.">⌘ Learn Python</button>
            </section>
            <section class="section panel">
                <div class="section-title">SYSTEM MONITOR</div>
                <div class="feed-item">Network <span class="status">● Ready</span></div>
                <div class="feed-item">AI response <span class="status" id="responseStatus">● Idle</span></div>
                <p class="muted">Hardware metrics are not measured by this website.</p>
            </section>
        </div>
    </div>

    <footer class="bottom panel">
        <span class="muted">◉ BARVIK PERSONAL AI</span>
        <span class="status" id="bottomStatus">● READY FOR COMMAND</span>
        <span class="muted">GEMINI POWERED</span>
    </footer>
</main>
</div>

<script>
const form = document.getElementById("form");
const input = document.getElementById("question");
const chat = document.getElementById("chat");
const send = document.getElementById("send");
const micButtons = [
    document.getElementById("mic"),
    document.getElementById("micMobile")
];

function addMessage(text, who) {
    const box = document.createElement("div");
    box.className = "message " + who;
    box.textContent = text;
    chat.appendChild(box);
    chat.scrollTop = chat.scrollHeight;
    return box;
}

function setStatus(text) {
    document.getElementById("bottomStatus").textContent = text;
}

function setClock() {
    document.getElementById("clock").textContent =
        new Date().toLocaleString([], {
            weekday: "short", hour: "2-digit", minute: "2-digit", second: "2-digit"
        });
}
setClock();
setInterval(setClock, 1000);

document.querySelectorAll(".nav button").forEach(button => {
    button.addEventListener("click", () => {
        document.querySelectorAll(".nav button").forEach(b => b.classList.remove("active"));
        button.classList.add("active");
        if (button.dataset.section !== "Command Center") {
            addMessage(
                "BARVIK: " + button.dataset.section +
                " is currently a dashboard section. Its extra functions can be added in a future update.",
                "bot"
            );
        }
    });
});

document.querySelectorAll(".quick").forEach(button => {
    button.addEventListener("click", () => {
        input.value = button.dataset.prompt;
        form.requestSubmit();
    });
});

form.addEventListener("submit", async event => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question || send.disabled) return;

    addMessage("YOU: " + question, "user");
    input.value = "";
    send.disabled = true;
    const waiting = addMessage("BARVIK: Processing request...", "bot");
    setStatus("● PROCESSING");
    document.getElementById("responseStatus").textContent = "● Working";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({question})
        });
        const data = await response.json();
        waiting.textContent = "BARVIK: " +
            (data.answer || data.error || "No answer received.");
        if (!response.ok) {
            setStatus("● REQUEST FAILED");
        } else {
            setStatus("● RESPONSE RECEIVED");
        }
    } catch (error) {
        waiting.textContent = "BARVIK: Connection error. Please try again.";
        setStatus("● CONNECTION ERROR");
    } finally {
        send.disabled = false;
        document.getElementById("responseStatus").textContent = "● Idle";
        chat.scrollTop = chat.scrollHeight;
        input.focus();
    }
});

const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;
    let isListening = false;

    micButtons.forEach(button => button.addEventListener("click", () => {
        if (isListening) return;
        try {
            recognition.start();
        } catch (error) {
            setStatus("● VOICE ALREADY ACTIVE");
        }
    }));

    recognition.onstart = () => {
        isListening = true;
        micButtons.forEach(button => button.classList.add("listening"));
        document.getElementById("voiceStatus").textContent = "Listening...";
        document.getElementById("voiceCard").textContent = "● Listening";
        setStatus("● LISTENING");
    };

    recognition.onresult = event => {
        input.value = event.results[0][0].transcript;
        form.requestSubmit();
    };

    recognition.onerror = event => {
        document.getElementById("voiceStatus").textContent =
            "Voice unavailable: " + event.error;
        setStatus("● CHECK MICROPHONE PERMISSION");
    };

    recognition.onend = () => {
        isListening = false;
        micButtons.forEach(button => button.classList.remove("listening"));
        document.getElementById("voiceStatus").textContent = "Voice standby";
        document.getElementById("voiceCard").textContent = "● Standby";
    };
} else {
    micButtons.forEach(button => button.addEventListener("click", () => {
        alert("Speech recognition is not supported in this browser. Try Chrome on a secure website.");
    }));
}
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({"error": "Please type a question."}), 400

    if len(question) > 4000:
        return jsonify({
            "error": "Please keep your question under 4000 characters."
        }), 400

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are BARVIK, a helpful personal AI assistant. "
                    "Your name is BARVIK, never JARVIS. "
                    "Be friendly, clear, and concise. "
                    "Use simple language when explaining things."
                ),
                max_output_tokens=150
            )
        )

        answer = response.text or "I could not generate an answer."
        return jsonify({"answer": answer})

    except Exception:
        app.logger.exception("Gemini API request failed")
        return jsonify({
            "error": (
                "I could not contact Gemini. Check your API key, "
                "internet connection, model availability, and API access."
            )
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
