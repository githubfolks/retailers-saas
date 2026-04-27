{
    'name': 'Remove Odoo Branding',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'sequence': 0,
    'depends': ['base', 'web'],
    'data': [
        'views/remove_branding.xml',
    ],
    'installable': True,
    'auto_install': False,
}
