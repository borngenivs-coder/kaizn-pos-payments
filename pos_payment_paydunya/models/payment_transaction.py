import hashlib
import hmac
import logging
from odoo import _, api, models
from odoo.exceptions import ValidationError

_log = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # -------------------------------------------------------------------------
    # Création du paiement
    # -------------------------------------------------------------------------

    def _send_payment_request(self):
        super()._send_payment_request()
        if self.provider_code != 'paydunya':
            return

        provider = self.provider_id
        base_url = self.get_base_url()
        payload = {
            'invoice': {
                'total_amount': int(self.amount),
                'description':  self.reference,
            },
            'store': {
                'name': self.company_id.name or 'KAIZN',
            },
            'actions': {
                'cancel_url':   f"{base_url}/payment/paydunya/cancel",
                'return_url':   f"{base_url}/payment/paydunya/return",
                'callback_url': f"{base_url}/payment/paydunya/webhook",
            },
            'custom_data': {
                'odoo_tx_ref': self.reference,
            },
        }

        data = provider._paydunya_request('checkout-invoice/create', payload)
        if data.get('response_code') == '00':
            self.provider_reference = data.get('token')
            _log.info('[PayDunya] Facture créée — token=%s', self.provider_reference)
        else:
            raise ValidationError(
                _('PayDunya : création facture échouée — %s') % data.get('response_text', '')
            )

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'paydunya':
            return res
        return {
            **res,
            'checkout_url': f"https://app.paydunya.com/checkout/invoice/{self.provider_reference}",
            'token': self.provider_reference,
        }

    # -------------------------------------------------------------------------
    # Traitement webhook
    # -------------------------------------------------------------------------

    def _process_notification_data(self, data):
        super()._process_notification_data(data)
        if self.provider_code != 'paydunya':
            return

        status = data.get('status', '')
        if status == 'completed':
            self._set_done()
        elif status in ('cancelled', 'expired'):
            self._set_canceled()
        else:
            _log.warning('[PayDunya] Statut webhook inconnu : %s (tx=%s)', status, self.reference)

    # -------------------------------------------------------------------------
    # Polling de secours (quand le webhook tarde)
    # -------------------------------------------------------------------------

    def _get_tx_status(self):
        if self.provider_code != 'paydunya':
            return super()._get_tx_status()
        if not self.provider_reference:
            return self.state

        data = self.provider_id._paydunya_request(
            f'checkout-invoice/confirm/{self.provider_reference}', method='GET'
        )
        status = data.get('status', '')
        if status == 'completed' and self.state != 'done':
            self._set_done()
        elif status in ('cancelled', 'expired') and self.state not in ('cancel', 'done'):
            self._set_canceled()

        return self.state

    @staticmethod
    def _verify_paydunya_webhook(payload_hash: str, master_key: str, token: str) -> bool:
        """Vérifie le hash PayDunya : sha512(MASTER_KEY + token)."""
        expected = hashlib.sha512(f"{master_key}{token}".encode()).hexdigest()
        return hmac.compare_digest(expected, payload_hash)

    @api.model
    def pos_paydunya_create(self, vals):
        """Point d'entrée RPC POS pour initier un paiement PayDunya."""
        tx = self._pos_create_transaction(
            vals['provider_id'],
            vals['amount'],
            vals.get('currency', 'XOF'),
            vals['reference'],
        )
        tx._send_payment_request()
        return {
            'reference':    tx.reference,
            'token':        tx.provider_reference,
            'checkout_url': f"https://app.paydunya.com/checkout/invoice/{tx.provider_reference}",
        }
