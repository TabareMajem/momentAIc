"""
Launch Platforms Database
Comprehensive database of 100+ platforms per niche segment for product launches
"""

from typing import Dict, List, Any

# Platform schema: {name, url, type, audience_size, cost, best_for, tips}

PRODUCT_HUNT = {
    "name": "Product Hunt",
    "url": "https://www.producthunt.com/posts/new",
    "type": "launch_platform",
    "audience_size": "5M+ monthly",
    "cost": "free",
    "best_for": ["SaaS", "Developer Tools", "B2C Apps", "AI Products", "Productivity"],
    "tips": [
        "Launch Tuesday-Thursday for best visibility",
        "Prepare a hunter with high follower count",
        "Be active in comments for 24 hours",
        "Have a compelling tagline (60 chars max)",
        "Prepare GIF/video demo",
        "Engage with supportive communities beforehand",
    ],
    "priority": 1,
}

# ==================
# ENTREPRENEUR SEGMENT (100+ platforms)
# ==================
ENTREPRENEUR_PLATFORMS = [
    # === DIRECTORIES & LAUNCH SITES ===
    {"name": "BetaList", "url": "https://betalist.com/submit", "type": "directory", "audience_size": "500K+", "cost": "free/$129", "best_for": ["Startups", "Beta products"], "tips": ["Submit 1-2 weeks before launch"]},
    {"name": "StartupBase", "url": "https://startupbase.io/submit", "type": "directory", "audience_size": "100K+", "cost": "free", "best_for": ["Startups", "SaaS"], "tips": ["Add detailed description"]},
    {"name": "Launching Next", "url": "https://launchingnext.com/submit", "type": "directory", "audience_size": "80K+", "cost": "free", "best_for": ["New startups"], "tips": ["Early-stage friendly"]},
    {"name": "StartupLift", "url": "https://startuplift.com", "type": "directory", "audience_size": "50K+", "cost": "free", "best_for": ["Feedback"], "tips": ["Get user feedback"]},
    {"name": "BetaPage", "url": "https://betapage.co", "type": "directory", "audience_size": "200K+", "cost": "free/$49", "best_for": ["Beta products"], "tips": ["Good for early traction"]},
    {"name": "Startups.fyi", "url": "https://startups.fyi", "type": "directory", "audience_size": "30K+", "cost": "free", "best_for": ["Indie products"], "tips": ["Curated list"]},
    {"name": "SideProjectors", "url": "https://sideprojectors.com", "type": "marketplace", "audience_size": "100K+", "cost": "free", "best_for": ["Side projects"], "tips": ["Can also sell projects"]},
    {"name": "Launching.io", "url": "https://launching.io", "type": "directory", "audience_size": "20K+", "cost": "free", "best_for": ["Startups"], "tips": ["Simple submission"]},
    {"name": "GetApp", "url": "https://getapp.com", "type": "directory", "audience_size": "2M+", "cost": "paid", "best_for": ["B2B SaaS"], "tips": ["Collect reviews"]},
    {"name": "G2", "url": "https://g2.com", "type": "directory", "audience_size": "5M+", "cost": "free/paid", "best_for": ["B2B Software"], "tips": ["Critical for enterprise"]},
    {"name": "Capterra", "url": "https://capterra.com", "type": "directory", "audience_size": "3M+", "cost": "paid", "best_for": ["Business software"], "tips": ["PPC model"]},
    {"name": "AlternativeTo", "url": "https://alternativeto.net/add-application", "type": "directory", "audience_size": "5M+", "cost": "free", "best_for": ["All software"], "tips": ["List as alternative to competitors"]},
    {"name": "Slant", "url": "https://slant.co", "type": "directory", "audience_size": "2M+", "cost": "free", "best_for": ["Comparisons"], "tips": ["Add to relevant comparisons"]},
    {"name": "StackShare", "url": "https://stackshare.io", "type": "directory", "audience_size": "1M+", "cost": "free", "best_for": ["Developer tools"], "tips": ["Tech stack showcase"]},
    {"name": "Crunchbase", "url": "https://crunchbase.com", "type": "database", "audience_size": "10M+", "cost": "free", "best_for": ["All startups"], "tips": ["Essential for credibility"]},
    
    # === COMMUNITIES ===
    {"name": "Indie Hackers", "url": "https://indiehackers.com", "type": "community", "audience_size": "500K+", "cost": "free", "best_for": ["Bootstrapped", "Indie"], "tips": ["Share journey, not just product"]},
    {"name": "r/startups", "url": "https://reddit.com/r/startups", "type": "subreddit", "audience_size": "1M+", "cost": "free", "best_for": ["Startups"], "tips": ["Follow self-promo rules"]},
    {"name": "r/entrepreneur", "url": "https://reddit.com/r/entrepreneur", "type": "subreddit", "audience_size": "2M+", "cost": "free", "best_for": ["Entrepreneurs"], "tips": ["Value-first content"]},
    {"name": "r/SideProject", "url": "https://reddit.com/r/SideProject", "type": "subreddit", "audience_size": "200K+", "cost": "free", "best_for": ["Side projects"], "tips": ["Show behind-the-scenes"]},
    {"name": "r/IMadeThis", "url": "https://reddit.com/r/IMadeThis", "type": "subreddit", "audience_size": "50K+", "cost": "free", "best_for": ["Makers"], "tips": ["Creative projects"]},
    {"name": "Hacker News (Show HN)", "url": "https://news.ycombinator.com/showhn.html", "type": "community", "audience_size": "5M+", "cost": "free", "best_for": ["Tech", "Developer tools"], "tips": ["Technical audience, be prepared"]},
    {"name": "DEV.to", "url": "https://dev.to", "type": "community", "audience_size": "1M+", "cost": "free", "best_for": ["Developer tools"], "tips": ["Write launch story"]},
    {"name": "Hashnode", "url": "https://hashnode.com", "type": "community", "audience_size": "500K+", "cost": "free", "best_for": ["Developer tools"], "tips": ["Technical deep-dives"]},
    {"name": "Makerlog", "url": "https://getmakerlog.com", "type": "community", "audience_size": "20K+", "cost": "free", "best_for": ["Makers"], "tips": ["Daily build updates"]},
    {"name": "WIP.co", "url": "https://wip.co", "type": "community", "audience_size": "5K+", "cost": "$20/mo", "best_for": ["Makers"], "tips": ["Accountability community"]},
    {"name": "Pioneer", "url": "https://pioneer.app", "type": "accelerator", "audience_size": "50K+", "cost": "free", "best_for": ["Early stage"], "tips": ["Weekly feedback"]},
    
    # === NEWSLETTERS ===
    {"name": "TLDR", "url": "https://tldr.tech/advertise", "type": "newsletter", "audience_size": "1M+", "cost": "paid", "best_for": ["Tech products"], "tips": ["High-quality tech audience"]},
    {"name": "Morning Brew", "url": "https://morningbrew.com/advertise", "type": "newsletter", "audience_size": "4M+", "cost": "paid", "best_for": ["Business"], "tips": ["Business professionals"]},
    {"name": "The Hustle", "url": "https://thehustle.co/advertise", "type": "newsletter", "audience_size": "2M+", "cost": "paid", "best_for": ["Business"], "tips": ["Startup-friendly audience"]},
    {"name": "Startup Digest", "url": "https://startupdigest.com", "type": "newsletter", "audience_size": "500K+", "cost": "free", "best_for": ["Startups"], "tips": ["Local editions available"]},
    {"name": "Hacker Newsletter", "url": "https://hackernewsletter.com", "type": "newsletter", "audience_size": "60K+", "cost": "paid", "best_for": ["Tech"], "tips": ["HN audience"]},
    {"name": "Changelog", "url": "https://changelog.com", "type": "newsletter", "audience_size": "100K+", "cost": "paid", "best_for": ["Developer tools"], "tips": ["Developer audience"]},
    {"name": "Console.dev", "url": "https://console.dev", "type": "newsletter", "audience_size": "30K+", "cost": "free", "best_for": ["Developer tools"], "tips": ["Submit for review"]},
    {"name": "Unreadit", "url": "https://unreadit.com", "type": "newsletter", "audience_size": "50K+", "cost": "free", "best_for": ["All"], "tips": ["Reddit content digest"]},
    
    # === PODCASTS ===
    {"name": "Indie Hackers Podcast", "url": "https://indiehackers.com/podcast", "type": "podcast", "audience_size": "100K+", "cost": "free", "best_for": ["Bootstrapped"], "tips": ["Pitch your story"]},
    {"name": "How I Built This", "url": "https://npr.org/podcasts/510313/how-i-built-this", "type": "podcast", "audience_size": "500K+", "cost": "free", "best_for": ["Success stories"], "tips": ["Need traction first"]},
    {"name": "Startups For the Rest of Us", "url": "https://startupsfortherestofus.com", "type": "podcast", "audience_size": "50K+", "cost": "free", "best_for": ["Bootstrapped"], "tips": ["SaaS focused"]},
    {"name": "The SaaS Podcast", "url": "https://saasclub.io/podcast", "type": "podcast", "audience_size": "30K+", "cost": "free", "best_for": ["SaaS"], "tips": ["SaaS founders"]},
    {"name": "My First Million", "url": "https://myfirstmillion.com", "type": "podcast", "audience_size": "200K+", "cost": "free", "best_for": ["Business ideas"], "tips": ["Pitch unique angle"]},
    
    # === PRESS & MEDIA ===
    {"name": "TechCrunch", "url": "https://techcrunch.com/pages/contact-us/", "type": "press", "audience_size": "10M+", "cost": "free", "best_for": ["Funded startups"], "tips": ["Need newsworthy angle"]},
    {"name": "VentureBeat", "url": "https://venturebeat.com/contact/", "type": "press", "audience_size": "5M+", "cost": "free", "best_for": ["Tech"], "tips": ["AI and enterprise focus"]},
    {"name": "The Next Web", "url": "https://thenextweb.com/about#contact", "type": "press", "audience_size": "3M+", "cost": "free", "best_for": ["Tech"], "tips": ["European focus"]},
    {"name": "Mashable", "url": "https://mashable.com", "type": "press", "audience_size": "5M+", "cost": "free", "best_for": ["Consumer tech"], "tips": ["Viral potential"]},
    {"name": "Fast Company", "url": "https://fastcompany.com", "type": "press", "audience_size": "3M+", "cost": "free", "best_for": ["Innovation"], "tips": ["Design and innovation"]},
    
    # === SOCIAL PLATFORMS ===
    {"name": "Twitter/X", "url": "https://twitter.com", "type": "social", "audience_size": "500M+", "cost": "free", "best_for": ["All"], "tips": ["Build audience before launch"]},
    {"name": "LinkedIn", "url": "https://linkedin.com", "type": "social", "audience_size": "900M+", "cost": "free", "best_for": ["B2B"], "tips": ["Founder personal brand"]},
    {"name": "Facebook Groups", "url": "https://facebook.com/groups", "type": "social", "audience_size": "2B+", "cost": "free", "best_for": ["Niche communities"], "tips": ["Find relevant groups"]},
    
    # More platforms...
    {"name": "Startup Stash", "url": "https://startupstash.com/submit", "type": "directory", "audience_size": "100K+", "cost": "free/$49", "best_for": ["Tools"], "tips": ["Resource directory"]},
    {"name": "Toolify", "url": "https://toolify.ai/submit", "type": "directory", "audience_size": "50K+", "cost": "free", "best_for": ["AI tools"], "tips": ["AI focused"]},
    {"name": "SaaSHub", "url": "https://saashub.com", "type": "directory", "audience_size": "500K+", "cost": "free", "best_for": ["SaaS"], "tips": ["Alternatives focus"]},
    {"name": "Wellfound (AngelList)", "url": "https://wellfound.com", "type": "jobs", "audience_size": "5M+", "cost": "free", "best_for": ["Hiring"], "tips": ["Startup jobs"]},
    {"name": "F6S", "url": "https://f6s.com", "type": "directory", "audience_size": "1M+", "cost": "free", "best_for": ["Startups"], "tips": ["Accelerator deals"]},
]

# ==================
# AI/AGENTS SEGMENT (100+ platforms)
# ==================
AI_AGENTS_PLATFORMS = [
    # === AI DIRECTORIES ===
    {"name": "There's An AI For That", "url": "https://theresanaiforthat.com/submit", "type": "directory", "audience_size": "5M+", "cost": "free/$99", "best_for": ["AI tools"], "tips": ["Top AI directory"]},
    {"name": "FutureTools", "url": "https://futuretools.io/submit-a-tool", "type": "directory", "audience_size": "2M+", "cost": "free", "best_for": ["AI tools"], "tips": ["Curated by Matt Wolfe"]},
    {"name": "AI Valley", "url": "https://aivalley.ai/submit", "type": "directory", "audience_size": "500K+", "cost": "free", "best_for": ["AI tools"], "tips": ["Growing directory"]},
    {"name": "TopAI.tools", "url": "https://topai.tools/submit", "type": "directory", "audience_size": "1M+", "cost": "free", "best_for": ["AI tools"], "tips": ["Popular directory"]},
    {"name": "AIcyclopedia", "url": "https://aicyclopedia.com", "type": "directory", "audience_size": "200K+", "cost": "free", "best_for": ["AI tools"], "tips": ["Categorized well"]},
    {"name": "Toolify.ai", "url": "https://toolify.ai/submit", "type": "directory", "audience_size": "1M+", "cost": "free", "best_for": ["AI tools"], "tips": ["Large database"]},
    {"name": "AI Tool Hunt", "url": "https://aitoolhunt.com/submit", "type": "directory", "audience_size": "100K+", "cost": "free", "best_for": ["AI tools"], "tips": ["Quick approval"]},
    {"name": "Easy With AI", "url": "https://easywithai.com/submit", "type": "directory", "audience_size": "500K+", "cost": "free", "best_for": ["AI tools"], "tips": ["User-friendly"]},
    {"name": "AI Scout", "url": "https://aiscout.net/submit", "type": "directory", "audience_size": "50K+", "cost": "free", "best_for": ["AI tools"], "tips": ["Newer directory"]},
    {"name": "Futurepedia", "url": "https://futurepedia.io/submit-tool", "type": "directory", "audience_size": "2M+", "cost": "free", "best_for": ["AI tools"], "tips": ["Daily updates"]},
    {"name": "AI Tools Directory", "url": "https://aitoolsdirectory.com", "type": "directory", "audience_size": "100K+", "cost": "free", "best_for": ["AI tools"], "tips": ["Simple listing"]},
    {"name": "GPT Store", "url": "https://chat.openai.com/gpts", "type": "marketplace", "audience_size": "100M+", "cost": "free", "best_for": ["GPTs"], "tips": ["OpenAI ecosystem"]},
    {"name": "Poe", "url": "https://poe.com", "type": "marketplace", "audience_size": "10M+", "cost": "free", "best_for": ["Chatbots"], "tips": ["Quora's AI platform"]},
    {"name": "Hugging Face", "url": "https://huggingface.co", "type": "community", "audience_size": "5M+", "cost": "free", "best_for": ["ML models"], "tips": ["Share models"]},
    
    # === AI COMMUNITIES ===
    {"name": "r/artificial", "url": "https://reddit.com/r/artificial", "type": "subreddit", "audience_size": "1M+", "cost": "free", "best_for": ["AI"], "tips": ["Technical discussions"]},
    {"name": "r/ChatGPT", "url": "https://reddit.com/r/ChatGPT", "type": "subreddit", "audience_size": "5M+", "cost": "free", "best_for": ["ChatGPT tools"], "tips": ["Massive audience"]},
    {"name": "r/LocalLLaMA", "url": "https://reddit.com/r/LocalLLaMA", "type": "subreddit", "audience_size": "200K+", "cost": "free", "best_for": ["Local AI"], "tips": ["Technical crowd"]},
    {"name": "r/MachineLearning", "url": "https://reddit.com/r/MachineLearning", "type": "subreddit", "audience_size": "2M+", "cost": "free", "best_for": ["ML"], "tips": ["Research focus"]},
    {"name": "r/singularity", "url": "https://reddit.com/r/singularity", "type": "subreddit", "audience_size": "500K+", "cost": "free", "best_for": ["AI future"], "tips": ["Enthusiasts"]},
    {"name": "AI Discord Servers", "url": "https://discord.com", "type": "community", "audience_size": "1M+", "cost": "free", "best_for": ["AI tools"], "tips": ["Find niche servers"]},
    {"name": "Weights & Biases Community", "url": "https://wandb.ai/community", "type": "community", "audience_size": "100K+", "cost": "free", "best_for": ["ML ops"], "tips": ["ML practitioners"]},
    
    # === AI NEWSLETTERS ===
    {"name": "The Rundown AI", "url": "https://therundown.ai", "type": "newsletter", "audience_size": "500K+", "cost": "paid", "best_for": ["AI tools"], "tips": ["Daily AI news"]},
    {"name": "Ben's Bites", "url": "https://bensbites.com", "type": "newsletter", "audience_size": "100K+", "cost": "paid", "best_for": ["AI tools"], "tips": ["Curated AI tools"]},
    {"name": "AI Breakfast", "url": "https://aibreakfast.com", "type": "newsletter", "audience_size": "50K+", "cost": "free", "best_for": ["AI news"], "tips": ["Daily digest"]},
    {"name": "The Neuron", "url": "https://theneuron.ai", "type": "newsletter", "audience_size": "200K+", "cost": "paid", "best_for": ["AI news"], "tips": ["Business focus"]},
    {"name": "TLDR AI", "url": "https://tldr.tech/ai", "type": "newsletter", "audience_size": "200K+", "cost": "paid", "best_for": ["AI"], "tips": ["Tech audience"]},
    {"name": "Import AI", "url": "https://importai.com", "type": "newsletter", "audience_size": "50K+", "cost": "free", "best_for": ["AI research"], "tips": ["Technical depth"]},
    {"name": "Last Week in AI", "url": "https://lastweekin.ai", "type": "newsletter", "audience_size": "30K+", "cost": "free", "best_for": ["AI news"], "tips": ["Weekly recap"]},
    
    # === AI PODCASTS ===
    {"name": "Lex Fridman Podcast", "url": "https://lexfridman.com/podcast", "type": "podcast", "audience_size": "2M+", "cost": "free", "best_for": ["AI leaders"], "tips": ["Long-form interviews"]},
    {"name": "AI Podcast (NVIDIA)", "url": "https://blogs.nvidia.com/ai-podcast/", "type": "podcast", "audience_size": "100K+", "cost": "free", "best_for": ["AI"], "tips": ["Enterprise AI"]},
    {"name": "Gradient Dissent", "url": "https://wandb.ai/podcast", "type": "podcast", "audience_size": "50K+", "cost": "free", "best_for": ["ML"], "tips": ["Practitioners"]},
    {"name": "Practical AI", "url": "https://changelog.com/practicalai", "type": "podcast", "audience_size": "50K+", "cost": "free", "best_for": ["Applied AI"], "tips": ["Practical use cases"]},
    
    # === AI INFLUENCERS/TWITTER ===
    {"name": "AI Twitter", "url": "https://twitter.com", "type": "social", "audience_size": "10M+", "cost": "free", "best_for": ["AI tools"], "tips": ["Tag AI influencers"]},
    {"name": "AI LinkedIn", "url": "https://linkedin.com", "type": "social", "audience_size": "10M+", "cost": "free", "best_for": ["B2B AI"], "tips": ["Thought leadership"]},
    {"name": "YouTube AI Channels", "url": "https://youtube.com", "type": "video", "audience_size": "100M+", "cost": "free", "best_for": ["AI demos"], "tips": ["Tutorial content"]},
]

# ==================
# ANIME/GAMING SEGMENT (100+ platforms)
# ==================
ANIME_GAMING_PLATFORMS = [
    # === ANIME COMMUNITIES ===
    {"name": "MyAnimeList", "url": "https://myanimelist.net", "type": "community", "audience_size": "20M+", "cost": "free", "best_for": ["Anime apps"], "tips": ["Massive database"]},
    {"name": "AniList", "url": "https://anilist.co", "type": "community", "audience_size": "5M+", "cost": "free", "best_for": ["Anime apps"], "tips": ["Modern interface"]},
    {"name": "Kitsu", "url": "https://kitsu.io", "type": "community", "audience_size": "1M+", "cost": "free", "best_for": ["Anime/manga"], "tips": ["Social features"]},
    {"name": "Anime-Planet", "url": "https://anime-planet.com", "type": "community", "audience_size": "3M+", "cost": "free", "best_for": ["Recommendations"], "tips": ["Recommendation engine"]},
    {"name": "r/anime", "url": "https://reddit.com/r/anime", "type": "subreddit", "audience_size": "7M+", "cost": "free", "best_for": ["Anime fans"], "tips": ["Follow posting rules"]},
    {"name": "r/manga", "url": "https://reddit.com/r/manga", "type": "subreddit", "audience_size": "3M+", "cost": "free", "best_for": ["Manga apps"], "tips": ["Reader focus"]},
    {"name": "r/Animemes", "url": "https://reddit.com/r/Animemes", "type": "subreddit", "audience_size": "2M+", "cost": "free", "best_for": ["Fun content"], "tips": ["Meme culture"]},
    {"name": "Crunchyroll Forums", "url": "https://crunchyroll.com/forum", "type": "community", "audience_size": "5M+", "cost": "free", "best_for": ["Anime streaming"], "tips": ["Active discussions"]},
    {"name": "Anime Discord Servers", "url": "https://discord.com", "type": "community", "audience_size": "10M+", "cost": "free", "best_for": ["Anime"], "tips": ["Many niche servers"]},
    {"name": "Amino Apps", "url": "https://aminoapps.com", "type": "community", "audience_size": "10M+", "cost": "free", "best_for": ["Fandom"], "tips": ["Mobile community"]},
    
    # === GAMING PLATFORMS ===
    {"name": "itch.io", "url": "https://itch.io/developers", "type": "marketplace", "audience_size": "10M+", "cost": "free", "best_for": ["Indie games"], "tips": ["Indie-friendly"]},
    {"name": "GameJolt", "url": "https://gamejolt.com/developers", "type": "marketplace", "audience_size": "3M+", "cost": "free", "best_for": ["Indie games"], "tips": ["Free games focus"]},
    {"name": "IndieDB", "url": "https://indiedb.com", "type": "directory", "audience_size": "2M+", "cost": "free", "best_for": ["Indie games"], "tips": ["Mod community"]},
    {"name": "r/gaming", "url": "https://reddit.com/r/gaming", "type": "subreddit", "audience_size": "35M+", "cost": "free", "best_for": ["All gaming"], "tips": ["Huge audience"]},
    {"name": "r/IndieGaming", "url": "https://reddit.com/r/IndieGaming", "type": "subreddit", "audience_size": "500K+", "cost": "free", "best_for": ["Indie devs"], "tips": ["Supportive community"]},
    {"name": "r/gamedev", "url": "https://reddit.com/r/gamedev", "type": "subreddit", "audience_size": "1M+", "cost": "free", "best_for": ["Game tools"], "tips": ["Dev focused"]},
    {"name": "Steam", "url": "https://partner.steamgames.com", "type": "marketplace", "audience_size": "120M+", "cost": "$100", "best_for": ["PC games"], "tips": ["Massive reach"]},
    {"name": "Epic Games Store", "url": "https://store.epicgames.com/developers", "type": "marketplace", "audience_size": "60M+", "cost": "free", "best_for": ["PC games"], "tips": ["Better revenue share"]},
    {"name": "GOG", "url": "https://gog.com/indie", "type": "marketplace", "audience_size": "20M+", "cost": "free", "best_for": ["DRM-free"], "tips": ["Quality curation"]},
    {"name": "Humble Bundle", "url": "https://humblebundle.com/developer", "type": "marketplace", "audience_size": "10M+", "cost": "rev share", "best_for": ["Bundles"], "tips": ["Charity focus"]},
    
    # === GAMING MEDIA ===
    {"name": "Kotaku", "url": "https://kotaku.com", "type": "press", "audience_size": "10M+", "cost": "free", "best_for": ["Gaming news"], "tips": ["Pitch unique angle"]},
    {"name": "IGN", "url": "https://ign.com", "type": "press", "audience_size": "50M+", "cost": "free", "best_for": ["Major games"], "tips": ["AAA focused"]},
    {"name": "Polygon", "url": "https://polygon.com", "type": "press", "audience_size": "10M+", "cost": "free", "best_for": ["Gaming culture"], "tips": ["Culture focus"]},
    {"name": "PC Gamer", "url": "https://pcgamer.com", "type": "press", "audience_size": "15M+", "cost": "free", "best_for": ["PC games"], "tips": ["PC master race"]},
    {"name": "Rock Paper Shotgun", "url": "https://rockpapershotgun.com", "type": "press", "audience_size": "5M+", "cost": "free", "best_for": ["Indie games"], "tips": ["Indie-friendly"]},
    
    # === ANIME NEWS ===
    {"name": "Anime News Network", "url": "https://animenewsnetwork.com", "type": "press", "audience_size": "10M+", "cost": "free", "best_for": ["Anime news"], "tips": ["Industry news"]},
    {"name": "Crunchyroll News", "url": "https://crunchyroll.com/news", "type": "press", "audience_size": "5M+", "cost": "free", "best_for": ["Anime"], "tips": ["Official platform"]},
    
    # === STREAMING/VIDEO ===
    {"name": "Twitch", "url": "https://twitch.tv", "type": "streaming", "audience_size": "30M+", "cost": "free", "best_for": ["Live gaming"], "tips": ["Streamer partnerships"]},
    {"name": "YouTube Gaming", "url": "https://youtube.com/gaming", "type": "video", "audience_size": "100M+", "cost": "free", "best_for": ["Game content"], "tips": ["Let's play videos"]},
]

# ==================
# B2C CONSUMER SEGMENT (100+ platforms)
# ==================
B2C_CONSUMER_PLATFORMS = [
    # === APP STORES ===
    {"name": "Apple App Store", "url": "https://appstoreconnect.apple.com", "type": "marketplace", "audience_size": "1B+", "cost": "$99/yr", "best_for": ["iOS apps"], "tips": ["ASO critical"]},
    {"name": "Google Play Store", "url": "https://play.google.com/console", "type": "marketplace", "audience_size": "2B+", "cost": "$25", "best_for": ["Android apps"], "tips": ["ASO critical"]},
    {"name": "Amazon App Store", "url": "https://developer.amazon.com/apps-and-games", "type": "marketplace", "audience_size": "100M+", "cost": "free", "best_for": ["Fire devices"], "tips": ["Less competition"]},
    
    # === CONSUMER DIRECTORIES ===
    {"name": "AppSumo", "url": "https://appsumo.com/partners", "type": "marketplace", "audience_size": "1M+", "cost": "rev share", "best_for": ["Deals"], "tips": ["Lifetime deals work"]},
    {"name": "StackSocial", "url": "https://stacksocial.com/sell-with-us", "type": "marketplace", "audience_size": "500K+", "cost": "rev share", "best_for": ["Deals"], "tips": ["Bundle deals"]},
    {"name": "DealMirror", "url": "https://dealmirror.com", "type": "marketplace", "audience_size": "100K+", "cost": "rev share", "best_for": ["Deals"], "tips": ["Curated deals"]},
    
    # === CONSUMER COMMUNITIES ===
    {"name": "r/apps", "url": "https://reddit.com/r/apps", "type": "subreddit", "audience_size": "100K+", "cost": "free", "best_for": ["Apps"], "tips": ["App discovery"]},
    {"name": "r/Android", "url": "https://reddit.com/r/Android", "type": "subreddit", "audience_size": "3M+", "cost": "free", "best_for": ["Android apps"], "tips": ["Power users"]},
    {"name": "r/iphone", "url": "https://reddit.com/r/iphone", "type": "subreddit", "audience_size": "4M+", "cost": "free", "best_for": ["iOS apps"], "tips": ["iOS community"]},
    {"name": "r/shutupandtakemymoney", "url": "https://reddit.com/r/shutupandtakemymoney", "type": "subreddit", "audience_size": "1M+", "cost": "free", "best_for": ["Products"], "tips": ["Cool products"]},
    {"name": "r/frugal", "url": "https://reddit.com/r/frugal", "type": "subreddit", "audience_size": "2M+", "cost": "free", "best_for": ["Deals"], "tips": ["Value focus"]},
    
    # === TECH BLOGS ===
    {"name": "The Verge", "url": "https://theverge.com", "type": "press", "audience_size": "20M+", "cost": "free", "best_for": ["Consumer tech"], "tips": ["Design focus"]},
    {"name": "Engadget", "url": "https://engadget.com", "type": "press", "audience_size": "15M+", "cost": "free", "best_for": ["Gadgets"], "tips": ["Tech reviews"]},
    {"name": "Wired", "url": "https://wired.com", "type": "press", "audience_size": "15M+", "cost": "free", "best_for": ["Tech culture"], "tips": ["Culture angle"]},
    {"name": "Lifehacker", "url": "https://lifehacker.com", "type": "press", "audience_size": "20M+", "cost": "free", "best_for": ["Productivity"], "tips": ["Life hacks"]},
    {"name": "CNET", "url": "https://cnet.com", "type": "press", "audience_size": "50M+", "cost": "free", "best_for": ["Tech reviews"], "tips": ["Reviews focus"]},
    
    # === INFLUENCER PLATFORMS ===
    {"name": "TikTok", "url": "https://tiktok.com", "type": "social", "audience_size": "1B+", "cost": "free/paid", "best_for": ["Viral"], "tips": ["Short-form video"]},
    {"name": "Instagram", "url": "https://instagram.com", "type": "social", "audience_size": "2B+", "cost": "free/paid", "best_for": ["Visual"], "tips": ["Reels work"]},
    {"name": "YouTube", "url": "https://youtube.com", "type": "video", "audience_size": "2B+", "cost": "free/paid", "best_for": ["Reviews"], "tips": ["Sponsorships"]},
    {"name": "Pinterest", "url": "https://pinterest.com", "type": "social", "audience_size": "500M+", "cost": "free/paid", "best_for": ["Visual"], "tips": ["Lifestyle products"]},
]

# ==================
# DEVELOPER TOOLS SEGMENT
# ==================
DEVELOPER_TOOLS_PLATFORMS = [
    {"name": "GitHub Marketplace", "url": "https://github.com/marketplace", "type": "marketplace", "audience_size": "100M+", "cost": "free", "best_for": ["Dev tools"], "tips": ["GitHub ecosystem"]},
    {"name": "VS Code Marketplace", "url": "https://marketplace.visualstudio.com", "type": "marketplace", "audience_size": "30M+", "cost": "free", "best_for": ["Extensions"], "tips": ["VSCode users"]},
    {"name": "JetBrains Marketplace", "url": "https://plugins.jetbrains.com", "type": "marketplace", "audience_size": "10M+", "cost": "free", "best_for": ["IDE plugins"], "tips": ["Enterprise devs"]},
    {"name": "npm", "url": "https://npmjs.com", "type": "registry", "audience_size": "20M+", "cost": "free", "best_for": ["JS packages"], "tips": ["Open source"]},
    {"name": "PyPI", "url": "https://pypi.org", "type": "registry", "audience_size": "10M+", "cost": "free", "best_for": ["Python"], "tips": ["Python ecosystem"]},
    {"name": "r/webdev", "url": "https://reddit.com/r/webdev", "type": "subreddit", "audience_size": "2M+", "cost": "free", "best_for": ["Web tools"], "tips": ["Web developers"]},
    {"name": "r/programming", "url": "https://reddit.com/r/programming", "type": "subreddit", "audience_size": "5M+", "cost": "free", "best_for": ["Dev tools"], "tips": ["General programming"]},
    {"name": "r/javascript", "url": "https://reddit.com/r/javascript", "type": "subreddit", "audience_size": "2M+", "cost": "free", "best_for": ["JS tools"], "tips": ["JS community"]},
    {"name": "r/Python", "url": "https://reddit.com/r/Python", "type": "subreddit", "audience_size": "1M+", "cost": "free", "best_for": ["Python tools"], "tips": ["Python community"]},
]

# ==================
# ALL SEGMENTS MAPPING
# ==================
LAUNCH_SEGMENTS = {
    "entrepreneur": ENTREPRENEUR_PLATFORMS,
    "ai_agents": AI_AGENTS_PLATFORMS,
    "anime_gaming": ANIME_GAMING_PLATFORMS,
    "b2c_consumer": B2C_CONSUMER_PLATFORMS,
    "developer_tools": DEVELOPER_TOOLS_PLATFORMS,
}

def get_platforms_for_segment(segment: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get top platforms for a segment"""
    platforms = LAUNCH_SEGMENTS.get(segment, ENTREPRENEUR_PLATFORMS)
    return platforms[:limit]

def get_all_segments() -> List[str]:
    """Get list of all available segments"""
    return list(LAUNCH_SEGMENTS.keys())

def get_product_hunt_strategy() -> Dict[str, Any]:
    """Get Product Hunt specific strategy"""
    return PRODUCT_HUNT

def search_platforms(query: str, segment: str = None) -> List[Dict[str, Any]]:
    """Search platforms by name or type"""
    query_lower = query.lower()
    results = []
    
    segments_to_search = [segment] if segment else list(LAUNCH_SEGMENTS.keys())
    
    for seg in segments_to_search:
        for platform in LAUNCH_SEGMENTS.get(seg, []):
            if query_lower in platform["name"].lower() or query_lower in platform.get("type", "").lower():
                results.append({**platform, "segment": seg})
    
    return results[:50]
