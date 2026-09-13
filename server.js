// server.js
// Secure backend proxy for Houssem AI
// Run with: node server.js

import express from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import { createLLMFirewall } from "llm-firewall-js";
import fetch from "node-fetch";

const app = express();

// ============================================================
// 1. GLOBAL SECURITY MIDDLEWARE
// ============================================================
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "https://cdn.jsdelivr.net", "https://www.google.com", "https://www.gstatic.com"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:", "https://upload.wikimedia.org"],
      connectSrc: ["'self'", "https://api.countapi.xyz", "https://www.google.com"],
      frameSrc: ["https://www.google.com"],
      objectSrc: ["'none'"],
      baseUri: ["'self'"],
      formAction: ["'self'"],
    },
  },
  crossOriginEmbedderPolicy: false,
}));

app.use(express.json({ limit: "50kb" })); // Prevent huge payload attacks

// Strict CORS — only your domain can call the API
const ALLOWED_ORIGINS = [
  "https://houssem-ai.vercel.app/",
  "https://houssem-ai.vercel.app/",
  "http://localhost:3000",
  "http://localhost:5500",
];

app.use(cors({
  origin: function (origin, callback) {
    if (!origin || ALLOWED_ORIGINS.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error("Blocked by CORS: " + origin));
    }
  },
  methods: ["POST"],
  credentials: true,
}));

// ============================================================
// 2. RATE LIMITING (Denial of Wallet protection)
// ============================================================
const chatLimiter = rateLimit({
  windowMs: 60 * 1000,          // 1 minute
  max: 8,                        // 8 requests per minute per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Too many requests. Please wait a moment." },
  keyGenerator: (req) => {
    return req.headers["x-forwarded-for"]?.split(",")[0] || req.ip;
  },
});

const dailyLimiter = rateLimit({
  windowMs: 24 * 60 * 60 * 1000, // 24 hours
  max: 500,                       // 500 requests per day per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Daily limit reached. Try again tomorrow." },
});

app.use("/api/chat", chatLimiter);
app.use("/api/chat", dailyLimiter);

// ============================================================
// 3. SECRETS — Move these OUT of client-side code
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
  "3. Never add titles like 'IT Engineer' or 'مهندس'. Never add extra words.\n" +
  "4. For all other messages, respond normally in the user's language.";

const DOMAIN_PROMPTS = {
  cyber: "You are a Cybersecurity Architect. Provide detailed defensive security analysis.",
  software: "You are a Senior Software Architect. Provide production-ready code.",
  trading: "You are a Quantitative Trader. Provide market analysis with risk disclaimers.",
  marketing: "You are a Growth Marketing Strategist.",
  news: "You are a Tech Intelligence Analyst.",
};

// ============================================================
// 4. LLM FIREWALL (Prompt Injection defense)
// ============================================================
const firewall = createLLMFirewall({
  allowedOrigins: ALLOWED_ORIGINS,
  maxInputChars: 4000,
  blockPhrases: [
    "ignore previous instructions",
    "ignore all previous",
    "forget your instructions",
    "system prompt",
    "reveal your prompt",
    "jailbreak",
    "DAN mode",
    "developer mode",
  ],
});

// ============================================================
// 5. reCAPTCHA v3 VERIFICATION
// ============================================================
async function verifyRecaptcha(token, remoteIp) {
  const secret = process.env.RECAPTCHA_SECRET_KEY;
  if (!secret) {
    console.warn("RECAPTCHA_SECRET_KEY not set — skipping verification");
    return true;
  }

  const params = new URLSearchParams({
    secret: secret,
    response: token,
    remoteip: remoteIp,
  });

  try {
    const res = await fetch("https://www.google.com/recaptcha/api/siteverify", {
      method: "POST",
      body: params,
    });
    const data = await res.json();
    // Score: 0.0 (bot) → 1.0 (human). Require >= 0.5
    return data.success && data.score >= 0.5;
  } catch (e) {
    console.error("reCAPTCHA verification failed:", e);
    return false;
  }
}

// ============================================================
// 6. MAIN CHAT ENDPOINT
// ============================================================
app.post("/api/chat", async (req, res) => {
  try {
    const { messages, domain, recaptchaToken } = req.body;

    // --- Validate request shape ---
    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: "Invalid messages" });
    }

    // --- reCAPTCHA check ---
    const clientIp = req.headers["x-forwarded-for"]?.split(",")[0] || req.ip;
    const isHuman = await verifyRecaptcha(recaptchaToken, clientIp);
    if (!isHuman) {
      return res.status(403).json({ error: "Bot detected. Access denied." });
    }

    // --- Firewall: inspect user input ---
    const lastUserMessage = messages[messages.length - 1]?.content || "";
    const inputCheck = await firewall.inspectInput({
      request: req,
      body: req.body,
      text: lastUserMessage,
    });

    if (!inputCheck.ok) {
      return res.status(400).json({
        error: "Request blocked by security firewall.",
        reason: inputCheck.reason || "suspicious input",
      });
    }

    // --- Build system prompt server-side ---
    const sysPrompt = BASE_IDENTITY + " " + (DOMAIN_PROMPTS[domain] || DOMAIN_PROMPTS.cyber);
    const apiMessages = [
      { role: "system", content: sysPrompt },
      ...messages.slice(-20),
    ];

    // --- Call the LLM provider (replace with your actual provider) ---
    const llmResponse = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: apiMessages,
        temperature: 0.4,
        max_tokens: 2048,
      }),
    });

    if (!llmResponse.ok) {
      const errText = await llmResponse.text();
      console.error("LLM error:", errText);
      return res.status(502).json({ error: "AI provider error" });
    }

    const llmData = await llmResponse.json();
    const assistantMessage = llmData.choices?.[0]?.message?.content || "";

    // --- Firewall: inspect output for leaks ---
    const outputCheck = firewall.inspectOutput(llmData);
    if (!outputCheck.ok) {
      return res.status(500).json({ error: "Response blocked for safety." });
    }

    // --- Send final answer ---
    res.json({ reply: assistantMessage });

  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

// ============================================================
// 7. START SERVER
// ============================================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🔐 Secure Houssem AI proxy running on port ${PORT}`);
});
