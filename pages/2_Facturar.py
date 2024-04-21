import streamlit as st
import json
import requests
from io import BytesIO
import pandas as pd

options = {
    'ATR': ['2.0TD', '3.0TD', '6.1TD', '6.2TD', '6.3TD', '6.4TD'],
    'POSITION': ['Pérdidas', 'Tasas', 'Precio Plano', 'Fuera de Fórmula']
}

# URL construction
BASE_URL = "http://127.0.0.1:8000"
endpoint_path = "/billing/consumption/calculate"

FORMULA = {
    'MARGEN': {},
    'FNEE': {}
}

if 'stage' not in st.session_state:
    st.session_state.stage = 0
    
response = None

with st.sidebar.form(key='form'):
    
    FILE = st.file_uploader('**Curva**', type=['csv'])
    ATR = st.selectbox('**ATR**', options['ATR'], index=1)
    DESVIOS = st.number_input('**DESVÍOS**', value=0.0, step=0.1)
    DATES = st.date_input('**Fechas**', [], key='dates', help='Fechas de inicio y fin del periodo de facturación')

    for column in FORMULA:
        st.write(f'**{column}**')
        col1, col2 = st.columns(2)
        with col1:
            FORMULA[column]['position'] = st.selectbox('Posición', options['POSITION'], key=f'{column}_position', label_visibility='collapsed', placeholder='Posición')
        with col2:
            FORMULA[column]['value'] = st.number_input('Valor', value=.0, step=0.1, key=f'{column}_value', label_visibility='collapsed', placeholder='Valor')
            
    button =  st.form_submit_button('Calcular')


def write_excel(data, sheet_name, index_col):
    df = pd.read_excel(data, sheet_name=sheet_name, index_col=index_col)
    dff = (df
        .style
            .highlight_null(props='color: transparent; background-color: transparent;')
        .to_html(escape=False)
    )
    st.write(dff, unsafe_allow_html=True)

if button:

    url = f"{BASE_URL}{endpoint_path}"
    DATES = [str(date) for date in DATES]
    
    data = {
        'data': json.dumps({
            'data': {
                'GENERAL': {
                    'ATR': ATR,
                    'DESVIOS': DESVIOS,
                    'DATES': DATES
                },
                'FORMULA': FORMULA
            }
        })
    }

    files = {'file': (FILE.name, FILE, FILE.type)}
    
    with st.spinner('Calculando...'):
        response = requests.post(url, files=files, data=data)
            
    st.write(f'# Resultados')

    data = BytesIO(response.content)
    
    col1, col2 = st.columns([.8,.2])
    
    with col1:
        st.info('Puedes descargar los siguientes reportes en un Excel →')
    with col2:
        st.download_button(label='Descargar', data=data, file_name='report.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
    mapping = {
        'PRECIO PONDERADO': {
            'sheet_name': 'PRECIO PONDERADO',
            'index_col': [0,1]
        },
        'ENERGÍA': {
            'sheet_name': 'ENERGÍA',
            'index_col': 0
        },
        'COSTE': {
            'sheet_name': 'COSTE',
            'index_col': [0,1]
        }
    }
    
    for key, value in mapping.items():
        
        st.write(f'## {key.title()}')
        
        write_excel(data, value['sheet_name'], value['index_col'])