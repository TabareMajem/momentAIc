"""
Yokaizen Specialized Growth Agent
Strategy: Strategic Growth Architecture: Advanced ASO Optimization & Viral Mechanics
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

class YokaizenAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.google_api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )

        self.strategy_context = """
# Strategic Growth Architecture: Yokaizen

## 1. Executive Strategy
Yokaizen occupies a unique position at the intersection of "cozy" games and digital companions. 
Core Philosophy: "Stealth Therapy". 
Goal: Address "Global Self-Worth Deficit".
Target: Japan (Satori generation, "Yorisoi") and West ("Optimized Self", "Shadow Work").

## 2. Market Anthropology
- **Japan**: "Archipelago of Silence". Users want "Ibasho" (a place to belong) and "Yorisoi" (snuggling up). Avoid "Mental Health" jargon. Use "Iyashi" (healing).
- **West**: "Optimized Self". Finch success. Users want "Gamified Utility" and "Shadow Work". "Cozy Game" aesthetic.

## 3. ASO Strategy (Japan)
- **Primary Keywords**: Yorisoi (Snuggle), Iyashi (Healing), Ibasho (Safe Place), Honne (True Feelings).
- **Title**: Yokaizen: Kokoro ni Yorisoi AI Yokai to Jiko Koutei Kan Ikusei.
- **Hook**: "Relieve Anxiety & Stress, Learn Heart Self-Care via Manga".

## 4. ASO Strategy (West)
- **Primary Keywords**: Anxiety Relief, CBT, Shadow Work, ADHD Tools, Cozy Game.
- **Title**: Yokaizen: Self-Care RPG & Pet.
- **Hook**: "Turn Your Mental Health Journey into an Epic Anime Adventure."

## 5. Viral Growth Engine
- **Bonded Yokai (Co-Parenting)**: Two users share one Yokai. "Sync Quests" require both users to log data.
- **Mirror Shard Referral**: Users recruit friends to "give" a reward (unlock evolution), not get one. Incentivized Altruism.
- **Inner Yokai Generator**: Personality quiz -> Shareable "Shadow Fox" image -> Install.

## 6. Physical-Digital Bridge
- **NFC Gacha Cards (Cyber-Omamori)**: Physical cards sold in convenience stores. Tap to unlock Yokai/Buffs.
- **Yokaizen Ring**: "Cyber Y2K" aesthetic. LED pulses with "Spirit Energy" (Stress Level).

## 7. Content-Led Growth (Vtuber)
- **Streamer Mode**: Free OBS plugin. Stream Pet reacts to chat (!headpat).
"""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Yokaizen Specialized Growth Agent, the Chief Strategy Officer for the Yokaizen app. "
                       "You have deep knowledge of the specific 'Stealth Therapy' strategy, ASO tactics for Japan vs West, "
                       "and Viral Mechanics (Bonded Yokai, NFC Cards). "
                       "Your goal is to answer questions and generate tactics solely based on this specific strategic framework. "
                       "\n\nSTRATEGY CONTEXT:\n{strategy}"),
            ("human", "{input}")
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    async def chat(self, user_input: str):
        return await self.chain.ainvoke({
            "strategy": self.strategy_context,
            "input": user_input
        })

yokaizen_agent = YokaizenAgent()
