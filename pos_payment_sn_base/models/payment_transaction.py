import logging
from odoo import _, api, models
from odoo.exceptions import UserError

_log = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_tx_status(self):
        """Interroge l'API distante pour le statut courant.
        Surchargée par chaque adaptateur (paydunya, wave).
        """
        return self.state

    @api.model
    def _pos_create_transaction(self, pos_payment_method_id, amount, currency_name, reference):
        """Crée une payment.transaction depuis le POS et retourne le record."""
        pm = self.env['pos.payment.method'].sudo().browse(pos_payment_method_id)
        if not pm.payment_provider_id:
            raise UserError(_(
                'Le mode de paiement POS "%s" n\'est pas lié à un fournisseur de paiement.'
            ) % pm.name)
        currency = self.env['res.currency'].search([('name', '=', currency_name)], limit=1)
        if not currency:
            raise UserError(_('Devise %s introuvable.') % currency_name)
        return self.sudo().create({
            'amount':      amount,
            'currency_id': currency.id,
            'provider_id': pm.payment_provider_id.id,
            'reference':   reference,
            'partner_id':  self.env.company.partner_id.id,
            'operation':   'online_redirect',
        })

    @api.model
    def cancel_pos_payment(self, reference):
        """Annule la transaction POS en attente — appelé depuis send_payment_cancel."""
        tx = self.sudo().search(
            [('reference', '=', reference), ('state', '=', 'pending')], limit=1
        )
        if tx:
            tx._set_canceled()
        return True

    @api.model
    def get_payment_status(self, reference):
        """Polling POS : retourne le statut d'une transaction par référence."""
        tx = self.sudo().search([('reference', '=', reference)], limit=1)
        if not tx:
            return {'state': 'error', 'message': 'Transaction introuvable'}
        if tx.state == 'pending':
            try:
                tx._get_tx_status()
            except Exception as e:
                _log.warning('[SN Poll] _get_tx_status échoué pour %s : %s', reference, e)
        return {'state': tx.state, 'reference': tx.reference}
