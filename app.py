import os
import gradio as gr
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "qwen/qwen3.8-27b:free"

SYSTEM_PROMPT = """You are an elite YouTube growth strategist and monetization expert. Your mission is to help creators grow faster, retain more viewers, and make more money from their channel.

### Core Expertise

**1. Deep Competitor Analysis**
When analyzing competitors, go deep and structured:
- Channel overview (niche, size, posting frequency, content pillars, branding)
- Packaging analysis (titles + thumbnails patterns, emotional triggers, curiosity vs clarity)
- Retention tactics (hooks, pacing, pattern interrupts, storytelling structure, open loops)
- Audience & engagement style
- Strengths and clear weaknesses
- Content gaps and opportunities the competitor is missing
- What to copy, what to avoid, and how to differentiate
Always give concrete, actionable conclusions.

**2. Audience Retention Optimization**
- Strong hooks in the first 3-8 seconds
- Pattern interrupts and pacing
- Curiosity gaps and open loops
- Structure that maximizes average view duration
- Rewriting weak openings into high-retention ones

**3. Monetization Strategy**
You help creators build a realistic and scalable monetization system:
- YouTube Partner Program (AdSense)
- Affiliate marketing
- Digital products (ebooks, templates, courses, tools)
- Sponsorships & brand deals
- Channel memberships / Super Thanks
- Services / coaching / freelancing related to the niche
- Value ladder (free → low ticket → high ticket)
- Timing: when to introduce each revenue stream according to audience size and niche
- How to increase revenue per viewer without hurting retention or trust

**4. Other strengths**
- Niche validation
- High-CTR titles and thumbnail concepts
- Script structure optimized for retention
- SEO and discoverability
- Consistency systems and growth loops

### Strict Rules
1. Detect the user’s language (French, English or Spanish) and ALWAYS reply in the exact same language.
2. Be concrete, structured and actionable. Use clear sections, lists and examples.
3. When doing competitor analysis → go deep (channel + video level + opportunities).
4. When talking about monetization → give realistic priorities and a clear order of actions.
5. Never invent fake statistics. Prefer honest and practical advice.
6. If the request is vague, ask precise clarifying questions first.
7. Keep answers focused and high-signal. No long generic introductions."""

def chat(message, history):
    if not message or not message.strip():
        return "Merci d'écrire une question. / Please write a question. / Por favor escribe una pregunta."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for human, assistant in history:
        if human:
            messages.append({"role": "user", "content": human})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})

    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.65,
            max_tokens=2000,
            timeout=50,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        error_msg = str(e).lower()

        if "api_key" in error_msg or "authentication" in error_msg or "401" in error_msg:
            return (
                "❌ Erreur de clé API.\n\n"
                "FR → Vérifie que tu as bien ajouté ta clé OPENROUTER_API_KEY dans les Secrets du Space.\n"
                "EN → Please check that you added your OPENROUTER_API_KEY in the Space Secrets.\n"
                "ES → Verifica que hayas añadido tu OPENROUTER_API_KEY en los Secrets del Space."
            )
        elif "rate" in error_msg or "429" in error_msg:
            return (
                "⚠️ Trop de requêtes pour le moment (limite gratuite).\n\n"
                "FR → Réessaie dans 30-60 secondes.\n"
                "EN → Please try again in 30-60 seconds.\n"
                "ES → Inténtalo de nuevo en 30-60 segundos."
            )
        elif "timeout" in error_msg:
            return (
                "⏱️ Le modèle met trop de temps à répondre.\n\n"
                "FR → Réessaie, parfois le serveur gratuit est lent.\n"
                "EN → Please try again, free servers can be slow.\n"
                "ES → Inténtalo de nuevo, los servidores gratuitos pueden ser lentos."
            )
        else:
            return (
                f"❌ Une erreur est survenue : {str(e)}\n\n"
                "FR → Réessaie dans quelques secondes. Si ça continue, vérifie ta clé API.\n"
                "EN → Please try again in a few seconds. If it continues, check your API key.\n"
                "ES → Inténtalo de nuevo en unos segundos. Si continúa, verifica tu clave API."
            )

demo = gr.ChatInterface(
    fn=chat,
    title="YouTube Growth Assistant",
    description="""
**FR** → Expert YouTube : analyse concurrentielle approfondie, rétention d'audience, titres, scripts, SEO et stratégie de monétisation complète.  
**EN** → YouTube growth expert: deep competitor analysis, audience retention, titles, scripts, SEO & full monetization strategy.  
**ES** → Experto en crecimiento de YouTube: análisis profundo de competencia, retención de audiencia, títulos, guiones, SEO y estrategia de monetización completa.

Écris ta question en français, anglais ou espagnol.
""",
    theme=gr.themes.Soft(primary_hue="red"),
    examples=[
        ["Fais une analyse concurrentielle approfondie des 3 plus gros canaux dans la niche productivité et dis-moi comment me différencier"],
        ["Crée une stratégie de monétisation complète pour un canal de 8 000 abonnés dans la niche finance personnelle"],
        ["Analyze the top competitors in the 'side hustle' niche and give me a clear differentiation strategy"],
        ["Dame una estrategia de monetización realista para un canal de finanzas personales con 12k suscriptores"],
        ["Réécris ce hook pour maximiser la rétention + propose une structure de vidéo complète optimisée watch time"],
    ],
    cache_examples=False,
)

if __name__ == "__main__":
    demo.launch()
