const API_URL = "http://127.0.0.1:8000/chat";

const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const personaSelect = document.getElementById("persona");
const planContent = document.getElementById("plan-content");
const voiceOutputCheckbox = document.getElementById("voice-output");
const sessionIdSpan = document.getElementById("session-id");

// Generate a simple random session ID
const sessionId = "sess_" + Math.random().toString(36).slice(2);
sessionIdSpan.textContent = sessionId;

// --- Chat UI helpers --- //

function addMessage(role, text, meta = "") {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = text.replace(/\n/g, "<br/>");

  const metaEl = document.createElement("div");
  metaEl.className = "meta";
  metaEl.textContent = meta;

  wrapper.appendChild(bubble);
  if (meta) wrapper.appendChild(metaEl);

  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// --- Plan UI helper --- //

function renderPlan(plan) {
  if (!plan) {
    planContent.innerHTML =
      '<p class="placeholder">No account plan yet. Ask me to “generate plan” once research is done.</p>';
    return;
  }

  const sectionOrder = [
    "company_overview",
    "key_initiatives",
    "org_map_and_stakeholders",
    "current_tech_landscape",
    "opportunities_for_us",
    "risks_and_red_flags",
    "next_steps",
  ];

  let html = "";
  sectionOrder.forEach((key) => {
    if (plan[key]) {
      const title = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
      html += `<div class="plan-section-block">
        <h3>${title}</h3>
        <p>${plan[key].replace(/\n/g, "<br/>")}</p>
      </div>`;
    }
  });

  planContent.innerHTML = html || '<p class="placeholder">Plan is empty.</p>';
}

// --- Text-to-speech --- //

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1.0;
  utter.pitch = 1.0;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
}

// --- Send message to backend --- //

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  const persona = personaSelect.value;

  addMessage("user", text);

  userInput.value = "";
  userInput.focus();

  // Temporary “Thinking…” message
  const loadingMarker = document.createElement("div");
  loadingMarker.className = "message assistant";
  loadingMarker.innerHTML = '<div class="bubble">Thinking...</div>';
  chatWindow.appendChild(loadingMarker);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        message: text,
        persona: persona,
      }),
    });

    if (!res.ok) {
      throw new Error("API error: " + res.status);
    }

    const data = await res.json();

    // Remove loading message
    if (loadingMarker && loadingMarker.parentNode === chatWindow) {
      chatWindow.removeChild(loadingMarker);
    }

    addMessage(
      "assistant",
      data.reply,
      `Mode: ${data.mode}${data.company ? " | Company: " + data.company : ""}`
    );

    if (data.account_plan) {
      renderPlan(data.account_plan);
    }

    if (voiceOutputCheckbox.checked) {
      const spokenText =
        data.reply.length > 700
          ? data.reply.slice(0, 700) + " ... (truncated)"
          : data.reply;
      speak(spokenText);
    }
  } catch (err) {
    console.error(err);
    if (loadingMarker && loadingMarker.parentNode === chatWindow) {
      chatWindow.removeChild(loadingMarker);
    }
    addMessage(
      "assistant",
      "Oops, something went wrong talking to the backend. Is the FastAPI server running?",
      "Error"
    );
  }
}

// --- Speech recognition --- //

let recognition = null;
let listening = false;

if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;

  recognition.onstart = () => {
    listening = true;
    micBtn.classList.add("listening");
    micBtn.textContent = "🔴";
  };

  recognition.onend = () => {
    listening = false;
    micBtn.classList.remove("listening");
    micBtn.textContent = "🎙️";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    sendMessage();
  };
} else {
  micBtn.disabled = true;
  micBtn.title = "Speech recognition not supported in this browser";
}

micBtn.addEventListener("click", () => {
  if (!recognition) return;
  if (!listening) {
    recognition.start();
  } else {
    recognition.stop();
  }
});

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Initial greeting
addMessage(
  "assistant",
  "Hi, I’m your Company Research Assistant 👋.<br/>" +
    "Tell me a company name, like <b>“Research Zeta company”</b>, and I’ll research it and generate an account plan for you.",
  "Mode: discovery"
);