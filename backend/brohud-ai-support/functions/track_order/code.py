#input_type_name: TrackOrderInput
#output_type_name: TrackOrderResult
#function_name: track_order

from pydantic import BaseModel
from lemma_sdk import FunctionContext


class TrackOrderInput(BaseModel):
    order_id: str


class TrackOrderResult(BaseModel):
    found: bool
    order_id: str
    status: str
    estimated_delivery: str
    message: str


MOCK_ORDERS = {
    "BH1001": {
        "status": "Shipped",
        "estimated_delivery": "Tomorrow"
    },
    "BH1002": {
        "status": "Processing",
        "estimated_delivery": "2 business days"
    },
    "BH1003": {
        "status": "Delivered",
        "estimated_delivery": "Delivered on June 25"
    }
}


async def track_order(
    ctx: FunctionContext,
    data: TrackOrderInput
) -> TrackOrderResult:

    order = MOCK_ORDERS.get(data.order_id.upper())

    if order:
        return TrackOrderResult(
            found=True,
            order_id=data.order_id.upper(),
            status=order["status"],
            estimated_delivery=order["estimated_delivery"],
            message=f"Your order is currently {order['status']}."
        )

    return TrackOrderResult(
        found=False,
        order_id=data.order_id.upper(),
        status="Unknown",
        estimated_delivery="N/A",
        message="Order not found."
    )