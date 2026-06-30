#input_type_name: RecommendProductsInput
#output_type_name: RecommendProductsResult
#function_name: recommend_products

from pydantic import BaseModel
from lemma_sdk import FunctionContext


class RecommendProductsInput(BaseModel):
    budget: int
    category: str


class RecommendProductsResult(BaseModel):
    product_name: str
    price: int
    color: str
    message: str


async def recommend_products(
    ctx: FunctionContext,
    data: RecommendProductsInput
) -> RecommendProductsResult:

    products = [
        {
            "name": "Oversized Hoodie",
            "category": "hoodie",
            "price": 1999,
            "color": "Black"
        },
        {
            "name": "Graphic T-Shirt",
            "category": "t-shirt",
            "price": 999,
            "color": "White"
        },
        {
            "name": "Cargo Pants",
            "category": "pants",
            "price": 1799,
            "color": "Olive"
        },
        {
            "name": "Denim Jacket",
            "category": "jacket",
            "price": 2499,
            "color": "Blue"
        }
    ]

    for product in products:
        if (
            product["category"].lower() == data.category.lower()
            and product["price"] <= data.budget
        ):
            return RecommendProductsResult(
                product_name=product["name"],
                price=product["price"],
                color=product["color"],
                message="Recommended product found."
            )

    return RecommendProductsResult(
        product_name="",
        price=0,
        color="",
        message="No products found matching your criteria."
    )