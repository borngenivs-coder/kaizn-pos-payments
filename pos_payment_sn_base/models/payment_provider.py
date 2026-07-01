import logging
import requests
from odoo import _, fields, models
from odoo.exceptions import ValidationError

_log = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[
            ('paydunya', 'PayDunya'),
            ('wave', 'Wave'),
        ],
        ondelete={
            'paydunya': 'set default',
            'wave': 'set default',
        },
    )

    def _sn_http_request(self, url, headers, payload=None, method='POST'):
        """Helper HTTP partagé par tous les adaptateurs SN."""
        try:
            if method == 'GET':
                resp = requests.get(url, headers=headers, timeout=30)
            else:
                resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            _log.error('[SN HTTP] %s %s — %s', method, url, e)
            raise ValidationError(_('Erreur réseau — %s') % e)
