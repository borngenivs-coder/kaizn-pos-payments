from odoo import api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    payment_provider_id = fields.Many2one(
        'payment.provider',
        string='Fournisseur de paiement',
        ondelete='restrict',
        help="Provider lié à ce mode de paiement POS (Wave, PayDunya...).",
    )

    @api.model
    def _get_payment_terminal_selection(self):
        result = super()._get_payment_terminal_selection()
        result += [
            ('paydunya', 'PayDunya (Orange Money / Visa)'),
            ('wave', 'Wave'),
        ]
        return result
