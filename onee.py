import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageFilter, ImageEnhance
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- USER CREDENTIALS ----------
USER_CREDENTIALS = {
    "admin": "admin123",
    "user": "user123"
}

# ---------- SESSION INIT ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'wishlist' not in st.session_state:
    st.session_state.wishlist = []

# ---------- LOGIN PAGE ----------
def login_page():
    st.title("🔐 Login Page")
    st.markdown("Enable and take a photo, then enter credentials to proceed.")

    col1, col2 = st.columns(2)
    with col1:
        enable_cam = st.checkbox("Enable Camera")
        picture = st.camera_input("Take a picture", disabled=not enable_cam)
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

    if st.button("Login"):
        if USER_CREDENTIALS.get(username) == password:
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
            st.balloons()
        else:
            st.error("❌ Invalid credentials!")

# ---------- IMAGE EFFECTS ----------
def apply_image_effect(img, effect):
    if effect == "Grayscale":
        return img.convert("L")
    elif effect == "Rotate":
        return img.rotate(45)
    elif effect == "Blur":
        return img.filter(ImageFilter.BLUR)
    elif effect == "Sharpen":
        return img.filter(ImageFilter.SHARPEN)
    elif effect == "Edge Enhance":
        return img.filter(ImageFilter.EDGE_ENHANCE)
    elif effect == "Brightness +30%":
        return ImageEnhance.Brightness(img).enhance(1.3)
    return img

# ---------- MAIN APP ----------
def main_app():
    
    st.title("🛍️ Fashion Data Explorer")
    st.image("logo_fash.jpg")
    st.sidebar.title("📂 Filters")

    df = pd.read_csv("fashion.csv")

    # Sidebar filters
    categories = st.sidebar.multiselect("Select Categories", df['category'].unique(), default=df['category'].unique()[0])
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.0)
    price_range = st.sidebar.slider("Price Range", int(df['price'].min()), int(df['price'].max()), (100, 1000))
    search = st.sidebar.text_input("Search Product ID or Category")

    filtered = df[df['category'].isin(categories)]
    filtered = filtered[(filtered['rating'] >= min_rating) & (filtered['price'].between(*price_range))]

    if search:
        filtered = filtered[filtered['product_id'].astype(str).str.contains(search) | filtered['category'].str.contains(search, case=False)]

    st.subheader("📋 Filtered Product Data")
    st.dataframe(filtered)
    st.download_button("Download Filtered Data", filtered.to_csv(index=False), "filtered_data.csv", "text/csv")

    st.write("### 📈 Summary Statistics")
    col1, col2 = st.columns(2)
    col1.metric("Average Price", f"₹ {filtered['price'].mean():.2f}")
    col2.metric("Average Rating", f"{filtered['rating'].mean():.2f} ⭐")

    # Image Viewer
    st.write("### 🖼️ Product Image Viewer")
    if not filtered.empty:
        selected_id = st.selectbox("Choose a Product ID", filtered['product_id'].tolist())
        selected_row = filtered[filtered['product_id'] == selected_id].iloc[0]
        img_name = selected_row['image_name']
        img_path = os.path.join("images", img_name)

        try:
            img = Image.open(img_path)
            st.image(img, caption=f"Product ID: {selected_id}", use_column_width=True)

            effect = st.selectbox("Apply Image Effect", ["None", "Grayscale", "Rotate", "Blur", "Sharpen", "Edge Enhance", "Brightness +30%"])
            st.image(apply_image_effect(img, effect), caption=f"{effect} Image", use_column_width=True)

            if st.button("💖 Add to Wishlist"):
                if selected_id not in st.session_state.wishlist:
                    st.session_state.wishlist.append(selected_id)
                    st.success("Added to wishlist!")

        except FileNotFoundError:
            st.error(f"Image not found: {img_path}")
    else:
        st.warning("No products available in selected categories.")

    # Visualization
    st.write("### 📊 Visualization Options")
    chart_type = st.radio("Select Chart Type", ["Bar Graph (Price)", "Boxplot (Rating)", "Scatter Plot (Price vs Rating)", "Pie Chart (Category Distribution)"], index=0)

    fig, ax = plt.subplots()
    if chart_type == "Bar Graph (Price)":
        sns.histplot(filtered['price'], kde=True, ax=ax, color="skyblue")
        ax.set_xlabel("Price")
        ax.set_ylabel("Count")
    elif chart_type == "Boxplot (Rating)":
        sns.boxplot(data=filtered, x='rating', color="orange", ax=ax)
        ax.set_xlabel("Rating")
    elif chart_type == "Scatter Plot (Price vs Rating)":
        sns.scatterplot(data=filtered, x='price', y='rating', hue='category', palette="Set2", s=100, ax=ax)
        ax.set_xlabel("Price")
        ax.set_ylabel("Rating")
    elif chart_type == "Pie Chart (Category Distribution)":
        filtered['category'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
        ax.set_ylabel("")
    st.pyplot(fig)

    # Wishlist
    st.write("### 💼 Your Wishlist")
    if st.session_state.wishlist:
        wishlist_df = df[df['product_id'].isin(st.session_state.wishlist)]
        st.dataframe(wishlist_df)
    else:
        st.info("Your wishlist is empty.")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# ---------- APP CONTROL ----------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
