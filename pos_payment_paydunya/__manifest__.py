{
    'name': 'POS Paiement — PayDunya (Orange Money / Visa)',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Paiement POS via PayDunya — Orange Money, Visa (Sénégal/CEDEAO)',
    'author': 'KAIZN SN',
    'website': 'https://kaiznsn.com',
    'depends': ['pos_payment_sn_base'],
    'data': [
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_payment_paydunya/static/src/app/payment_paydunya.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
