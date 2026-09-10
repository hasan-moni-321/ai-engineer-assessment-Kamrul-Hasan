const form = document.getElementById("chat-form");
const question = document.getElementById("question");
const statusEl = document.getElementById("status");
const answerEl = document.getElementById("answer");
const answerText = document.getElementById("answer-text");
const routeEl = document.getElementById("route");
const sourcesEl = document.getElementById("sources");
const metadataEl = document.getElementById("metadata");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  statusEl.textContent = "Thinking...";
  answerEl.classList.add("hidden");

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: question.value}),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Request failed");
    }

    answerText.textContent = data.answer;
    routeEl.textContent = JSON.stringify(data.route, null, 2);
    metadataEl.textContent = JSON.stringify(data.metadata, null, 2);

    sourcesEl.innerHTML = "";
    for (const source of data.sources || []) {
      const div = document.createElement("div");
      div.className = "source";
      div.textContent = JSON.stringify(source, null, 2);
      sourcesEl.appendChild(div);
    }

    answerEl.classList.remove("hidden");
    statusEl.textContent = "";
  } catch (error) {
    statusEl.textContent = error.message;
  }
});
