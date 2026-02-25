"""
Guerrilla Marketing Agents
Stealth growth tactics for startup acquisition
"""

from app.agents.guerrilla.reddit_agent import reddit_agent, RedditSleeperAgent
from app.agents.guerrilla.reddit_sniper_agent import reddit_sniper, RedditSniperAgent
from app.agents.guerrilla.twitter_interceptor import twitter_interceptor, TwitterInterceptorAgent
from app.agents.guerrilla.trend_agent import trend_agent, TrendSurferAgent
from app.agents.guerrilla.discord_agent import discord_dispute_bot, DiscordDisputeBot
from app.agents.guerrilla.guerrilla_campaign_agent import guerrilla_campaign_agent, GuerrillaCampaignAgent
from app.agents.guerrilla.asset_factory_agent import asset_factory_agent, AssetFactoryAgent

__all__ = [
    # Reddit
    "reddit_agent",
    "RedditSleeperAgent",
    "reddit_sniper",
    "RedditSniperAgent",
    # Twitter
    "twitter_interceptor",
    "TwitterInterceptorAgent",
    # Trends
    "trend_agent",
    "TrendSurferAgent",
    # Discord
    "discord_dispute_bot",
    "DiscordDisputeBot",
    # Guerrilla Campaigns
    "guerrilla_campaign_agent",
    "GuerrillaCampaignAgent",
    # Asset Factory
    "asset_factory_agent",
    "AssetFactoryAgent",
]

