/** @odoo-module */
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class WavePaymentDialog extends Component {
    static template = "pos_payment_sn_base.WavePaymentDialog";
    static components = { Dialog };
    static props = {
        waveUrl: String,
        amount: Number,
        close: Function,
    };
}
