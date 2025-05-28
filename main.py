import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

POWERS = [2**i for i in range(1,9)]

def quantize(value):
     quantize_scale = st.session_state.get('quantize_scale', POWERS[0])
     
     increment = 256 / (quantize_scale - 1)

     res = round(value/increment) * increment

     if res >= 256:
          return 255

     return res

def convert_image(img):
     image_array = np.array(img)

     for r, array in enumerate(image_array):
          for c, _ in enumerate(array):
               image_array[r][c] = quantize(image_array[r][c])

     modified_image = Image.fromarray(image_array)
     return modified_image

def update_quantize_scale_value(i):
     st.session_state.quantize_scale = st.session_state.get(f"select_slider_tab{i + 1}", POWERS[0])

st.sidebar.title("Menu de Opções")
st.sidebar.file_uploader(label="Escolha uma Imagem", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="uploaded_files")
st.sidebar.radio(label="Personalização de Imagem", options=["Tons de Cinza", "Quantização"], index=None, key="radio")

files = st.session_state.get("uploaded_files", [])

if not files:
     st.warning("Carregue uma imagem para continuar", icon="⚠️")
else:
     tabs_list = [f"Imagem {i + 1}" for i in range(len(files))]
     tabs = st.tabs(tabs_list)

     for i, file in enumerate(files):
          update_quantize_scale_value(i)
          with tabs[i]:
               if st.session_state.radio is None:
                    st.image(file, "Imagem Original")

               if st.session_state.radio == "Tons de Cinza":
                    st.image(file, "Imagem Original")
                    pil_image = Image.open(file)
                    slider_key = f"select_slider_tab{i + 1}"
                    quantize_scale = st.select_slider("Selecione a Quantização da Imagem", POWERS, POWERS[0], key=slider_key)
                    st.session_state.quantize_scale = quantize_scale
                    pil_image_gray = pil_image.convert("L")

                    # utilizando o point() do Image, 
                    lut = [quantize(i) for i in range(256)]
                    gray_image_modified = pil_image_gray.point(lut)

                    # Fazendo na raça
                    # gray_image_modified = convert_image(pil_image_gray)
                    
                    st.image(gray_image_modified, caption="Imagem Usando Escala Cinza")

               if st.session_state.radio == "Quantização":
                    pil_image = Image.open(file)
                    slider_key = f"select_slider_tab{i + 1}"
                    pil_image_rgb = pil_image.convert("RGB")

                    # Utilizando o eval() do Image, ele faz a iteração de cada pixel de forma automática
                    modified_image = Image.eval(pil_image_rgb, quantize)

                    # Fazendo na raça
                    # r_modified, g_modified, b_modified = [
                    #      convert_image(channel)
                    #      for channel in pil_image_rgb.split()
                    # ]
                    
                    # modified_image = Image.merge("RGB", (r_modified, g_modified, b_modified))
                    st.image(modified_image, "Imagem Quantizada")

                    quantize_scale = st.select_slider("Selecione a Quantização da Imagem", POWERS, POWERS[0], key=slider_key)

                    r, g, b = modified_image.split()
                    with st.expander("Imagem divida nos três canais", icon="🎨"):
                         col1, col2, col3 = st.columns(3)

                         with col1:
                              st.subheader("Canal R")
                              st.image(r)
                         
                         with col2:
                              st.subheader("Canal G")
                              st.image(g)

                         with col3:
                              st.subheader("Canal B")
                              st.image(b)
                    
                    with st.expander("Imagem Negativa", icon="📉"):
                         st.subheader("Imagem Quantizada Invertida")
                         inverted_image = Image.eval(modified_image, lambda px: 255 - px)
                         st.image(inverted_image)

                    with st.expander("Histograma dos Canais de Cor", icon="📊"):
                         r_arr = np.array(r)
                         g_arr = np.array(g)
                         b_arr = np.array(b)

                         channel_data = {
                              'R': {'array': r_arr, 'color': 'red'},
                              'G': {'array': g_arr, 'color': 'green'},
                              'B': {'array': b_arr, 'color': 'blue'}
                         }

                         fig, axs = plt.subplots(1, 3, figsize=(18, 6))

                         for i, (channel_key, data) in enumerate(channel_data.items()):
                              ax = axs[i]
                              ax.hist(data['array'].ravel(), bins=256, color=data['color'], alpha=.6)
                              ax.set_title(f"Canal {channel_key}")
                              ax.grid(True)

                         plt.tight_layout()
                         st.pyplot(fig)
