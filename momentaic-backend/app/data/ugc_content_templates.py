"""
UGC Content Templates
Platform-specific templates for value-first content generation.

These templates follow key principles:
1. Help first, mention product second
2. Sound like a real person, not marketing
3. Platform-specific formatting
"""

from typing import Dict, List, Any


# ═══════════════════════════════════════════════════════════════════════════════
# REDDIT TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

REDDIT_TEMPLATES = {
    # Red Flag Receipt - for denial/gaslighting threads
    "red_flag_receipt": """
My partner used to deny {pain_point} too until we started tracking it visually.

We found this receipt/scorecard thing from a relationship app (BondQuests I think?) that tracks the "Ick" score. Seeing it on a scorecard stopped the argument instantly.

{helpful_advice}

Might help visualize the issue for them.
""",
    
    # Gamified Breakthrough - UPDATE style posts
    "gamified_breakthrough_update": """
UPDATE: My [{age_range}] {partner} refused therapy for our {issue} issues, but agreed to 'play a video game' about it. It actually worked.

Original post: We were stuck in the same {issue} loop. Every conversation ended in frustration. They wouldn't do therapy - said it "felt like work."

I stumbled onto this thing called BondQuests that turns relationship stuff into RPG-style quests. I pitched it as "relationship video game" instead of "therapy."

They actually agreed.

We did something called a "Sync Test" last night - it shows where you're misaligned. Turns out we had completely different views on {specific_topic}.

The thing that made it work: it didn't feel like we were "working on our relationship." We were playing together. We laughed. We talked. First time in months.

Not saying it's for everyone, but if your partner shuts down at "therapy" or "we need to talk," maybe try the game angle?

Happy to share more if anyone's interested.

---
*Edit: A lot of people asking what game - it's called BondQuests. Has these "quests" you do together and your "stats" change based on how you communicate.*
""",
    
    # Value-first comment - for general advice threads
    "value_first_comment": """
{empathy_opener}

{actionable_advice}

What worked for us: {personal_experience}. There are apps that gamify this stuff too - makes it less "we need to talk" and more like a co-op game.

{soft_cta}
""",
    
    # Pain point response - for specific complaints
    "pain_point_response": """
I felt this. {validation}

Something that actually helped: {solution_without_product}

If you want to make it less awkward, there are relationship "game" type things that help - we use something called BondQuests that tracks this stuff like a video game. Takes the edge off the serious conversations.

Either way, hope things get better. 🙏
""",
}


# ═══════════════════════════════════════════════════════════════════════════════
# TWITTER TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

TWITTER_TEMPLATES = {
    # Competitor intercept - reply to frustrated users
    "competitor_intercept": """
Hey, sorry to hear that! {empathy}

Not to pitch, but check out {product_name} - we built it specifically because {competitor} didn't handle {pain_point} well.

{differentiator}

Happy to help if you have Qs!
""",
    
    # Trend jack - ride viral trends
    "trend_jack": """
{trend_hook}

This is why we built {product_name}.

{connection_to_trend}

{cta}
""",
    
    # Hot take - controversial opinion
    "hot_take": """
Controversial take: {controversial_statement}

Here's why: {reasoning}

{product_tie_in}
""",
    
    # Quote tweet - reaction to relevant content
    "quote_tweet": """
This right here. 👆

{expansion}

(Shameless plug: we're building {product_name} to help with exactly this)
""",
}


# ═══════════════════════════════════════════════════════════════════════════════
# LINKEDIN TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

LINKEDIN_TEMPLATES = {
    # Relationship story - personal narrative
    "relationship_story": """
I almost gave up on my relationship last year.

{hook_detail}

But then we tried something different.

{turning_point}

What I learned:
{lesson_1}
{lesson_2}
{lesson_3}

{product_tie_in}

Has anyone else found unconventional ways to strengthen relationships?

#relationships #growth #gamification
""",
    
    # Founder insight - thought leadership
    "founder_insight": """
Why I built {product_name}:

{personal_story}

The problem: {market_gap}

Our solution: {differentiator}

Early results:
• {metric_1}
• {metric_2}
• {metric_3}

{cta}

#startup #founder #reltech
""",
    
    # Industry observation - RelTech angle
    "industry_observation": """
The "RelTech" industry is about to explode.

Here's why:

1. {reason_1}
2. {reason_2}
3. {reason_3}

We're building in this space ({product_name}) because {our_angle}.

Who else is watching this trend?

#reltech #startups #relationships
""",
}


# ═══════════════════════════════════════════════════════════════════════════════
# DISCORD TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

DISCORD_TEMPLATES = {
    # BondJudge intro - bot personality
    "bond_judge_intro": """
⚖️ **ORDER IN THE COURT!** ⚖️

BondJudge presiding. {witty_opener}

Tag me with `@BondJudge settle this` when you need relationship arbitration.

*No couple too chaotic. No dispute too petty.*
""",
    
    # Sync test invite - game link message
    "sync_test_invite": """
**⚔️ THE CHALLENGE HAS BEEN SET ⚔️**

{user1} and {user2}, the court demands you prove your compatibility!

**Click your link below to begin the Sync Test:**
🔷 Player 1: {player1_link}
🔷 Player 2: {player2_link}

*Both players must complete the test within {duration}.*
*Results will be posted here when complete!*
""",
    
    # Resolution announcement - results
    "resolution_announcement": """
🎉 **THE VERDICT IS IN** 🎉

{user1} vs {user2}

{winner_announcement}

{verdict}

**Compatibility Score:** {score}/100 {score_emoji}

**Fun Fact:** {fun_fact}

---
*{share_text}*

Want to play more? → bondquests.com
""",
    
    # Quick poll - who's right format
    "quick_poll": """
⚖️ **THE COURT ASKS THE PEOPLE** ⚖️

*{question}*

{teaser}

React below:
🔵 {user1} is right
🔴 {user2} is right
⚪ They're both wrong
🟡 They're both right (relationship goals!)

*Voting closes in {duration}...*
""",
}


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_template(platform: str, template_type: str) -> str:
    """Get a template by platform and type."""
    templates = {
        "reddit": REDDIT_TEMPLATES,
        "twitter": TWITTER_TEMPLATES,
        "linkedin": LINKEDIN_TEMPLATES,
        "discord": DISCORD_TEMPLATES,
    }
    
    platform_templates = templates.get(platform.lower(), {})
    return platform_templates.get(template_type, "")


def fill_template(template: str, **kwargs) -> str:
    """Fill a template with provided values."""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result.strip()


def get_platform_templates(platform: str) -> Dict[str, str]:
    """Get all templates for a platform."""
    templates = {
        "reddit": REDDIT_TEMPLATES,
        "twitter": TWITTER_TEMPLATES,
        "linkedin": LINKEDIN_TEMPLATES,
        "discord": DISCORD_TEMPLATES,
    }
    return templates.get(platform.lower(), {})


def list_all_templates() -> Dict[str, List[str]]:
    """List all available templates by platform."""
    return {
        "reddit": list(REDDIT_TEMPLATES.keys()),
        "twitter": list(TWITTER_TEMPLATES.keys()),
        "linkedin": list(LINKEDIN_TEMPLATES.keys()),
        "discord": list(DISCORD_TEMPLATES.keys()),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT STYLE GUIDES
# ═══════════════════════════════════════════════════════════════════════════════

STYLE_GUIDES = {
    "reddit": {
        "tone": "casual, authentic, like a friend giving advice",
        "persona": "someone who's been through it and found something that helped",
        "rules": [
            "Never sound like marketing",
            "Help FIRST, mention product second",
            "Use 'we' and 'us' language",
            "Be under 100 words for comments",
            "No direct links (let people ask)",
        ],
    },
    "twitter": {
        "tone": "punchy, witty, slightly provocative",
        "persona": "startup founder who gets it",
        "rules": [
            "Under 280 characters when possible",
            "Use threads for longer content",
            "One clear CTA per tweet",
            "Emoji sparingly",
        ],
    },
    "linkedin": {
        "tone": "professional but human, storytelling",
        "persona": "thought leader sharing insights",
        "rules": [
            "Start with a hook (first 2 lines visible)",
            "Use line breaks for readability",
            "Include 3-5 hashtags at end",
            "Ask questions to drive engagement",
        ],
    },
    "discord": {
        "tone": "playful, dramatic, judge-like",
        "persona": "BondJudge - wise but fun arbiter",
        "rules": [
            "Use emojis and formatting",
            "Be theatrical but helpful",
            "Always include game links",
            "Post results back to channel",
        ],
    },
}


def get_style_guide(platform: str) -> Dict[str, Any]:
    """Get the style guide for a platform."""
    return STYLE_GUIDES.get(platform.lower(), STYLE_GUIDES["reddit"])
