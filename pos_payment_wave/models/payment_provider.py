import logging
import requests
from odoo import _, fields, models
from odoo.exceptions import ValidationError

_log = logging.getLogger(__name__)

_WAVE_API = 'https://api.wave.com/v1'


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    wave_api_key        = fields.Char('Clé API Wave',        groups='base.group_system')
    wave_webhook_secret = fields.Char('Secret Webhook Wave', groups='base.group_system')

    def _wave_headers(self):
        return {
            'Authorization': f"Bearer {self.sudo().wave_api_key or ''}",
            'Content-Type':  'application/json',
        }

    def _wave_request(self, endpoint, payload=None, method='POST'):
        url = f"{_WAVE_API}/{endpoint}"
        try:
            if method == 'GET':
                resp = requests.get(url, headers=self._wave_headers(), timeout=30)
            else:
                resp = requests.post(url, json=payload, headers=self._wave_headers(), timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            _log.error('[Wave] %s %s — %s', method, endpoint, e)
            raise ValidationError(_('Wave : erreur réseau — %s') % e)
