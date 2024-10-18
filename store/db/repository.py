from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound

from .sqlmodels import (
    product_table,
    order_table,
    order_item_table,
)

class ProductRepository:
    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, product_id):
        stmt = select(product_table).where(product_table.c.id == product_id)
        result = self.connection.execute(stmt).fetchone()
        if not result:
            raise NoResultFound("Product not found")
        return result


class OrderRepository:
    def __init__(self, connection):
        self.connection = connection

    def get_or_create(self, customer_id, complete=False):
        # Try to find an existing order
        stmt = select(order_table).where(order_table.c.customer_id == customer_id, order_table.c.complete == complete)
        order = self.connection.execute(stmt).fetchone()

        if not order:
            # If no order exists, create a new one
            stmt = insert(order_table).values(customer_id=customer_id, complete=complete)
            self.connection.execute(stmt)
            self.connection.commit()
            order = self.connection.execute(stmt).fetchone()

        return order


class OrderItemRepository:
    def __init__(self, connection):
        self.connection = connection

    def get_or_create(self, order_id, product_id):
        # Try to find an existing order item
        stmt = select(order_item_table).where(order_item_table.c.order_id == order_id, order_item_table.c.product_id == product_id)
        order_item = self.connection.execute(stmt).fetchone()

        if not order_item:
            # If no order item exists, create a new one
            stmt = insert(order_item_table).values(order_id=order_id, product_id=product_id, quantity=1)
            self.connection.execute(stmt)
            self.connection.commit()
            order_item = self.connection.execute(stmt).fetchone()

        return order_item

    def update_quantity(self, order_item_id, new_quantity):
        stmt = update(order_item_table).where(order_item_table.c.id == order_item_id).values(quantity=new_quantity)
        self.connection.execute(stmt)
        self.connection.commit()

    def delete(self, order_item_id):
        stmt = delete(order_item_table).where(order_item_table.c.id == order_item_id)
        self.connection.execute(stmt)
        self.connection.commit()
