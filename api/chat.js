// Vercel Serverless Function — /api/chat
// This runs on Vercel's servers. The Groq key stays here, hidden from users.

export const config = {
    runtime: 'edge',
};

export default async function handler(req) {
    // Only allow POST
    if (req.method !== 'POST') {
        return new Response(JSON.stringify({ error: 'Method not allowed' }), {
            status: 405,
            headers: { 'Content-Type': 'application/json' },
        });
    }

    // Get API key from environment variable
    const apiKey = process.env.GROQ_API_KEY;
    if (!apiKey) {
        return new Response(
            JSON.stringify({ error: 'Server misconfigured: GROQ_API_KEY not set' }),
            { status: 500, headers: { 'Content-Type': 'application/json' } }
        );
    }

    // Parse body
    let body;
    try {
        body = await req.json();
    } catch (e) {
        return new Response(
            JSON.stringify({ error: 'Invalid JSON' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
    }

    // Basic validation
    const { messages, temperature = 0.4, max_tokens = 2048 } = body;
    if (!Array.isArray(messages) || messages.length === 0) {
        return new Response(
            JSON.stringify({ error: 'Messages required' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
    }

    // Call Groq
    try {
        const groqResponse = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
                model: 'openai/gpt-oss-20b',
                messages,
                temperature,
                max_tokens,
                stream: true,
            }),
        });

        if (!groqResponse.ok) {
            const err = await groqResponse.text();
            return new Response(err, {
                status: groqResponse.status,
                headers: { 'Content-Type': 'application/json' },
            });
        }

        // Stream the response back to the browser
        return new Response(groqResponse.body, {
            status: 200,
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            },
        });

    } catch (err) {
        return new Response(
            JSON.stringify({ error: 'Groq request failed: ' + err.message }),
            { status: 500, headers: { 'Content-Type': 'application/json' } }
        );
    }
}
