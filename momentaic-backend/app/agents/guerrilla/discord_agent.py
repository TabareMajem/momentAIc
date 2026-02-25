"""
Discord Dispute Bot ("BondJudge")
Discord bot integration for couple dispute resolution.

Features:
- @BondJudge settle this → Serves Sync Test link
- Mini conflict resolution games
- Posts winner/result back to channel
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import structlog
import datetime
import json
import re
import uuid

from app.agents.base import get_llm

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class DisputeContext(BaseModel):
    """Context for a dispute request"""
    channel_id: str = Field(description="Discord channel ID")
    guild_id: str = Field(description="Discord server/guild ID")
    user1_id: str = Field(description="First user Discord ID")
    user2_id: str = Field(description="Second user Discord ID")
    dispute_topic: Optional[str] = Field(default=None, description="Topic of the dispute if mentioned")
    message_context: Optional[str] = Field(default=None, description="Recent messages for context")


class SyncTestLink(BaseModel):
    """Generated Sync Test game link"""
    game_id: str = Field(description="Unique game session ID")
    player1_link: str = Field(description="Link for first player")
    player2_link: str = Field(description="Link for second player")
    spectator_link: str = Field(description="Link for channel to view results")
    expires_at: str = Field(description="Link expiration timestamp")


class DisputeResolution(BaseModel):
    """Result of a dispute resolution game"""
    winner: Optional[str] = Field(default=None, description="Winner username if applicable")
    verdict: str = Field(description="BondJudge's verdict")
    compatibility_score: int = Field(description="Compatibility score 1-100")
    fun_fact: str = Field(description="Fun fact about the couple based on responses")
    share_text: str = Field(description="Shareable result text")


class MiniGame(BaseModel):
    """A quick dispute resolution mini-game"""
    game_type: str = Field(description="Type of game")
    question: str = Field(description="Question/prompt for players")
    options: List[str] = Field(description="Answer options")
    scoring_rule: str = Field(description="How answers are scored")


# ═══════════════════════════════════════════════════════════════════════════════
# DISCORD SERVICE (Bot Management)
# ═══════════════════════════════════════════════════════════════════════════════

class DiscordService:
    """
    Discord Bot Token management and interaction.
    
    Note: This is a content/response generator. 
    Actual Discord API calls would be handled by a separate bot process.
    """
    
    BASE_GAME_URL = "https://bondquests.com/sync-test"
    
    def generate_game_links(self, game_id: str) -> SyncTestLink:
        """Generate unique links for a Sync Test session."""
        base_url = self.BASE_GAME_URL
        expires = datetime.datetime.now() + datetime.timedelta(hours=24)
        
        return SyncTestLink(
            game_id=game_id,
            player1_link=f"{base_url}?game={game_id}&player=1",
            player2_link=f"{base_url}?game={game_id}&player=2",
            spectator_link=f"{base_url}?game={game_id}&mode=spectate",
            expires_at=expires.isoformat(),
        )
    
    def format_bot_response(self, content: str, style: str = "judge") -> Dict[str, Any]:
        """
        Format a bot response for Discord embedding.
        
        Args:
            content: Message content
            style: judge, playful, formal
            
        Returns:
            Discord embed-ready dict
        """
        colors = {
            "judge": 0x9B59B6,  # Purple (regal)
            "playful": 0xE91E63,  # Pink
            "formal": 0x3498DB,  # Blue
        }
        
        return {
            "embeds": [{
                "title": "⚖️ BondJudge",
                "description": content,
                "color": colors.get(style, colors["judge"]),
                "footer": {
                    "text": "Test your compatibility at bondquests.com"
                }
            }]
        }


discord_service = DiscordService()


# ═══════════════════════════════════════════════════════════════════════════════
# DISCORD DISPUTE BOT AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class DiscordDisputeBot:
    """
    Discord Bot - "BondJudge" for Couple Disputes
    
    Target: Cozy Gamer Discord servers, e-dating communities
    
    Commands:
    - @BondJudge settle this → Serves Sync Test link
    - @BondJudge who's right → Quick poll game
    - @BondJudge rate us → Compatibility check
    
    Growth: Discord bots spread rapidly between servers
    """
    
    BOT_PERSONA = """
You are BondJudge, a wise but playful bot that helps couples settle disputes.
Your personality:
- Fair and impartial (like a courtroom judge, but fun)
- Uses relationship/gaming metaphors
- Gives verdicts in dramatic, entertaining ways
- Never takes sides unfairly
- Encourages healthy communication with humor
"""
    
    @property
    def llm(self):
        return get_llm("gemini-flash", temperature=0.8)
    
    @property
    def service(self):
        return discord_service
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND: SETTLE THIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_settle_command(
        self,
        context: DisputeContext,
    ) -> Dict[str, Any]:
        """
        Handle "@BondJudge settle this" command.
        
        Generates:
        1. A witty acknowledgment message
        2. Sync Test game links for both users
        3. Instructions for playing
        
        Returns:
            Response with links and embed data
        """
        game_id = str(uuid.uuid4())[:8]
        links = self.service.generate_game_links(game_id)
        
        # Generate witty intro
        intro = await self._generate_judge_intro(context.dispute_topic)
        
        response_content = f"""
{intro}

**⚔️ THE CHALLENGE HAS BEEN SET ⚔️**

<@{context.user1_id}> and <@{context.user2_id}>, the court demands you prove your compatibility!

**Click your link below to begin the Sync Test:**
🔷 Player 1: {links.player1_link}
🔷 Player 2: {links.player2_link}

*Both players must complete the test within 24 hours.*
*Results will be posted here when complete!*
"""
        
        return {
            "message": response_content,
            "embed": self.service.format_bot_response(intro, style="judge"),
            "game_links": links.model_dump() if hasattr(links, 'model_dump') else links.__dict__,
            "game_id": game_id,
        }
    
    async def _generate_judge_intro(self, topic: Optional[str] = None) -> str:
        """Generate a dramatic judge intro."""
        if not self.llm:
            return "The court is now in session! 🔨"
        
        prompt = f"""
You are BondJudge. Generate a dramatic but playful one-liner to start a dispute resolution.

{"Topic of dispute: " + topic if topic else "General dispute"}

Rules:
- Under 50 words
- Sound like a wise but fun judge
- Use humor
- Reference relationships/gaming subtly

Just the intro line, no formatting.
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content.strip()
        except Exception:
            return "Order in the court! 🔨 BondJudge presiding. Let the games begin!"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND: WHO'S RIGHT (Quick Poll)
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_whos_right_command(
        self,
        context: DisputeContext,
        question: str,
    ) -> Dict[str, Any]:
        """
        Handle "@BondJudge who's right [question]" command.
        
        Creates a quick poll for the channel to vote on.
        
        Returns:
            Poll message with reactions
        """
        verdict_intro = await self._generate_verdict_teaser(question)
        
        response = f"""
⚖️ **THE COURT ASKS THE PEOPLE** ⚖️

*{question}*

{verdict_intro}

React below:
🔵 <@{context.user1_id}> is right
🔴 <@{context.user2_id}> is right
⚪ They're both wrong
🟡 They're both right (relationship goals!)

*Voting closes in 5 minutes...*
"""
        
        return {
            "message": response,
            "reactions": ["🔵", "🔴", "⚪", "🟡"],
            "poll_duration_minutes": 5,
        }
    
    async def _generate_verdict_teaser(self, question: str) -> str:
        """Generate a teaser for the verdict."""
        if not self.llm:
            return "The council shall decide your fate..."
        
        try:
            response = await self.llm.ainvoke(f"""
Generate a one-line dramatic teaser for this dispute:
"{question}"

Make it sound like a reality TV moment. Under 20 words.
""")
            return response.content.strip()
        except Exception:
            return "The people shall render judgment..."
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND: RATE US (Quick Compatibility)
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_rate_us_command(
        self,
        context: DisputeContext,
    ) -> Dict[str, Any]:
        """
        Handle "@BondJudge rate us" command.
        
        Serves a quick compatibility mini-game.
        
        Returns:
            Mini-game content
        """
        mini_game = await self._generate_mini_game()
        
        response = f"""
💕 **COMPATIBILITY CHECK** 💕

BondJudge will test your connection with ONE question!

**{mini_game.question}**

<@{context.user1_id}> and <@{context.user2_id}>, reply with your answers!

Options:
{chr(10).join([f"{i+1}. {opt}" for i, opt in enumerate(mini_game.options)])}

*Answer within 60 seconds. Match = +10 Love Points!*
"""
        
        return {
            "message": response,
            "game": mini_game.model_dump() if hasattr(mini_game, 'model_dump') else mini_game.__dict__,
            "timeout_seconds": 60,
        }
    
    async def _generate_mini_game(self) -> MiniGame:
        """Generate a random compatibility mini-game."""
        if not self.llm:
            return MiniGame(
                game_type="quick_match",
                question="If you were a pizza topping, what would you be?",
                options=["Pepperoni (classic)", "Pineapple (controversial)", "Mushroom (underrated)", "Extra cheese (extra love)"],
                scoring_rule="Match = +10 points, Close = +5 points"
            )
        
        try:
            response = await self.llm.ainvoke("""
Create a fun, quick compatibility question for a couple.

Requirements:
- Question should be light and playful
- 4 answer options
- Options should be revealing about personality but not too serious
- Make it shareable/meme-worthy

Example format:
Question: "Your partner is sick. You bring them:"
Options: ["Soup and meds (caretaker)", "Memes to cheer up (comedian)", "Space and peace (introvert)", "Full hospital setup at home (extra)"]

Return JSON:
{
    "game_type": "quick_match",
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "scoring_rule": "Match = +10 points"
}
""")
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return MiniGame(**data)
                
        except Exception as e:
            logger.error("Mini game generation failed", error=str(e))
        
        return MiniGame(
            game_type="quick_match",
            question="It's movie night. You pick:",
            options=["Action (explosions!)", "Comedy (laughs only)", "Horror (cuddle excuse)", "Documentary (we're learning)"],
            scoring_rule="Match = +10 points"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RESULT POSTING
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_resolution_message(
        self,
        resolution: DisputeResolution,
        context: DisputeContext,
    ) -> Dict[str, Any]:
        """
        Generate the resolution message after a Sync Test completes.
        
        Posted back to the original channel.
        """
        winner_text = f"🏆 **{resolution.winner} has the high ground!**" if resolution.winner else "⚖️ **It's a tie! You're both winners (or both wrong? 🤔)**"
        
        message = f"""
🎉 **THE VERDICT IS IN** 🎉

<@{context.user1_id}> vs <@{context.user2_id}>

{winner_text}

{resolution.verdict}

**Compatibility Score:** {resolution.compatibility_score}/100 {"🔥" if resolution.compatibility_score > 80 else "💕" if resolution.compatibility_score > 50 else "🤔"}

**Fun Fact:** {resolution.fun_fact}

---
*{resolution.share_text}*

Want to play more? → bondquests.com
"""
        
        return {
            "message": message,
            "embed": self.service.format_bot_response(resolution.verdict, style="playful"),
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BOT INSTALLATION PITCH
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_bot_invite_content(self) -> Dict[str, Any]:
        """
        Generate content for bot installation/invite.
        
        Used for marketing the bot to Discord server admins.
        """
        return {
            "name": "BondJudge",
            "tagline": "The Ultimate Relationship Referee for Discord",
            "description": """
🎮 **BondJudge** settles couple disputes the fun way!

**Commands:**
• `@BondJudge settle this` - Start a Sync Test
• `@BondJudge who's right [question]` - Quick poll
• `@BondJudge rate us` - Compatibility check

**Perfect for:**
• Cozy gamer servers
• E-dating communities
• Friend groups
• Streaming communities

*Free to use. Spreads joy and settles arguments!*
""",
            "features": [
                "Sync Test compatibility games",
                "Quick dispute polls",
                "Fun compatibility questions",
                "Shareable results",
            ],
            "invite_url": "https://bondquests.com/discord/invite",
        }


# Singleton instance
discord_dispute_bot = DiscordDisputeBot()
