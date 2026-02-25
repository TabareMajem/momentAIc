"""
Tests for Social UGC Agents & Campaigns
Covers Reddit Sniper, Viral Campaigns, Discord Bot, and Guerrilla Marketing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.agents.guerrilla.reddit_sniper_agent import reddit_sniper, RelationshipThread
from app.agents.viral_campaign_agent import viral_campaign_agent
from app.agents.guerrilla.discord_agent import discord_dispute_bot, DisputeContext
from app.agents.guerrilla.guerrilla_campaign_agent import guerrilla_campaign_agent

# ═══════════════════════════════════════════════════════════════════════════════
# REDDIT SNIPER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_reddit_red_flag_receipt_generation():
    """Test generating a Red Flag Receipt comment."""
    with patch.object(reddit_sniper.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        # Mock LLM response
        mock_llm.return_value.content = """
        {
            "intro_hook": "My partner used to deny this too.",
            "evidence_description": "We started using a scorecard.",
            "subtle_mention": "Found this app called BondQuests.",
            "call_to_action": "It really stopped the denial.",
            "full_comment": "My partner used to deny this too. We started using a scorecard from BondQuests. It really worked."
        }
        """
        
        receipt = await reddit_sniper.generate_red_flag_receipt(
            thread_context={
                "title": "BF denies gaslighting",
                "pain_point": "He says I'm crazy",
                "subreddit": "r/relationships"
            },
            product_context={"name": "BondQuests"}
        )
        
        assert receipt.intro_hook == "My partner used to deny this too."
        assert "BondQuests" in receipt.subtle_mention
        assert receipt.full_comment is not None

@pytest.mark.asyncio
async def test_reddit_breakthrough_story():
    """Test generating a Breakthrough Story."""
    with patch.object(reddit_sniper.creative_llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = """
        {
            "title": "UPDATE: Gamification saved us",
            "backstory": "We fought about money.",
            "turning_point": "We played a game.",
            "specific_result": "We laughed.",
            "product_mention": "It's BondQuests.",
            "full_post": "UPDATE: Gamification saved us. We fought about money. We played a game. We laughed."
        }
        """
        
        story = await reddit_sniper.generate_breakthrough_story(
            theme="money",
            product_context={"name": "BondQuests"},
            age_range="30M/29F"
        )
        
        assert "UPDATE" in story.title
        assert story.backstory == "We fought about money."
        assert story.product_mention == "It's BondQuests."

@pytest.mark.asyncio
async def test_find_relationship_opportunities():
    """Test scanning for opportunities."""
    with patch("app.agents.base.web_search.ainvoke", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = "Search results for gaslighting"
        
        with patch.object(reddit_sniper.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value.content = """
            [
                {
                    "title": "BF gaslights me",
                    "url": "http://reddit.com/123",
                    "subreddit": "r/relationships",
                    "pain_point": "Denial",
                    "gamification_angle": "Scorecard",
                    "engagement_score": 9
                }
            ]
            """
            
            opps = await reddit_sniper.find_relationship_opportunities(limit=1)
            
            assert len(opps) == 1
            assert opps[0].title == "BF gaslights me"
            assert opps[0].engagement_score == 9

# ═══════════════════════════════════════════════════════════════════════════════
# VIRAL CAMPAIGN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_exit_survey_content():
    """Test generating Exit Survey content."""
    with patch.object(viral_campaign_agent.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = """
        {
            "intro_screen_text": "Rate your ex.",
            "questions": [{"question": "Q1", "options": ["a", "b"]}],
            "result_categories": [{"name": "The Ghost"}],
            "share_text": "I rated my ex.",
            "cta_text": "Sign up."
        }
        """
        
        content = await viral_campaign_agent.generate_exit_survey_content()
        
        assert content.intro_screen_text == "Rate your ex."
        assert len(content.questions) == 1

@pytest.mark.asyncio
async def test_wedding_vows_generation():
    """Test generating Wedding Vows."""
    with patch.object(viral_campaign_agent.creative_llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = """
        {
            "opening_line": "Player 2 ready.",
            "body": "I love you.",
            "closing_promise": "Game on.",
            "full_vow": "Player 2 ready. I love you. Game on.",
            "gaming_references": ["Player 2"]
        }
        """
        
        vow = await viral_campaign_agent.generate_wedding_vows(
            bond_stats={},
            partner_name="Alex"
        )
        
        assert vow.opening_line == "Player 2 ready."
        assert "Player 2" in vow.gaming_references

@pytest.mark.asyncio
async def test_relationship_stats_card():
    """Test generating Stats Card."""
    with patch.object(viral_campaign_agent.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = """
        {
            "character_name": "Alex the Great",
            "level": 50,
            "class_type": "Tank",
            "stats": {"Humor": 99},
            "special_abilities": ["Laugh"],
            "weaknesses": ["Snoring"],
            "share_text": "My stats."
        }
        """
        
        card = await viral_campaign_agent.generate_relationship_stats_card(user_data={})
        
        assert card.character_name == "Alex the Great"
        assert card.level == 50
        assert card.stats["Humor"] == 99

# ═══════════════════════════════════════════════════════════════════════════════
# DISCORD AGENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_discord_settle_command():
    """Test Discord settle command handling."""
    with patch.object(discord_dispute_bot.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = "Order in the court!"
        
        context = DisputeContext(
            channel_id="123",
            guild_id="456",
            user1_id="u1",
            user2_id="u2"
        )
        
        response = await discord_dispute_bot.handle_settle_command(context)
        
        assert "Order in the court!" in response["message"]
        assert "game_links" in response
        assert "game_id" in response

@pytest.mark.asyncio
async def test_discord_mini_game():
    """Test Discord mini-game generation."""
    with patch.object(discord_dispute_bot.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = """
        {
            "game_type": "poll",
            "question": "Pizza?",
            "options": ["Yes", "No"],
            "scoring_rule": "Match"
        }
        """
        
        mini_game = await discord_dispute_bot._generate_mini_game()
        
        assert mini_game.question == "Pizza?"
        assert len(mini_game.options) == 2

# ═══════════════════════════════════════════════════════════════════════════════
# GUERRILLA CAMPAIGN TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_product_mockup_concept():
    """Test Product Mockup Concept generation."""
    with patch.object(guerrilla_campaign_agent.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = """
        {
            "product_name": "Starter Pack",
            "tagline": "Get good.",
            "box_copy": ["Feature 1"],
            "visual_description": "Blue box.",
            "store_setting": "Target",
            "reddit_caption": "Found this."
        }
        """
        
        concept = await guerrilla_campaign_agent.generate_product_mockup_concept()
        
        assert concept.product_name == "Starter Pack"
        assert concept.store_setting == "Target"

@pytest.mark.asyncio
async def test_parking_ticket_generation():
    """Test Parking Ticket generation."""
    with patch.object(guerrilla_campaign_agent.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = """
        {
            "violation_code": "123",
            "violation_type": "No Date",
            "violation_description": "Sad.",
            "fine": "Play game.",
            "issuing_officer": "Cop",
            "date_issued": "Today",
            "additional_notes": "None"
        }
        """
        
        ticket = await guerrilla_campaign_agent.generate_parking_ticket()
        
        assert ticket.violation_type == "No Date"
        assert ticket.fine == "Play game."

@pytest.mark.asyncio
async def test_wedding_embed_generation():
    """Test Wedding Embed generation."""
    with patch.object(guerrilla_campaign_agent.llm, "ainvoke", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = """
        {
            "game_title": "Quiz",
            "questions": [],
            "result_messages": {},
            "embed_code": "<iframe></iframe>",
            "cta_url": "link"
        }
        """
        
        embed = await guerrilla_campaign_agent.generate_wedding_embed(couple_data={})
        
        assert embed.game_title == "Quiz"
        assert "iframe" in embed.embed_code
