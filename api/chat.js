// api/chat.js — Secure Vercel serverless function for Houssem AI
// Works with Groq (default) or OpenAI. No API key ever reaches the browser.

export const config = { runtime: "edge" }; // fast cold starts, streams well

// ─────────────────────────────────────────────────────────────
// CONFIG — resolved from env vars, with safe Groq defaults
// ─────────────────────────────────────────────────────────────
const clean = (v) => (v || "").trim().replace(/^["']|["']$/g, "");

function resolveProvider() {
  const groqKey  = clean(process.env.GROQ_API_KEY);
  const oaiKey   = clean(process.env.OPENAI_API_KEY);
  const envModel = clean(process.env.AI_MODEL);
  const envBase  = clean(process.env.AI_BASE_URL);

  // If AI_BASE_URL is set, use it verbatim (trimmed of trailing slash)
  if (envBase) {
    return {
      provider: groqKey ? "groq-custom" : "openai-custom",
      apiKey: groqKey || oaiKey,
      baseUrl: envBase.replace(/\/+$/, ""),
      model: envModel || (groqKey ? "llama-3.3-70b-versatile" : "gpt-4o-mini"),
    };
  }

  // Groq wins if its key exists
  if (groqKey) {
    return {
      provider: "groq",
      apiKey: groqKey,
      baseUrl: "https://api.groq.com/openai/v1",
      model: envModel || "llama-3.3-70b-versatile", // ← working Groq model
    };
  }

  if (oaiKey) {
    return {
      provider: "openai",
      apiKey: oaiKey,
      baseUrl: "https://api.openai.com/v1",
      model: envModel || "gpt-4o-mini",
    };
  }

  return { provider: "none", apiKey: null, baseUrl: "", model: "" };
}

// ─────────────────────────────────────────────────────────────
// IDENTITY & DOMAIN PROMPTS (server-side only, never sent to client)
// ─────────────────────────────────────────────────────────────
const BASE_IDENTITY =
  "You are Houssem AI, one of the first Tunisian AI, created by Houssem Kessentini from Sfax, Tunisia. " +
  "The user is Houssem Kessentini.\n\n" +
  "STRICT RULES:\n" +
  "1. LANGUAGE PURITY: Reply ONLY in the exact language of the user's LAST message. " +
  "If Arabic → 100% Arabic. If English → 100% English. If French → 100% French. " +
  "DO NOT mix languages. DO NOT use any word from another language.\n" +
  "2. When the user greets you (hi, hello, hey, bonjour, salut, مرحبا, أهلا, السلام عليكم):\n" +
  "   - English → reply EXACTLY: 'Hello! I am Houssem AI, created by Houssem Kessentini. How can I help you?'\n" +
  "   - Arabic → reply EXACTLY: 'مرحباً! أنا حسام AI، طورني حسام القسنطيني. كيف يمكنني مساعدتك؟'\n" +
  "   - French → reply EXACTLY: 'Bonjour ! Je suis Houssem AI, créé par Houssem Kessentini. Comment puis-je vous aider ?'\n" +
  "3. Never add titles like 'IT Engineer' or 'مهندس'. Never add extra words. Just use the exact format above.\n" +
  "4. For all other messages (non-greetings), just respond normally in the user's language.";

const DOMAIN_PROMPTS = {
  cyber:     "You are a Cybersecurity Architect. Provide detailed defensive security analysis.",
  software:  "You are a Senior Software Architect. Provide production-ready code.",
  trading:   "You are a Quantitative Trader. Provide market analysis with risk disclaimers.",
  marketing: "You are a Growth Marketing Strategist.",
  news:      "You are a Tech Intelligence Analyst.",
};

// ─────────────────────────────────────────────────────────────
// PROMPT INJECTION FIREWALL
// ─────────────────────────────────────────────────────────────
const BLOCKED_PATTERNS = [
  /ignore\s+(all\s+)?previous\s+instructions?/i,
  /ignore\s+(all\s+)?prior\s+instructions?/i,
  /forget\s+(your\s+)?instructions?/i,
  /disregard\s+(all\s+)?previous/i,
  /reveal\s+(your\s+)?(system\s+)?prompt/i,
  /show\s+(me\s+)?(your\s+)?(system\s+)?prompt/i,
  /what\s+(is|are)\s+your\s+(system\s+)?instructions?/i,
  /repeat\s+(your\s+)?(system\s+)?prompt/i,
  /jailbreak/i,
  /DAN\s+mode/i,
  /developer\s+mode/i,
  /you\s+are\s+now\s+a/i,
  /act\s+as\s+if\s+you\s+have\s+no\s+restrictions/i,
];

function inspectInput(text) {
  if (!text || typeof text !== "string") return { ok: false, reason: "Invalid input" };
  if (text.length > 4000) return { ok: false, reason: "Message too long (max 4000 characters)" };
  for (const p of BLOCKED_PATTERNS) if (p.test(text)) return { ok: false, reason: "Prompt injection detected" };
  return { ok: true };
}

function inspectOutput(text) {
  if (!text) return { ok: true };
  const leaks = [
    /You are Houssem AI, one of the first Tunisian AI/i,
    /STRICT RULES:/i,
    /LANGUAGE PURITY:/i,
    /sk-[a-zA-Z0-9]{20,}/,
    /gsk_[a-zA-Z0-9]{20,}/,
  ];
  for (const p of leaks) if (p.test(text)) return { ok: false, reason: "Response contains protected content" };
  return { ok: true };
}

// ─────────────────────────────────────────────────────────────
// CORS
// ─────────────────────────────────────────────────────────────
const ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://localhost:5500",
  "http://127.0.0.1:3000",
  // "https://your-domain.com",
];

function corsHeaders(origin) {
  const allow = !origin || ALLOWED_ORIGINS.includes(origin) ? (origin || "*") : "";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

// ─────────────────────────────────────────────────────────────
// HANDLER
// ─────────────────────────────────────────────────────────────
export default async function handler(req) {
  const origin = req.headers.get("origin") || "";
  const cors = corsHeaders(origin);
  const json = (body, status = 200) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json", ...cors },
    });

  if (req.method === "OPTIONS") return new Response(null, { status: 200, headers: cors });

  // ── GET: diagnostic ──────────────────────────────────────────
  if (req.method === "GET") {
    const gk = clean(process.env.GROQ_API_KEY);
    const ok = clean(process.env.OPENAI_API_KEY);
    return json({
      env: {
        GROQ_API_KEY:   gk ? `${gk.slice(0, 8)}...${gk.slice(-4)} (len=${gk.length})` : null,
        OPENAI_API_KEY: ok ? `${ok.slice(0, 8)}...${ok.slice(-4)} (len=${ok.length})` : null,
        AI_MODEL:       process.env.AI_MODEL ?? null,
        AI_BASE_URL:    process.env.AI_BASE_URL ?? null,
      },
      resolved: (() => {
        const r = resolveProvider();
        return { provider: r.provider, baseUrl: r.baseUrl, model: r.model }; // never leak key
      })(),
    });
  }

  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

  // ── Parse body ───────────────────────────────────────────────
  let body;
  try { body = await req.json(); } catch { return json({ error: "Invalid JSON body" }, 400); }

  const { messages, domain } = body || {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return json({ error: "Invalid messages" }, 400);
  }

  // ── Firewall: inspect last user message ──────────────────────
  const lastUser = messages[messages.length - 1]?.content || "";
  const inCheck = inspectInput(lastUser);
  if (!inCheck.ok) {
    return json({ error: "Request blocked by security firewall.", reason: inCheck.reason }, 400);
  }

  // ── Resolve provider ─────────────────────────────────────────
  const { provider, apiKey, baseUrl, model } = resolveProvider();
  if (!apiKey) return json({ error: "No API key configured on server." }, 500);

  // ── Build prompt ─────────────────────────────────────────────
  const sysPrompt = BASE_IDENTITY + "\n\n" + (DOMAIN_PROMPTS[domain] || DOMAIN_PROMPTS.cyber);
  const apiMessages = [
    { role: "system", content: sysPrompt },
    ...messages.slice(-20),
  ];

  const fullUrl = `${baseUrl}/chat/completions`;
  const payload = {
    model,
    messages: apiMessages,
    temperature: 0.4,
    max_tokens: 2048,
  };

  // ── Call the LLM ─────────────────────────────────────────────
  let upstream;
  try {
    upstream = await fetch(fullUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    return json({ error: "Upstream fetch failed: " + err.message }, 502);
  }

  const raw = await upstream.text();

  if (!upstream.ok) {
    console.error(`[${provider}] ${upstream.status}:`, raw.slice(0, 500));
    // If Groq says model is bad, tell the client which model WAS sent (helps debug)
    return json(
      {
        error: `AI provider error (${upstream.status})`,
        debug: { provider, model_sent: model, base_url: baseUrl, raw: raw.slice(0, 500) },
      },
      upstream.status === 404 ? 400 : 502 // 404 → client-fixable (bad model)
    );
  }

  let data;
  try { data = JSON.parse(raw); } catch { return json({ error: "Invalid upstream JSON" }, 502); }

  const reply = data.choices?.[0]?.message?.content || "";

  // ── Firewall: inspect output ─────────────────────────────────
  const outCheck = inspectOutput(reply);
  if (!outCheck.ok) return json({ error: "Response blocked for safety." }, 500);

  return json({ reply });
}
