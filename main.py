"""Skewer: SKU generator and receipt generator (runs in the browser via PyScript)."""

from datetime import datetime
from html import escape

from pyscript import document

# Menu for the receipt page: (name, price in pesos).
# Replace these with the items from your own Skills Test.
MENU = [
    ("Americano", 99),
    ("Spanish Latte", 129),
    ("Silky Brew Mane", 189),
    ("Affogato", 159),
    ("Caramel Macchiato", 129),
]  


def get(element_id):
    """Shortcut for finding an element on the page."""
    return document.getElementById(element_id)


def clean(text):
    """Keep only letters and numbers, in uppercase."""
    return "".join(ch for ch in text if ch.isalnum()).upper()


def show_error(element_id, message):
    """Show a red error message inside the given element."""
    get(element_id).innerHTML = f'<span class="error">{message}</span>'


# ---------- Page switching ----------

def show_sku_page(event):
    get("sku-page").style.display = "block"
    get("receipt-page").style.display = "none"
    get("nav-sku").classList.add("active")
    get("nav-receipt").classList.remove("active")


def show_receipt_page(event):
    get("sku-page").style.display = "none"
    get("receipt-page").style.display = "block"
    get("nav-sku").classList.remove("active")
    get("nav-receipt").classList.add("active")


# ---------- SKU generator ----------

def generate_sku(event):
    """SKU format: CC-PPP-QQQ (category, product, quantity)."""
    category = get("category").value
    name = get("productName").value.strip()

    # Validate the product name
    if clean(name) == "":
        show_error("skuResult", "Please enter a product name.")
        return

    # Validate the quantity (0 to 999)
    try:
        quantity = int(get("stockQty").value)
    except ValueError:
        quantity = -1
    if quantity < 0 or quantity > 999:
        show_error("skuResult", "Stock quantity must be from 0 to 999.")
        return

    category_code = clean(category)[:2]
    product_code = clean(name).ljust(3, "X")[:3]
    sku = f"{category_code}-{product_code}-{quantity:03d}"

    get("skuResult").innerHTML = f"""
        <div>Your SKU</div>
        <div class="sku-code">{sku}</div>
        <div class="small">
            {category_code} = {escape(category)} |
            {product_code} = {escape(name)} |
            {quantity:03d} = in stock
        </div>"""


# ---------- Receipt generator ----------

def build_menu():
    """Draw the menu with a quantity box for each item."""
    rows = ""
    for index, (name, price) in enumerate(MENU):
        rows += f"""
        <div class="menu-item">
            <span class="name">{name}</span>
            <span class="price">₱{price}</span>
            <input type="number" id="qty{index}" value="0" min="0" max="99">
        </div>"""
    get("menu").innerHTML = rows


def create_order(event):
    """Build the receipt from the customer name and chosen quantities."""
    customer = get("customerName").value.strip()
    if customer == "":
        show_error("summary", "Please enter the customer name.")
        return

    lines = ""
    total = 0
    for index, (name, price) in enumerate(MENU):
        try:
            qty = int(get(f"qty{index}").value)
        except ValueError:
            qty = 0
        if qty > 0:
            total += price * qty
            lines += f'<div class="row"><span>{qty} x {name}</span><span>₱{price * qty:,.2f}</span></div>'

    if lines == "":
        show_error("summary", "Please choose at least one item (quantity 1 or more).")
        return

    now = datetime.now()
    get("summary").innerHTML = f"""
        <div class="receipt">
            <h3>OBMC Entrep Fair</h3>
            <div class="center">Group 1 - Coffee Shop</div>
            <div class="center">{now:%b %d, %Y %I:%M %p} | OR-{now:%H%M%S}</div>
            <hr>
            <div class="row"><span>Customer:</span><span>{escape(customer)}</span></div>
            <hr>
            {lines}
            <div class="row total"><span>TOTAL</span><span>₱{total:,.2f}</span></div>
            <div class="center">Thank you for your purchase!</div>
        </div>"""


build_menu()
