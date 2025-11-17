import streamlit as st
import pandas as pd
import re

# ---------------------------------------------------
# 1. FULL CATEGORY LOGIC (Your Original Intelligence)
# ---------------------------------------------------
category_keywords = {
    "Tea/Coffee": ["tea", "coffee", "ccd", "café", "cafe", "brew"],
    "Restaurant": ["hotel", "restaurant", "rest", "food", "dine"],
    "Fuel": ["petrol", "diesel", "fuel", "hp", "bunk", "shell"],
    "Groceries/Vegetables": ["veg", "vegetable", "market", "grocery", "supermart"],
    "Daily Essentials": ["milk", "dairy", "bread", "essentials"],
    "Fast Food": ["fast food", "burger", "pizza", "dominos", "kfc", "mcd", "subway"],
    "Bakeries/Sweets": ["bakery", "cake", "pastry", "mithai", "sweet shop", "halwai"],
    "Medical/Pharmacy": ["pharmacy", "chemist", "medical", "medplus", "apollo", "drug store"],
    "Telecom/Internet": ["recharge", "airtel", "jio", "vi", "internet", "broadband", "fiber"],
    "Utilities": ["electricity", "water bill", "gas", "power", "bescom", "bills", "bijli"],
    "Apparel/Fashion": ["clothes", "apparel", "fashion", "menswear", "womenswear", "boutique", "shopper", "max", "lifestyle"],
    "Electronics": ["electronics", "mobile", "ac", "tv", "laptop", "chroma", "reliancedigital", "gadget"],
    "E-commerce": ["amazon", "flipkart", "myntra", "meesho", "snapdeal", "shop", "cart"],
    "Travel/Transport": ["bus", "train", "auto", "ola", "uber", "taxi", "irctc"],
    "Beauty/Salon": ["salon", "parlour", "spa", "beauty", "barber", "haircut"],
    "Government/Tax": ["tax", "municipal", "property tax", "government", "challan"],
    "Education": ["school", "college", "fees", "university", "tuition", "coaching"],
    "Alcohol/Liquor": ["bar", "pub", "liquor", "wine", "beer", "desi", "tasmak"],
    "Others (Large Payments)": ["jewellery", "gold", "debt", "loan", "emi", "insurance", "mutual fund", "broker", "securities"]
}

# ---------------------------------------------------
# 2. FULL LOCATION LOGIC
# ---------------------------------------------------
location_map = {
    "ap": "Andhra Pradesh",
    "gnt": "Andhra Pradesh",
    "vij": "Andhra Pradesh",
    "hyd": "Telangana",
    "tlg": "Telangana",
    "chn": "Tamil Nadu",
    "tnd": "Tamil Nadu",
    "krl": "Kerala",
    "ker": "Kerala",
    "gang": "Sikkim",
    "gangtok": "Sikkim"
}

# ---------------------------------------------------
# Prediction Functions
# ---------------------------------------------------
def predict_category(text: str):
    text = (text or "").lower()
    best = None
    best_score = 0

    for category, keywords in category_keywords.items():
        score = sum(1 for k in keywords if k in text)
        if score > best_score:
            best_score = score
            best = category

    confidence = min(1.0, best_score / 3)
    return best or "Unknown", round(confidence, 2)


def predict_location(text: str):
    text = (text or "").lower()
    for code, state in location_map.items():
        if code in text:
            return state
    return "Unknown"


def extract_amount(text):
    if not isinstance(text, str):
        return 0
    amt = re.search(r"₹\s?([\d,]+)", text)
    if amt:
        try:
            return int(amt.group(1).replace(",", ""))
        except:
            return 0
    # fallback: last long number
    nums = re.findall(r"(\d{2,})", text.replace(",", ""))
    if nums:
        try:
            return int(nums[-1])
        except:
            return 0
    return 0


# ---------------------------------------------------
# CLEAN UI
# ---------------------------------------------------
st.set_page_config(page_title="ReverseCoder AI", page_icon="🤖", layout="wide")

st.markdown("<h1 style='text-align:center;'>🤖 ReverseCoder AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color:gray;'>AI Powered Transaction Categorization</h3>", unsafe_allow_html=True)

st.write("")
st.markdown("---")

# -------------------- Manual Input --------------------
st.subheader("💬 Manual Transaction Input")

txn = st.text_input(
    "Enter a transaction:",
    placeholder="e.g., CCD AP 11:58 TXN#001 ₹892"
)

if st.button("Predict"):
    if txn.strip():
        cat, conf = predict_category(txn)
        loc = predict_location(txn)
        amt = extract_amount(txn)

        st.success("Prediction Complete!")
        st.write(f"**Category:** {cat}")
        st.write(f"**Location:** {loc}")
        st.write(f"**Confidence:** {conf}")
        st.write(f"**Amount:** ₹{amt}")

    else:
        st.warning("Please enter a transaction!")

st.markdown("---")

# -------------------- CSV Upload --------------------
st.subheader("📁 Upload CSV File")

csv = st.file_uploader("Upload CSV (must contain 'merchant' column)", type=["csv"])

if csv:
    df = pd.read_csv(csv)

    if "merchant" not in df.columns:
        st.error("CSV must contain a 'merchant' column!")
    else:
        st.success(f"CSV uploaded successfully! Rows: {len(df)}")

        # ---------------------------------------------------
        # PART 2 — ANALYTICS
        # ---------------------------------------------------
        st.markdown("---")
        st.subheader("📊 Analytics & Insights")

        # Add prediction columns
        df["Predicted_Category"] = df["merchant"].apply(lambda x: predict_category(str(x))[0])
        df["Confidence"] = df["merchant"].apply(lambda x: predict_category(str(x))[1])
        df["Predicted_Location"] = df["merchant"].apply(lambda x: predict_location(str(x)))
        df["Amount"] = df["merchant"].apply(lambda x: extract_amount(str(x)))

        # -------------------- TABLE --------------------
        st.markdown("### 🧾 All Transactions")
        st.dataframe(
            df[["merchant", "Predicted_Category", "Predicted_Location", "Amount", "Confidence"]],
            height=5000
        )

        # -------------------- BUTTONS --------------------
        st.markdown("### 📈 Choose a Chart to View")

        colA, colB, colC, colD = st.columns(4)

        show_cat = colA.button("📊 Category Chart")
        show_loc = colB.button("📍 Location Chart")
        show_amt = colC.button("💰 Amount Chart")
        show_summary = colD.button("📦 Summary Box")

        # -------------------- CATEGORY CHART --------------------
        if show_cat:
            st.subheader("📊 Category Distribution")
            st.bar_chart(df["Predicted_Category"].value_counts())

        # -------------------- LOCATION CHART --------------------
        if show_loc:
            st.subheader("📍 Location Distribution")
            st.bar_chart(df["Predicted_Location"].value_counts())

        # -------------------- AMOUNT CHART --------------------
        if show_amt:
            st.subheader("💰 Total Amount by Category")
            amount_group = df.groupby("Predicted_Category")["Amount"].sum()
            st.bar_chart(amount_group)

        # -------------------- SUMMARY --------------------
        if show_summary:
            st.subheader("📦 Summary")

            total_txn = len(df)
            total_amt = df["Amount"].sum()
            # safe mode for mode()
            top_cat = df["Predicted_Category"].mode().iat[0] if not df["Predicted_Category"].mode().empty else "N/A"
            top_loc = df["Predicted_Location"].mode().iat[0] if not df["Predicted_Location"].mode().empty else "N/A"

            st.write(f"**Total Transactions:** {total_txn}")
            st.write(f"**Total Amount (₹):** {total_amt}")
            st.write(f"**Most Common Category:** {top_cat}")
            st.write(f"**Most Common Location:** {top_loc}")

        # -------------------- DOWNLOAD BUTTON --------------------
        st.markdown("---")
        st.subheader("⬇ Download Results")

        out_csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV with Predictions",
            out_csv,
            "reversecoder_results.csv",
            "text/csv"
        )
