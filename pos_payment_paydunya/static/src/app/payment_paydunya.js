import { PaymentSNInterface } from "@pos_payment_sn_base/app/payment_sn_interface";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

export class PaymentPayDunya extends PaymentSNInterface {

    async _initPayment(line, uuid) {
        const rand = Math.random().toString(36).slice(2, 7);
        const reference = `POS-PD-${this.pos.session.id}-${Date.now()}-${rand}`;
        try {
            const result = await this.pos.data.call(
                "payment.transaction",
                "pos_paydunya_create",
                [[], {
                    amount:            line.amount,
                    currency:          this.pos.currency.name,
                    reference,
                    payment_method_id: this.payment_method.id,
                }]
            );

            if (!result?.token) {
                this.pos.env.services.notification.add(
                    _t("PayDunya : impossible de créer le paiement."),
                    { type: "danger" }
                );
                return null;
            }

            this.pos.env.services.notification.add(
                _t("Paiement PayDunya lancé — en attente de confirmation."),
                { type: "info", sticky: true }
            );

            return { reference: result.reference };

        } catch (e) {
            this.pos.env.services.notification.add(
                _t("PayDunya : erreur — %s", e.message),
                { type: "danger" }
            );
            return null;
        }
    }
}

registry.category("pos_payment_methods").add("paydunya", PaymentPayDunya);
