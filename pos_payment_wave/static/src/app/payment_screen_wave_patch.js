/** @odoo-module */
/**
 * Patch PaymentScreen : ouvre le QR Wave dès la sélection du mode de paiement,
 * sans attendre que le caissier clique "Valider".
 *
 * Méthodes Odoo 17 ciblées :
 *   - PaymentScreen.addNewPaymentLine(paymentMethod) — sélection du mode
 *
 * Diagnostic du bug original (Promise.resolve().then) :
 *   sendPaymentRequest() Odoo 17 appelle getPendingPaymentLine() qui retourne
 *   la ligne dont payment_status === 'waiting'. Une ligne nouvellement créée
 *   a le statut 'pending'. getPendingPaymentLine() retourne donc null →
 *   PaymentSNInterface.send_payment_request() sort en return false →
 *   _initPayment() n'est jamais appelé → pas de dialog QR.
 *
 * Fix : on force manuellement le statut 'waiting' sur la ligne avant
 * d'appeler le terminal, puis on restaure 'done' ou 'retry' selon le résultat.
 * On appelle directement le terminal (payment_method.payment_terminal)
 * pour éviter les préconditions UI de PaymentScreen.sendPaymentRequest().
 */
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    addNewPaymentLine(paymentMethod) {
        const result = super.addNewPaymentLine(...arguments);

        if (paymentMethod?.use_payment_terminal !== "wave") {
            return result;
        }

        // Deux ticks : le premier laisse OWL insérer la ligne dans le DOM,
        // le second garantit que paymentLines est bien à jour.
        Promise.resolve().then(() => Promise.resolve().then(async () => {
            const waveLine = this.paymentLines.at(-1);
            if (!waveLine) return;

            const terminal = paymentMethod.payment_terminal;
            if (!terminal?._initPayment) return;

            // Marque la ligne 'waiting' pour satisfaire getPendingPaymentLine()
            // si jamais le flux standard est déclenché par ailleurs.
            waveLine.set_payment_status("waiting");

            const uuid = waveLine.uuid;
            terminal._clearPollTimer?.();
            terminal._startTime = Date.now();

            try {
                const initResult = await terminal._initPayment(waveLine, uuid);
                if (!initResult) {
                    waveLine.set_payment_status("retry");
                    return;
                }

                terminal._currentReference = initResult.reference;

                // Polling asynchrone — met à jour le statut quand Wave confirme
                terminal._pollUntilDone(initResult.reference, uuid).then((success) => {
                    // Ferme le dialog Wave (défini dans PaymentWave._closeWaveDialog)
                    if (typeof terminal._closeDialog === "function") {
                        terminal._closeDialog();
                    }
                    waveLine.set_payment_status(success ? "done" : "retry");
                }).catch(() => {
                    if (typeof terminal._closeDialog === "function") {
                        terminal._closeDialog();
                    }
                    waveLine.set_payment_status("retry");
                });

            } catch (e) {
                console.error("[Wave patch] Erreur _initPayment :", e);
                waveLine.set_payment_status("retry");
            }
        }));

        return result;
    },
});
