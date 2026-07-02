import logging
from odoo import http
from odoo.http import request
from odoo.addons.pos_payment_sn_base.controllers.main import SnWebhookMixin

_log = logging.getLogger(__name__)


class PayDunyaController(SnWebhookMixin, http.Controller):

    @http.route('/payment/paydunya/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def paydunya_webhook(self, **kwargs):
        def get_reference(data):
            return (data.get('custom_data') or {}).get('odoo_tx_ref')

        def verify(tx, payload_bytes, data):
            master_key = tx.provider_id.sudo().paydunya_master_key or ''
            if not master_key:
                _log.error('[PayDunya] paydunya_master_key non configuré pour %s', tx.provider_id.name)
                return False
            payload_hash = data.get('hash') or ''
            token = data.get('token') or ''
            return tx._verify_paydunya_webhook(payload_hash, master_key, token)

        return self._handle_sn_webhook('PayDunya', get_reference, verify)

    @http.route('/payment/paydunya/return', type='http', auth='public')
    def paydunya_return(self, **kwargs):
        return request.redirect('/odoo/point-of-sale')

    @http.route('/payment/paydunya/cancel', type='http', auth='public')
    def paydunya_cancel(self, **kwargs):
        return request.redirect('/odoo/point-of-sale')
