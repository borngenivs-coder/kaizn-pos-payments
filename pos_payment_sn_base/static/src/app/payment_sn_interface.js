import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { _t } from "@web/core/l10n/translation";

export class PaymentSNInterface extends PaymentInterface {

    get POLL_INTERVAL() { return 2500; }
    get PAYMENT_TIMEOUT() { return 120000; }

    setup() {
        super.setup(...arguments);
        this._pollTimer = null;
        this._startTime = null;
        this._currentReference = null;
    }

    async send_payment_request(uuid) {
        this._clearPollTimer();
        const line = this.pos.getPendingPaymentLine();
        if (!line) return false;

        this._startTime = Date.now();
        const result = await this._initPayment(line, uuid);
        if (!result) return false;

        this._currentReference = result.reference;
        return await this._pollUntilDone(result.reference, uuid);
    }

    async send_payment_cancel(order, uuid) {
        this._clearPollTimer();
        const ref = this._currentReference;
        this._currentReference = null;
        if (ref) {
            try {
                await this.pos.data.call(
                    "payment.transaction",
                    "cancel_pos_payment",
                    [[], ref]
                );
            } catch (e) {
                // non-bloquant : le cron Odoo nettoiera les transactions expirées
            }
        }
        return true;
    }

    async _initPayment(line, uuid) {
        throw new Error("_initPayment() doit être surchargé par chaque adaptateur");
    }

    async _pollUntilDone(reference, uuid) {
        return new Promise((resolve) => {
            const check = async () => {
                if (Date.now() - this._startTime > this.PAYMENT_TIMEOUT) {
                    this._clearPollTimer();
                    this._currentReference = null;
                    this.pos.env.services.notification.add(
                        _t("Paiement expiré — veuillez réessayer."),
                        { type: "danger" }
                    );
                    resolve(false);
                    return;
                }
                try {
                    const status = await this.pos.data.call(
                        "payment.transaction",
                        "get_payment_status",
                        [[], reference]
                    );
                    if (status.state === "done") {
                        this._clearPollTimer();
                        this._currentReference = null;
                        resolve(true);
                    } else if (["cancel", "error", "refused"].includes(status.state)) {
                        this._clearPollTimer();
                        this._currentReference = null;
                        resolve(false);
                    } else {
                        this._pollTimer = setTimeout(check, this.POLL_INTERVAL);
                    }
                } catch (e) {
                    this._pollTimer = setTimeout(check, this.POLL_INTERVAL);
                }
            };
            check();
        });
    }

    _clearPollTimer() {
        if (this._pollTimer) {
            clearTimeout(this._pollTimer);
            this._pollTimer = null;
        }
    }
}
