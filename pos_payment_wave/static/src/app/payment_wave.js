import { PaymentSNInterface } from "@pos_payment_sn_base/app/payment_sn_interface";
import { WavePaymentDialog } from "@pos_payment_sn_base/app/payment_sn_wave_dialog";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

export class PaymentWave extends PaymentSNInterface {

    setup() {
        super.setup(...arguments);
        this._closeWaveDialog = null;
    }

    async send_payment_request(uuid) {
        const result = await super.send_payment_request(uuid);
        this._closeDialog();
        return result;
    }

    async send_payment_cancel(order, uuid) {
        this._closeDialog();
        return super.send_payment_cancel(order, uuid);
    }

    async _initPayment(line, uuid) {
        const rand = Math.random().toString(36).slice(2, 7);
        const reference = `POS-WAVE-${this.pos.session.id}-${Date.now()}-${rand}`;
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

            this._closeWaveDialog = this.pos.env.services.dialog.add(WavePaymentDialog, {
                waveUrl: result.wave_launch_url,
                amount:  line.amount,
            });

            return { reference: result.reference };

        } catch (e) {
            this.pos.env.services.notification.add(
                _t("Wave : erreur — %s", e.message),
                { type: "danger" }
            );
            return null;
        }
    }

    _closeDialog() {
        if (this._closeWaveDialog) {
            this._closeWaveDialog();
            this._closeWaveDialog = null;
        }
    }
}

registry.category("pos_payment_methods").add("wave", PaymentWave);
