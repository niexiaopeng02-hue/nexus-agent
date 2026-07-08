from collections.abc import Awaitable, Callable

from pydantic import BaseModel, Field

from app.services.store import store


class OrderInput(BaseModel):
    order_id: str


class InventoryInput(BaseModel):
    product_id: str


class ProductSearchInput(BaseModel):
    query: str


class TicketInput(BaseModel):
    summary: str = Field(min_length=3)
    category: str = "technical_support"
    priority: str = "normal"
    customer_email: str | None = None


class HandoffInput(BaseModel):
    reason: str
    conversation_id: str | None = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_model: type[BaseModel]
    handler: Callable[[BaseModel], Awaitable[dict]]

    class Config:
        arbitrary_types_allowed = True


async def get_order_status(payload: BaseModel) -> dict:
    data = payload.model_dump()
    order = store.orders.get(data["order_id"])
    if not order:
        return {"found": False, "message": "Order not found"}
    return {"found": True, **order}


async def check_inventory(payload: BaseModel) -> dict:
    data = payload.model_dump()
    inventory = store.inventory.get(data["product_id"])
    if not inventory:
        return {"found": False, "message": "Inventory record not found"}
    product = store.products.get(data["product_id"], {})
    return {"found": True, "product_name": product.get("name"), **inventory}


async def search_products(payload: BaseModel) -> dict:
    query = payload.model_dump()["query"].lower()
    matches = [
        product for product in store.products.values() if query in product["name"].lower() or query in product["description"].lower()
    ]
    return {"results": matches}


async def create_support_ticket(payload: BaseModel) -> dict:
    return store.create_ticket(**payload.model_dump())


async def create_handoff_request(payload: BaseModel) -> dict:
    return store.create_handoff(**payload.model_dump())


TOOLS: dict[str, ToolDefinition] = {
    "get_order_status": ToolDefinition(
        name="get_order_status", description="Look up a NovaTech demo order by order id.", input_model=OrderInput, handler=get_order_status
    ),
    "check_inventory": ToolDefinition(
        name="check_inventory",
        description="Check demo inventory for a NovaTech product.",
        input_model=InventoryInput,
        handler=check_inventory,
    ),
    "search_products": ToolDefinition(
        name="search_products", description="Search demo products.", input_model=ProductSearchInput, handler=search_products
    ),
    "create_support_ticket": ToolDefinition(
        name="create_support_ticket", description="Create a support ticket.", input_model=TicketInput, handler=create_support_ticket
    ),
    "create_handoff_request": ToolDefinition(
        name="create_handoff_request",
        description="Create a human handoff request.",
        input_model=HandoffInput,
        handler=create_handoff_request,
    ),
}


async def execute_tool(name: str, raw_input: dict) -> dict:
    tool = TOOLS[name]
    payload = tool.input_model(**raw_input)
    try:
        output = await tool.handler(payload)
        store.tool_logs.append({"tool_name": name, "status": "success", "input": raw_input, "output": output})
        return output
    except Exception as exc:
        store.tool_logs.append({"tool_name": name, "status": "error", "input": raw_input, "error": str(exc)})
        raise
