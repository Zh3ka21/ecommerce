from .utils import send_to_queue


def send_order_to_queue(order_data: dict) -> None:
    """Send order details to the 'order_queue'."""
    send_to_queue("order_queue", order_data)

def send_to_canceled_channel(canceled_data: dict) -> None:
    """Send canceled order details to the 'canceled_orders' channel."""
    send_to_queue("canceled_orders", canceled_data)

def send_to_confirmed_channel(confirmed_data: dict) -> None:
    """Send confirmed order details to the 'confirmed_orders' channel."""
    send_to_queue("confirmed_orders", confirmed_data)
