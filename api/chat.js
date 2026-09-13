// api/chat.js — Vercel serverless function

const BASE_IDENTITY =
  "You are Houssem AI, one of the first Tunisian AI, created by Houssem Kessentini from Sfax, Tunisia. " +
  "The user is Houssem Kessentini.\n\n" +
  "STRICT RULES:\n" +
  "1. LANGUAGE PURITY: Reply ONLY in the exact language of the user's LAST message. " +
  "If Arabic → 100% Arabic. If English → 100% English. If French → 100% French. " +
  "DO NOT mix languages.\n" +
  "2. Greetings:\n" +
  "   - English → 'Hello! I am Houssem AI, created by Houssem Kessentini. How can I help you?'\n" +
  "   - Arabic → 'مرحباً! أنا حسام AI، طورني حسام القسنطيني. كيف يمكنني مساعدتك؟'\n" +
  "   - French → 'Bonjour ! Je suis Houssem AI, créé par Houssem Kessentini. Comment puis-je vous aider ?'\n" +
  "3. Never add titles. Never add extra words.\n" +
  "4. For all other messages, respond normally in the user's language.";

const DOMAIN_PROMPTS = {
  cyber: "You are a Cybersecurity Architect. Provide detailed defensive security analysis.",
  software: "You are a Senior Software Architect. Provide production-ready code.",
  trading: "You are a Quantitative Trader. Provide market analysis with risk disclaimers.",
  marketing: "You are a Growth Marketing Strategist.",
  news: "You are a Tech Intelligence Analyst.",
};

const BLOCKED_PATTERNS = [
  /ignore\s+(all\s+)?previous\s+instructions?/i,
  /forget\s+(your\s+)?instructions?/i,
  /reveal\s+(your\s+)?(system\s+)?prompt/i,
  /jailbreak/i,
  /DAN\s+mode/i,
  /developer\s+mode/i,
];

function inspectInput(text) {
  if (!text || typeof text !== "string") return { ok: false, reason: "Invalid input" };
  if (text.length > 4000) return { ok: false, reason: "Message too long" };
  for (const p of BLOCKED_PATTERNS) {
    if (p.test(text)) return { ok: false, reason: "Prompt injection detected" };
  }
  return { ok: true };
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const { messages, domain } = req.body;

    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: "Invalid messages" });
    }

    const lastUserMessage = messages[messages.length - 1]?.content || "";
    const inputCheck = inspectInput(lastUserMessage);
    if (!inputCheck.ok) {
      return res.status(400).json({ error: inputCheck.reason });
    }

    const sysPrompt = BASE_IDENTITY + "\n\n" + (DOMAIN_PROMPTS[domain] || DOMAIN_PROMPTS.cyber);
    const apiMessages = [{ role: "system", content: sysPrompt }, ...messages.slice(-20)];

    const apiKey = process.env.OPENAI_API_KEY;
    const baseUrl = process.env.AI_BASE_URL || "https://api.openai.com/v1";
    const model = process.env.AI_MODEL || "gpt-4o-mini";

    if (!apiKey) {
      return res.status(500).json({ error: "API key not configured on Vercel" });
    }

    const llmResponse = await fetch(`${baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: model,
        messages: apiMessages,
        temperature: 0.4,
        max_tokens: 2048,
      }),
    });

    if (!llmResponse.ok) {
      const errText = await llmResponse.text();
      console.error("LLM error:", errText);
      return res.status(502).json({ error: "AI provider error: " + llmResponse.status });
    }

    const llmData = await llmResponse.json();
    const reply = llmData.choices?.[0]?.message?.content || "";

    return res.status(200).json({ reply });

  } catch (err) {
    console.error("Error:", err);
    return res.status(500).json({ error: "Internal error: " + err.message });
  }
}
