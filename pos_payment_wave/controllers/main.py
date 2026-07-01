import json
import logging
from odoo import http
from odoo.http import request

_log = logging.getLogger(__name__)


class WaveController(http.Controller):

    @http.route('/payment/wave/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def wave_webhook(self, **kwargs):
        payload_bytes = request.httprequest.get_data()
        signature     = request.httprequest.headers.get('X-Wave-Signature', '')

        try:
            data = json.loads(payload_bytes)
        except json.JSONDecodeError:
            _log.warning('[Wave] Webhook : payload JSON invalide')
            return request.make_response('Bad Request', status=400)

        client_ref = (data.get('data') or {}).get('client_reference')
        if not client_ref:
            _log.warning('[Wave] Webhook : client_reference manquant')
            return request.make_response('Missing reference', status=400)

        tx = request.env['payment.transaction'].sudo().search(
            [('reference', '=', client_ref)], limit=1
        )
        if not tx:
            _log.warning('[Wave] Webhook : transaction %s introuvable', client_ref)
            return request.make_response('Not found', status=404)

        secret = tx.provider_id.sudo().wave_webhook_secret
        if not secret:
            _log.error('[Wave] wave_webhook_secret non configuré pour %s', tx.provider_id.name)
            return request.make_response('Webhook secret not configured', status=500)

        if not tx._verify_wave_webhook(payload_bytes, signature, secret):
            _log.error('[Wave] Signature invalide pour %s', client_ref)
            return request.make_response('Invalid signature', status=401)

        tx._process_notification_data(data)
        return request.make_response('OK', status=200)

    @http.route('/payment/wave/return', type='http', auth='public')
    def wave_return(self, **kwargs):
        return request.redirect('/odoo/point-of-sale')

    @http.route('/payment/wave/cancel', type='http', auth='public')
    def wave_cancel(self, **kwargs):
        return request.redirect('/odoo/point-of-sale')
