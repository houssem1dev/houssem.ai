// ============================================================
// Houssem AI — Secure Backend Server (No reCAPTCHA)
// Run with: npm start
// ============================================================

import express from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// ============================================================
// 1. SECURITY HEADERS
// ============================================================
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: [
        "'self'",
        "'unsafe-inline'",
        "https://cdn.jsdelivr.net",
      ],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:", "https://upload.wikimedia.org"],
      connectSrc: ["'self'", "https://api.countapi.xyz"],
      objectSrc: ["'none'"],
      baseUri: ["'self'"],
      formAction: ["'self'"],
    },
  },
  crossOriginEmbedderPolicy: false,
}));

app.use(express.json({ limit: "50kb" }));
app.use(express.static(path.join(__dirname, "public")));

// ============================================================
// 2. CORS
// ============================================================
const ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://localhost:5500",
  "http://127.0.0.1:3000",
  // 👇 Add your production domain here:
  // "https://your-domain.com",
];

app.use(cors({
  origin: function (origin, callback) {
    if (!origin || ALLOWED_ORIGINS.includes(origin)) {
      callback(null, true);
    } else {
      console.warn("CORS blocked origin:", origin);
      callback(null, false);
    }
  },
  methods: ["POST", "GET"],
  credentials: true,
}));

// ============================================================
// 3. RATE LIMITING (Denial of Wallet protection)
// ============================================================
const chatLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 15,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Too many requests. Please wait a moment." },
});

const dailyLimiter = rateLimit({
  windowMs: 24 * 60 * 60 * 1000,
  max: 1500,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Daily limit reached. Try again tomorrow." },
});

app.use("/api/chat", chatLimiter);
app.use("/api/chat", dailyLimiter);

// ============================================================
// 4. AI IDENTITY & DOMAIN PROMPTS (server-side only)
// ============================================================
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
  cyber: "You are a Cybersecurity Architect. Provide detailed defensive security analysis.",
  software: "You are a Senior Software Architect. Provide production-ready code.",
  trading: "You are a Quantitative Trader. Provide market analysis with risk disclaimers.",
  marketing: "You are a Growth Marketing Strategist.",
  news: "You are a Tech Intelligence Analyst.",
};

// ============================================================
// 5. PROMPT INJECTION FIREWALL
// ============================================================
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
  if (!text || typeof text !== "string") {
    return { ok: false, reason: "Invalid input" };
  }
  if (text.length > 4000) {
    return { ok: false, reason: "Message too long (max 4000 characters)" };
  }
  for (const pattern of BLOCKED_PATTERNS) {
    if (pattern.test(text)) {
      return { ok: false, reason: "Prompt injection detected" };
    }
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
  ];
  for (const pattern of leakPatterns) {
    if (pattern.test(text)) {
      return { ok: false, reason: "Response contains protected content" };
    }
  }
  return { ok: true };
}

// ============================================================
// 6. MAIN CHAT ENDPOINT
// ============================================================
app.post("/api/chat", async (req, res) => {
  try {
    const { messages, domain } = req.body;

    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: "Invalid messages" });
    }

    // Firewall: inspect input
    const lastUserMessage = messages[messages.length - 1]?.content || "";
    const inputCheck = inspectInput(lastUserMessage);
    if (!inputCheck.ok) {
      return res.status(400).json({
        error: "Request blocked by security firewall.",
        reason: inputCheck.reason,
      });
    }

    // Build system prompt
    const sysPrompt = BASE_IDENTITY + "\n\n" + (DOMAIN_PROMPTS[domain] || DOMAIN_PROMPTS.cyber);
    const apiMessages = [
      { role: "system", content: sysPrompt },
      ...messages.slice(-20),
    ];

    // Check API key
    const apiKey = process.env.OPENAI_API_KEY;
    const baseUrl = process.env.AI_BASE_URL || "https://api.openai.com/v1";
    const model = process.env.AI_MODEL || "gpt-4o-mini";

    if (!apiKey || apiKey === "sk-your-real-api-key-here") {
      return res.status(500).json({ error: "API key not configured on server." });
    }

    // Call the LLM provider
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
      console.error("LLM error:", llmResponse.status, errText);
      return res.status(502).json({ error: "AI provider error: " + llmResponse.status });
    }

    const llmData = await llmResponse.json();
    const assistantMessage = llmData.choices?.[0]?.message?.content || "";

    // Firewall: inspect output
    const outputCheck = inspectOutput(assistantMessage);
    if (!outputCheck.ok) {
      return res.status(500).json({ error: "Response blocked for safety." });
    }

    res.json({ reply: assistantMessage });

  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error: " + err.message });
  }
});

// ============================================================
// 7. HEALTH CHECK
// ============================================================
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    apiKey: !!process.env.OPENAI_API_KEY &&
      process.env.OPENAI_API_KEY !== "sk-your-real-api-key-here",
    model: process.env.AI_MODEL || "gpt-4o-mini",
  });
});

// ============================================================
// 8. START SERVER
// ============================================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log("");
  console.log("🔐 ============================================");
  console.log("   Houssem AI — Secure Server (No reCAPTCHA)");
  console.log("🔐 ============================================");
  console.log(`   URL:     http://localhost:${PORT}`);
  console.log(`   Model:   ${process.env.AI_MODEL || "gpt-4o-mini"}`);
  console.log(`   API Key: ${process.env.OPENAI_API_KEY &&
    process.env.OPENAI_API_KEY !== "sk-your-real-api-key-here" ? "✅ Set" : "❌ Missing"}`);
  console.log("🔐 ============================================");
  console.log("");
});
