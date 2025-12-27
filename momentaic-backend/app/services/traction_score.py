"""
Founder Traction Score Engine
Performance-based ranking system - the Anti-YC pedigree approach
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import structlog

logger = structlog.get_logger()


class TractionMetric(str, Enum):
    """Core traction metrics"""
    MRR = "mrr"
    ARR = "arr"
    MRR_GROWTH = "mrr_growth"
    USERS = "users"
    DAU = "dau"
    WAU = "wau"
    MAU = "mau"
    RETENTION_D1 = "retention_d1"
    RETENTION_D7 = "retention_d7"
    RETENTION_D30 = "retention_d30"
    NPS = "nps"
    CHURN_RATE = "churn_rate"
    CAC = "cac"
    LTV = "ltv"
    BURN_RATE = "burn_rate"
    RUNWAY_MONTHS = "runway_months"
    TEAM_SIZE = "team_size"
    GITHUB_COMMITS = "github_commits"
    SOCIAL_FOLLOWERS = "social_followers"
    WAITLIST = "waitlist"


@dataclass
class TractionScore:
    """Calculated traction score with breakdown"""
    overall_score: float  # 0-100
    velocity_score: float  # Growth speed
    product_score: float  # Engagement/retention
    revenue_score: float  # Revenue metrics
    momentum_score: float  # Week-over-week change
    percentile: float  # Compared to other startups
    tier: str  # "rising", "scaling", "rocket"
    breakdown: Dict[str, float]
    verified: bool
    last_updated: datetime


class TractionScoreEngine:
    """
    Calculate and rank startups by real performance
    
    NO pedigree, NO school names, NO who you know.
    Pure METRICS. Show, don't tell.
    """
    
    # Weights for score calculation
    SCORE_WEIGHTS = {
        "revenue": 0.35,      # Revenue metrics
        "growth": 0.25,       # Growth velocity
        "engagement": 0.20,   # User engagement
        "momentum": 0.20,     # Recent trajectory
    }
    
    # Tier thresholds
    TIERS = {
        "rocket": 80,      # Top tier, investor ready
        "scaling": 60,     # Strong growth
        "rising": 40,      # Early traction
        "building": 20,    # Pre-traction
        "ideation": 0,     # Idea stage
    }
    
    def __init__(self):
        self._benchmarks = self._load_benchmarks()
    
    def calculate_score(
        self,
        metrics: Dict[str, Any],
        startup_id: str = None
    ) -> TractionScore:
        """
        Calculate comprehensive traction score
        
        Args:
            metrics: Dict of metric values from integrations
            startup_id: Optional startup ID for comparison
        
        Returns:
            TractionScore with full breakdown
        """
        breakdown = {}
        
        # 1. Revenue Score (35%)
        revenue_score = self._calculate_revenue_score(metrics)
        breakdown["revenue"] = revenue_score
        
        # 2. Growth Velocity Score (25%)
        growth_score = self._calculate_growth_score(metrics)
        breakdown["growth"] = growth_score
        
        # 3. Engagement Score (20%)
        engagement_score = self._calculate_engagement_score(metrics)
        breakdown["engagement"] = engagement_score
        
        # 4. Momentum Score (20%)
        momentum_score = self._calculate_momentum_score(metrics)
        breakdown["momentum"] = momentum_score
        
        # Calculate weighted overall score
        overall = (
            revenue_score * self.SCORE_WEIGHTS["revenue"] +
            growth_score * self.SCORE_WEIGHTS["growth"] +
            engagement_score * self.SCORE_WEIGHTS["engagement"] +
            momentum_score * self.SCORE_WEIGHTS["momentum"]
        )
        
        # Determine tier
        tier = self._get_tier(overall)
        
        # Calculate percentile (would compare against DB in production)
        percentile = min(99, overall + 10)  # Simplified
        
        return TractionScore(
            overall_score=round(overall, 1),
            velocity_score=round(growth_score, 1),
            product_score=round(engagement_score, 1),
            revenue_score=round(revenue_score, 1),
            momentum_score=round(momentum_score, 1),
            percentile=round(percentile, 1),
            tier=tier,
            breakdown=breakdown,
            verified=self._is_verified(metrics),
            last_updated=datetime.utcnow()
        )
    
    def _calculate_revenue_score(self, metrics: Dict) -> float:
        """Score based on revenue metrics"""
        score = 0
        
        # MRR scoring (up to 40 points)
        mrr = metrics.get("mrr", 0)
        if mrr > 100000:
            score += 40
        elif mrr > 50000:
            score += 35
        elif mrr > 10000:
            score += 30
        elif mrr > 5000:
            score += 25
        elif mrr > 1000:
            score += 20
        elif mrr > 0:
            score += 10
        
        # MRR Growth scoring (up to 30 points)
        mrr_growth = metrics.get("mrr_growth", 0)
        if mrr_growth > 30:  # >30% MoM
            score += 30
        elif mrr_growth > 20:
            score += 25
        elif mrr_growth > 10:
            score += 20
        elif mrr_growth > 5:
            score += 15
        elif mrr_growth > 0:
            score += 10
        
        # LTV/CAC ratio (up to 30 points)
        ltv = metrics.get("ltv", 0)
        cac = metrics.get("cac", 1)
        ratio = ltv / cac if cac > 0 else 0
        if ratio > 5:
            score += 30
        elif ratio > 3:
            score += 25
        elif ratio > 2:
            score += 20
        elif ratio > 1:
            score += 15
        
        return min(100, score)
    
    def _calculate_growth_score(self, metrics: Dict) -> float:
        """Score based on growth velocity"""
        score = 0
        
        # User growth (up to 40 points)
        user_growth = metrics.get("user_growth", 0)
        if user_growth > 50:
            score += 40
        elif user_growth > 30:
            score += 35
        elif user_growth > 20:
            score += 30
        elif user_growth > 10:
            score += 25
        elif user_growth > 0:
            score += 15
        
        # Waitlist size (up to 30 points)
        waitlist = metrics.get("waitlist", 0)
        if waitlist > 10000:
            score += 30
        elif waitlist > 5000:
            score += 25
        elif waitlist > 1000:
            score += 20
        elif waitlist > 100:
            score += 15
        
        # Social followers growth (up to 30 points)
        social_growth = metrics.get("social_growth", 0)
        if social_growth > 100:
            score += 30
        elif social_growth > 50:
            score += 25
        elif social_growth > 20:
            score += 20
        elif social_growth > 0:
            score += 10
        
        return min(100, score)
    
    def _calculate_engagement_score(self, metrics: Dict) -> float:
        """Score based on product engagement"""
        score = 0
        
        # DAU/MAU ratio (up to 40 points)
        dau = metrics.get("dau", 0)
        mau = metrics.get("mau", 1)
        dau_mau_ratio = (dau / mau * 100) if mau > 0 else 0
        if dau_mau_ratio > 40:
            score += 40
        elif dau_mau_ratio > 25:
            score += 35
        elif dau_mau_ratio > 15:
            score += 25
        elif dau_mau_ratio > 10:
            score += 20
        elif dau_mau_ratio > 0:
            score += 10
        
        # D30 Retention (up to 40 points)
        retention_d30 = metrics.get("retention_d30", 0)
        if retention_d30 > 30:
            score += 40
        elif retention_d30 > 20:
            score += 35
        elif retention_d30 > 15:
            score += 30
        elif retention_d30 > 10:
            score += 25
        elif retention_d30 > 0:
            score += 15
        
        # NPS (up to 20 points)
        nps = metrics.get("nps", 0)
        if nps > 50:
            score += 20
        elif nps > 30:
            score += 15
        elif nps > 0:
            score += 10
        
        return min(100, score)
    
    def _calculate_momentum_score(self, metrics: Dict) -> float:
        """Score based on week-over-week momentum"""
        score = 0
        
        # Calculate average WoW improvement
        wow_metrics = [
            metrics.get("mrr_wow", 0),
            metrics.get("users_wow", 0),
            metrics.get("engagement_wow", 0),
        ]
        
        avg_wow = sum(wow_metrics) / len(wow_metrics) if wow_metrics else 0
        
        if avg_wow > 20:
            score = 100
        elif avg_wow > 15:
            score = 85
        elif avg_wow > 10:
            score = 70
        elif avg_wow > 5:
            score = 55
        elif avg_wow > 0:
            score = 40
        elif avg_wow == 0:
            score = 30
        else:
            score = max(0, 30 + avg_wow * 2)  # Negative momentum
        
        return score
    
    def _get_tier(self, score: float) -> str:
        """Get tier based on score"""
        for tier, threshold in self.TIERS.items():
            if score >= threshold:
                return tier
        return "ideation"
    
    def _is_verified(self, metrics: Dict) -> bool:
        """Check if metrics are from verified integrations"""
        return metrics.get("_source") == "integration" or metrics.get("_verified", False)
    
    def _load_benchmarks(self) -> Dict:
        """Load benchmark data for comparison"""
        return {
            "mrr_p50": 5000,
            "mrr_p90": 50000,
            "growth_p50": 10,
            "growth_p90": 30,
        }
    
    async def generate_investor_memo(
        self,
        score: TractionScore,
        startup_data: Dict[str, Any]
    ) -> str:
        """
        Generate Hood Investment Memo
        
        AI-powered VC-quality memos for the 100,000 founders building billion-dollar companies.
        Uses Gemini 2.0 to create institutional-grade deal memos.
        The Hood = where real builders come from.
        """
        from app.services.gemini_service import get_gemini_service
        
        gemini = get_gemini_service()
        
        prompt = f"""
        Act as a Partner at a Tier-1 Venture Capital Firm (like Sequoia or a16z).
        Write an internal Investment Memo for the following startup based ONLY on their verified metrics.
        
        ## Startup Profile
        Name: {startup_data.get('name', 'Unknown')}
        Tagline: {startup_data.get('tagline', 'N/A')}
        Category: {startup_data.get('category', 'Tech')}
        
        ## Verified Traction Data
        - Overall Traction Score: {score.overall_score}/100 (Tier: {score.tier.upper()})
        - Revenue Score: {score.revenue_score}/100
        - Growth Score: {score.velocity_score}/100
        - Engagement Score: {score.product_score}/100
        
        ## Key Metrics
        - MRR: ${startup_data.get('mrr', 0):,}
        - MRR Growth (MoM): {startup_data.get('mrr_growth', 0)}%
        - Total Users: {startup_data.get('users', 0):,}
        - DAU/MAU Ratio: {startup_data.get('dau_mau_ratio', 0)}%
        - Retention (D30): {startup_data.get('retention_d30', 0)}%
        - Burn Rate: ${startup_data.get('burn_rate', 0):,}/mo
        
        ## Instructions
        Write a concise, rigorous 1-page memo in Markdown format.
        Structure:
        1. **Executive Summary**: One-paragraph hook.
        2. **The Numbers**: Analyze the metrics. Are they top-tier? Any red flags?
        3. **Bull Case**: Why this could be a billion-dollar company (Unfair advantage).
        4. **Bear Case**: Key risks and why it might fail (Analysis of churn, burn, or slow growth).
        5. **Market Context**: Brief implied market fit based on category.
        6. **Verdict**: {self._get_verdict_label(score.overall_score)}
        
        Tone: Professional, objective, data-driven. No fluff.
        """
        
        try:
            response = await gemini.generate(prompt)
            return response.text
        except Exception as e:
            logger.error("Failed to generate AI memo", error=str(e))
            return self._generate_fallback_memo(score, startup_data)

    def _get_verdict_label(self, score: float) -> str:
        if score >= 80: return "STRONG BUY (Series A Ready)"
        if score >= 60: return "INVEST (Seed/Growth Ready)"
        if score >= 40: return "WATCH (Promising Early Signs)"
        return "PASS (Too Early / Insufficient Traction)"

    def _generate_fallback_memo(self, score: TractionScore, startup_data: Dict) -> str:
        """Fallback static memo if AI fails"""
        return f"""
# Investment Memo: {startup_data.get('name')} (Fallback)

## Traction Score: {score.overall_score}/100 ({score.tier.upper()})

### Key Metrics
- MRR: ${startup_data.get('mrr', 0):,}
- Growth: {startup_data.get('mrr_growth', 0)}%

*AI generation unavailable. Showing raw data.*
"""


# Singleton
_engine: Optional[TractionScoreEngine] = None


def get_traction_engine() -> TractionScoreEngine:
    """Get the traction score engine"""
    global _engine
    if _engine is None:
        _engine = TractionScoreEngine()
    return _engine
