import requests
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'   # Extend Odoo's built-in Sales Order model

    # Extra fields for BaaSey integration
    baasey_reference = fields.Char(string="BaaSey Reference", readonly=True)
    baasey_status = fields.Selection(
        [('unsettled', 'Unsettled'),
         ('settled', 'Settled')],
        string="BaaSey Settlement Status",
        default="unsettled",
        readonly=True
    )
    baasey_virtual_account = fields.Char(string="BaaSey Virtual Account", readonly=True)

    def action_generate_baasey_link(self):
        """Generate a dedicated account from BaaSey for this order"""

        # ✅ Base URL from your Postman collection (Sandbox)
        base_url = "https://sandbox-baas-api.pup.finance/api/v1"

        # API key is stored in Odoo System Parameters for security
        api_key = self.env['ir.config_parameter'].sudo().get_param('baasey.secret_key')

        for order in self:
            payload = {
                "reference": str(order.id),          # Use Odoo Order ID as unique reference
                "amount": str(order.amount_total),   # Exact order total
            }
            headers = {
                "Authorization": api_key,            # Secret key from Odoo Settings
                "Content-Type": "application/json"
            }

            # ✅ Correct endpoint per Postman collection
            url = f"{base_url}/business/accounts"

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response_data = response.json()

                # ✅ Check success: HTTP 200 and response contains "data"
                if response.status_code == 200 and "data" in response_data:
                    account_details = response_data["data"]
                    order.write({
                        'baasey_reference': payload["reference"],
                        'baasey_virtual_account': account_details.get("account_number", ""),
                        'baasey_status': 'unsettled'
                    })
                else:
                    raise Exception(f"BaaSey API Error: {response_data}")
            
            except Exception as e:
                raise Exception(f"Failed to create BaaSey account: {str(e)}")
