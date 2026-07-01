import { PaymentSNInterface } from "@pos_payment_sn_base/app/payment_sn_interface";
import { _t } from "@web/core/l10n/translation";

export class PaymentWave extends PaymentSNInterface {

    async _initPayment(line, uuid) {
        const reference = `POS-WAVE-${this.pos.session.id}-${Date.now()}`;
        try {
            const result = await this.pos.data.call(
                "payment.transaction",
                "pos_wave_create",
                [[], {
                    amount:            line.amount,
                    currency:          "XOF",
                    reference,
                    payment_method_id: this.payment_method.id,
                }]
            );

            if (!result?.session_id) {
                this.pos.env.services.notification.add(
                    _t("Wave : impossible de créer le paiement."),
                    { type: "danger" }
                );
                return null;
            }

            this.pos.env.services.notification.add(
                _t("Scannez le QR Wave ou partagez le lien de paiement."),
                { type: "info", sticky: true }
            );

            return { reference: result.reference };

        } catch (e) {
            this.pos.env.services.notification.add(
                _t("Wave : erreur — %s", e.message),
                { type: "danger" }
            );
            return null;
        }
    }
}

// TODO: vérifier le nom exact du registre sur Odoo 19 (peut différer d'Odoo 17)
import { paymentMethodRegistry } from "@point_of_sale/app/payment/payment_method_registry";
paymentMethodRegistry.add("wave", PaymentWave);
