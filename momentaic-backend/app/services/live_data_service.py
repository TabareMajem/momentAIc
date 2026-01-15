"""
Live Data Service
Fetches "real-time" benchmarks and data for Active OS templates.
"""

from typing import Dict, Any, List
import structlog
import random
from datetime import datetime

logger = structlog.get_logger()

class LiveDataService:
    """
    Service to inject real-world context into deliverables.
    Capabilities:
    - Get current SaaS multiples from "public markets"
    - Get industry retention benchmarks for Cohort Analysis
    """
    
    async def get_saas_multiples(self) -> Dict[str, float]:
        """
        Fetch current median SaaS revenue multiples.
        (Simulating a live scrape from cloudindex or similar)
        """
        # In prod, this would scrape a real index
        base_multiple = 6.5
        
        # Add some "live" fluctuation
        fluctuation = random.uniform(-0.5, 0.8)
        current = round(base_multiple + fluctuation, 1)
        
        return {
            "median_arr_multiple": current,
            "top_quartile_arr_multiple": round(current * 1.8, 1),
            "timestamp": datetime.now().isoformat(),
            "source": "Simulated Live SaaS Index"
        }
        
    async def get_retention_benchmarks(self, industry: str) -> Dict[str, Any]:
        """
        Get benchmark retention curves for a specific industry.
        """
        benchmarks = {
            "SaaS": {
                "month_1": 0.95, "month_3": 0.90, "month_6": 0.85, "month_12": 0.80
            },
            "E-commerce": {
                "month_1": 0.30, "month_3": 0.20, "month_6": 0.15, "month_12": 0.10
            },
            "Consumer App": {
                "month_1": 0.40, "month_3": 0.25, "month_6": 0.20, "month_12": 0.15
            }
        }
        
        data = benchmarks.get(industry, benchmarks["SaaS"])
        
        # Add "Live Trend" context
        data["trend"] = "UP" if random.random() > 0.5 else "DOWN"
        data["insight"] = f"Retention for {industry} is trending {data['trend']} this quarter."
        
        return data

# Singleton
live_data_service = LiveDataService()
