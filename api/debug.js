export const config = { runtime: 'edge' };

export default async function handler(req) {
    const key = process.env.GROQ_API_KEY;
    return new Response(JSON.stringify({
        has_key: !!key,
        key_length: key ? key.length : 0,
        key_start: key ? key.slice(0, 10) : null,
        key_end: key ? key.slice(-6) : null,
    }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
    });
}
