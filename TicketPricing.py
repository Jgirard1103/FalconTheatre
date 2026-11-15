"""
The Falcon Performing Arts Center - Streamlit Box Office
Fall 2026 CS 230 Teamwork 4
"""

import os
from datetime import date

import streamlit as st

# =============================================================================
# PART 1: DATA DESIGN
# =============================================================================
# Why it is built this way:
#
# 1. SHOW_PRICES is a NESTED DICTIONARY:  show -> {seating section -> price}.
#    Every show carries its OWN seating dictionary, so Improv Comedy Night
#    simply has {"General Admission": 20, "VIP Table": 40} instead of
#    Orchestra / Mezzanine / Balcony. Because the code always looks up
#    SHOW_PRICES[show][section], there is NO special-case code for Improv.
#    Adding a new show (or a new section) only means adding to this dictionary.
#
# 2. SHOW_DESCRIPTIONS is keyed by show name, so the description lookup is a
#    single SHOW_DESCRIPTIONS[show]. (Kept separate from prices so the price
#    dictionary only holds numbers we do math on.)
#
# 3. ADD_ON_PRICES is a dictionary (add-on -> price) rather than a list,
#    because each add-on has its own price. Its keys fill the multiselect, and
#    we loop over the selected names to look up and sum each price.
#
# 4. Single-value rules are NAMED CONSTANTS (ALL_CAPS) so nothing is hard-coded
#    inside the logic: parking fee, student discount rate, max add-ons, and
#    min/max tickets.
#
# 5. SHOW_IMAGES maps show -> image file in the images/ folder (relative path).
#    A show with no image of its own falls back to the arts-center banner.
# =============================================================================

# ---- Constants -------------------------------------------------------------
PARKING_FEE = 10.00          # flat fee per order
STUDENT_DISCOUNT_RATE = 0.20  # 20% off the ticket subtotal only
MAX_ADD_ONS = 3              # most add-ons allowed per order
MIN_TICKETS = 1              # fewest tickets per order
MAX_TICKETS = 8              # most tickets per order

# ---- Nested dictionary: show -> {seating section -> ticket price} ----------
SHOW_PRICES = {
    "The Glass Menagerie": {
        "Orchestra": 48.00,
        "Mezzanine": 36.00,
        "Balcony": 24.00,
    },
    "Into the Woods": {
        "Orchestra": 62.00,
        "Mezzanine": 48.00,
        "Balcony": 32.00,
    },
    "Symphony Pops Night": {
        "Orchestra": 55.00,
        "Mezzanine": 42.00,
        "Balcony": 28.00,
    },
    "Improv Comedy Night": {  # Special Event: different seating!
        "General Admission": 20.00,
        "VIP Table": 40.00,
    },
}

# ---- Show descriptions, keyed by show name ---------------------------------
SHOW_DESCRIPTIONS = {
    "The Glass Menagerie": "A moving classic of memory and family.",
    "Into the Woods": "A musical fairy-tale mash-up.",
    "Symphony Pops Night": "Movie and Broadway favorites, live.",
    "Improv Comedy Night": "Unscripted laughs built from audience suggestions.",
}

# ---- Add-ons: add-on name -> price (per order) -----------------------------
ADD_ON_PRICES = {
    "Souvenir Program": 8.00,
    "Intermission Snack Box": 12.00,
    "Coat Check": 4.00,
    "Signed Poster": 15.00,
    "Backstage Tour": 25.00,
}

# ---- Images (relative paths inside the images/ subfolder) ------------------
IMAGE_FOLDER = "images"
BANNER_IMAGE = "falcon_performing_arts_center.jpg"
SHOW_IMAGES = {
    "The Glass Menagerie": "the_glass_menagerie.jpg",
    "Into the Woods": "into_the_woods.jpg",
    "Symphony Pops Night": "symphony_pops_night.jpg",
    # "Improv Comedy Night" has no image yet -> the banner is used instead.
}


# =============================================================================
# HELPERS
# =============================================================================
def money(amount):
    """Format a number as dollars with two decimals, e.g. 116 -> '$116.00'."""
    return f"${amount:,.2f}"


def image_path(filename):
    """Build a path to an image relative to this file (works locally + cloud)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, IMAGE_FOLDER, filename)


def calculate_order(show, section, num_tickets, add_ons, is_student, wants_parking):
    """Return an itemized breakdown of the order as a dictionary.

    Order of operations: ticket subtotal -> student discount (tickets only)
    -> add-ons -> parking -> grand total.
    """
    # Nested lookup: show -> its seating dictionary -> section -> ticket price
    seating_options = SHOW_PRICES[show]
    ticket_price = seating_options[section]
    ticket_subtotal = ticket_price * num_tickets

    # Student discount applies to the ticket subtotal ONLY
    discount = ticket_subtotal * STUDENT_DISCOUNT_RATE if is_student else 0.0

    # Sum the add-ons by looping and looking up each price
    add_on_total = 0.0
    for add_on in add_ons:
        add_on_total += ADD_ON_PRICES[add_on]

    parking = PARKING_FEE if wants_parking else 0.0

    grand_total = (ticket_subtotal - discount) + add_on_total + parking

    return {
        "ticket_price": ticket_price,
        "ticket_subtotal": ticket_subtotal,
        "discount": discount,
        "add_on_total": add_on_total,
        "parking": parking,
        "grand_total": grand_total,
    }


# =============================================================================
# PART 2: THE APP
# =============================================================================
st.set_page_config(
    page_title="Falcon Performing Arts Center - Box Office",
    page_icon="🎭",
    layout="wide",
)

# A little styling for a polished look
st.markdown(
    """
    <style>
        .total-box {
            background: linear-gradient(135deg, #7a1f2b, #b8860b);
            color: white;
            padding: 18px 22px;
            border-radius: 12px;
            text-align: center;
            margin-top: 8px;
        }
        .total-box h2 { margin: 0; color: white; }
        .total-box p  { margin: 0; opacity: 0.9; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Sidebar: patron info ---------------------------------------------------
st.sidebar.header("🎟️ Patron Info")
patron_name = st.sidebar.text_input("Patron name", placeholder="Enter your full name")
is_student = st.sidebar.toggle(
    f"Student discount ({STUDENT_DISCOUNT_RATE:.0%} off tickets)"
)
wants_parking = st.sidebar.checkbox(f"Reserved parking ({money(PARKING_FEE)})")
st.sidebar.caption("Student discount applies to the ticket subtotal only.")

# ---- Header / banner --------------------------------------------------------
st.title("🎭 The Falcon Performing Arts Center")
st.subheader("Box Office")
st.image(image_path(BANNER_IMAGE), use_container_width=True)

st.header("1. Choose Your Show")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    # Options come straight from the dictionary keys
    show = st.selectbox("Show", list(SHOW_PRICES.keys()))

    # Seating options come from THIS show's nested dictionary
    seating_options = SHOW_PRICES[show]
    section = st.radio(
        "Seating section",
        list(seating_options.keys()),
        format_func=lambda name: f"{name} ({money(seating_options[name])})",
        key=f"section_{show}",  # new key per show so the radio resets cleanly
    )

    num_tickets = st.slider(
        "Number of tickets", min_value=MIN_TICKETS, max_value=MAX_TICKETS, value=MIN_TICKETS
    )

    performance_date = st.date_input("Performance date", value=date.today())

    selected_add_ons = st.multiselect(
        f"Add-ons (choose up to {MAX_ADD_ONS})",
        list(ADD_ON_PRICES.keys()),
        format_func=lambda name: f"{name} ({money(ADD_ON_PRICES[name])})",
    )

with right_col:
    # Show image changes with the selection (banner is the fallback)
    show_image_file = SHOW_IMAGES.get(show, BANNER_IMAGE)
    st.image(image_path(show_image_file), caption=show, use_container_width=True)
    st.subheader(show)
    st.write(SHOW_DESCRIPTIONS[show])

st.divider()

# ---- Price breakdown (with validation) -------------------------------------
st.header("2. Price Breakdown")

if len(selected_add_ons) > MAX_ADD_ONS:
    # Validation rule: too many add-ons -> error and NO total
    st.error(
        f"You selected {len(selected_add_ons)} add-ons. "
        f"Please choose no more than {MAX_ADD_ONS} add-ons to see your total."
    )
else:
    order = calculate_order(
        show, section, num_tickets, selected_add_ons, is_student, wants_parking
    )

    breakdown_col, summary_col = st.columns([1, 1], gap="large")

    with breakdown_col:
        st.write(
            f"**Tickets:** {num_tickets} × {money(order['ticket_price'])} "
            f"({section})"
        )
        st.write(f"Ticket subtotal: **{money(order['ticket_subtotal'])}**")

        if is_student:
            st.write(
                f"Student discount ({STUDENT_DISCOUNT_RATE:.0%}): "
                f"**-{money(order['discount'])}**"
            )

        if selected_add_ons:
            st.write(f"Add-ons: **{money(order['add_on_total'])}**")
            for add_on in selected_add_ons:
                st.caption(f"• {add_on} — {money(ADD_ON_PRICES[add_on])}")
        else:
            st.write(f"Add-ons: **{money(0)}**")

        st.write(f"Reserved parking: **{money(order['parking'])}**")

        st.markdown(
            f"""
            <div class="total-box">
                <p>Grand Total</p>
                <h2>{money(order['grand_total'])}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Order summary (requires a name) -----------------------------------
    with summary_col:
        st.subheader("Order Summary")
        if patron_name.strip() == "":
            st.warning("Please enter your name in the sidebar to see your order summary.")
        else:
            ticket_word = "ticket" if num_tickets == 1 else "tickets"
            st.success(
                f"Thank you, **{patron_name.strip()}**! Here is your order:"
            )
            st.write(f"🎭 **Show:** {show}")
            st.write(f"📅 **Date:** {performance_date.strftime('%A, %B %d, %Y')}")
            st.write(f"💺 **Seating:** {section}")
            st.write(f"🎟️ **Tickets:** {num_tickets} {ticket_word}")
            if selected_add_ons:
                st.write(f"➕ **Add-ons:** {', '.join(selected_add_ons)}")
            st.write(f"💵 **Total:** {money(order['grand_total'])}")

st.divider()
st.caption("© The Falcon Performing Arts Center — CS 230 Teamwork 4")
