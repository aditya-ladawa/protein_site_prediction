import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

yeast_names_path = os.path.join("yeast_names.txt")
yeast_data_path = os.path.join("yeast_data.txt")

# --- Load model and data ---
@st.cache_resource
def load_model():
    with open("best_model.pkl", "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_data(path):
    cols = [
        "Sequence_Name", "mcg", "gvh", "alm",
        "mit", "erl", "pox", "vac", "nuc",
        "Localization_Site"
    ]
    return pd.read_csv(path, sep=r"\s+", names=cols)

@st.cache_resource
def create_label_encoder(df):
    le = LabelEncoder()
    le.fit(df["Localization_Site"])
    return le

# Load data and model first to fit LabelEncoder
df = load_data(yeast_data_path)
le = create_label_encoder(df)
model = load_model()

st.title("Protein Localization Site Predictor")
st.write("Predict the cellular localization site of yeast proteins using a trained model.")

# --- Sidebar Selection ---
mode = st.sidebar.selectbox(
    "Choose inference mode:",
    ["Custom Input", "Random Sample"]
)

if mode == "Custom Input":
    st.header("Custom Input Prediction")
    st.write("Enter feature values below:")
    features = ['mcg','gvh','alm','mit','erl','pox','vac','nuc']
    user_input = [
        st.number_input(f"{feat}", format="%.3f", key=feat)
        for feat in features
    ]
    if st.button("Predict", key="predict_button"):
        pred_enc = model.predict([user_input])[0]
        label = le.inverse_transform([pred_enc])[0]
        st.success(f"Predicted localization site: **{label}**")

else:
    st.header("Random Sample Prediction")
    n = st.slider("How many random samples?", min_value=1, max_value=10, value=3)
    if st.button("Sample & Predict", key="sample_button"):
        samples = df.sample(n=n).reset_index(drop=True)
        X_rand = samples[['mcg','gvh','alm','mit','erl','pox','vac','nuc']]
        preds = model.predict(X_rand)
        samples['Predicted_Site'] = le.inverse_transform(preds)
        st.write(samples)

# --- Appendix ---
st.markdown("---")
st.header("Appendix: Full Analysis Report")

from PIL import Image
import re

def render_markdown_file(md_path, image_folder=""):
    if not os.path.exists(md_path):
        st.error(f"{md_path} not found.")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    buffer = ""
    for line in lines:
        img_match = re.search(r"!\[.*\]\((.*?)\)", line)
        if img_match:
            if buffer.strip():
                st.markdown(buffer.strip())
                buffer = ""
            img_path = img_match.group(1)
            full_img_path = os.path.join(image_folder, img_path)
            if os.path.exists(full_img_path):
                st.image(Image.open(full_img_path))
            else:
                st.warning(f"Image not found: {full_img_path}")
        elif line.strip().startswith("#"):
            if buffer.strip():
                st.markdown(buffer.strip())
                buffer = ""
            st.subheader(line.strip().lstrip("#").strip())
        else:
            buffer += line

    if buffer.strip():
        st.markdown(buffer.strip())

render_markdown_file("model_comparison.md", image_folder="")
