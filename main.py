import streamlit as st
import importlib
import os

st.set_page_config(
    page_title="Some Audio Tools",
    page_icon="AT",
    layout="wide"
)

st.title("Tools collection")

CARPETA = "tools"

archivos = []

for archivo in os.listdir(CARPETA):

    if archivo.endswith(".py") and archivo != "__init__.py":

        archivos.append(archivo[:-3])

archivos.sort()

opcion = st.sidebar.selectbox(

    "Select one tool",

    archivos

)

modulo = importlib.import_module(f"{CARPETA}.{opcion}")

modulo.run()