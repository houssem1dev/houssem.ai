function resolveProvider() {
  const clean = (v) => (v || "").trim().replace(/^["']|["']$/g, "");
  const groqKey = clean(process.env.GROQ_API_KEY);
  const oaiKey  = clean(process.env.OPENAI_API_KEY);

  if (groqKey) {
    return {
      provider: "groq",
      apiKey: groqKey,
      baseUrl: "https://api.groq.com/openai/v1",
      model: "llama-3.3-70b-versatile",   // ← hardcoded, no env var needed
    };
  }

  if (oaiKey) {
    return {
      provider: "openai",
      apiKey: oaiKey,
      baseUrl: "https://api.openai.com/v1",
      model: "gpt-4o-mini",
    };
  }

  return { provider: "none", apiKey: null, baseUrl: "", model: "" };
}
