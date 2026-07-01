import logging
import requests
from odoo import _, fields, models
from odoo.exceptions import ValidationError

_log = logging.getLogger(__name__)

_SANDBOX_URL = 'https://app.paydunya.com/sandbox-api/v1'
_PROD_URL    = 'https://app.paydunya.com/api/v1'


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    paydunya_master_key  = fields.Char('Master Key',  groups='base.group_system')
    paydunya_private_key = fields.Char('Private Key', groups='base.group_system')
    paydunya_public_key  = fields.Char('Public Key',  groups='base.group_system')
    paydunya_token       = fields.Char('Token',       groups='base.group_system')

    def _paydunya_base_url(self):
        return _PROD_URL if self.state == 'enabled' else _SANDBOX_URL

    def _paydunya_checkout_url(self, token):
        if self.state == 'enabled':
            return f"https://app.paydunya.com/checkout/invoice/{token}"
        return f"https://app.paydunya.com/sandbox-checkout/invoice/{token}"

    def _paydunya_headers(self):
        return {
            'PAYDUNYA-MASTER-KEY':  self.sudo().paydunya_master_key  or '',
            'PAYDUNYA-PRIVATE-KEY': self.sudo().paydunya_private_key or '',
            'PAYDUNYA-PUBLIC-KEY':  self.sudo().paydunya_public_key  or '',
            'PAYDUNYA-TOKEN':       self.sudo().paydunya_token       or '',
            'Content-Type': 'application/json',
        }

    def _paydunya_request(self, endpoint, payload=None, method='POST'):
        url = f"{self._paydunya_base_url()}/{endpoint}"
        try:
            if method == 'GET':
                resp = requests.get(url, headers=self._paydunya_headers(), timeout=30)
            else:
                resp = requests.post(url, json=payload, headers=self._paydunya_headers(), timeout=30)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            _log.error('[PayDunya] %s %s — %s', method, endpoint, e)
            raise ValidationError(_('PayDunya : erreur réseau — %s') % e)
