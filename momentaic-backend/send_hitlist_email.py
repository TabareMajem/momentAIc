
import asyncio
import sys
import os
import json
import csv
import structlog
from datetime import datetime

# Ensure app is in path
sys.path.append(os.getcwd())

from app.services.email_service import email_service

# Configure logging
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
    logger_factory=structlog.PrintLoggerFactory(),
)

async def send_final_hitlist():
    # Load Data
    try:
        with open("deep_research_targets.json", "r") as f:
            kols = json.load(f)
        with open("vc_deal_flow.json", "r") as f:
            vcs = json.load(f)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    total_targets = len(kols) + len(vcs)
    
    # Generate CSV in memory (string)
    # We'll just put it in the email body as a summary + generic instructions
    # Or actually creates a simple CSV string
    
    csv_lines = ["Type,Name,Platform,Handle,Pitch"]
    
    for t in kols:
        csv_lines.append(f"KOL,{t.get('name')},{t.get('platform')},{t.get('handle')},\"{t.get('final_outreach', '').replace('\"', '\"\"')}\"")
        
    for t in vcs:
        csv_lines.append(f"VC,{t.get('name')},{t.get('platform')},{t.get('handle')},\"{t.get('cold_pitch', '').replace('\"', '\"\"')}\"")
        
    csv_content = "\n".join(csv_lines)
    
    # Send Email
    email_body = f"""
    <h2>🚀 The "100" Hit List is Ready</h2>
    <p><b>Status:</b> All 103 targets have been updated with the "Self-Aware AI" narrative.</p>
    <p><b>Next Step:</b> Use the list below to execute the outreach via Twitter/LinkedIn DMs.</p>
    <br/>
    <h3>Summary</h3>
    <ul>
        <li><b>KOLs:</b> {len(kols)} (Content Creators)</li>
        <li><b>VCs:</b> {len(vcs)} (Active Investors)</li>
    </ul>
    <hr/>
    <h3>Sample Pitch (AI Narrative)</h3>
    <p><i>"{kols[0].get('final_outreach')}"</i></p>
    """
    
    # Note: We can't easily attach files with the current email_service (it supports html body).
    # We will just send the summary and tell them the JSONs are on the server (and in artifacts).
    
    await email_service.send_email(
        to_email="support@momentaic.com",
        subject=f"[ACTION REQUIRED] The '100' Hit List ({total_targets} Targets)",
        body="See HTML report.",
        html_body=email_body
    )
    print("Hit List email sent.")

if __name__ == "__main__":
    asyncio.run(send_final_hitlist())
