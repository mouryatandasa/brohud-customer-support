#input_type_name: CreateSupportTicketInput
#output_type_name: CreateSupportTicketResult
#function_name: create_support_ticket

from pydantic import BaseModel
from lemma_sdk import FunctionContext


class CreateSupportTicketInput(BaseModel):
    customer_name: str
    issue: str


class CreateSupportTicketResult(BaseModel):
    ticket_id: str
    status: str
    message: str


async def create_support_ticket(
    ctx: FunctionContext,
    data: CreateSupportTicketInput
) -> CreateSupportTicketResult:

    ticket_id = "SUP1001"

    return CreateSupportTicketResult(
        ticket_id=ticket_id,
        status="Created",
        message=f"Support ticket {ticket_id} has been created successfully."
    )