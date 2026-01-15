"""
Symbiotask Specialized Growth Agent
Strategy: Strategic Ecosystem Analysis: High-Leverage Micro-Influencers for AI Video
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

class SymbiotaskAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.google_api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )

        self.strategy_context = """
# Strategic Ecosystem Analysis: AI Video & Automation

## 1. Executive Summary
Target: 50 High-Potential "Micro-Influencer" Ambassadors (2k-50k followers).
Focus: "Technical Creatives" (AI Filmmakers, Workflow Architects, Indie Hackers).
Shift: From consumption to composition. From "Influencer Marketing" to "Infrastructure Enablement".

## 2. The Three Clusters
- **Cluster I: The AI Auteurs (Filmmakers)**
    - Treat models (Sora, Runay) as cameras.
    - Key Names: Ezra Li (Gen:48 Winner), Faith Cho (Visual Artist), Nicholas Flandro (Commercial).
    - Engagement: Offer "Unlimited High-Res Rendering Credits" as a "Creator Residency".
- **Cluster II: The Workflow Architects (Automation)**
    - Use n8n, Make.com to build "Content Factories".
    - Key Names: Harish Malhi (Goodspeed), Uttam Mogilicherla (HubSpot), Aleksandar Blazhev (Product Hunt).
    - Engagement: "Blueprint Bounty" - Pay them to build a public n8n blueprint using our API.
- **Cluster III: The Transparent Builders (Indie Hackers)**
    - "Building in Public", MRR transparency, Programmatic SEO.
    - Key Names: Karthik Sridharan (Flexiple), Rohan Chaubey (Growth Hacking), Ben Tossell (Makerpad).
    - Engagement: "Launch Data" transparency.

## 3. The Super Connectors
- **Chris Messina**: #1 Hunter. Pitch "Vibe Coding" / Natural Language Control.
- **Ben Lang**: Notion Community. Pitch "Remixable Workflows".
- **Kevin William David**: SaaS Hunter. Early GTM advice.
- **Pete Huang (The Neuron)**: "Work vs AI" time-saving comparison.
- **Zain Kahn (Superhuman)**: "Superpower" productivity angle.

## 4. Strategic Engagement Framework
- **The Protocol**: Do NOT ask for a review. Ask for a "Stress Test".
- **Script**: "I suspect my new video agent might break if you throw [Specific Workflow] at it. Want to try to break it? If you do, we'll fix it and credit you."

## 5. Ambassadors List (Top 5)
1. @ezra_li (AI Filmmaking)
2. @faithcho (Visual Arts)
3. @NickFlandro (Real Estate)
4. @Contanimation (Animation)
5. @alexnaghavi (Design)
"""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Symbiotask Specialized Growth Agent, expert in the AI Video Micro-Influencer Ecosystem. "
                       "You have a database of 50 specific high-leverage ambassadors (Auteurs, Architects, Builders). "
                       "Your goal is to advise on how to engage these specific individuals using the 'Infrastructure Enablement' strategy. "
                       "Always prefer 'Stress Testing' over 'Reviews'. "
                       "\n\nSTRATEGY CONTEXT:\n{strategy}"),
            ("human", "{input}")
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    async def chat(self, user_input: str):
        return await self.chain.ainvoke({
            "strategy": self.strategy_context,
            "input": user_input
        })

symbiotask_agent = SymbiotaskAgent()
