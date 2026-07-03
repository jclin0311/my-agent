from dotenv import load_dotenv
import asyncio
from openai import AsyncOpenAI
import json

load_dotenv()
async_client = AsyncOpenAI()

async def research_one_competitor(competitor: str) -> dict:
    """Single worker: researches one competitor and returns structured data."""
    response = await async_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a competitive researcher.
            Return a JSON object with these fields:
            - name: company name
            - pricing: monthly price for main plan (e.g. "$20/month")
            - main_feature: the one thing they do best (1 sentence)
            - weakness: their biggest limitation (1 sentence)
            - best_for: who should use this tool (1 sentence)"""},
            {"role": "user", "content": f"Research this AI coding tool: {competitor}"}
        ]
    )

    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    result = json.loads(text)
    print(f"[Researched {competitor}]")
    return result

async def fan_out_research(competitors: list[str]) -> list[dict]:
    """Fan out: research all competitors in parallel."""
    tasks = [research_one_competitor(c) for c in competitors]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"[Error researching {competitors[i]}]: {result}")
        else:
            successful.append(result)

    return successful

async def full_intel_workflow(topic: str, num_competitors: int = 5) -> str:
    """
    Real workflow combining all three patterns:
    1. Supervisor: decides what competitors to research
    2. Fan-out: researches all competitors in parallel
    3. Pipeline: analysis -> formatting -> final report
    """

    # Stage 1: Supervisor identifies the competitors
    print("[Stage 1] Identifying competitors...")
    competitor_list_raw = await async_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""Return a JSON array of exactly
            {num_competitors} competitor names in the space.
            Return ONLY the JSON array of strings."""},
            {"role": "user", "content": f"Top competitors in: {topic}"}
        ]
    )

    text = competitor_list_raw.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    competitors = json.loads(text)

    # Stage 2: Fan-out research on all competitors
    print(f"[Stage 2] Researching {len(competitors)} competitors in parallel...")
    research = await fan_out_research(competitors)

    # Stage 3: Pipeline — analysis agent then report agent
    print("[Stage 3] Running analysis pipeline...")

    analysis = await async_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a market analyst.
            Identify the 3 most important patterns and insights from this
            competitive research. Be specific, not generic."""},
            {"role": "user", "content": json.dumps(research, indent=2)}
        ]
    )
    analysis_text = analysis.choices[0].message.content

    report = await async_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a technical writer.
            Given competitive research and analysis, write a crisp executive
            brief (400 words max). Structure: situation, key findings,
            implications, recommendation."""},
            {"role": "user", "content": f"""Research: {json.dumps(research, indent=2)}

            Analysis insights: {analysis_text}

            Write the brief."""}
        ]
    )

    return report.choices[0].message.content


# if __name__=="__main__":
#     result = asyncio.run(full_intel_workflow("AI coding assistants"))
#     print(result)