import streamlit as st
import utils
import pandas as pd
from io import BytesIO
import json
import requests
import plotly.express as px

if 'stage' not in st.session_state:
    st.session_state.stage = 0

with st.sidebar:
    file = st.file_uploader('**Curva de carga**', type=['csv', 'xlsx'], on_change=utils.set_stage, args=(1,))
    
    if st.session_state.stage >= 1:
        io = BytesIO(file.getvalue())
        if file.name.endswith('.csv'):
            delimiter = utils.get_delimiter(file.read()[:1024])
            df = pd.read_csv(io, delimiter=delimiter)
        else:
            df = pd.read_excel(io, engine='openpyxl')
            
        columns = df.columns.tolist()
        
    if st.session_state.stage >= 1:
        datetime_column_sep = st.checkbox('Fecha y hora en columnas separadas', on_change=utils.set_stage, args=(2,))

    if st.session_state.stage >= 2:
        st.write('**Selecciona columnas**')
        
        if datetime_column_sep:
            columns = {
                'FECHA': st.selectbox('Fecha', columns, placeholder='Fecha', index=None, label_visibility='collapsed'),
                'HORA': st.selectbox('Hora', columns, placeholder='Hora', index=None, label_visibility='collapsed'),
                'ENERGIA': st.selectbox('Energía', columns, placeholder='Energía', index=None, label_visibility='collapsed'),
            }
            
        else:
            columns = {
                'FECHA_HORA': st.selectbox('Fecha y hora', columns, placeholder='Fecha y hora', index=None, label_visibility='collapsed'),
                'ENERGIA': st.selectbox('Energía', columns, placeholder='Energía', index=None, label_visibility='collapsed'),
            }
            
        button = st.button('Preprocesar', on_click=utils.set_stage, args=(3,))
        
if st.session_state.stage >= 3:
    BASE_URL = st.secrets['API_URL']
    ENDPOINT = "/consumption/preprocess"
    url = f"{BASE_URL}{ENDPOINT}"
    
    files = {'file': (file.name, file.getvalue(), file.type)}
    
    data = {
        'data': json.dumps({
            'columns': columns
        })
    }
    
    response = requests.post(url, files=files, data=data)
    
    col1,col2 = st.columns([.1,.9])
    with col1:
        emo = ':floppy_disk:'
        button = st.download_button(emo, response.content, file.name, file.type)
    with col2:
        st.info('Descarga el archivo preprocesado y continúa en la página **Facturar**')
    
    df = pd.read_csv(BytesIO(response.content))
    
    fig = px.line(df, x='DATETIME', y='ENERGY')
    st.plotly_chart(fig)