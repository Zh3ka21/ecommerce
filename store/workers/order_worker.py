import json

import pika

from store.messaging import send_to_canceled_channel, send_to_confirmed_channel


def process_order_message(order_data) -> None:
    """Process the order message by confirming or canceling the order."""
    # Simulate an employee decision
    print("Processing order:", order_data)
    action = input("Confirm or cancel the order? (confirm/cancel): ").strip().lower()

    if action == "confirm":
        confirmed_data = {
            "order_id": order_data["order_id"],
            "items": order_data["items"],
            "total_amount": order_data["total_amount"],
        }
        send_to_confirmed_channel(confirmed_data)
        print(f"Order {order_data['order_id']} confirmed and sent to confirmed channel.")
    elif action == "cancel":
        canceled_data = {
            "order_id": order_data["order_id"],
            "reason": "Employee canceled manually",
            "lost_revenue": order_data["total_amount"],
        }
        send_to_canceled_channel(canceled_data)
        print(f"Order {order_data['order_id']} canceled and sent to canceled channel.")
    else:
        print("Invalid action. Skipping order.")

def callback(ch, method, properties, body) -> None:
    """Callback to process incoming messages."""
    order_data = json.loads(body)
    process_order_message(order_data)

def start_worker() -> None:
    """Start the worker to consume messages from the 'order_queue'."""
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="order_queue")
    channel.basic_consume(queue="order_queue", on_message_callback=callback, auto_ack=True)
    print("Worker started. Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
