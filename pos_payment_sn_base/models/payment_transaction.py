import logging
from odoo import models

_log = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_tx_status(self):
        """Interroge l'API distante pour le statut courant.

        Méthode de secours appelée par le polling POS quand le webhook n'est
        pas encore arrivé. Surchargée par chaque adaptateur (paydunya, wave).
        """
        return self.state
