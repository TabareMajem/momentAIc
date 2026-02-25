"""
Launch Strategist Agent
AI-powered product launch strategy with comprehensive platform database
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog
import re

from app.agents.base import get_llm
from app.data.launch_platforms import (
    get_platforms_for_segment,
    get_all_segments,
    get_product_hunt_strategy,
    search_platforms,
    PRODUCT_HUNT,
    LAUNCH_SEGMENTS,
)

logger = structlog.get_logger()


@dataclass
class Platform:
    """Platform recommendation"""
    name: str
    url: str
    type: str
    priority: int
    timing: str
    custom_copy: str = ""
    tips: List[str] = field(default_factory=list)


@dataclass
class LaunchPhase:
    """Launch phase with actions"""
    name: str
    timing: str
    actions: List[Dict[str, str]]


@dataclass
class ProductHuntStrategy:
    """Product Hunt specific launch strategy"""
    optimal_day: str
    optimal_time: str
    tagline: str
    first_comment: str
    hunter_recommendation: str
    preparation_checklist: List[str]


@dataclass
class LaunchStrategy:
    """Complete launch strategy"""
    product_name: str
    detected_segment: str
    confidence: float
    summary: str
    
    # Phases
    pre_launch: LaunchPhase
    launch_day: LaunchPhase
    post_launch: LaunchPhase
    
    # Platforms
    top_platforms: List[Platform]
    
    # Optional Product Hunt
    product_hunt_strategy: Optional[ProductHuntStrategy] = None
    
    # Calendar
    calendar: List[Dict[str, Any]] = field(default_factory=list)
    
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            "product_name": self.product_name,
            "detected_segment": self.detected_segment,
            "confidence": self.confidence,
            "summary": self.summary,
            "strategy": {
                "pre_launch": {
                    "name": self.pre_launch.name,
                    "timing": self.pre_launch.timing,
                    "actions": self.pre_launch.actions,
                },
                "launch_day": {
                    "name": self.launch_day.name,
                    "timing": self.launch_day.timing,
                    "actions": self.launch_day.actions,
                },
                "post_launch": {
                    "name": self.post_launch.name,
                    "timing": self.post_launch.timing,
                    "actions": self.post_launch.actions,
                },
            },
            "platforms": [
                {
                    "name": p.name,
                    "url": p.url,
                    "type": p.type,
                    "priority": p.priority,
                    "timing": p.timing,
                    "custom_copy": p.custom_copy,
                    "tips": p.tips,
                }
                for p in self.top_platforms
            ],
            "product_hunt_strategy": {
                "optimal_day": self.product_hunt_strategy.optimal_day,
                "optimal_time": self.product_hunt_strategy.optimal_time,
                "tagline": self.product_hunt_strategy.tagline,
                "first_comment": self.product_hunt_strategy.first_comment,
                "hunter_recommendation": self.product_hunt_strategy.hunter_recommendation,
                "preparation_checklist": self.product_hunt_strategy.preparation_checklist,
            } if self.product_hunt_strategy else None,
            "calendar": self.calendar,
            "error": self.error,
        }


class LaunchStrategistAgent:
    """
    Launch Strategist Agent - AI-powered product launch planning
    
    Capabilities:
    - Segment detection from product description
    - Platform matching (100+ per segment)
    - Product Hunt launch optimization
    - Launch calendar generation
    - Platform-specific copy generation
    """
    
    SEGMENT_KEYWORDS = {
        "ai_agents": ["ai", "artificial intelligence", "machine learning", "gpt", "llm", "chatbot", "agent", "automation", "neural", "model"],
        "developer_tools": ["developer", "api", "sdk", "cli", "ide", "github", "code", "programming", "devops", "infrastructure"],
        "anime_gaming": ["anime", "manga", "game", "gaming", "esports", "twitch", "steam", "rpg", "pixel", "indie game"],
        "b2c_consumer": ["app", "mobile", "consumer", "lifestyle", "fitness", "health", "photo", "social", "dating", "food"],
        "entrepreneur": ["startup", "saas", "business", "productivity", "marketing", "sales", "crm", "analytics", "b2b"],
    }
    
    async def detect_segment(self, description: str) -> tuple[str, float]:
        """Detect product segment from description"""
        description_lower = description.lower()
        
        scores = {}
        for segment, keywords in self.SEGMENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in description_lower)
            scores[segment] = score
        
        best_segment = max(scores, key=scores.get)
        total_keywords = sum(scores.values())
        confidence = scores[best_segment] / max(total_keywords, 1)
        
        # Use AI for better detection if confidence is low
        if confidence < 0.3:
            llm = get_llm("gemini-flash", temperature=0.1)
            if llm:
                prompt = f"""Classify this product into exactly ONE of these segments:
- ai_agents (AI tools, chatbots, ML products)
- developer_tools (APIs, SDKs, dev infrastructure)
- anime_gaming (anime apps, games, gaming tools)
- b2c_consumer (consumer apps, lifestyle, health)
- entrepreneur (SaaS, business tools, productivity)

Product: {description}

Respond with ONLY the segment name, nothing else."""
                
                try:
                    response = await llm.ainvoke(prompt)
                    content = response.content if hasattr(response, 'content') else str(response)
                    detected = content.strip().lower().replace(" ", "_")
                    if detected in self.SEGMENT_KEYWORDS:
                        return detected, 0.8
                except Exception as e:
                    logger.warning("AI segment detection failed", error=str(e))
        
        return best_segment, min(confidence * 2, 1.0)  # Scale up confidence
    
    async def generate_launch_strategy(
        self,
        product_name: str,
        description: str,
        target_audience: str,
        include_product_hunt: bool = True,
    ) -> LaunchStrategy:
        """Generate complete launch strategy for a product"""
        
        # 1. Detect segment
        segment, confidence = await self.detect_segment(description)
        
        # 2. Get platforms for segment
        platforms = get_platforms_for_segment(segment, limit=20)
        
        # 3. Generate platform recommendations with AI
        top_platforms = await self._generate_platform_recommendations(
            product_name, description, platforms
        )
        
        # 4. Generate launch phases
        pre_launch = await self._generate_phase(
            "Pre-Launch", "T-14 to T-1", product_name, description, segment
        )
        launch_day = await self._generate_phase(
            "Launch Day", "T-0", product_name, description, segment
        )
        post_launch = await self._generate_phase(
            "Post-Launch", "T+1 to T+30", product_name, description, segment
        )
        
        # 5. Product Hunt strategy (if requested)
        ph_strategy = None
        if include_product_hunt:
            ph_strategy = await self._generate_product_hunt_strategy(
                product_name, description, target_audience
            )
        
        # 6. Generate calendar
        calendar = self._generate_calendar(top_platforms, ph_strategy)
        
        # 7. Generate summary
        summary = await self._generate_summary(
            product_name, segment, len(top_platforms)
        )
        
        return LaunchStrategy(
            product_name=product_name,
            detected_segment=segment,
            confidence=confidence,
            summary=summary,
            pre_launch=pre_launch,
            launch_day=launch_day,
            post_launch=post_launch,
            top_platforms=top_platforms,
            product_hunt_strategy=ph_strategy,
            calendar=calendar,
        )
    
    async def _generate_platform_recommendations(
        self,
        product_name: str,
        description: str,
        platforms: List[Dict],
    ) -> List[Platform]:
        """Generate prioritized platform recommendations with custom copy"""
        
        recommendations = []
        llm = get_llm("gemini-flash", temperature=0.5)
        
        for i, platform in enumerate(platforms[:15]):  # Top 15
            # Generate custom copy for top 5
            custom_copy = ""
            if i < 5 and llm:
                try:
                    prompt = f"""Write a 1-sentence tagline for {product_name} specifically for {platform['name']}.
Product: {description}
Platform audience: {platform.get('best_for', [])}

Keep it under 100 characters. Be punchy and platform-appropriate."""
                    
                    response = await llm.ainvoke(prompt)
                    custom_copy = response.content.strip()[:120] if hasattr(response, 'content') else ""
                except Exception:
                    pass
            
            # Determine timing
            timing = "T-7" if i < 5 else ("T-3" if i < 10 else "T-0")
            
            recommendations.append(Platform(
                name=platform["name"],
                url=platform["url"],
                type=platform.get("type", "directory"),
                priority=i + 1,
                timing=timing,
                custom_copy=custom_copy,
                tips=platform.get("tips", []),
            ))
        
        return recommendations
    
    async def _generate_phase(
        self,
        phase_name: str,
        timing: str,
        product_name: str,
        description: str,
        segment: str,
    ) -> LaunchPhase:
        """Generate launch phase actions"""
        
        llm = get_llm("gemini-flash", temperature=0.5)
        
        actions = []
        
        if llm:
            try:
                prompt = f"""Generate 5 specific, actionable tasks for the {phase_name} phase of launching {product_name}.

Product: {description}
Segment: {segment}
Timing: {timing}

Format each action as: ACTION: [task] | PRIORITY: [high/medium/low]"""
                
                response = await llm.ainvoke(prompt)
                content = response.content if hasattr(response, 'content') else ""
                
                for line in content.split("\n"):
                    if "ACTION:" in line:
                        parts = line.split("|")
                        action = parts[0].replace("ACTION:", "").strip()
                        priority = "high"
                        if len(parts) > 1 and "low" in parts[1].lower():
                            priority = "low"
                        elif len(parts) > 1 and "medium" in parts[1].lower():
                            priority = "medium"
                        
                        actions.append({"action": action, "priority": priority})
            except Exception as e:
                logger.warning(f"Phase generation failed: {e}")
        
        # Fallback actions
        if not actions:
            if "Pre" in phase_name:
                actions = [
                    {"action": "Build email waiting list", "priority": "high"},
                    {"action": "Create demo video/GIF", "priority": "high"},
                    {"action": "Prepare press kit", "priority": "medium"},
                    {"action": "Reach out to beta testers", "priority": "high"},
                    {"action": "Set up analytics tracking", "priority": "medium"},
                ]
            elif "Day" in phase_name:
                actions = [
                    {"action": "Submit to Product Hunt", "priority": "high"},
                    {"action": "Post on all social channels", "priority": "high"},
                    {"action": "Send launch email to list", "priority": "high"},
                    {"action": "Engage in all comments/discussions", "priority": "high"},
                    {"action": "Reach out to press contacts", "priority": "medium"},
                ]
            else:
                actions = [
                    {"action": "Follow up with users for feedback", "priority": "high"},
                    {"action": "Submit to remaining directories", "priority": "medium"},
                    {"action": "Write launch retrospective", "priority": "low"},
                    {"action": "Analyze launch metrics", "priority": "high"},
                    {"action": "Plan next feature based on feedback", "priority": "medium"},
                ]
        
        return LaunchPhase(name=phase_name, timing=timing, actions=actions)
    
    async def _generate_product_hunt_strategy(
        self,
        product_name: str,
        description: str,
        target_audience: str,
    ) -> ProductHuntStrategy:
        """Generate Product Hunt specific strategy"""
        
        llm = get_llm("gemini-pro", temperature=0.6)
        
        tagline = f"{product_name} - {description[:50]}..."
        first_comment = "Thanks for checking us out! Happy to answer any questions."
        
        if llm:
            try:
                prompt = f"""Create a Product Hunt launch strategy for:

Product: {product_name}
Description: {description}
Target: {target_audience}

Provide:
1. TAGLINE: (max 60 chars, punchy, value-focused)
2. FIRST_COMMENT: (founder's introduction, 2-3 sentences, authentic)
3. HUNTER_TIP: (who would be a good hunter for this product)

Format exactly as above with labels."""
                
                response = await llm.ainvoke(prompt)
                content = response.content if hasattr(response, 'content') else ""
                
                # Parse response
                if "TAGLINE:" in content:
                    tagline_match = re.search(r"TAGLINE:\s*(.+?)(?:\n|$)", content)
                    if tagline_match:
                        tagline = tagline_match.group(1).strip()[:60]
                
                if "FIRST_COMMENT:" in content:
                    comment_match = re.search(r"FIRST_COMMENT:\s*(.+?)(?=HUNTER_TIP:|$)", content, re.DOTALL)
                    if comment_match:
                        first_comment = comment_match.group(1).strip()[:500]
                
            except Exception as e:
                logger.warning(f"PH strategy generation failed: {e}")
        
        return ProductHuntStrategy(
            optimal_day="Tuesday",
            optimal_time="12:01 AM PST",
            tagline=tagline,
            first_comment=first_comment,
            hunter_recommendation="Find a hunter with 1000+ followers in your niche",
            preparation_checklist=[
                "Create compelling thumbnail (240x240)",
                "Prepare 5+ screenshots/GIFs",
                "Write detailed description with features",
                "Prepare for 24-hour engagement window",
                "Alert your network to support at launch",
                "Prepare FAQ for common questions",
            ],
        )
    
    def _generate_calendar(
        self,
        platforms: List[Platform],
        ph_strategy: Optional[ProductHuntStrategy],
    ) -> List[Dict[str, Any]]:
        """Generate launch calendar"""
        
        today = datetime.utcnow()
        launch_date = today + timedelta(days=14)  # Assume 2 weeks from now
        
        calendar = []
        
        # Pre-launch activities
        calendar.append({
            "date": (launch_date - timedelta(days=14)).strftime("%Y-%m-%d"),
            "timing": "T-14",
            "action": "Start building launch hype on social media",
            "platform": "Twitter/LinkedIn",
        })
        
        calendar.append({
            "date": (launch_date - timedelta(days=7)).strftime("%Y-%m-%d"),
            "timing": "T-7",
            "action": "Submit to early access directories",
            "platform": "BetaList, BetaPage",
        })
        
        # Platform submissions based on timing
        for platform in platforms[:10]:
            days_before = 7 if platform.timing == "T-7" else (3 if platform.timing == "T-3" else 0)
            calendar.append({
                "date": (launch_date - timedelta(days=days_before)).strftime("%Y-%m-%d"),
                "timing": platform.timing,
                "action": f"Submit to {platform.name}",
                "platform": platform.name,
                "url": platform.url,
            })
        
        # Product Hunt
        if ph_strategy:
            calendar.append({
                "date": launch_date.strftime("%Y-%m-%d"),
                "timing": "T-0",
                "action": "Product Hunt Launch (12:01 AM PST)",
                "platform": "Product Hunt",
                "priority": "CRITICAL",
            })
        
        # Sort by date
        calendar.sort(key=lambda x: x["date"])
        
        return calendar
    
    async def _generate_summary(
        self,
        product_name: str,
        segment: str,
        platform_count: int,
    ) -> str:
        """Generate launch strategy summary"""
        
        return f"Launch strategy for {product_name} targeting the {segment.replace('_', ' ')} segment. " \
               f"Recommended submission to {platform_count} platforms with a 3-phase approach: " \
               f"Pre-launch (T-14 to T-1), Launch Day (T-0), and Post-launch (T+1 to T+30)."
    
    async def get_segment_platforms(self, segment: str, limit: int = 50) -> List[Dict]:
        """Get all platforms for a segment"""
        return get_platforms_for_segment(segment, limit)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a launch strategy request"""
        
        # Extract product name and description from context
        product_name = startup_context.get("name", "Your Product")
        description = startup_context.get("description", message)
        target = startup_context.get("target_audience", "early adopters")
        
        strategy = await self.generate_launch_strategy(
            product_name=product_name,
            description=description,
            target_audience=target,
        )
        
        return {
            "response": f"🚀 Launch Strategy Generated for {product_name}!\n\n"
                       f"**Segment**: {strategy.detected_segment}\n"
                       f"**Top Platforms**: {len(strategy.top_platforms)}\n"
                       f"**Product Hunt Ready**: {'Yes' if strategy.product_hunt_strategy else 'No'}\n\n"
                       f"Use the API endpoint for the full strategy JSON.",
            "data": strategy.to_dict(),
            "agent": "launch_strategist",
        }


# Singleton instance
launch_strategist_agent = LaunchStrategistAgent()
