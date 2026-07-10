from odoo import api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    wave_static_mode = fields.Boolean(
        related='payment_provider_id.wave_static_mode',
        string='Mode statique Wave',
        readonly=True,
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        fields_list += ['wave_static_mode']
        return fields_list
