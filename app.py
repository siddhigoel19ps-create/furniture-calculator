# =============================================================================
#  Heritage Oak Furniture Studio - Furniture Cost Calculator
#  Course : Python Programming for Business Students (End-Term Project)
#  Tools  : Python + Streamlit (no external database)
#
#  What this app does:
#  A customer chooses furniture, material, size, quantity, delivery, etc.
#  The app then calculates an estimated bill with a full cost breakdown.
#
#  Run it with:   streamlit run app.py
# =============================================================================

import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE SETTINGS  (must be the first Streamlit command in the file)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Heritage Oak Furniture Studio",
    page_icon="🛋️",
    layout="wide",
)

# -----------------------------------------------------------------------------
# 2. PRICE LIST AND BUSINESS RULES  (all pricing assumptions live here)
# -----------------------------------------------------------------------------
# Dictionary: furniture category -> base price per item (in Indian rupees).
# We use a dictionary because we can look up a price directly by its name.
FURNITURE_PRICES = {
    "Sofa": 25000,
    "Bed": 30000,
    "Dining Table": 22000,
    "Wardrobe": 28000,
    "Study Table": 9000,
}

# Fixed charges (assumptions for this project)
CUSTOMIZATION_CHARGE_PER_ITEM = 1500   # Rs per item if customization is chosen
STANDARD_DELIVERY_CHARGE = 1500        # Rs per order
EXPRESS_DELIVERY_CHARGE = 3000         # Rs per order
PREMIUM_EXTRA_DISCOUNT = 5             # extra % discount for Premium customers

# Limits used for input validation
MIN_QUANTITY = 1
MAX_QUANTITY = 50

# Default values of every input (also used by the Reset button)
DEFAULTS = {
    "category": "Sofa",
    "material": "Engineered Wood",
    "size": "Medium",
    "quantity": 1,
    "customization": False,
    "delivery": "Standard",
    "customer_type": "Regular",
}


# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def format_rupees(amount):
    """Convert a number into Indian rupee format, e.g. 150000 -> Rs 1,50,000."""
    # Remember the sign, then work with a positive whole number
    sign = ""
    if amount < 0:
        sign = "- "
        amount = -amount
    digits = str(round(amount))

    # Indian style: last 3 digits together, then groups of 2 digits
    if len(digits) <= 3:
        return sign + "₹" + digits
    last_three = digits[-3:]
    remaining = digits[:-3]
    groups = []                      # a list that will hold the 2-digit groups
    while len(remaining) > 2:
        groups.insert(0, remaining[-2:])   # add the group at the front
        remaining = remaining[:-2]
    if remaining != "":
        groups.insert(0, remaining)
    groups.append(last_three)
    return sign + "₹" + ",".join(groups)


def calculate_bill(category, material, size, quantity,
                   wants_customization, delivery, customer_type):
    """Calculate the full furniture bill and return all the numbers in a dictionary.

    Raises ValueError with a friendly message if any input is invalid.
    """
    # ---- Step 1: Validate the inputs so the app never crashes ----
    if category not in FURNITURE_PRICES:
        raise ValueError("Please select a valid furniture category.")

    try:
        quantity = int(quantity)             # make sure quantity is a whole number
    except (TypeError, ValueError):
        raise ValueError("Quantity must be a whole number.")

    if quantity < MIN_QUANTITY:
        raise ValueError("Quantity must be at least 1. Zero or negative is not allowed.")
    if quantity > MAX_QUANTITY:
        raise ValueError("For more than 50 items, please contact our store for a bulk quote.")

    # ---- Step 2: Base price from the dictionary ----
    base_price = FURNITURE_PRICES[category]

    # ---- Step 3: Material adjustment (percentage of the base price) ----
    if material == "Engineered Wood":
        material_adjustment = 0                          # standard material
    elif material == "Solid Wood":
        material_adjustment = round(base_price * 0.30)   # +30%
    elif material == "Metal":
        material_adjustment = round(base_price * 0.10)   # +10%
    else:
        raise ValueError("Please select a valid material.")

    # ---- Step 4: Size adjustment (percentage of the base price) ----
    if size == "Small":
        size_adjustment = -round(base_price * 0.10)      # -10% (less material used)
    elif size == "Medium":
        size_adjustment = 0                              # standard size
    elif size == "Large":
        size_adjustment = round(base_price * 0.25)       # +25%
    else:
        raise ValueError("Please select a valid size.")

    # ---- Step 5: Price of ONE item and total for all items ----
    price_per_item = base_price + material_adjustment + size_adjustment
    furniture_total = price_per_item * quantity

    # ---- Step 6: Customization charges (bool: True / False from the checkbox) ----
    if wants_customization:
        customization_charges = CUSTOMIZATION_CHARGE_PER_ITEM * quantity
    else:
        customization_charges = 0

    # Value of the goods (used to decide the discount, delivery is NOT discounted)
    goods_total = furniture_total + customization_charges

    # ---- Step 7: Delivery charges ----
    if delivery == "Standard":
        delivery_charges = STANDARD_DELIVERY_CHARGE
    elif delivery == "Express":
        delivery_charges = EXPRESS_DELIVERY_CHARGE
    else:
        raise ValueError("Please select a valid delivery option.")

    # ---- Step 8: Subtotal  (formula given in the project brief) ----
    subtotal = goods_total + delivery_charges

    # ---- Step 9: Discount rule ----
    # Rule A: bigger orders get a bigger discount (based on goods_total)
    if goods_total >= 150000:
        discount_percent = 10
    elif goods_total >= 75000:
        discount_percent = 7
    elif goods_total >= 40000:
        discount_percent = 5
    else:
        discount_percent = 0

    # Rule B: Premium customers get an extra discount
    if customer_type == "Premium":
        discount_percent = discount_percent + PREMIUM_EXTRA_DISCOUNT
    elif customer_type != "Regular":
        raise ValueError("Please select a valid customer type.")

    discount_amount = round(goods_total * discount_percent / 100)

    # ---- Step 10: Final bill (max() makes sure it can never be negative) ----
    final_bill = max(subtotal - discount_amount, 0)

    # Send all results back together in one dictionary
    return {
        "base_price": base_price,
        "material_adjustment": material_adjustment,
        "size_adjustment": size_adjustment,
        "price_per_item": price_per_item,
        "quantity": quantity,
        "furniture_total": furniture_total,
        "customization_charges": customization_charges,
        "goods_total": goods_total,
        "delivery_charges": delivery_charges,
        "subtotal": subtotal,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "final_bill": final_bill,
    }


def reset_form():
    """Put every input back to its default value (used by the Reset button)."""
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


# -----------------------------------------------------------------------------
# 4. STYLING  (small amount of CSS for a warm wooden furniture-store look)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #FAF3E8; }
    [data-testid="stWidgetLabel"] p, .stMarkdown p, .stMarkdown li,
    h2, h3 { color: #3E2723 !important; }
    .store-banner {
        background: linear-gradient(90deg, #5D3A1A, #8B5A2B);
        padding: 24px; border-radius: 12px; text-align: center;
    }
    .store-banner h1 { color: #FFF8EE !important; margin: 0; }
    .store-banner p  { color: #F4E3C8 !important; margin: 6px 0 0 0; font-size: 1.05rem; }
    .bill-box {
        background-color: #5D3A1A; padding: 18px; border-radius: 12px;
        text-align: center; margin-top: 12px;
    }
    .bill-box p  { color: #F4E3C8 !important; margin: 0; }
    .bill-box h2 { color: #F4C98B !important; margin: 4px 0 0 0; font-size: 2.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. STORE HEADER AND WELCOME MESSAGE
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="store-banner">
        <h1>🛋️ Heritage Oak Furniture Studio</h1>
        <p>Furniture Cost Calculator – estimate your bill before you order</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")
st.write(
    "Welcome! Choose your furniture and options on the left. "
    "Your estimated bill updates instantly on the right."
)

# Give every input its starting value the first time the page opens
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Two columns: inputs on the left, results on the right
left_column, right_column = st.columns(2, gap="large")

# -----------------------------------------------------------------------------
# 6. USER INPUTS (left column) - 7 widgets of 4 different types
# -----------------------------------------------------------------------------
with left_column:
    with st.container(border=True):
        st.subheader("1. Choose your furniture")
        # Widget 1: selectbox (dropdown) - keys come from the price dictionary
        category = st.selectbox(
            "Furniture category", list(FURNITURE_PRICES.keys()), key="category"
        )
        # Widget 2: selectbox - material
        material = st.selectbox(
            "Material", ["Engineered Wood", "Solid Wood", "Metal"], key="material"
        )
        # Widget 3: radio buttons - size
        size = st.radio(
            "Size", ["Small", "Medium", "Large"], horizontal=True, key="size"
        )
        # Widget 4: number_input - quantity (min/max stop invalid values)
        quantity = st.number_input(
            "Quantity (number of items)",
            min_value=MIN_QUANTITY,
            max_value=MAX_QUANTITY,
            step=1,
            key="quantity",
        )

    with st.container(border=True):
        st.subheader("2. Extras and delivery")
        # Widget 5: checkbox - returns True or False
        wants_customization = st.checkbox(
            f"Add customization (+{format_rupees(CUSTOMIZATION_CHARGE_PER_ITEM)} per item)",
            key="customization",
        )
        # Widget 6: selectbox - delivery type
        delivery = st.selectbox(
            "Delivery type", ["Standard", "Express"], key="delivery"
        )
        st.caption(
            f"Standard delivery: {format_rupees(STANDARD_DELIVERY_CHARGE)}  |  "
            f"Express delivery: {format_rupees(EXPRESS_DELIVERY_CHARGE)}"
        )

    with st.container(border=True):
        st.subheader("3. Customer details")
        # Widget 7: radio buttons - customer type
        customer_type = st.radio(
            "Customer type", ["Regular", "Premium"], horizontal=True, key="customer_type"
        )

    # Reset button: on_click runs reset_form() before the page refreshes
    st.button("🔄 Reset / Start over", on_click=reset_form)

# -----------------------------------------------------------------------------
# 7. CALCULATION WITH ERROR HANDLING
# -----------------------------------------------------------------------------
try:
    bill = calculate_bill(
        category, material, size, quantity,
        wants_customization, delivery, customer_type,
    )
except ValueError as error:
    # Friendly message for invalid input - the app does not crash
    with right_column:
        st.error(f"⚠️ {error}")
    st.stop()
except Exception:
    # Safety net for any unexpected problem
    with right_column:
        st.error("⚠️ Something went wrong. Please check your inputs and try again.")
    st.stop()

# -----------------------------------------------------------------------------
# 8. RESULTS (right column) - live summary, breakdown and final bill
# -----------------------------------------------------------------------------
with right_column:
    with st.container(border=True):
        st.subheader("🧾 Live order summary")
        st.markdown(
            f"- **Item:** {bill['quantity']} × {category} ({material}, {size})\n"
            f"- **Customization:** {'Yes' if wants_customization else 'No'}\n"
            f"- **Delivery:** {delivery}\n"
            f"- **Customer type:** {customer_type}"
        )

    with st.container(border=True):
        st.subheader("📊 Itemized cost breakdown")

        # A list of (label, amount) pairs - we loop over it to build the table
        breakdown_rows = [
            (f"Base price ({format_rupees(bill['base_price'])} × {bill['quantity']})",
             bill["base_price"] * bill["quantity"]),
            (f"Material adjustment ({material})",
             bill["material_adjustment"] * bill["quantity"]),
            (f"Size adjustment ({size})",
             bill["size_adjustment"] * bill["quantity"]),
            ("Furniture total", bill["furniture_total"]),
            ("Customization charges", bill["customization_charges"]),
            (f"Delivery charges ({delivery})", bill["delivery_charges"]),
            ("Subtotal", bill["subtotal"]),
            (f"Discount ({bill['discount_percent']}% on furniture + customization)",
             -bill["discount_amount"]),
        ]

        # Build a markdown table row by row using a for loop
        table_text = "| Cost item | Amount |\n|---|---:|\n"
        for label, amount in breakdown_rows:
            table_text = table_text + f"| {label} | {format_rupees(amount)} |\n"
        st.markdown(table_text)

    # Final bill shown prominently
    st.markdown(
        f"""
        <div class="bill-box">
            <p>ESTIMATED FINAL BILL</p>
            <h2>{format_rupees(bill['final_bill'])}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tell the customer which discount they received and why
    if bill["discount_percent"] > 0:
        st.success(f"🎉 You saved {format_rupees(bill['discount_amount'])} "
                   f"({bill['discount_percent']}% discount applied).")
    else:
        st.info("Order goods worth ₹40,000 or more to unlock a discount.")

# -----------------------------------------------------------------------------
# 9. PRICING ASSUMPTIONS (clearly explained for the customer and examiner)
# -----------------------------------------------------------------------------
with st.expander("📘 Price list and pricing rules (assumptions)"):
    st.markdown("**Base price per item**")
    price_text = "| Category | Base price |\n|---|---:|\n"
    for name, price in FURNITURE_PRICES.items():
        price_text = price_text + f"| {name} | {format_rupees(price)} |\n"
    st.markdown(price_text)

    st.markdown(
        f"""
**Adjustments (percentage of base price)**
- Material: Engineered Wood +0%, Solid Wood +30%, Metal +10%
- Size: Small −10%, Medium +0%, Large +25%

**Charges**
- Customization: {format_rupees(CUSTOMIZATION_CHARGE_PER_ITEM)} per item
- Delivery (per order): Standard {format_rupees(STANDARD_DELIVERY_CHARGE)}, Express {format_rupees(EXPRESS_DELIVERY_CHARGE)}

**Discount rule** (on furniture + customization; delivery is not discounted)
- Goods value ₹40,000 or more: 5%  |  ₹75,000 or more: 7%  |  ₹1,50,000 or more: 10%
- Premium customers get an extra 5%

**Formulas**
- Subtotal = (Base + Material + Size) × Quantity + Customization + Delivery
- Final Bill = Subtotal − Discount (never below ₹0)

All prices are estimates in Indian rupees and are assumed to include GST.
        """
    )
