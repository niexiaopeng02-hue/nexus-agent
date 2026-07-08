from collections.abc import Awaitable, Callable

from pydantic import BaseModel, ConfigDict, Field

from app.repositories import BusinessRepository


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
    handler: Callable[[BusinessRepository, BaseModel], Awaitable[dict]]

    model_config = ConfigDict(arbitrary_types_allowed=True)


async def get_order_status(repo: BusinessRepository, payload: BaseModel) -> dict:
    data = payload.model_dump()
    order = await repo.get_order(data["order_id"])
    if not order:
        return {"found": False, "message": "Order not found"}
    return {"found": True, **order}


async def check_inventory(repo: BusinessRepository, payload: BaseModel) -> dict:
    data = payload.model_dump()
    inventory = await repo.get_inventory(data["product_id"])
    if not inventory:
        return {"found": False, "message": "Inventory record not found"}
    return {"found": True, **inventory}


async def search_products(repo: BusinessRepository, payload: BaseModel) -> dict:
    query = payload.model_dump()["query"].lower()
    matches = await repo.search_products(query)
    return {"results": matches}


async def create_support_ticket(repo: BusinessRepository, payload: BaseModel) -> dict:
    return await repo.create_ticket(**payload.model_dump())


async def create_handoff_request(repo: BusinessRepository, payload: BaseModel) -> dict:
    return await repo.create_handoff(**payload.model_dump())


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


async def execute_tool(repo: BusinessRepository, name: str, raw_input: dict) -> dict:
    tool = TOOLS[name]
    payload = tool.input_model(**raw_input)
    try:
        output = await tool.handler(repo, payload)
        await repo.log_tool(name, "success", raw_input, output)
        return output
    except Exception as exc:
        await repo.log_tool(name, "error", raw_input, {"error": str(exc)})
        raise
