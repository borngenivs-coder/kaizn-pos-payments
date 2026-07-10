/** @odoo-module */
import { PaymentSNInterface } from "@pos_payment_sn_base/app/payment_sn_interface";
import { WavePaymentDialog } from "@pos_payment_sn_base/app/payment_sn_wave_dialog";
import { WaveStaticDialog } from "@pos_payment_wave/app/payment_wave_static_dialog";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

export class PaymentWave extends PaymentSNInterface {

    setup() {
        super.setup(...arguments);
        this._closeWaveDialog = null;
    }

    async send_payment_request(uuid) {
        // Si un paiement Wave est déjà en cours (lancé par le patch auto-trigger),
        // on ne recrée pas un nouveau checkout — on attend juste la fin du polling.
        if (this._currentReference) {
            // Mode statique : référence déjà résolue, pas de polling nécessaire
            if (this._currentReference.startsWith("STATIC-WAVE-")) {
                return true;
            }
            return await this._pollUntilDone(this._currentReference, uuid).then((success) => {
                this._closeDialog();
                return success;
            });
        }
        const result = await super.send_payment_request(uuid);
        this._closeDialog();
        return result;
    }

    async send_payment_cancel(order, uuid) {
        this._closeDialog();
        return super.send_payment_cancel(order, uuid);
    }

    async _initPayment(line, uuid) {
        // Détection mode statique : QR statique configuré et pas de clé API
        if (this.payment_method.wave_static_mode && this.payment_method.wave_static_qr) {
            return await this._initStaticPayment(line, uuid);
        }
        return await this._initDynamicPayment(line, uuid);
    }

    async _initStaticPayment(line, uuid) {
        return new Promise((resolve) => {
            const qrSrc = `data:image/png;base64,${this.payment_method.wave_static_qr}`;

            const closeDialog = this.pos.env.services.dialog.add(WaveStaticDialog, {
                amount: line.amount,
                qrSrc,
                onConfirm: () => {
                    closeDialog();
                    this._closeWaveDialog = null;
                    resolve({ reference: `STATIC-WAVE-${Date.now()}` });
                },
                onCancel: () => {
                    closeDialog();
                    this._closeWaveDialog = null;
                    resolve(null);
                },
            });
            this._closeWaveDialog = closeDialog;
        });
    }

    async _initDynamicPayment(line, uuid) {
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

    async _pollUntilDone(reference, uuid) {
        // Mode statique : le caissier a confirmé manuellement, pas de polling API
        if (reference.startsWith("STATIC-WAVE-")) {
            return true;
        }
        return super._pollUntilDone(reference, uuid);
    }

    _closeDialog() {
        if (this._closeWaveDialog) {
            this._closeWaveDialog();
            this._closeWaveDialog = null;
        }
    }
}

registry.category("pos_payment_methods").add("wave", PaymentWave);
