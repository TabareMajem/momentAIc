import structlog
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

logger = structlog.get_logger()

class DomainWarmUpScheduler:
    """
    Algorithmic Domain Warm-Up Engine
    Designed to protect sender reputation when launching new domains for outreach.
    
    Phases:
    1. Dormant (0-7 days): No sends.
    2. Warm-up (8-30 days): Strict daily limits, scaling algorithmically.
    3. Production: Full volume based on domain health.
    """
    
    def __init__(self, data_file: str = "domain_stats.json"):
        # For this prototype, we store stats in a local file.
        # In a fully productionized system, this binds to PostgreSQL or Redis.
        self.data_dir = Path("/root/momentaic/momentaic-backend/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / data_file
        
        # Core algorithmic constraints
        self.BASE_WARMUP_LIMIT = 10  # Start at 10 emails/day
        self.SCALE_FACTOR = 1.25     # 25% increase per progression step

    def _load_stats(self) -> Dict[str, Any]:
        if not self.data_file.exists():
            return {}
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error("failed_to_load_warmup_stats", error=str(e))
            return {}
            
    def _save_stats(self, stats: Dict[str, Any]) -> None:
        try:
            with open(self.data_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            logger.error("failed_to_save_warmup_stats", error=str(e))

    def register_domain(self, domain: str) -> None:
        """Initializes a new domain for warm-up tracking"""
        stats = self._load_stats()
        if domain not in stats:
            stats[domain] = {
                "registered_at": datetime.utcnow().isoformat(),
                "status": "dormant",
                "current_limit": 0,
                "history": {},
                "spam_score": 0.0,
                "bounces": 0
            }
            self._save_stats(stats)
            logger.info("domain_registered_for_warmup", domain=domain)
            
    def get_daily_allowance(self, domain: str) -> int:
        """
        Calculates how many emails can be sent TODAY securely.
        Implements the Algorithmic Pacing outlined in the Symbiotask Framework.
        """
        stats = self._load_stats()
        if domain not in stats:
            self.register_domain(domain)
            stats = self._load_stats()
            
        domain_data = stats[domain]
        reg_date = datetime.fromisoformat(domain_data["registered_at"]) - timedelta(days=8)
        days_active = (datetime.utcnow() - reg_date).days
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Emergency stop mechanism
        if domain_data.get("spam_score", 0) > 3.0 or domain_data.get("bounces", 0) > 5:
            logger.warning("domain_warmup_halted_due_to_poor_health", domain=domain)
            return 0
            
        # Algorithmic phases constraint
        calculated_limit = 0
        if days_active < 7:
            # The Initial Dormant Phase
            calculated_limit = 0
        else:
            # Controlled Micro-Volume Escalation
            progression_steps = days_active - 7
            calculated_limit = int(self.BASE_WARMUP_LIMIT * (self.SCALE_FACTOR ** (progression_steps // 3))) # Scale every 3 days
            
        # Retrieve how many sent today to calculate remainder
        sent_today = domain_data.get("history", {}).get(today, {}).get("sent", 0)
        allowance = max(0, calculated_limit - sent_today)
        
        # Override limit based on hard-saved 'current_limit' state if manual intervention occurred
        if domain_data.get("current_limit", 0) > 0 and domain_data.get("status") != "dormant":
             allowance = max(0, domain_data["current_limit"] - sent_today)

        logger.debug("warmup_allowance_calculated", 
                     domain=domain, 
                     days_active=days_active,
                     calculated_limit=calculated_limit, 
                     sent_today=sent_today, 
                     allowance=allowance)
                     
        return allowance

    def log_dispatch(self, domain: str, count: int = 1) -> bool:
        """
        Logs that emails were sent, deducting from the daily allowance.
        Returns True if successful, False if the limit was breached.
        """
        allowance = self.get_daily_allowance(domain)
        if count > allowance:
            logger.warning("warmup_throttle_breached", domain=domain, requested=count, allowed=allowance)
            return False
            
        stats = self._load_stats()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        if today not in stats[domain]["history"]:
            stats[domain]["history"][today] = {"sent": 0, "bounces": 0}
            
        stats[domain]["history"][today]["sent"] += count
        
        # Transition out of dormant status upon first send
        if stats[domain]["status"] == "dormant":
             stats[domain]["status"] = "warming_up"
             stats[domain]["current_limit"] = self.BASE_WARMUP_LIMIT
             
        self._save_stats(stats)
        logger.info("warmup_dispatch_logged", domain=domain, amount=count, total_today=stats[domain]["history"][today]["sent"])
        return True
        
    def report_bounce(self, domain: str) -> None:
        """Registers a bounce to penalize domain health"""
        stats = self._load_stats()
        if domain in stats:
             stats[domain]["bounces"] += 1
             today = datetime.utcnow().strftime("%Y-%m-%d")
             if today in stats[domain]["history"]:
                 stats[domain]["history"][today]["bounces"] = stats[domain]["history"][today].get("bounces", 0) + 1
             self._save_stats(stats)
             logger.warning("domain_bounce_recorded", domain=domain, total_bounces=stats[domain]["bounces"])

domain_warmup_service = DomainWarmUpScheduler()
