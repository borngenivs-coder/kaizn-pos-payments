/** @odoo-module */
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class WaveStaticDialog extends Component {
    static template = "pos_payment_wave.WaveStaticDialog";
    static components = { Dialog };
    static props = {
        amount: Number,
        qrSrc: String,
        onConfirm: Function,
        onCancel: Function,
        close: Function,
    };
}
