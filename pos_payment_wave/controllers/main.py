import logging
from odoo import http
from odoo.http import request
from odoo.addons.pos_payment_sn_base.controllers.main import SnWebhookMixin

_log = logging.getLogger(__name__)


class WaveController(SnWebhookMixin, http.Controller):

    @http.route('/payment/wave/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def wave_webhook(self, **kwargs):
        def get_reference(data):
            return (data.get('data') or {}).get('client_reference')

        def verify(tx, payload_bytes, data):
            signature = request.httprequest.headers.get('X-Wave-Signature', '')
            secret = tx.provider_id.sudo().wave_webhook_secret
            if not secret:
                _log.error('[Wave] wave_webhook_secret non configuré pour %s', tx.provider_id.name)
                return False
            return tx._verify_wave_webhook(payload_bytes, signature, secret)

        return self._handle_sn_webhook('Wave', get_reference, verify)

    @http.route('/payment/wave/return', type='http', auth='public')
    def wave_return(self, **kwargs):
        return request.redirect('/odoo/point-of-sale')

    @http.route('/payment/wave/cancel', type='http', auth='public')
    def wave_cancel(self, **kwargs):
        return request.redirect('/odoo/point-of-sale')
