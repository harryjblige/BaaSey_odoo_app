from odoo import http
import hmac, hashlib, json

class BaaseyWebhook(http.Controller):

    @http.route('/baasey/webhook', type='json', auth='public', csrf=False)
    def baasey_webhook(self, **kwargs):
        """
        Webhook endpoint for BaaSey settlement events
        """

        # ✅ Get your secret key from Odoo Settings → System Parameters
        secret_key = http.request.env['ir.config_parameter'].sudo().get_param('baasey.secret_key')

        # ✅ Raw webhook body (from BaaSey)
        raw_body = http.request.httprequest.data.decode('utf-8')

        # ✅ Signature sent by BaaSey (header: x-swim-token)
        signature = http.request.httprequest.headers.get("x-swim-token")

        # -------------------------------
        # Step 1: Verify webhook signature
        # -------------------------------
        computed = hmac.new(secret_key.encode(), raw_body.encode(), hashlib.sha256).hexdigest()
        if computed != signature:
            return {"status": "error", "message": "Invalid Signature"}

        # -------------------------------
        # Step 2: Parse event payload
        # -------------------------------
        data = json.loads(raw_body)
        event = data.get("event")
        payload = data.get("data")

        # -------------------------------
        # Step 3: Handle Collection Event
        # -------------------------------
        if event == "event.collection":
            # Ensure payment is completed and amount is correct
            if payload.get("completed") and not payload.get("amount_mismatch"):
                reference = payload.get("reference")
                amount_received = payload.get("amount")

                # Find the matching Sales Order in Odoo
                order = http.request.env['sale.order'].sudo().search([('id', '=', reference)])
                if order:
                    # Update order as Settled
                    order.write({
                        'baasey_status': 'settled'
                    })
                    # Create and post the invoice
                    order.action_confirm()
                    invoice = order._create_invoices()
                    invoice.action_post()

                    return {
                        "status": "success",
                        "message": f"Order {reference} marked as paid",
                        "amount_received": amount_received
                    }

        # -------------------------------
        # Step 4: Handle Transfer Events
        # -------------------------------
        elif event in ["event.transfer.success", "event.transfer.failed", "event.transfer.reversed"]:
            # You can extend here to log payout events or update accounting
            return {"status": "ok", "message": f"Received transfer event: {event}"}

        # -------------------------------
        # Default: Unhandled Event
        # -------------------------------
        return {"status": "ok", "message": f"Unhandled event {event}"}
