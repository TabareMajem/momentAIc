    async def check_spam_score(self, email_content: str) -> Dict[str, Any]:
        """
        Analyze email content for spam triggers.
        """
        if not self.llm:
            return {"score": 0, "analysis": "AI Unavailable"}
            
        prompt = f"""Analyze this email for spam triggers.

EMAIL:
{email_content}

Rate from 0-10 (0=Clean, 10=Spam) based on:
- Trigger words (free, urgent, $$$)
- Formatting (ALL CAPS, excessive !!!)
- Domain reputation risks
- Authentication risks (implied)

Return JSON:
{{
    "score": <int>,
    "risk_level": "Low"|"Medium"|"High",
    "triggers": ["list", "of", "issues"],
    "suggestions": ["how", "to", "fix"]
}}"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            # In production, use JSON output parser
            return {"score": 0, "analysis": response.content} # Placeholder parsing
        except Exception:
            return {"score": 0, "error": "Check failed"}
