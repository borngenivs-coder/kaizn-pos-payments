from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[
            ('paydunya', 'PayDunya'),
            ('wave', 'Wave'),
        ],
        ondelete={
            'paydunya': 'set default',
            'wave': 'set default',
        },
    )
