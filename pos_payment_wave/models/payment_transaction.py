import hashlib
import hmac
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_log = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    wave_checkout_url = fields.Char(readonly=True, copy=False)

    def _send_payment_request(self):
        super()._send_payment_request()
        if self.provider_code != 'wave':
            return

        provider = self.provider_id
        base_url = self.get_base_url()
        payload = {
            'amount':           str(int(self.amount)),
            'currency':         'XOF',
            'client_reference': self.reference,
            'success_url':      f"{base_url}/payment/wave/return",
            'error_url':        f"{base_url}/payment/wave/cancel",
        }

        if self.currency_id.name != 'XOF':
            raise ValidationError(_(
                'Wave ne supporte que le XOF (devise actuelle : %s)'
            ) % self.currency_id.name)

        data = provider._wave_request('checkout/sessions', payload)
        session_id      = data.get('id')
        wave_launch_url = data.get('wave_launch_url')

        if not session_id or not wave_launch_url:
            raise ValidationError(_('Wave : réponse invalide — %s') % data)

        self.provider_reference = session_id
        self.wave_checkout_url  = wave_launch_url
        _log.info('[Wave] Checkout session créée — id=%s', session_id)

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'wave':
            return res
        return {
            **res,
            'session_id':      self.provider_reference,
            'wave_launch_url': self.wave_checkout_url or '',
        }

    # -------------------------------------------------------------------------
    # Traitement webhook
    # -------------------------------------------------------------------------

    def _process_notification_data(self, data):
        super()._process_notification_data(data)
        if self.provider_code != 'wave':
            return

        event_type = data.get('type', '')
        session    = data.get('data', {})

        if event_type == 'checkout.session.completed':
            if session.get('payment_status') == 'succeeded':
                self._set_done()
            else:
                _log.warning('[Wave] completed mais payment_status=%s', session.get('payment_status'))
        elif event_type == 'checkout.session.payment_failed':
            self._set_canceled()
        else:
            _log.warning('[Wave] Événement webhook inconnu : %s', event_type)

    # -------------------------------------------------------------------------
    # Polling de secours
    # -------------------------------------------------------------------------

    def _get_tx_status(self):
        if self.provider_code != 'wave':
            return super()._get_tx_status()
        if not self.provider_reference:
            return self.state

        data   = self.provider_id._wave_request(
            f'checkout/sessions/{self.provider_reference}', method='GET'
        )
        status = data.get('payment_status', '')
        if status == 'succeeded' and self.state != 'done':
            self._set_done()
        elif status in ('failed', 'cancelled') and self.state not in ('cancel', 'done'):
            self._set_canceled()

        return self.state

    # -------------------------------------------------------------------------
    # Vérification signature webhook
    # -------------------------------------------------------------------------

    @staticmethod
    def _verify_wave_webhook(payload_bytes: bytes, signature_header: str, secret: str) -> bool:
        expected  = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
        sig_value = signature_header.removeprefix('sha256=')
        return hmac.compare_digest(expected, sig_value)

    def _sn_pos_response(self):
        if self.provider_code != 'wave':
            return super()._sn_pos_response()
        return {
            'reference':       self.reference,
            'session_id':      self.provider_reference,
            'wave_launch_url': self.wave_checkout_url or '',
        }

    @api.model
    def pos_wave_create(self, vals):
        """Point d'entrée RPC POS pour initier un paiement Wave."""
        return self._sn_pos_create(vals)
