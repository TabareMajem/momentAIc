"""
Stripe Integration
Revenue and subscription data from Stripe
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

from app.integrations.base import BaseIntegration, IntegrationCredentials, SyncResult
from app.core.config import settings

logger = structlog.get_logger()


class StripeIntegration(BaseIntegration):
    """
    Stripe integration for revenue metrics
    
    Data types:
    - mrr: Monthly Recurring Revenue
    - arr: Annual Recurring Revenue
    - customers: Customer count
    - subscriptions: Active subscriptions
    - charges: Recent charges
    """
    
    provider = "stripe"
    display_name = "Stripe"
    description = "Sync revenue, subscription, and customer data from Stripe"
    oauth_required = False  # Uses API key
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(credentials, config)
        self.api_key = credentials.api_key if credentials else settings.stripe_secret_key
        self.base_url = "https://api.stripe.com/v1"
    
    async def get_auth_url(self, redirect_uri: str, state: str) -> str:
        """Stripe uses Connect for OAuth, but we typically use API keys"""
        return f"https://dashboard.stripe.com/apikeys?state={state}"
    
    async def exchange_code(self, code: str, redirect_uri: str) -> IntegrationCredentials:
        """For Stripe, we just validate the API key"""
        return IntegrationCredentials(api_key=code)
    
    async def refresh_tokens(self) -> IntegrationCredentials:
        """API keys don't expire"""
        return self.credentials
    
    async def sync_data(self, data_types: List[str] = None) -> SyncResult:
        """Sync revenue and customer data from Stripe"""
        if not self.api_key:
            return SyncResult(success=False, errors=["No API key configured"])
        
        data_types = data_types or ["mrr", "customers", "subscriptions"]
        
        try:
            result_data = {}
            records = 0
            
            if "mrr" in data_types or "arr" in data_types:
                mrr = await self._calculate_mrr()
                result_data["mrr"] = mrr
                result_data["arr"] = mrr * 12
                records += 2
            
            if "customers" in data_types:
                customers = await self._get_customer_counts()
                result_data["customers"] = customers
                records += 1
            
            if "subscriptions" in data_types:
                subs = await self._get_subscription_stats()
                result_data["subscriptions"] = subs
                records += 1
            
            return SyncResult(
                success=True,
                records_synced=records,
                data=result_data
            )
        except Exception as e:
            logger.error("Stripe sync failed", error=str(e))
            return SyncResult(success=False, errors=[str(e)])
    
    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Stripe actions (limited - mainly for data retrieval)"""
        actions = {
            "get_balance": self._get_balance,
            "get_recent_charges": self._get_recent_charges,
            "list_invoices": self._list_invoices,
            "create_invoice": self._create_invoice,
            "retry_failed_payment": self._retry_failed_payment,
            "get_revenue_timeline": self._get_revenue_timeline,
        }
        
        if action not in actions:
            return {"error": f"Unknown action: {action}"}
        
        return await actions[action](params)
    
    async def _calculate_mrr(self) -> float:
        """Calculate MRR from active subscriptions"""
        try:
            mrr = 0.0
            has_more = True
            starting_after = None
            
            while has_more:
                params = {"status": "active", "limit": 100}
                if starting_after:
                    params["starting_after"] = starting_after
                    
                response = await self.http_client.get(
                    f"{self.base_url}/subscriptions",
                    params=params,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                
                if response.status_code != 200:
                    logger.warning("Stripe API call failed", status=response.status_code)
                    break
                
                data = response.json()
                subs = data.get("data", [])
                
                for sub in subs:
                    # Handle multi-item subscriptions
                    for item in sub.get("items", {}).get("data", []):
                        price = item.get("price", {})
                        amount = price.get("unit_amount", 0) / 100
                        interval = price.get("recurring", {}).get("interval", "month")
                        quantity = item.get("quantity", 1) or 1
                        
                        if interval == "year":
                            mrr += (amount * quantity) / 12
                        else:
                            mrr += amount * quantity
                
                has_more = data.get("has_more", False)
                if has_more and subs:
                    starting_after = subs[-1]["id"]
            
            return round(mrr, 2)
        except Exception as e:
            logger.error("MRR calculation failed", error=str(e))
            return 0.0
    
    async def _get_customer_counts(self) -> Dict[str, int]:
        """Get customer counts"""
        try:
            # Note: For exact counts on large datasets, Stripe suggests using exports or search
            # Here we iterate up to a reasonable limit for dashboard speed
            total = 0
            has_more = True
            starting_after = None
            
            while has_more and total < 1000: # Cap at 1000 for performance
                params = {"limit": 100}
                if starting_after:
                    params["starting_after"] = starting_after
                    
                response = await self.http_client.get(
                    f"{self.base_url}/customers",
                    params=params,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                batch = data.get("data", [])
                total += len(batch)
                
                has_more = data.get("has_more", False)
                if has_more and batch:
                    starting_after = batch[-1]["id"]
            
            # Simple "new this month" check using search API if available, or simplified logic
            # For now, just return total
            # Dynamic fetch for this month's customers
            thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())
            response_new = await self.http_client.get(
                f"{self.base_url}/customers",
                params={"created[gte]": thirty_days_ago, "limit": 100},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            new_this_month = 0
            if response_new.status_code == 200:
                new_this_month = len(response_new.json().get("data", []))
                
            return {
                "total": total, 
                "new_this_month": new_this_month
            }
        except Exception as e:
            logger.error("Customer counting failed", error=str(e))
            return {"total": 0, "new_this_month": 0}
    
    async def _get_subscription_stats(self) -> Dict[str, Any]:
        """Get real subscription statistics from Stripe"""
        try:
            stats = {"active": 0, "trialing": 0, "canceled_this_month": 0, "churn_rate": 0.0}
            
            for status in ["active", "trialing"]:
                response = await self.http_client.get(
                    f"{self.base_url}/subscriptions",
                    params={"status": status, "limit": 1},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                if response.status_code == 200:
                    data = response.json()
                    # Use total_count from Stripe's list if available, else count
                    stats[status] = data.get("total_count", len(data.get("data", [])))
            
            # Canceled in last 30 days
            thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())
            response = await self.http_client.get(
                f"{self.base_url}/subscriptions",
                params={
                    "status": "canceled",
                    "created[gte]": thirty_days_ago,
                    "limit": 100,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            if response.status_code == 200:
                canceled = response.json().get("data", [])
                stats["canceled_this_month"] = len(canceled)
            
            # Calculate churn rate
            total_subs = stats["active"] + stats["canceled_this_month"]
            if total_subs > 0:
                stats["churn_rate"] = round((stats["canceled_this_month"] / total_subs) * 100, 1)
            
            return stats
        except Exception as e:
            logger.error("Subscription stats failed", error=str(e))
            return {"active": 0, "trialing": 0, "canceled_this_month": 0, "churn_rate": 0.0}
    
    async def _get_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Stripe balance"""
        try:
            response = await self.http_client.get(
                f"{self.base_url}/balance",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            
            if response.status_code != 200:
                return {"error": "Failed to get balance"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_recent_charges(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent charges"""
        limit = params.get("limit", 10)
        try:
            response = await self.http_client.get(
                f"{self.base_url}/charges",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            
            if response.status_code != 200:
                return {"error": "Failed to get charges"}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # NEW: Invoice Management & Revenue Intelligence
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _list_invoices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        List invoices with optional filtering.
        Params: status (draft|open|paid|uncollectible|void), limit, customer
        """
        try:
            query = {"limit": params.get("limit", 25)}
            if params.get("status"):
                query["status"] = params["status"]
            if params.get("customer"):
                query["customer"] = params["customer"]

            response = await self.http_client.get(
                f"{self.base_url}/invoices",
                params=query,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if response.status_code != 200:
                return {"error": "Failed to list invoices", "details": response.text[:300]}

            data = response.json()
            invoices = []
            for inv in data.get("data", []):
                invoices.append({
                    "id": inv["id"],
                    "customer": inv.get("customer"),
                    "customer_email": inv.get("customer_email"),
                    "status": inv.get("status"),
                    "amount_due": inv.get("amount_due", 0) / 100,
                    "amount_paid": inv.get("amount_paid", 0) / 100,
                    "currency": inv.get("currency", "usd"),
                    "due_date": inv.get("due_date"),
                    "created": inv.get("created"),
                    "hosted_invoice_url": inv.get("hosted_invoice_url"),
                    "description": inv.get("description"),
                })

            return {
                "invoices": invoices,
                "total": len(invoices),
                "has_more": data.get("has_more", False),
                "overdue_count": sum(1 for i in invoices if i["status"] == "open" and i.get("due_date") and i["due_date"] < int(datetime.now().timestamp())),
            }
        except Exception as e:
            logger.error("List invoices failed", error=str(e))
            return {"error": str(e)}

    async def _create_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and optionally send an invoice.
        Params: customer (required), amount_cents, description, auto_send (bool)
        """
        try:
            customer = params.get("customer")
            if not customer:
                return {"error": "customer ID is required"}

            # 1. Create invoice item
            item_payload = {
                "customer": customer,
                "amount": params.get("amount_cents", 0),
                "currency": params.get("currency", "usd"),
                "description": params.get("description", "Service charge"),
            }
            
            item_resp = await self.http_client.post(
                f"{self.base_url}/invoiceitems",
                data=item_payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            
            if item_resp.status_code != 200:
                return {"error": "Failed to create invoice item", "details": item_resp.text[:300]}

            # 2. Create the invoice
            inv_payload = {"customer": customer, "auto_advance": "true"}
            inv_resp = await self.http_client.post(
                f"{self.base_url}/invoices",
                data=inv_payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

            if inv_resp.status_code != 200:
                return {"error": "Failed to create invoice", "details": inv_resp.text[:300]}

            invoice = inv_resp.json()

            # 3. Optionally finalize + send
            if params.get("auto_send", False):
                send_resp = await self.http_client.post(
                    f"{self.base_url}/invoices/{invoice['id']}/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                if send_resp.status_code == 200:
                    invoice = send_resp.json()

            return {
                "invoice_id": invoice["id"],
                "status": invoice.get("status"),
                "amount_due": invoice.get("amount_due", 0) / 100,
                "hosted_invoice_url": invoice.get("hosted_invoice_url"),
                "customer_email": invoice.get("customer_email"),
            }
        except Exception as e:
            logger.error("Create invoice failed", error=str(e))
            return {"error": str(e)}

    async def _retry_failed_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retry payment on an open/failed invoice.
        Params: invoice_id (required)
        """
        try:
            invoice_id = params.get("invoice_id")
            if not invoice_id:
                return {"error": "invoice_id is required"}

            response = await self.http_client.post(
                f"{self.base_url}/invoices/{invoice_id}/pay",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

            if response.status_code == 200:
                inv = response.json()
                return {
                    "success": True,
                    "invoice_id": inv["id"],
                    "status": inv.get("status"),
                    "amount_paid": inv.get("amount_paid", 0) / 100,
                }
            else:
                return {"success": False, "error": response.text[:300]}
        except Exception as e:
            logger.error("Retry payment failed", error=str(e))
            return {"error": str(e)}

    async def _get_revenue_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get MRR trend over the last N months by analyzing charges.
        Params: months (default 12)
        """
        try:
            months = params.get("months", 12)
            timeline = []

            for i in range(months):
                month_start = datetime.now().replace(day=1) - timedelta(days=30 * i)
                month_end = (month_start + timedelta(days=32)).replace(day=1)

                response = await self.http_client.get(
                    f"{self.base_url}/charges",
                    params={
                        "created[gte]": int(month_start.timestamp()),
                        "created[lt]": int(month_end.timestamp()),
                        "limit": 100,
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )

                month_revenue = 0.0
                if response.status_code == 200:
                    charges = response.json().get("data", [])
                    month_revenue = sum(
                        c.get("amount", 0) / 100
                        for c in charges
                        if c.get("status") == "succeeded" and not c.get("refunded")
                    )

                timeline.append({
                    "month": month_start.strftime("%Y-%m"),
                    "revenue": round(month_revenue, 2),
                })

            timeline.reverse()

            # Calculate trend
            if len(timeline) >= 2 and timeline[-2]["revenue"] > 0:
                growth = ((timeline[-1]["revenue"] - timeline[-2]["revenue"]) / timeline[-2]["revenue"]) * 100
            else:
                growth = 0.0

            return {
                "timeline": timeline,
                "current_month_revenue": timeline[-1]["revenue"] if timeline else 0,
                "mom_growth_pct": round(growth, 1),
                "total_revenue": round(sum(m["revenue"] for m in timeline), 2),
            }
        except Exception as e:
            logger.error("Revenue timeline failed", error=str(e))
            return {"error": str(e)}

    async def create_checkout_session(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        client_reference_id: Optional[str] = None,
        mode: str = "payment",
    ) -> Dict[str, Any]:
        """Create a Stripe Checkout Session"""
        try:
            payload = {
                "line_items": [{"price": price_id, "quantity": 1}],
                "mode": mode,
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
            
            if customer_email:
                payload["customer_email"] = customer_email
            
            if client_reference_id:
                payload["client_reference_id"] = client_reference_id
                
            response = await self.http_client.post(
                f"{self.base_url}/checkout/sessions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
            )
            
            if response.status_code != 200:
                logger.error("Stripe Checkout failed", status=response.status_code, response=response.text)
                return {"error": "Failed to create checkout session", "details": response.text}
            return response.json()
            
        except Exception as e:
            logger.error("Stripe Checkout error", error=str(e))
            return {"error": str(e)}
            
    async def create_split_transfer(
        self,
        amount_cents: int,
        destination_account_id: str,
        description: str = "Equity-for-Compute Split",
        transfer_group: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Phantom Co-Founders: Perform a Stripe Connect transfer for Equity-for-Compute splits.
        Routes automated percentage payouts to autonomous agents or remote partners.
        """
        try:
            payload = {
                "amount": amount_cents,
                "currency": "usd",
                "destination": destination_account_id,
                "description": description
            }
            if transfer_group:
                payload["transfer_group"] = transfer_group
                
            response = await self.http_client.post(
                f"{self.base_url}/transfers",
                data=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            if response.status_code != 200:
                logger.error("Stripe Connect transfer failed", status=response.status_code, response=response.text)
                return {"error": "Failed to execute split transfer", "details": response.text}
                
            return response.json()
        except Exception as e:
            logger.error("Stripe split transfer error", error=str(e))
            return {"error": str(e)}
    
    
    def get_supported_actions(self) -> List[Dict[str, Any]]:
        return [
            {"name": "get_balance", "description": "Get Stripe balance"},
            {"name": "get_recent_charges", "description": "Get recent charges"},
            {"name": "create_split_transfer", "description": "Execute an Equity-for-Compute revenue split transfer via Connect"},
            {"name": "list_invoices", "description": "List invoices (filter by status: draft/open/paid/uncollectible/void)"},
            {"name": "create_invoice", "description": "Create and optionally send an invoice to a customer"},
            {"name": "retry_failed_payment", "description": "Retry payment on a failed/open invoice"},
            {"name": "get_revenue_timeline", "description": "Get MRR trend over last N months"},
        ]

