/** @odoo-module */
/**
 * Patch PaymentScreen : ouvre le QR Wave dès la sélection du mode de paiement,
 * sans attendre que le caissier clique "Valider".
 *
 * Méthodes Odoo 17 ciblées :
 *   - PaymentScreen.addNewPaymentLine(paymentMethod) — sélection du mode
 *   - PaymentScreen.sendPaymentRequest()             — déclenche le terminal
 */
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    addNewPaymentLine(paymentMethod) {
        const result = super.addNewPaymentLine(...arguments);
        if (paymentMethod?.use_payment_terminal === "wave") {
            // Décaler d'un tick pour laisser OWL mettre à jour la ligne
            // avant que sendPaymentRequest() ne cherche la "pending line".
            Promise.resolve().then(() => {
                const waveLine = this.paymentLines.at(-1);
                if (waveLine) this.sendPaymentRequest(waveLine);
            });
        }
        return result;
    },
});
