import json

import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Azure AI API Sandbox</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Geist:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['Geist', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
            mono: ['Geist Mono', 'monospace'],
          }
        }
      }
    }
  </script>
</head>
<body class="bg-white text-zinc-950 font-sans min-h-screen antialiased selection:bg-zinc-200">

  <!-- Navbar -->
  <header class="border-b border-zinc-200 sticky top-0 bg-white/80 backdrop-blur-sm z-50">
    <div class="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-4 h-4 rounded bg-zinc-950 flex items-center justify-center">
          <div class="w-2 h-2 bg-white rounded-sm"></div>
        </div>
        <span class="text-sm font-semibold tracking-tight text-zinc-900">poc-pama / ai-gateway</span>
      </div>
    </div>
  </header>

  <!-- Main Workspace -->
  <main class="max-w-7xl mx-auto px-6 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- Left Column: Config & Request -->
      <section class="lg:col-span-6 space-y-6">

        <!-- Target Config Box -->
        <div class="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold tracking-tight text-zinc-900">Gateway Target</h3>
            <span class="text-[11px] font-mono text-zinc-600 bg-zinc-100 border border-zinc-200 px-2 py-0.5 rounded">POST</span>
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-medium text-zinc-600">Target Endpoint URL</label>
            <input type="text" id="endpoint"
              class="w-full bg-zinc-50/50 border border-zinc-200 rounded-md px-3 py-2 text-xs font-mono text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950 transition placeholder:text-zinc-400"
              value="https://pama-apim.azure-api.net/api2/openai/deployments/gpt-5.4-mini/chat/completions?api-version=2025-03-01-preview" />
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-medium text-zinc-600">Subscription Key <span class="text-zinc-400 font-normal">(Auto-injected ke query/header)</span></label>
            <input type="password" id="subscriptionKey" placeholder="f6d9a969c6464a2f8add..."
              class="w-full bg-zinc-50/50 border border-zinc-200 rounded-md px-3 py-2 text-xs font-mono text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950 transition placeholder:text-zinc-400" />
          </div>
        </div>

        <!-- Payload Editor Box -->
        <div class="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div class="flex space-x-2">
              <button onclick="switchMode('builder')" id="tabBuilder"
                class="px-2.5 py-1 text-xs font-medium rounded-md bg-zinc-900 text-white shadow-sm">Visual Form</button>
              <button onclick="switchMode('json')" id="tabJson"
                class="px-2.5 py-1 text-xs font-medium rounded-md text-zinc-600 hover:text-zinc-950 hover:bg-zinc-100 transition">Raw JSON</button>
            </div>
            <span class="text-[11px] text-zinc-500 font-mono">application/json</span>
          </div>

          <!-- Tab 1: Visual Form -->
          <div id="builderView" class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <label class="text-xs font-medium text-zinc-600">Model Deployment</label>
                <input type="text" id="modelInput" value="gpt-5.4-mini"
                  class="w-full bg-zinc-50/50 border border-zinc-200 rounded-md px-3 py-1.5 text-xs font-mono text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950" />
              </div>
              <div class="space-y-1.5">
                <label class="text-xs font-medium text-zinc-600">Max Tokens</label>
                <input type="number" id="tokensInput" value="5000"
                  class="w-full bg-zinc-50/50 border border-zinc-200 rounded-md px-3 py-1.5 text-xs font-mono text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950" />
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-xs font-medium text-zinc-600">System Instruction</label>
              <input type="text" id="systemPrompt" value="You are an advanced AI assistant. Provide a detailed, highly structured, and comprehensive response."
                class="w-full bg-zinc-50/50 border border-zinc-200 rounded-md px-3 py-2 text-xs text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950" />
            </div>

            <div class="space-y-1.5">
              <label class="text-xs font-medium text-zinc-600">User Prompt</label>
              <textarea id="userPrompt" rows="4"
                class="w-full bg-zinc-50/50 border border-zinc-200 rounded-md px-3 py-2 text-xs text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950 resize-none font-sans"
                placeholder="Type your prompt here...">create golang code for basic djikstra simulation</textarea>
            </div>
          </div>

          <!-- Tab 2: Raw JSON -->
          <div id="jsonView" class="space-y-2 hidden">
            <textarea id="rawJsonArea" rows="12"
              class="w-full bg-zinc-50 border border-zinc-200 rounded-md p-3 text-xs font-mono text-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-950 leading-relaxed resize-y"></textarea>
          </div>

          <!-- Action Button -->
          <button onclick="dispatchRequest()" id="btnSend"
            class="w-full inline-flex items-center justify-center rounded-md text-xs font-medium transition-colors bg-zinc-950 text-white hover:bg-zinc-800 h-9 px-4 py-2 font-semibold shadow-sm">
            Send Request (Ctrl + Enter)
          </button>
        </div>
      </section>

      <!-- Right Column: Response Inspector -->
      <section class="lg:col-span-6 space-y-6">
        <div class="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm space-y-4 flex flex-col h-full min-h-[500px]">

          <div class="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div class="flex items-center space-x-3">
              <h3 class="text-sm font-semibold tracking-tight text-zinc-900">Inspector</h3>
              <div id="statusBadge" class="hidden text-[11px] font-mono px-2 py-0.5 rounded-full border"></div>
              <span id="latencyBadge" class="hidden text-[11px] font-mono text-zinc-500 font-medium"></span>
            </div>
            <button onclick="copyResponse()" id="btnCopy"
              class="text-xs text-zinc-600 hover:text-zinc-950 border border-zinc-200 px-2 py-1 rounded bg-zinc-50 hover:bg-zinc-100 transition shadow-xs">
              Copy JSON
            </button>
          </div>

          <!-- Response Container -->
          <div class="relative flex-1 bg-zinc-50 border border-zinc-200 rounded-md overflow-hidden">
            <pre id="responseBox" class="p-4 text-xs font-mono text-zinc-800 overflow-auto h-[480px] leading-relaxed select-all">// Responses from APIM will stream here...</pre>
          </div>
        </div>
      </section>

    </div>
  </main>

  <script>
    let activeMode = 'builder';

    function switchMode(mode) {
      activeMode = mode;
      const bView = document.getElementById('builderView');
      const jView = document.getElementById('jsonView');
      const tabB = document.getElementById('tabBuilder');
      const tabJ = document.getElementById('tabJson');

      if (mode === 'builder') {
        bView.classList.remove('hidden');
        jView.classList.add('hidden');
        tabB.className = "px-2.5 py-1 text-xs font-medium rounded-md bg-zinc-900 text-white shadow-sm";
        tabJ.className = "px-2.5 py-1 text-xs font-medium rounded-md text-zinc-600 hover:text-zinc-950 hover:bg-zinc-100 transition";
      } else {
        document.getElementById('rawJsonArea').value = JSON.stringify(constructPayloadFromForm(), null, 2);
        bView.classList.add('hidden');
        jView.classList.remove('hidden');
        tabJ.className = "px-2.5 py-1 text-xs font-medium rounded-md bg-zinc-900 text-white shadow-sm";
        tabB.className = "px-2.5 py-1 text-xs font-medium rounded-md text-zinc-600 hover:text-zinc-950 hover:bg-zinc-100 transition";
      }
    }

    function constructPayloadFromForm() {
      return {
        model: document.getElementById('modelInput').value.trim() || 'gpt-5.4-mini',
        messages: [
          { role: "system", content: document.getElementById('systemPrompt').value },
          { role: "user", content: document.getElementById('userPrompt').value }
        ],
        max_completion_tokens: parseInt(document.getElementById('tokensInput').value) || 5000
      };
    }

    async function dispatchRequest() {
      const btn = document.getElementById('btnSend');
      const resBox = document.getElementById('responseBox');
      const statusBadge = document.getElementById('statusBadge');
      const latencyBadge = document.getElementById('latencyBadge');

      const endpoint = document.getElementById('endpoint').value.trim();
      const subscriptionKey = document.getElementById('subscriptionKey').value.trim();

      if (!endpoint) {
        alert("Target endpoint URL is mandatory.");
        return;
      }

      let payload;
      if (activeMode === 'builder') {
        payload = constructPayloadFromForm();
      } else {
        try {
          payload = JSON.parse(document.getElementById('rawJsonArea').value);
        } catch(e) {
          alert("Invalid JSON format in payload editor: " + e.message);
          return;
        }
      }

      btn.disabled = true;
      btn.innerText = "Dispatching...";
      resBox.innerText = "Waiting for response from APIM gateway...";
      statusBadge.className = "hidden";
      latencyBadge.className = "hidden";

      const startTime = performance.now();

      try {
        const res = await fetch('/api/proxy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            endpoint: endpoint,
            subscriptionKey: subscriptionKey,
            payload: payload
          })
        });

        const elapsed = Math.round(performance.now() - startTime);
        const data = await res.json();

        // Status Code Badge
        statusBadge.innerText = `${res.status} ${res.statusText || (res.status === 200 ? 'OK' : 'ERR')}`;
        statusBadge.classList.remove('hidden');
        if (res.status >= 200 && res.status < 300) {
          statusBadge.className = "text-[11px] font-mono px-2 py-0.5 rounded-full border border-emerald-300 bg-emerald-50 text-emerald-700";
        } else {
          statusBadge.className = "text-[11px] font-mono px-2 py-0.5 rounded-full border border-rose-300 bg-rose-50 text-rose-700";
        }

        // Latency Badge
        latencyBadge.innerText = `${elapsed}ms`;
        latencyBadge.classList.remove('hidden');

        resBox.innerText = JSON.stringify(data, null, 2);
      } catch (err) {
        resBox.innerText = "Connection Failed: " + err.message;
        statusBadge.innerText = "500 Client Error";
        statusBadge.className = "text-[11px] font-mono px-2 py-0.5 rounded-full border border-rose-300 bg-rose-50 text-rose-700";
        statusBadge.classList.remove('hidden');
      } finally {
        btn.disabled = false;
        btn.innerText = "Send Request (Ctrl + Enter)";
      }
    }

    function copyResponse() {
      const text = document.getElementById('responseBox').innerText;
      navigator.clipboard.writeText(text);
      const btn = document.getElementById('btnCopy');
      btn.innerText = "Copied!";
      setTimeout(() => btn.innerText = "Copy JSON", 1500);
    }

    // Keyboard shortcut: Ctrl + Enter / Cmd + Enter
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        dispatchRequest();
      }
    });
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/healthz", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/api/proxy", methods=["POST"])
def proxy():
    req_data = request.get_json(force=True)
    target_url = req_data.get("endpoint", "").strip()
    sub_key = req_data.get("subscriptionKey", "").strip()
    payload = req_data.get("payload", {})

    if sub_key and "subscription-key=" not in target_url:
        separator = "&" if "?" in target_url else "?"
        target_url = f"{target_url}{separator}subscription-key={sub_key}"

    headers = {"Content-Type": "application/json"}
    if sub_key:
        headers["Ocp-Apim-Subscription-Key"] = sub_key

    try:
        resp = requests.post(
            target_url,
            json=payload,
            headers=headers,
            timeout=90
        )
        try:
            return jsonify(resp.json()), resp.status_code
        except ValueError:
            return jsonify({"raw_response": resp.text}), resp.status_code
    except Exception as e:
        return jsonify({"proxy_error": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
