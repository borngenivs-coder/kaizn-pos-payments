{
    'name': 'POS Paiement — Wave',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Paiement POS directement via Wave (API officielle wave.com) — Sénégal',
    'author': 'KAIZN SN',
    'website': 'https://kaiznsn.com',
    'depends': ['pos_payment_sn_base'],
    'data': [
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_payment_wave/static/src/app/payment_wave.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
