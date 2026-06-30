from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

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
