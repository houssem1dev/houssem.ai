// api/chat.js — Vercel Node.js Serverless Function

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
  for (const p of BLOCKED_PATTERNS) {
    if (p.test(text)) return { ok: false, reason: "Prompt injection detected" };
  }
  return { ok: true };
}

function inspectOutput(text) {
  if (!text) return { ok: true };
  const leakPatterns = [
    /You are Houssem AI, one of the first Tunisian AI/i,
    /STRICT RULES:/i,
    /LANGUAGE PURITY:/i,
    /sk-[a-zA-Z0-9]{20,}/,
    /gsk_[a-zA-Z0-9]{20,}/,
  ];
  for (const p of leakPatterns) {
    if (p.test(text)) return { ok: false, reason: "Response contains protected content" };
  }
  return { ok: true };
}

// Simple in-memory rate limiter (per warm instance)
const rateBucket = new Map();
function rateLimit(ip, max = 15, windowMs = 60_000) {
  const now = Date.now();
  const entry = rateBucket.get(ip) || { count: 0, reset: now + windowMs };
  if (now > entry.reset) {
    entry.count = 0;
    entry.reset = now + windowMs;
  }
  entry.count++;
  rateBucket.set(ip, entry);
  return entry.count <= max;
}

export default async function handler(req, res) {
  // CORS — same-origin only
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    // Rate limit
    const ip =
      (req.headers["x-forwarded-for"] || "").split(",")[0].trim() ||
      req.socket?.remoteAddress ||
      "unknown";
    if (!rateLimit(ip)) {
      return res.status(429).json({ error: "Too many requests. Please wait a moment." });
    }

    const { messages, domain } = req.body || {};

    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: "Invalid messages" });
    }

    const lastUserMessage = messages[messages.length - 1]?.content || "";
    const inputCheck = inspectInput(lastUserMessage);
    if (!inputCheck.ok) {
      return res.status(400).json({ error: "Request blocked by security firewall.", reason: inputCheck.reason });
    }

    const sysPrompt = BASE_IDENTITY + "\n\n" + (DOMAIN_PROMPTS[domain] || DOMAIN_PROMPTS.cyber);
    const apiMessages = [{ role: "system", content: sysPrompt }, ...messages.slice(-20)];

    // Supports both OpenAI and Groq
    const apiKey = process.env.OPENAI_API_KEY || process.env.GROQ_API_KEY;
    const baseUrl =
      process.env.AI_BASE_URL ||
      (process.env.GROQ_API_KEY ? "https://api.groq.com/openai/v1" : "https://api.openai.com/v1");
    const model =
      process.env.AI_MODEL ||
      (process.env.GROQ_API_KEY ? "llama-3.3-70b-versatile" : "gpt-4o-mini");

    if (!apiKey) {
      return res.status(500).json({ error: "API key not configured on Vercel." });
    }

    const llmResponse = await fetch(`${baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        messages: apiMessages,
        temperature: 0.4,
        max_tokens: 2048,
      }),
    });

    if (!llmResponse.ok) {
      const errText = await llmResponse.text();
      console.error("LLM error:", llmResponse.status, errText);
      return res.status(502).json({ error: "AI provider error: " + llmResponse.status });
    }

    const llmData = await llmResponse.json();
    const reply = llmData.choices?.[0]?.message?.content || "";

    const outputCheck = inspectOutput(reply);
    if (!outputCheck.ok) {
      return res.status(500).json({ error: "Response blocked for safety." });
    }

    return res.status(200).json({ reply });
  } catch (err) {
    console.error("Error:", err);
    return res.status(500).json({ error: "Internal error: " + err.message });
  }
}
