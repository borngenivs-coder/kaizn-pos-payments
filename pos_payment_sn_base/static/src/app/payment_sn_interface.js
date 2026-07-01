import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { _t } from "@web/core/l10n/translation";

/**
 * Classe de base pour les providers de paiement mobile SN.
 * Pattern : créer transaction → afficher QR/USSD → poll statut → done/timeout.
 */
export class PaymentSNInterface extends PaymentInterface {

    get POLL_INTERVAL() { return 2500; }
    get PAYMENT_TIMEOUT() { return 120000; }

    setup() {
        super.setup(...arguments);
        this._pollTimer = null;
        this._startTime = null;
    }

    async send_payment_request(uuid) {
        const line = this.pos.getPendingPaymentLine();
        if (!line) return false;

        this._startTime = Date.now();
        const result = await this._initPayment(line, uuid);
        if (!result) return false;

        return await this._pollUntilDone(result.reference, uuid);
    }

    async send_payment_cancel(order, uuid) {
        this._clearPollTimer();
        return true;
    }

    /**
     * Surchargée par chaque adaptateur.
     * Doit créer la transaction côté serveur et retourner {reference, ...}.
     */
    async _initPayment(line, uuid) {
        throw new Error("_initPayment() doit être surchargé par chaque adaptateur");
    }

    async _pollUntilDone(reference, uuid) {
        return new Promise((resolve) => {
            const check = async () => {
                if (Date.now() - this._startTime > this.PAYMENT_TIMEOUT) {
                    this._clearPollTimer();
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
                        resolve(true);
                    } else if (["cancel", "error", "refused"].includes(status.state)) {
                        this._clearPollTimer();
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
