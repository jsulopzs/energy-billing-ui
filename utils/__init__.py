import streamlit as st
import csv

def set_stage(stage):
    st.session_state.stage = stage
    

def get_delimiter(content):
    dialect = csv.Sniffer().sniff(content.decode('utf-8'))
    return dialect.delimiter