import json
import logging
from odoo import http
from odoo.http import request

_log = logging.getLogger(__name__)


class PayDunyaController(http.Controller):

    @http.route('/payment/paydunya/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def paydunya_webhook(self, **kwargs):
        payload_bytes = request.httprequest.get_data()
        try:
            data = json.loads(payload_bytes)
        except json.JSONDecodeError:
            _log.warning('[PayDunya] Webhook : payload JSON invalide')
            return request.make_response('Bad Request', status=400)

        ref = (data.get('custom_data') or {}).get('odoo_tx_ref')
        if not ref:
            _log.warning('[PayDunya] Webhook : odoo_tx_ref manquant dans custom_data')
            return request.make_response('Missing reference', status=400)

        tx = request.env['payment.transaction'].sudo().search(
            [('reference', '=', ref)], limit=1
        )
        if not tx:
            _log.warning('[PayDunya] Webhook : transaction %s introuvable', ref)
            return request.make_response('Not found', status=404)

        master_key    = tx.provider_id.sudo().paydunya_master_key or ''
        payload_hash  = data.get('hash') or ''
        token         = data.get('token') or ''

        if not master_key:
            _log.error('[PayDunya] paydunya_master_key non configuré pour %s', tx.provider_id.name)
            return request.make_response('Webhook key not configured', status=500)

        if not tx._verify_paydunya_webhook(payload_hash, master_key, token):
            _log.error('[PayDunya] Hash invalide pour %s', ref)
            return request.make_response('Invalid hash', status=401)

        tx._process_notification_data(data)
        return request.make_response('OK', status=200)

    @http.route('/payment/paydunya/return', type='http', auth='public')
    def paydunya_return(self, **kwargs):
        return request.redirect('/odoo/point-of-sale')

    @http.route('/payment/paydunya/cancel', type='http', auth='public')
    def paydunya_cancel(self, **kwargs):
        return request.redirect('/odoo/point-of-sale')
