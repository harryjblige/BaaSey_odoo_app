{
    'name': 'BaaSey Settlement Engine',
    'version': '1.0',
    'summary': 'Automated order settlement & reconciliation using P-UP BaaSey',
    'description': """
        BaaSey Settlement Engine integrates your Odoo sales orders 
        with BaaSey Banking-as-a-Service. 
        - Auto-generate virtual accounts per order
        - Track Settled vs Unsettled Orders
        - Automatic reconciliation once payment is received
    """,
    'author': 'P-UP Financial Innovation Services',
    'website': 'www.pup.finance',
    'category': 'Accounting/Payments',
    'depends': ['sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/settlement_queue_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
