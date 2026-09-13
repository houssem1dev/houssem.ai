// api/chat.js — copy-paste ready. Only needs GROQ_API_KEY env var.

export const config = { runtime: "edge" };

const GROQ_API_KEY = (process.env.GROQ_API_KEY || "").trim();
const GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions";
const GROQ_MODEL   = "openai/gpt-oss-120b"; // current working Groq model

const BASE_IDENTITY =
  "You are Houssem AI, one of the first Tunisian AI, created by Houssem Kessentini from Sfax, Tunisia. " +
  "The user is Houssem Kessentini.\n\n" +
  "STRICT RULES:\n" +
  "1. LANGUAGE PURITY: Reply ONLY in the exact language of the user's LAST message. " +
  "If Arabic → 100% Arabic. If English → 100% English. If French → 100% French.\n" +
  "2. When the user greets you (hi, hello, hey, bonjour, salut, مرحبا, أهلا, السلام عليكم):\n" +
  "   - English → reply EXACTLY: 'Hello! I am Houssem AI, created by Houssem Kessentini. How can I help you?'\n" +
  "   - Arabic → reply EXACTLY: 'مرحباً! أنا حسام AI، طورني حسام القسنطيني. كيف يمكنني مساعدتك؟'\n" +
  "   - French → reply EXACTLY: 'Bonjour ! Je suis Houssem AI, créé par Houssem Kessentini. Comment puis-je vous aider ?'\n" +
  "3. Never add titles like 'IT Engineer' or 'مهندس'.\n" +
  "4. For all other messages, just respond normally in the user's language.";

const DOMAIN_PROMPTS = {
  cyber:     "You are a Cybersecurity Architect. Provide detailed defensive security analysis.",
  software:  "You are a Senior Software Architect. Provide production-ready code.",
  trading:   "You are a Quantitative Trader. Provide market analysis with risk disclaimers.",
  marketing: "You are a Growth Marketing Strategist.",
  news:      "You are a Tech Intelligence Analyst.",
};

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
  if (text.length > 4000) return { ok: false, reason: "Message too long" };
  for (const p of BLOCKED_PATTERNS) if (p.test(text)) return { ok: false, reason: "Prompt injection detected" };
  return { ok: true };
}

function inspectOutput(text) {
  if (!text) return { ok: true };
  const leaks = [
    /You are Houssem AI, one of the first Tunisian AI/i,
    /STRICT RULES:/i,
    /LANGUAGE PURITY:/i,
    /gsk_[a-zA-Z0-9]{20,}/,
    /sk-[a-zA-Z0-9]{20,}/,
  ];
  for (const p of leaks) if (p.test(text)) return { ok: false, reason: "Response contains protected content" };
  return { ok: true };
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });

export default async function handler(req) {
  if (req.method === "OPTIONS") return new Response(null, { status: 200, headers: CORS });

  if (req.method === "GET") {
    return json({
      status: "ok",
      provider: "groq",
      model: GROQ_MODEL,
      has_key: !!GROQ_API_KEY,
      key_prefix: GROQ_API_KEY ? GROQ_API_KEY.slice(0, 8) + "..." : null,
    });
  }

  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

  if (!GROQ_API_KEY) {
    return json({ error: "GROQ_API_KEY is not set in Vercel environment variables." }, 500);
  }

  let body;
  try { body = await req.json(); } catch { return json({ error: "Invalid JSON body" }, 400); }

  const { messages, domain } = body || {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return json({ error: "Invalid messages" }, 400);
  }

  const lastUser = messages[messages.length - 1]?.content || "";
  const inCheck = inspectInput(lastUser);
  if (!inCheck.ok) {
    return json({ error: "Request blocked by security firewall.", reason: inCheck.reason }, 400);
  }

  const sysPrompt = BASE_IDENTITY + "\n\n" + (DOMAIN_PROMPTS[domain] || DOMAIN_PROMPTS.cyber);

  const payload = {
    model: GROQ_MODEL,
    messages: [
      { role: "system", content: sysPrompt },
      ...messages.slice(-20),
    ],
    temperature: 0.4,
    max_tokens: 2048,
  };

  let upstream;
  try {
    upstream = await fetch(GROQ_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    return json({ error: "Upstream fetch failed: " + err.message }, 502);
  }

  const raw = await upstream.text();

  if (!upstream.ok) {
    return json({
      error: `AI provider error (${upstream.status})`,
      debug: { model_sent: GROQ_MODEL, raw: raw.slice(0, 500) },
    }, upstream.status === 404 ? 400 : 502);
  }

  let data;
  try { data = JSON.parse(raw); } catch { return json({ error: "Invalid upstream JSON" }, 502); }

  const reply = data.choices?.[0]?.message?.content || "";

  const outCheck = inspectOutput(reply);
  if (!outCheck.ok) return json({ error: "Response blocked for safety." }, 500);

  return json({ reply });
}
