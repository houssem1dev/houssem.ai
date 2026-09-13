// api/chat.js — Debug version. Shows exactly what's sent to Groq.
export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();

  // ── GET: full env diagnostic ─────────────────────────
  if (req.method === "GET") {
    const gk = process.env.GROQ_API_KEY || "";
    const ok = process.env.OPENAI_API_KEY || "";
    return res.status(200).json({
      env: {
        GROQ_API_KEY:   gk ? `${gk.slice(0,8)}...${gk.slice(-4)} (len=${gk.length})` : null,
        OPENAI_API_KEY: ok ? `${ok.slice(0,8)}...${ok.slice(-4)} (len=${ok.length})` : null,
        AI_MODEL:       process.env.AI_MODEL ?? null,
        AI_BASE_URL:    process.env.AI_BASE_URL ?? null,
      },
      resolved: resolveProvider(),
    });
  }

  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const { messages, domain } = req.body || {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: "Invalid messages" });
  }

  const { provider, apiKey, baseUrl, model } = resolveProvider();
  if (!apiKey) {
    return res.status(500).json({ error: "No API key configured" });
  }

  const fullUrl = `${baseUrl}/chat/completions`;
  const body = {
    model,
    messages: [
      { role: "system", content: "You are a helpful assistant. Reply in the user's language." },
      ...messages.slice(-10),
    ],
    temperature: 0.4,
    max_tokens: 1024,
  };

  console.log("[DEBUG] URL:", fullUrl);
  console.log("[DEBUG] MODEL:", JSON.stringify(model));
  console.log("[DEBUG] KEY PREFIX:", apiKey.slice(0, 8));

  try {
    const r = await fetch(fullUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const raw = await r.text();
    console.log("[DEBUG] Groq status:", r.status);
    console.log("[DEBUG] Groq body:", raw);

    if (!r.ok) {
      return res.status(r.status).json({
        error: `Provider ${r.status}`,
        debug: {
          url: fullUrl,
          model_sent: model,
          provider,
          raw_response: raw.slice(0, 500),
        },
      });
    }

    const data = JSON.parse(raw);
    const reply = data.choices?.[0]?.message?.content || "";
    return res.status(200).json({ reply });

  } catch (err) {
    return res.status(500).json({ error: err.message, stack: err.stack });
  }
}

function resolveProvider() {
  // Clean env values — trim whitespace, strip quotes
  const clean = (v) => (v || "").trim().replace(/^["']|["']$/g, "");
  const groqKey  = clean(process.env.GROQ_API_KEY);
  const oaiKey   = clean(process.env.OPENAI_API_KEY);
  const envModel = clean(process.env.AI_MODEL);
  const envBase  = clean(process.env.AI_BASE_URL);

  // Explicit override
  if (envBase) {
    return {
      provider: groqKey ? "groq-custom" : "openai-custom",
      apiKey: groqKey || oaiKey,
      baseUrl: envBase.replace(/\/+$/, ""),
      model: envModel || (groqKey ? "llama-3.1-8b-instant" : "gpt-4o-mini"),
    };
  }

  if (groqKey) {
    return {
      provider: "groq",
      apiKey: groqKey,
      baseUrl: "https://api.groq.com/openai/v1",
      model: envModel || "llama-3.1-8b-instant",
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
