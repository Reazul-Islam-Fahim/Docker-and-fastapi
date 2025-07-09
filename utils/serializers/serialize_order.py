def serialize_order(order):
    return {
        "id": order.id,
        "total_amount": order.total_amount,
        "is_paid": order.is_paid,
        "status": order.status,
        "delivery_status": order.delivery_status,
        "delivery_charge": order.delivery_charge,
        "placed_at": order.placed_at,
        "user_id": order.user_id,
        "shipping_address_id": order.shipping_address_id,
    }


def serialize_order_item(item):
    return {
        "id": item.id,
        "product_id": item.product_id,
        "quantity": item.quantity,
        "cost": item.cost,
        "product_image": item.products.highlighted_image if item.products else None
    }
