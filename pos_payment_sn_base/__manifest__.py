{
    'name': 'POS Paiement Mobile SN — Socle',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Socle commun pour connecteurs paiement mobile Sénégal/CEDEAO (Wave, Orange Money, Visa)',
    'author': 'KAIZN SN',
    'website': 'https://kaiznsn.com',
    'depends': ['point_of_sale', 'payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_method_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_payment_sn_base/static/src/app/payment_sn_interface.js',
            'pos_payment_sn_base/static/src/app/payment_sn_wave_dialog.js',
            'pos_payment_sn_base/static/src/app/payment_sn_qr_dialog.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
