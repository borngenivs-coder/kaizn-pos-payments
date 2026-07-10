import logging
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_log = logging.getLogger(__name__)

_WAVE_API = 'https://api.wave.com/v1'


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    wave_api_key        = fields.Char('Clé API Wave',        groups='base.group_system')
    wave_webhook_secret = fields.Char('Secret Webhook Wave', groups='base.group_system')
    wave_test_mode      = fields.Boolean('Mode test (sans appel API)', default=False)
    wave_static_mode    = fields.Boolean('Mode statique (QR fixe)', default=False)

    def _wave_headers(self):
        return {
            'Authorization': f"Bearer {self.sudo().wave_api_key or ''}",
            'Content-Type':  'application/json',
        }

    def _wave_request(self, endpoint, payload=None, method='POST'):
        return self._sn_http_request(
            f"{_WAVE_API}/{endpoint}",
            self._wave_headers(),
            payload, method,
        )
