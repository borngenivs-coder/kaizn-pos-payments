from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    payment_provider_id = fields.Many2one(
        'payment.provider',
        string='Fournisseur de paiement',
        ondelete='restrict',
        help="Provider lié à ce mode de paiement POS (Wave, PayDunya...).",
    )

    use_payment_terminal = fields.Selection(
        selection_add=[
            ('paydunya', 'PayDunya (Orange Money / Visa)'),
            ('wave', 'Wave'),
        ],
        ondelete={
            'paydunya': 'set default',
            'wave': 'set default',
        },
    )
