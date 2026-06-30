import logging
from odoo import http
from odoo.http import request

_log = logging.getLogger(__name__)


class PosSNPaymentController(http.Controller):

    @http.route('/pos_payment_sn/poll_status', type='json', auth='user')
    def poll_status(self, transaction_ref):
        """RPC appelé par le frontend POS pour vérifier le statut de paiement."""
        tx = request.env['payment.transaction'].sudo().search(
            [('reference', '=', transaction_ref)], limit=1
        )
        if not tx:
            return {'state': 'error', 'message': 'Transaction introuvable'}

        if tx.state == 'pending':
            try:
                tx._get_tx_status()
            except Exception as e:
                _log.warning('[SN Poll] _get_tx_status échoué pour %s : %s', transaction_ref, e)

        return {'state': tx.state, 'reference': tx.reference}
