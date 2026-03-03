"""
Content Creator Agent
LangGraph-based content generation agent
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog

from app.agents.base import (
    get_llm,
    get_agent_config,
    web_search,
    get_trending_topics,
    generate_hashtags,
    BaseAgent,
    safe_parse_json,
)
from app.models.conversation import AgentType
from app.models.growth import ContentPlatform

logger = structlog.get_logger()


# Platform-specific constraints
PLATFORM_CONSTRAINTS = {
    ContentPlatform.LINKEDIN: {
        "max_chars": 3000,
        "optimal_chars": 1500,
        "format": "professional",
        "hashtag_limit": 5,
        "best_times": ["Tuesday 10am", "Wednesday 12pm", "Thursday 8am"],
        "tips": [
            "Start with a hook",
            "Use line breaks for readability",
            "End with a question or CTA",
            "Professional but personal tone",
        ],
    },
    ContentPlatform.TWITTER: {
        "max_chars": 280,
        "thread_max": 25,
        "format": "concise",
        "hashtag_limit": 3,
        "best_times": ["Weekdays 12pm-3pm"],
        "tips": [
            "Hook in first tweet",
            "Number threads (1/n)",
            "Use emojis sparingly",
            "End with CTA",
        ],
    },
    ContentPlatform.BLOG: {
        "min_words": 800,
        "optimal_words": 1500,
        "format": "long-form",
        "tips": [
            "SEO-optimized title",
            "Use headers and subheaders",
            "Include actionable takeaways",
            "Add internal/external links",
        ],
    },
}


class ContentAgent(BaseAgent):
    """
    Content Creator Agent - Generates viral, platform-optimized content
    
    Workflow:
    1. Trend Research → Find relevant trends
    2. Ideation → Generate hook ideas
    3. Drafting → Create platform-specific content
    4. Optimization → Add hashtags, format for platform
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.CONTENT_CREATOR)
        self.llm = get_llm("gemini-pro", temperature=0.8)  # Higher temp for creativity
    
    async def generate(
        self,
        platform: ContentPlatform,
        topic: str,
        startup_context: Dict[str, Any],
        content_type: str = "post",
        tone: str = "professional",
        trend_based: bool = False,
        custom_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate content for a specific platform
        """
        if isinstance(platform, str):
            try:
                platform = ContentPlatform(platform.lower())
            except ValueError:
                logger.warning(f"Invalid platform '{platform}', defaulting to LinkedIn")
                platform = ContentPlatform.LINKEDIN

        logger.info(
            "Content Agent: Generating content",
            platform=platform.value,
            topic=topic,
            type=content_type,
        )
        
        # Get platform constraints
        constraints = PLATFORM_CONSTRAINTS.get(platform, {})
        
        # Step 1: Research trends if requested
        trends = []
        if trend_based:
            industry = startup_context.get("industry", "tech")
            trends = await get_trending_topics.ainvoke({"industry": industry, "platform": platform.value})
        
        # Step 2: Generate content
        # ... check self.llm ...
        if not self.llm:
            return {
                "success": False,
                "error": "AI Service Unavailable. Please configure keys.",
                "platform": platform.value,
                "trends_used": trends if trend_based else None,
            }
        
        # Build prompt
        prompt = self._build_generation_prompt(
            platform=platform,
            topic=topic,
            startup_context=startup_context,
            content_type=content_type,
            tone=tone,
            constraints=constraints,
            trends=trends,
            custom_context=custom_context,
        )
        
        try:
            full_prompt = f"{self.config['system_prompt']}\n\n{prompt}"
            
            # Use self-correction loop for high quality
            response_content = await self.self_correcting_call(
                prompt=full_prompt,
                goal=f"Generate high-quality {platform} content",
                target_audience=startup_context.get("industry", "general audience"),
                model_name="gemini-pro",
                threshold=85
            )
            
            content = self._parse_response(response_content, platform)
            
            # Step 3: Generate hashtags
            hashtags = await generate_hashtags.ainvoke({"topic": topic, "platform": platform.value})
            content["hashtags"] = hashtags[:constraints.get("hashtag_limit", 5)]
            
            # Step 4: Validate and optimize
            content = self._optimize_for_platform(content, platform, constraints)
            
            return {
                "success": True,
                "content": content,
                "platform": platform.value,
                "trends_used": trends if trend_based else None,
                "generated_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error("Content generation failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    def _build_generation_prompt(
        self,
        platform: ContentPlatform,
        topic: str,
        startup_context: Dict[str, Any],
        content_type: str,
        tone: str,
        constraints: Dict[str, Any],
        trends: List[str],
        custom_context: Optional[str],
    ) -> str:
        """Build the content generation prompt"""
        
        trend_section = ""
        if trends:
            trend_section = f"\nTrending topics to potentially incorporate:\n" + "\n".join(f"- {t}" for t in trends)
        
        custom_section = ""
        if custom_context:
            custom_section = f"\nAdditional context:\n{custom_context}"
        
        return f"""Generate {content_type} content for {platform.value}.

Topic: {topic}

About the startup:
- Name: {startup_context.get('name', 'Our Startup')}
- Industry: {startup_context.get('industry', 'Tech')}
- Description: {startup_context.get('description', '')}
- Tagline: {startup_context.get('tagline', '')}

Tone: {tone}

Platform constraints:
{self._format_constraints(constraints)}

Platform tips:
{chr(10).join(f'- {tip}' for tip in constraints.get('tips', []))}
{trend_section}
{custom_section}

Generate content with:
1. A compelling hook (first line that grabs attention)
2. Main body (valuable, engaging content)
3. A call-to-action
4. Suggested title

Format your response as:
TITLE: [title]
HOOK: [opening hook]
BODY: [main content]
CTA: [call to action]"""
    
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format platform constraints as string"""
        lines = []
        if "max_chars" in constraints:
            lines.append(f"- Maximum characters: {constraints['max_chars']}")
        if "optimal_chars" in constraints:
            lines.append(f"- Optimal length: {constraints['optimal_chars']} chars")
        if "min_words" in constraints:
            lines.append(f"- Minimum words: {constraints['min_words']}")
        if "thread_max" in constraints:
            lines.append(f"- Max tweets in thread: {constraints['thread_max']}")
        return "\n".join(lines)
    
    def _parse_response(self, response: str, platform: ContentPlatform) -> Dict[str, Any]:
        """Parse LLM response into structured content"""
        content = {
            "title": "",
            "hook": "",
            "body": "",
            "cta": "",
        }
        
        # Simple parsing (in production, use structured outputs)
        lines = response.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                current_section = "title"
                content["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("HOOK:"):
                current_section = "hook"
                content["hook"] = line.replace("HOOK:", "").strip()
            elif line.startswith("BODY:"):
                current_section = "body"
                content["body"] = line.replace("BODY:", "").strip()
            elif line.startswith("CTA:"):
                current_section = "cta"
                content["cta"] = line.replace("CTA:", "").strip()
            elif current_section and line:
                content[current_section] += "\n" + line
        
        return content
    
    def _optimize_for_platform(
        self,
        content: Dict[str, Any],
        platform: ContentPlatform,
        constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Optimize content for platform constraints"""
        
        # Combine into final body
        full_content = f"{content['hook']}\n\n{content['body']}\n\n{content['cta']}"
        
        # Check character limits
        max_chars = constraints.get("max_chars")
        if max_chars and len(full_content) > max_chars:
            # Truncate intelligently
            full_content = full_content[:max_chars-3] + "..."
            content["truncated"] = True
        
        content["full_body"] = full_content
        content["char_count"] = len(full_content)
        content["word_count"] = len(full_content.split())
        
        return content
    
    
    async def generate_ideas(
        self,
        startup_context: Dict[str, Any],
        count: int = 5,
    ) -> List[Dict[str, str]]:
        """Generate content ideas based on startup context"""
        
        industry = startup_context.get("industry", "tech")
        trends = await get_trending_topics.ainvoke({"industry": industry, "platform": "linkedin"})
        
        if not self.llm:
             return []
        
        prompt = f"""Generate {count} content ideas for a {industry} startup.

Startup: {startup_context.get('name', 'Our Startup')}
Description: {startup_context.get('description', '')}

Current trends: {', '.join(trends)}

For each idea, provide:
- Topic
- Best platform (linkedin, twitter, blog)
- Content type (post, thread, article)
- Why it would work

Format each as: TOPIC | PLATFORM | TYPE | REASON"""
        
        response = await self.llm.ainvoke([
            SystemMessage(content="You are a content strategist for startups."),
            HumanMessage(content=prompt),
        ])
        
        # Parse response
        ideas = []
        for line in response.content.split("\n"):
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    ideas.append({
                        "topic": parts[0],
                        "platform": parts[1].lower(),
                        "type": parts[2].lower(),
                        "reason": parts[3] if len(parts) > 3 else "",
                    })
        
        return ideas[:count]

    # ==== TWIN.SO KILLER FEATURES ====
    
    async def repurpose_content(
        self,
        original_content: str,
        source_format: str = "blog",
        target_formats: List[str] = None,
        startup_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Turn 1 piece of content into 10+ platform-optimized versions.
        Superior to twin.so: handles blog → thread → carousel → video script.
        """
        target_formats = target_formats or ["linkedin_post", "twitter_thread", "carousel", "video_script"]
        startup_context = startup_context or {}
        
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        prompt = f"""You are a content repurposing expert. Transform this content into multiple formats.

ORIGINAL CONTENT ({source_format}):
{original_content[:5000]}

STARTUP CONTEXT:
{startup_context.get('name', 'Our Startup')} - {startup_context.get('description', '')}

Generate content for these formats: {', '.join(target_formats)}

For each format, provide:
1. The optimized content
2. Best posting time
3. Hashtags (if applicable)

Format as JSON:
{{
    "linkedin_post": {{"content": "...", "hashtags": [...], "best_time": "..."}},
    "twitter_thread": {{"tweets": ["1/5 Hook...", "2/5...", ...], "hashtags": [...]}},
    "carousel": {{"slides": ["Slide 1: Title", "Slide 2: Point 1", ...]}},
    "video_script": {{"hook": "...", "body": "...", "cta": "...", "duration": "60s"}}
}}"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a viral content expert who maximizes reach across platforms."),
                HumanMessage(content=prompt),
            ])
            
            parsed = safe_parse_json(response.content)
            if parsed:
                return {
                    "success": True,
                    "source_format": source_format,
                    "repurposed": parsed,
                    "count": len(parsed),
                    "agent": AgentType.CONTENT_CREATOR.value
                }
            else:
                return {"success": False, "raw": response.content}
                
        except Exception as e:
            logger.error("Content repurposing failed", error=str(e))
            return {"error": str(e)}

    async def batch_schedule(
        self,
        content_items: List[Dict[str, Any]],
        schedule_type: str = "optimal",  # "optimal", "burst", "drip"
    ) -> Dict[str, Any]:
        """
        Schedule multiple posts across platforms with optimal timing.
        Superior to twin.so: AI-powered timing + cross-platform strategy.
        """
        if not content_items:
            return {"error": "No content items provided"}
            
        # Import Typefully for scheduling
        from app.integrations.typefully import TypefullyIntegration
        typefully = TypefullyIntegration()
        
        scheduled = []
        from datetime import datetime, timedelta
        
        # Generate optimal schedule
        base_time = datetime.utcnow()
        
        for i, item in enumerate(content_items):
            platform = item.get("platform", "twitter")
            content = item.get("content", "")
            
            # Calculate optimal time based on strategy
            if schedule_type == "burst":
                # All within 2 hours
                post_time = base_time + timedelta(minutes=i * 15)
            elif schedule_type == "drip":
                # Spread over week
                post_time = base_time + timedelta(days=i)
            else:
                # Optimal: Peak engagement times
                peak_hours = [9, 12, 17]  # 9am, noon, 5pm
                day_offset = i // 3
                hour_index = i % 3
                post_time = base_time.replace(hour=peak_hours[hour_index]) + timedelta(days=day_offset)
            
            # Schedule via Typefully
            if platform in ["twitter", "x"]:
                result = await typefully.execute_action("schedule_thread", {
                    "content": content,
                    "date": post_time.isoformat()
                })
                scheduled.append({
                    "platform": platform,
                    "scheduled_at": post_time.isoformat(),
                    "status": "scheduled" if result.get("success") else "failed",
                    "result": result
                })
            else:
                # For other platforms, mark as draft
                scheduled.append({
                    "platform": platform,
                    "scheduled_at": post_time.isoformat(),
                    "status": "draft_created",
                    "content_preview": content[:100]
                })
        
        return {
            "success": True,
            "scheduled_count": len(scheduled),
            "schedule_type": schedule_type,
            "posts": scheduled,
            "agent": AgentType.CONTENT_CREATOR.value
        }

    async def content_performance_analysis(
        self,
        past_posts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze what content performs best and why.
        Returns actionable insights for future content.
        """
        if not self.llm or not past_posts:
            return {"error": "LLM not initialized or no posts provided"}
        
        prompt = f"""Analyze these past posts and identify patterns:

POSTS:
{past_posts[:20]}

Provide:
1. Top performing themes
2. Best posting times observed
3. Content formats that work
4. Hashtags that drove engagement
5. Recommendations for future content

Format as JSON."""

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            parsed = safe_parse_json(response.content)
            if parsed:
                return parsed
            return {"raw_analysis": response.content}
        except Exception as e:
            return {"error": str(e)}

    async def auto_generate_daily(
        self,
        startup_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Autonomous Mode: Generate a daily content post for a startup.
        Called by the scheduler — no human prompt needed.
        
        Flow:
        1. Scan trends in the startup's industry
        2. Pick the best topic
        3. Generate platform-optimized content (LinkedIn by default)
        4. Return ready-to-schedule content
        """
        logger.info("ContentAgent: Auto-generating daily content", startup=startup_context.get("name"))
        
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        try:
            industry = startup_context.get("industry", "Technology")
            
            # 1. Find trending topic
            try:
                trends = await get_trending_topics.ainvoke({"industry": industry, "platform": "linkedin"})
            except Exception:
                trends = [f"Latest {industry} innovations", "AI transformation", "Growth strategies"]
            
            # 2. Pick best topic via LLM
            topic_prompt = f"""Pick the ONE most viral topic for a {industry} startup from these trends:
{chr(10).join(f'- {t}' for t in trends[:10])}

Startup: {startup_context.get('name', 'Our Startup')} - {startup_context.get('description', '')}

Return ONLY the topic (max 8 words)."""
            
            try:
                topic_resp = await self.llm.ainvoke([HumanMessage(content=topic_prompt)])
                topic = topic_resp.content.strip().strip('"')
            except Exception:
                topic = trends[0] if trends else f"The Future of {industry}"
            
            # 3. Generate content for LinkedIn (highest B2B ROI)
            result = await self.generate(
                platform=ContentPlatform.LINKEDIN,
                topic=topic,
                startup_context=startup_context,
                content_type="post",
                tone="professional",
                trend_based=False,
            )
            
            if result.get("success"):
                content = result.get("content", {})
                return {
                    "success": True,
                    "topic": topic,
                    "platform": "linkedin",
                    "title": content.get("title", ""),
                    "full_body": content.get("full_body", ""),
                    "hashtags": content.get("hashtags", []),
                    "char_count": content.get("char_count", 0),
                    "agent": "content_agent",
                }
            else:
                return {"error": result.get("error", "Generation failed")}
                
        except Exception as e:
            logger.error("ContentAgent: Auto-generate failed", error=str(e))
            return {"error": str(e)}

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively identify content opportunities:
        - Content gaps from competitor strategies
        - Trending topics to capitalize on
        - Cross-agent signals (e.g., new leads → case study opportunity)
        """
        actions = []
        shared = self.get_shared_context()
        
        # React to competitor intel
        for signal in shared.get("recent_agent_signals", []):
            if signal.get("topic") in ["competitor_pricing_change", "competitor_scan_scheduled"]:
                actions.append({
                    "name": "counter_content",
                    "description": f"Create comparison content responding to competitor activity: {signal['data'].get('summary', '')}",
                    "priority": "high",
                    "agent": "ContentAgent",
                })
        
        # Suggest evergreen content creation
        actions.append({
            "name": "weekly_content_calendar",
            "description": "Generate this week's content calendar: 3 LinkedIn posts, 1 blog article, 2 Twitter threads.",
            "priority": "medium",
            "agent": "ContentAgent",
        })
        
        if actions:
            await self.publish_to_bus(
                topic="content_opportunities_found",
                data={"summary": f"Identified {len(actions)} content opportunities"},
            )
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Execute a proactive content action using REAL services.
        Generates content and schedules it for real posting.
        """
        action_type = action.get("action", action.get("name", "unknown"))
        
        try:
            if action_type in ("counter_content", "weekly_content_calendar"):
                # Generate real content using the agent's existing pipeline
                result = await self.auto_generate_daily(startup_context=startup_context)
                
                if result.get("success"):
                    # Schedule the content for real posting
                    from app.services.social_scheduler import social_scheduler
                    from datetime import datetime
                    
                    content_body = result.get("full_body", "")
                    if content_body:
                        post = await social_scheduler.schedule_post(
                            startup_id=startup_context.get("id", startup_context.get("startup_id", "")),
                            content=content_body,
                            platforms=["linkedin"],
                            scheduled_at=datetime.utcnow(),
                        )
                        
                        # Wire Typefully Integration: Auto-schedule Twitter Thread
                        try:
                            from app.integrations.typefully import TypefullyIntegration
                            _typefully = TypefullyIntegration()
                            await _typefully.execute_action("create_draft", {
                                "content": content_body,
                                "schedule": True 
                            })
                            logger.info("Typefully: Thread scheduled successfully")
                        except Exception as typ_e:
                            logger.error("Typefully integration failed", error=str(typ_e))
                        
                        await self.publish_to_bus(
                            topic="content_scheduled",
                            data={
                                "summary": f"Content scheduled for LinkedIn & Typefully: {result.get('topic', 'auto-generated')}",
                                "post_id": str(post.id),
                            },
                        )
                        return f"Content generated and scheduled (post_id: {post.id}, topic: {result.get('topic', 'N/A')})"
                    
                    return f"Content generated but no body to schedule"
                
                return f"Content generation failed: {result.get('error', 'unknown')}"
            
            else:
                # Fallback: check for distribution_engineer or thought_leadership
                if action_type == "distribution_engineer":
                    # For each content piece, auto-generate platform-native variants
                    source_content = action.get("content", "")
                    if not source_content and self.llm:
                        # Generate fresh content first
                        daily = await self.auto_generate_daily(startup_context)
                        source_content = daily.get("full_body", "")

                    if source_content and self.llm:
                        prompt = f"""You are a content distribution engineer. Take this content and create platform-native variants optimized for maximum reach.

ORIGINAL CONTENT:
{source_content[:3000]}

STARTUP: {startup_context.get('name', 'Our Startup')} — {startup_context.get('industry', 'Tech')}

Generate ALL of these variants:

1. **Twitter/X Thread** (5-7 tweets, each under 280 chars):
   - Hook tweet must be a contrarian take or surprising stat
   - Number format: 1/ 2/ 3/
   - Last tweet = CTA

2. **LinkedIn Carousel** (8-10 slides):
   - Slide 1: Bold statement hook
   - Slides 2-8: One insight per slide (under 30 words each)
   - Last slide: CTA
   
3. **Hacker News Post**:
   - Title (clickbait-free, factual)
   - Show HN format if applicable

4. **Reddit Post** (r/startups or r/SaaS):
   - Title + body (genuine, not promotional)
   - Adds value first, mentions product only if relevant

5. **YouTube Shorts Script** (60 seconds):
   - Hook (3 seconds)
   - Problem (10 seconds)
   - Solution (30 seconds)
   - CTA (7 seconds)

Format as JSON with keys: twitter_thread, linkedin_carousel, hackernews, reddit, youtube_short"""

                        response = await self.llm.ainvoke(prompt)
                        from app.agents.base import safe_parse_json
                        variants = safe_parse_json(response.content)

                        # Try to schedule the Twitter thread via Typefully
                        if variants and isinstance(variants, dict) and variants.get("twitter_thread"):
                            try:
                                from app.integrations.typefully import TypefullyIntegration
                                typefully = TypefullyIntegration()
                                tweets = variants["twitter_thread"]
                                thread_content = "\n\n---\n\n".join(tweets) if isinstance(tweets, list) else str(tweets)
                                await typefully.execute_action("create_draft", {"content": thread_content, "schedule": True})
                            except Exception:
                                pass

                        await self.publish_to_bus(
                            topic="content_distributed",
                            data={"summary": f"Content distributed to {len(variants) if variants else 0} platforms", "platforms": list(variants.keys()) if variants else []},
                        )
                        return f"Distribution variants generated for {len(variants) if isinstance(variants, dict) else 0} platforms"
                    return "No content to distribute"

                elif action_type == "thought_leadership_pipeline":
                    # Auto-curate industry data into founder's voice for authority building
                    if self.llm:
                        industry = startup_context.get("industry", "Technology")
                        
                        # Search for fresh industry data
                        from app.agents.base import web_search
                        try:
                            search_results = await web_search.ainvoke(f"{industry} statistics data trends 2025 2026")
                        except Exception:
                            search_results = "No fresh data available"

                        prompt = f"""You are a thought leadership ghostwriter for the founder of {startup_context.get('name', 'this startup')}.

Industry: {industry}
Founder voice: Confident, data-driven, contrarian when appropriate

Latest industry data:
{str(search_results)[:3000]}

Create a 7-day thought leadership content pipeline:

For each day, generate:
1. **LinkedIn Post** (150-300 words): Insights + hot take wrapped in the founder's voice
2. **Key Stat**: The data point that anchors the post
3. **Hashtags**: 3-5 relevant hashtags
4. **Engagement Hook**: Question or poll to drive comments

Day themes:
- Mon: Industry insight
- Tue: Behind-the-scenes / building in public
- Wed: Contrarian take
- Thu: Customer success story framework
- Fri: Tool/resource recommendation
- Sat: Weekend read / long-form teaser
- Sun: Week-ahead preview + ask

Format as JSON array: [{{"day": "Monday", "post": "...", "key_stat": "...", "hashtags": [...], "hook": "..."}}]"""

                        response = await self.llm.ainvoke(prompt)
                        parsed = safe_parse_json(response.content)

                        return f"7-day thought leadership pipeline generated: {len(parsed) if isinstance(parsed, list) else 0} posts"
                    return "LLM not available"

                else:
                    return await super().autonomous_action(action, startup_context)
                
        except Exception as e:
            logger.error("ContentAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"


# Singleton instance
content_agent = ContentAgent()
