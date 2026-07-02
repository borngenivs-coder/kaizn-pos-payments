import json
import logging
from odoo.http import request

_log = logging.getLogger(__name__)


class SnWebhookMixin:
    """Squelette commun aux contrôleurs webhook SN (Wave, PayDunya).

    Les sous-classes fournissent uniquement :
      - get_reference(data) -> str | None  : comment extraire la référence Odoo
      - verify(tx, payload_bytes, data) -> bool : comment vérifier la signature
    """

    def _handle_sn_webhook(self, provider_name, get_reference, verify):
        payload_bytes = request.httprequest.get_data()
        try:
            data = json.loads(payload_bytes)
        except json.JSONDecodeError:
            _log.warning('[%s] Webhook : payload JSON invalide', provider_name)
            return request.make_response('Bad Request', status=400)

        ref = get_reference(data)
        if not ref:
            _log.warning('[%s] Webhook : référence manquante', provider_name)
            return request.make_response('Missing reference', status=400)

        tx = request.env['payment.transaction'].sudo().search(
            [('reference', '=', ref)], limit=1
        )
        if not tx:
            _log.warning('[%s] Webhook : transaction %s introuvable', provider_name, ref)
            return request.make_response('Not found', status=404)

        if not verify(tx, payload_bytes, data):
            _log.error('[%s] Vérification signature échouée pour %s', provider_name, ref)
            return request.make_response('Invalid signature', status=401)

        tx._process_notification_data(data)
        return request.make_response('OK', status=200)
