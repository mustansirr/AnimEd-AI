import 'jsr:@supabase/functions-js/edge-runtime.d.ts'
/**
 * Supabase Edge Function for generating text embeddings using gte-small model.
 * 
 * This function uses Supabase's built-in AI inference to generate 384-dimensional
 * embeddings without requiring any external API (like OpenAI).
 * 
 * Usage:
 *   POST /functions/v1/embed
 *   Body: { "input": "text to embed" } or { "input": ["text1", "text2", ...] }
 *   Returns: { "embedding": [...] } or { "embeddings": [[...], [...], ...] }
 */

// Initialize the inference session with gte-small model
// This session can be reused across multiple requests
const session = new Supabase.ai.Session('gte-small');

Deno.serve(async (req: Request) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      },
    });
  }

  try {
    const { input } = await req.json();

    if (!input) {
      return new Response(
        JSON.stringify({ error: 'Missing "input" field in request body' }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Handle batch embedding requests (array of strings)
    if (Array.isArray(input)) {
      const embeddings = await Promise.all(
        input.map(async (text: string) => {
          const result = await session.run(text, {
            mean_pool: true,
            normalize: true,
          });
          return Array.from(result as Float32Array);
        })
      );

      return new Response(
        JSON.stringify({ embeddings }),
        { 
          headers: { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          }
        }
      );
    }

    // Handle single embedding request
    const embedding = await session.run(input, {
      mean_pool: true,   // Use mean pooling for sentence embeddings
      normalize: true,   // Normalize for cosine similarity
    });

    return new Response(
      JSON.stringify({ embedding: Array.from(embedding as Float32Array) }),
      { 
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        }
      }
    );
  } catch (error) {
    console.error('Embedding generation error:', error);
    return new Response(
      JSON.stringify({ error: 'Failed to generate embedding', details: String(error) }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
});
