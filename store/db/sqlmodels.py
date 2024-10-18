from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import MetaData

metadata = MetaData()

product_table = Table('product', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255)),
)

order_table = Table('order', metadata,
    Column('id', Integer, primary_key=True),
    Column('customer_id', Integer, ForeignKey('customer.id')),
    Column('complete', Boolean, default=False),
)

order_item_table = Table('order_item', metadata,
    Column('id', Integer, primary_key=True),
    Column('order_id', Integer, ForeignKey('order.id')),
    Column('product_id', Integer, ForeignKey('product.id')),
    Column('quantity', Integer, default=0),
)
