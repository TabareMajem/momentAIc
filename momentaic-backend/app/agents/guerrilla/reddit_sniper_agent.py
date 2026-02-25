"""
Reddit Sniper Agent ("The Trojan Horse")
Advanced Reddit growth strategies using narrative marketing.

Strategies:
1. "Red Flag Receipt" Comment - Visual evidence approach for r/relationships
2. "Gamified Breakthrough" Story - UPDATE-style posts methodology
3. Value-First Comments - Helpful responses with subtle product mentions
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import structlog
import datetime
import json
import re

from app.agents.base import get_llm, web_search

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS FOR STRUCTURED OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

class RelationshipThread(BaseModel):
    """A Reddit thread with relationship pain points"""
    title: str = Field(description="Thread title")
    url: str = Field(description="Thread URL")
    subreddit: str = Field(description="Subreddit name")
    pain_point: str = Field(description="The relationship issue being discussed")
    gamification_angle: str = Field(description="How BondQuests could help")
    engagement_score: int = Field(description="1-10 score of thread engagement potential")


class RedFlagReceipt(BaseModel):
    """Generated 'Red Flag Receipt' content"""
    intro_hook: str = Field(description="Opening line that builds rapport")
    evidence_description: str = Field(description="How the receipt/scorecard helped")
    subtle_mention: str = Field(description="Natural product mention")
    call_to_action: str = Field(description="Soft CTA without being salesy")
    full_comment: str = Field(description="Complete comment ready to post")


class BreakthroughStory(BaseModel):
    """UPDATE-style success story post"""
    title: str = Field(description="Reddit post title with [UPDATE] tag")
    backstory: str = Field(description="Brief recap of the original problem")
    turning_point: str = Field(description="What changed - the gamification discovery")
    specific_result: str = Field(description="Concrete outcome (we laughed, connected)")
    product_mention: str = Field(description="Natural mention when asked in comments")
    full_post: str = Field(description="Complete post content")


class ThreadAnalysis(BaseModel):
    """List of analyzed threads"""
    threads: List[RelationshipThread]


# ═══════════════════════════════════════════════════════════════════════════════
# REDDIT SNIPER AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class RedditSniperAgent:
    """
    Reddit Sniper Agent - "Trojan Horse" Narrative Marketing
    
    WARNING: r/relationships has strict "No Self-Promotion" rules.
    This agent generates content for HUMAN REVIEW, not auto-posting.
    
    Core Strategies:
    1. Red Flag Receipt - Evidence-based comments
    2. Gamified Breakthrough - Success story updates  
    3. Value-First - Helpful responses first, product second
    """
    
    # Target subreddits for relationship content
    TARGET_SUBREDDITS = [
        "r/relationships",
        "r/relationship_advice",
        "r/dating_advice",
        "r/Marriage",
        "r/AskMenOver30",
        "r/AskWomenOver30",
        "r/LongDistance",
        "r/dating",
    ]
    
    # High-intent keywords that signal opportunity
    PAIN_KEYWORDS = [
        "gaslighting",
        "he denies",
        "she denies",
        "never takes responsibility",
        "communication issues",
        "refuses therapy",
        "boring relationship",
        "spark died",
        "same fight",
        "always arguing",
        "doesn't listen",
        "feeling disconnected",
    ]
    
    @property
    def llm(self):
        return get_llm("gemini-flash", temperature=0.7)
    
    @property
    def creative_llm(self):
        """Higher temperature for story generation"""
        return get_llm("gemini-flash", temperature=0.85)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STRATEGY 1: RED FLAG RECEIPT COMMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_red_flag_receipt(
        self,
        thread_context: Dict[str, Any],
        product_context: Dict[str, Any],
    ) -> RedFlagReceipt:
        """
        Generate a "Red Flag Receipt" style comment.
        
        This is used when responding to threads where someone's partner
        denies behavior. The "receipt" is a gamified scorecard that
        provides visual evidence.
        
        Args:
            thread_context: Info about the Reddit thread
            product_context: BondQuests product details
            
        Returns:
            RedFlagReceipt with complete comment
        """
        if not self.llm:
            return RedFlagReceipt(
                intro_hook="",
                evidence_description="",
                subtle_mention="",
                call_to_action="",
                full_comment=""
            )
        
        prompt = f"""
You are drafting a helpful Reddit comment for r/relationships.

THREAD CONTEXT:
Title: {thread_context.get('title', 'Partner denies bad behavior')}
Problem: {thread_context.get('pain_point', 'Partner gaslighting about arguments')}
Subreddit: {thread_context.get('subreddit', 'r/relationships')}

PRODUCT CONTEXT:
Name: {product_context.get('name', 'BondQuests')}
Description: {product_context.get('description', 'Relationship gamification app')}

YOUR TASK:
Write a comment using the "Red Flag Receipt" strategy:

1. INTRO HOOK: Start with empathy. "My partner used to do this too..."
2. EVIDENCE APPROACH: Mention using a visual scorecard/receipt to track issues
3. SUBTLE MENTION: Reference the app NATURALLY ("this thing called BondQuests I think?")
4. RESULT: Focus on how it stopped the argument/denial

CRITICAL RULES:
- Sound like a real person sharing experience, NOT marketing
- Be under 100 words
- Don't use corporate language
- Don't link directly to the product
- Focus on helping THEM, not selling

Return JSON with these fields:
- intro_hook: Opening empathetic line
- evidence_description: How the receipt/scorecard helped
- subtle_mention: Natural product mention
- call_to_action: Soft helpful suggestion
- full_comment: Complete ready-to-post comment
"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a helpful Redditor sharing genuine relationship advice."),
                HumanMessage(content=prompt)
            ])
            
            # Parse JSON response
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return RedFlagReceipt(**data)
            else:
                # Fallback: treat entire response as comment
                return RedFlagReceipt(
                    intro_hook="My partner used to deny things too.",
                    evidence_description="We started tracking it visually.",
                    subtle_mention="There's this app I found...",
                    call_to_action="Might help you too.",
                    full_comment=content
                )
                
        except Exception as e:
            logger.error("Red flag receipt generation failed", error=str(e))
            return RedFlagReceipt(
                intro_hook="",
                evidence_description="",
                subtle_mention="",
                call_to_action="",
                full_comment=""
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STRATEGY 2: GAMIFIED BREAKTHROUGH STORY
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def generate_breakthrough_story(
        self,
        theme: str = "communication",
        product_context: Dict[str, Any] = None,
        age_range: str = "28M/26F",
    ) -> BreakthroughStory:
        """
        Generate an UPDATE-style success story post.
        
        These posts follow the Reddit pattern:
        "UPDATE: [Original problem] but [unexpected solution] worked"
        
        Args:
            theme: communication, intimacy, boredom, money
            product_context: BondQuests details
            age_range: Poster age/gender format
            
        Returns:
            BreakthroughStory with title and full post
        """
        if not self.creative_llm:
            return BreakthroughStory(
                title="",
                backstory="",
                turning_point="",
                specific_result="",
                product_mention="",
                full_post=""
            )
        
        product_context = product_context or {
            "name": "BondQuests",
            "description": "Relationship gamification app that turns issues into RPG stats"
        }
        
        theme_contexts = {
            "communication": "Partner refused therapy for communication issues",
            "intimacy": "Spark died, relationship felt boring",
            "boredom": "Same routine every week, felt disconnected",
            "money": "Constant fights about spending and saving",
        }
        
        problem = theme_contexts.get(theme, theme_contexts["communication"])
        
        prompt = f"""
You are writing a Reddit UPDATE post for r/relationships.

ORIGINAL PROBLEM: {problem}
POSTER: [{age_range}]
SOLUTION: Gamification instead of traditional therapy

PRODUCT CONTEXT:
Name: {product_context.get('name')}
Key Feature: Turns relationship issues into RPG-style stats
Specific Tool: "Sync Test" that reveals different views

YOUR TASK:
Write an UPDATE post that:

1. TITLE: "UPDATE: My [{age_range.split('/')[0]}] partner refused therapy for our {theme} issues, but agreed to 'play a video game' about it. It actually worked."

2. STRUCTURE:
   - Brief recap of original problem (2-3 sentences)
   - Mention "therapy felt like work" (relatable)
   - Discovery of the gamification approach
   - Specific moment it worked ("We did a Sync Test and realized...")
   - Focus on RESULT (laughter, connection) not features

3. CRUCIAL:
   - Under 300 words
   - Sound like a real person, not marketing
   - DON'T link to the product in the post
   - Let commenters ask "What game?" so you can reply organically

Return JSON with:
- title: Full Reddit title
- backstory: Problem recap
- turning_point: Discovery moment
- specific_result: What happened (emotional)
- product_mention: What to say when asked in comments
- full_post: Complete post body
"""

        try:
            response = await self.creative_llm.ainvoke([
                SystemMessage(content="You are writing an authentic Reddit relationship success story."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return BreakthroughStory(**data)
            else:
                return BreakthroughStory(
                    title=f"UPDATE: Gamification actually fixed our {theme} issues",
                    backstory=problem,
                    turning_point="We tried a relationship game instead of therapy",
                    specific_result="We actually talked and laughed together",
                    product_mention="It's called BondQuests - turns relationship stuff into RPG stats",
                    full_post=content
                )
                
        except Exception as e:
            logger.error("Breakthrough story generation failed", error=str(e))
            return BreakthroughStory(
                title="",
                backstory="",
                turning_point="",
                specific_result="",
                product_mention="",
                full_post=""
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OPPORTUNITY SCANNING
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def find_relationship_opportunities(
        self,
        limit: int = 5,
    ) -> List[RelationshipThread]:
        """
        Scan Reddit for high-intent relationship threads.
        
        Looks for discussions where:
        - Partner denies/gaslights behavior
        - Communication has broken down
        - Traditional therapy was rejected
        - Relationship feels stale
        
        Returns:
            List of threads with gamification angles
        """
        if not self.llm:
            return []
        
        opportunities = []
        
        # Search for pain point keywords across target subreddits
        for keyword in self.PAIN_KEYWORDS[:5]:  # Limit to avoid rate limits
            try:
                query = f"site:reddit.com ({' OR '.join(self.TARGET_SUBREDDITS)}) {keyword}"
                search_results = await web_search.ainvoke(query)
                
                analysis_prompt = f"""
Analyze these Reddit search results about relationship issues:
{search_results}

Find threads where:
1. Someone's partner is in denial about behavior
2. Communication has broken down  
3. Therapy was rejected or "feels like work"
4. The relationship feels stale/boring

For each relevant thread, identify the GAMIFICATION ANGLE:
How could turning the issue into a "game" or visual scorecard help?

Return JSON array:
[
    {{
        "title": "Thread title",
        "url": "Thread URL",
        "subreddit": "Subreddit name",
        "pain_point": "The specific relationship problem",
        "gamification_angle": "How BondQuests could help",
        "engagement_score": 1-10
    }}
]

Only include threads with engagement_score >= 7.
"""
                
                response = await self.llm.ainvoke([
                    SystemMessage(content="You are analyzing Reddit for growth marketing opportunities."),
                    HumanMessage(content=analysis_prompt)
                ])
                
                content = response.content
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    threads = json.loads(json_match.group(0))
                    for thread in threads:
                        if thread.get('engagement_score', 0) >= 7:
                            opportunities.append(RelationshipThread(**thread))
                            
            except Exception as e:
                logger.error(f"Reddit scan failed for keyword: {keyword}", error=str(e))
                continue
        
        # Deduplicate and sort by engagement
        seen_urls = set()
        unique_opportunities = []
        for opp in sorted(opportunities, key=lambda x: x.engagement_score, reverse=True):
            if opp.url not in seen_urls:
                seen_urls.add(opp.url)
                unique_opportunities.append(opp)
                if len(unique_opportunities) >= limit:
                    break
        
        return unique_opportunities
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VALUE-FIRST COMMENT DRAFTING
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def draft_value_first_comment(
        self,
        thread: RelationshipThread,
        product_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Draft a value-first comment for a specific thread.
        
        Rule: Answer their question FIRST, then mention product naturally.
        
        Returns:
            Dict with comment text and metadata
        """
        if not self.llm:
            return {"error": "LLM not available"}
        
        product_context = product_context or {
            "name": "BondQuests",
            "description": "Relationship gamification app"
        }
        
        prompt = f"""
Write a helpful Reddit comment for this thread:

THREAD:
Title: {thread.title}
Subreddit: {thread.subreddit}
Problem: {thread.pain_point}
Gamification Angle: {thread.gamification_angle}

PRODUCT:
Name: {product_context.get('name')}

RULES:
1. HELP FIRST: Give genuine, actionable advice (2-3 sentences)
2. SHARE EXPERIENCE: "What worked for us..." (if applicable)
3. SUBTLE MENTION: Only if it fits naturally
4. NO LINKS: Never link directly
5. SOUND HUMAN: No corporate speak, sound like a friend

Max 80 words. Be genuine and helpful.
"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a supportive Redditor giving relationship advice."),
                HumanMessage(content=prompt)
            ])
            
            return {
                "thread_url": thread.url,
                "thread_title": thread.title,
                "comment": response.content,
                "strategy": "value_first",
                "generated_at": datetime.datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error("Value-first comment failed", error=str(e))
            return {"error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BATCH OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def run_sniper_campaign(
        self,
        product_context: Dict[str, Any],
        stories_count: int = 2,
        comments_count: int = 5,
    ) -> Dict[str, Any]:
        """
        Run a complete Reddit Sniper campaign.
        
        Generates:
        1. Breakthrough stories for posting
        2. Value-first comments for opportunities
        3. Red flag receipt comments
        
        Returns:
            Campaign results with all generated content
        """
        logger.info("Starting Reddit Sniper campaign")
        
        results = {
            "breakthrough_stories": [],
            "opportunity_comments": [],
            "red_flag_receipts": [],
            "generated_at": datetime.datetime.now().isoformat(),
        }
        
        # Generate breakthrough stories
        themes = ["communication", "boredom", "intimacy", "money"]
        for theme in themes[:stories_count]:
            story = await self.generate_breakthrough_story(
                theme=theme,
                product_context=product_context,
            )
            if story.full_post:
                results["breakthrough_stories"].append({
                    "theme": theme,
                    "title": story.title,
                    "post": story.full_post,
                    "comment_reply": story.product_mention,
                })
        
        # Find opportunities and draft comments
        opportunities = await self.find_relationship_opportunities(limit=comments_count)
        for opp in opportunities:
            comment = await self.draft_value_first_comment(opp, product_context)
            if "error" not in comment:
                results["opportunity_comments"].append(comment)
            
            # Generate red flag receipt for denial-related threads
            if "deny" in opp.pain_point.lower() or "gaslight" in opp.pain_point.lower():
                receipt = await self.generate_red_flag_receipt(
                    thread_context={
                        "title": opp.title,
                        "pain_point": opp.pain_point,
                        "subreddit": opp.subreddit,
                    },
                    product_context=product_context,
                )
                if receipt.full_comment:
                    results["red_flag_receipts"].append({
                        "thread": opp.title,
                        "comment": receipt.full_comment,
                    })
        
        logger.info(
            "Reddit Sniper campaign complete",
            stories=len(results["breakthrough_stories"]),
            comments=len(results["opportunity_comments"]),
            receipts=len(results["red_flag_receipts"]),
        )
        
        return results


# Singleton instance
reddit_sniper = RedditSniperAgent()
