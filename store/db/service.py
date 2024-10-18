from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from store.db.repository import OrderItemRepository, OrderRepository, ProductRepository

class OrderService:
    def __init__(self, connection):
        self.connection = connection
        self.product_repo = ProductRepository(connection)
        self.order_repo = OrderRepository(connection)
        self.order_item_repo = OrderItemRepository(connection)

    def update_item(self, customer_id, product_id, action):
        # Fetch the product and order
        product = self.product_repo.get_by_id(product_id)
        order = self.order_repo.get_or_create(customer_id)

        # Fetch or create the order item
        order_item = self.order_item_repo.get_or_create(order.id, product.id)

        # Update quantity based on the action
        if action == 'add':
            new_quantity = order_item.quantity + 1
        elif action == 'remove':
            new_quantity = order_item.quantity - 1

        if new_quantity > 0:
            self.order_item_repo.update_quantity(order_item.id, new_quantity)
        else:
            self.order_item_repo.delete(order_item.id)
        
        return "Item was updated successfully"
