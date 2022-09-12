# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 20:02:42 2022

@author: matte
"""

import pandas as pd  # pip install pandas openpyxl

import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go  # pip install plotly
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu

import sys
sys.path.append('C:/Users\matte\OneDrive\Desktop\HecoEnergy\HECO\Analisi\Analisi Mercato\Italia\Tool')
import database as heco

from deta import Deta  # pip install deta



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
page_title = "Configuratore Heco"
page_icon = ":chart_with_upwards_trend:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"

st.set_page_config(page_title= page_title, page_icon= page_icon, layout= layout)
st.title(page_title + " " + page_icon)

#-----------------------------------------------------------------------------
# ---- READ EXCEL ----

df = pd.read_excel(
        io="C:/Users\matte\OneDrive\Desktop\HecoEnergy\HECO\Analisi\Analisi Mercato\Italia\Tool/Online_tool.xlsx",
        engine="openpyxl",
        sheet_name="Tabella A_ comuni e zone climat",
        usecols="A:O",
    )

cons_res = pd.read_excel(
        io="C:/Users\matte\OneDrive\Desktop\HecoEnergy\HECO\Analisi\Analisi Mercato\Italia\Tool/Online_tool.xlsx",
        engine="openpyxl",
        sheet_name="Res kWhmqK per zona climatica",
        usecols="A:E",
    )

cons_ind = pd.read_excel(
        io="C:/Users\matte\OneDrive\Desktop\HecoEnergy\HECO\Analisi\Analisi Mercato\Italia\Tool/Online_tool.xlsx",
        engine="openpyxl",
        sheet_name="Ind kWhmqK per zona climatica",
        usecols="A:E",
    )

combustibile = pd.read_excel(
        io="C:/Users\matte\OneDrive\Desktop\HecoEnergy\HECO\Analisi\Analisi Mercato\Italia\Tool/Online_tool.xlsx",
        engine="openpyxl",
        sheet_name="Fuel",
        usecols="A",
    )

fatt_corr = pd.read_excel(
        io="C:/Users\matte\OneDrive\Desktop\HecoEnergy\HECO\Analisi\Analisi Mercato\Italia\Tool/Online_tool.xlsx",
        engine="openpyxl",
        sheet_name="FattoreCorrettivo_Cl_en",
        usecols="A:U",
    )

H = pd.read_excel(
        io="C:/Users\matte\OneDrive\Desktop\HecoEnergy\HECO\Analisi\Analisi Mercato\Italia\Tool/Heco_System.xlsx",
        engine="openpyxl",
        sheet_name="Heco_Rendim",
        usecols="A:F",
    )

classe_en = fatt_corr['Classe_energetica'].unique().tolist()
regiorni = df['Regione'].unique().tolist()
provincia = df['Provincia'].unique().tolist()
tipologia = df['tipologia'].unique().tolist()
combustibile = combustibile['Combustibile'].unique().tolist()
metriquadri = ['Superficie']
#consumi = ['Bolletta gas mc', 'Bolletta gas eur', 'Bolletta elettricità kWh', 'Bolletta elettricità eur']

# --- DATABASE INTERFACE ---
def get_all_locations():
    items = heco.fetch_all_locations()
    locations = [item["key"] for item in items]
    return locations

#-----------------------------------------------------------------------------
# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Dati Input", "Visualizzazione Dati"],
    icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

# --- INPUT & SAVE LOCATION ---
if selected == "Dati Input":
    st.header(f"Dati Input utente")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Seleziona Regione:", regiorni, key="regione")
        col2.selectbox("Seleziona Provincia:", provincia, key="provincia")
        
        "---"
        with st.expander("Edificio"):
            st.selectbox("Tipologia Edificio:", tipologia, key='tipo')    
        with st.expander("Combustibile"):
            st.selectbox("Tipologia Combustibile:", combustibile, key='fuel')       
        with st.expander("Metri Quadri"):
            for mq in metriquadri:
                st.number_input(f"{mq}:", min_value=0, format="%i", step=10, key=mq)
        with st.expander("Classe Energetica"):
            st.selectbox("Classe Energetica:", classe_en, key='classe')
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here ...")

        "---"
        submitted = st.form_submit_button("Elabora Dati")
        if submitted:
            location = str(st.session_state["regione"]) + "_" + str(st.session_state["provincia"])
            regione = str(st.session_state["regione"])
            provincia = str(st.session_state["provincia"])
            tipologia = str(st.session_state["tipo"])
            combustibile = str(st.session_state["fuel"])
            classe_en = str(st.session_state["classe"])
            metriquadri = {mq: st.session_state[mq] for mq in metriquadri}
            heco.insert_location(location, regione, provincia, tipologia, combustibile, metriquadri, classe_en, comment)
            st.success("Dati elaborati!")

# --- PLOT PERIODS ---
if selected == "Visualizzazione Dati":
    st.header("Visualizzazione Dati")
    with st.form("saved_location"):
        location = st.selectbox("Seleziona Luogo:", get_all_locations())
        submitted = st.form_submit_button("Elaborazione")
        if submitted:
            # Get data from database
            location_data = heco.get_location(location)
            regione = location_data.get("regione")
            provincia = location_data.get("provincia")
            tipologia = location_data.get("tipologia")
            combustibile = location_data.get("combustibile")
            metriquadri = location_data.get("metriquadri")
            classe_en = location_data.get("classe_en")
            comment = location_data.get("comment")

            # Create metrics
            m_q = list(heco.get_location(location)['metriquadri'].values())[0]
            heco_system = H.loc[(H.Regione== heco.get_location(location)['regione']),['Coeff_spesa_nuova']].iat[0,0]
            zona_climatica = df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione== heco.get_location(location)['regione'])&(df.Provincia== heco.get_location(location)['provincia']),['Zona']].iat[0,0]
            fattore_corr_CO2 = fatt_corr.loc[(fatt_corr.Classe_energetica== classe_en),['FC_CO2_%s_%s' %(tipologia,zona_climatica)]].iat[0,0]
            fattore_corr_nren = fatt_corr.loc[(fatt_corr.Classe_energetica== classe_en),['FC_Epgl,nren_%s_%s' %(tipologia,zona_climatica)]].iat[0,0]
            fabbisogno_en = round(df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),['Fabbisogno_medio_nren [kWh/mqa]']].iat[0,0] * m_q*fattore_corr_nren, 1)
            fabbisogno_fuel = round(df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),['Fabbisogno_medio_%s' %(combustibile)]].iat[0,0]* m_q, 1)
            CO2 = round(df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),['CO2_%s [Kg]' %(combustibile)]].iat[0,0]* m_q*fattore_corr_CO2, 1)
            spesa = round(df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),['Spesa_medio_%s [€]' %(combustibile)]].iat[0,0] * m_q *fattore_corr_nren, 1)
            mappa = pd.DataFrame(columns=['lat','lon'])
            mappa['lat'] = df.loc[(df.Provincia==heco.get_location(location)['provincia']) ,'lat']
            mappa['lon'] = df.loc[(df.Provincia==heco.get_location(location)['provincia']) ,'lon']
            
            colA, colB = st.columns(2)
            colA.metric("Spesa annua", f"{spesa} €/anno", f"200% 2021", "inverse")
            colB.map(mappa,  zoom = 3, use_container_width=True)
            col1, col2, col4 = st.columns(3)
            col1.metric("Zona Climatica", f"{zona_climatica}")
            col2.metric("Fabbisogno en risc", f"{fabbisogno_en}", f"kW/anno", "off")
            #col3.metric("Combustibile necessario", f"{fabbisogno_fuel}", f"mc")
            col4.metric("Emissioni di CO2", f"{CO2}", f"Kg", "off")
            st.text(f"Comment: {comment}")
            
            # Create bar chart
                # consumi
            conf_consumi = pd.DataFrame(columns=['Scenario attuale', 'Scenario Heco'])
            conf_consumi['Scenario attuale'] = df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),'Fabbisogno_medio_%s' %(combustibile)] * m_q *fattore_corr_nren
            conf_consumi['Scenario Heco'] = df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),'Fabbisogno_medio_%s' %(combustibile)]* m_q * H.loc[(H.Regione== heco.get_location(location)['regione']),['Coeff_spesa_nuova']].iat[0,0]*fattore_corr_nren
            conf_consumi.rename(index={0: 'consumi combustibile'}, inplace = True)
                
                # costi
            conf_spesa = pd.DataFrame(columns=['Scenario attuale', 'Scenario Heco'])
            conf_spesa['Scenario attuale'] = df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),'Spesa_medio_%s [€]' %(combustibile)] * m_q *fattore_corr_nren
            conf_spesa['Scenario Heco'] = df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),'Spesa_medio_%s [€]' %(combustibile)] * heco_system * m_q *fattore_corr_nren
            conf_spesa.rename(index={0: 'bollette gas'}, inplace = True)
            
                #CO2
            conf_emissioni = pd.DataFrame(columns=['Scenario attuale', 'Scenario Heco'])
            conf_emissioni['Scenario attuale'] = df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),'CO2_%s [Kg]' %(combustibile)] * m_q*fattore_corr_CO2
            conf_emissioni['Scenario Heco'] = df.loc[(df.tipologia== heco.get_location(location)['tipologia'])&(df.Regione==heco.get_location(location)['regione'])&(df.Provincia==heco.get_location(location)['provincia']),'CO2_%s [Kg]' %(combustibile)] * heco_system * m_q*fattore_corr_CO2
            conf_emissioni.rename(index={0: 'emissioni di CO2'}, inplace = True)

            fig_conf_consumi = go.Figure(data=[
                go.Bar(name='Attuale', x=['Attuale'], y=conf_consumi['Scenario attuale'], text=round(conf_consumi['Scenario attuale'],2)),
                go.Bar(name='Heco', x=['Heco'], y=conf_consumi['Scenario Heco'], text=round(conf_consumi['Scenario Heco'],2))])
            
            fig_conf_consumi.update_layout(
                title="Consumi energetici",
                title_font_size= 15,
                xaxis_title="Scenari",
                yaxis_title="Consumi [kWh/anno]",
                template="plotly_white",
                width=200, height=400
            )
            
            fig_conf_spesa = go.Figure(data=[
                go.Bar(name='Attuale', x=['Attuale'], y=conf_spesa['Scenario attuale'], text=round(conf_spesa['Scenario attuale'],2)),
                go.Bar(name='Heco', x=['Heco'], y=conf_spesa['Scenario Heco'], text=round(conf_spesa['Scenario Heco'],2))])
            
            fig_conf_spesa.update_layout(
                title="Costo per riscaldamento a confronto",
                title_font_size= 25,
                xaxis_title="Scenari",
                yaxis_title="Spesa [€/anno]",
                template="plotly_white",
                width=200, height=400
            )
 
            fig_conf_emissioni = go.Figure(data=[
                go.Bar(name='Attuale', x=['Attuale'], y=conf_emissioni['Scenario attuale'], text=round(conf_emissioni['Scenario attuale'],2)),
                go.Bar(name='Heco', x=['Heco'], y=conf_emissioni['Scenario Heco'], text=round(conf_emissioni['Scenario Heco'],2))])
            
            fig_conf_emissioni.update_layout(
                title="CO2 emessa per risc",
                title_font_size= 15,
                xaxis_title="Scenari",
                yaxis_title="Emissioni [Kg/anno]",
                template="plotly_white",
                width=200, height=400
            )    
           

            # Display bar chart
            st.plotly_chart(fig_conf_spesa, use_container_width=True)
            left_column, right_column = st.columns(2)
            left_column.plotly_chart(fig_conf_consumi, use_container_width=True)
            right_column.plotly_chart(fig_conf_emissioni, use_container_width=True)
            
            page_subtitle = "I flussi energetici a confronto"
            page_icon_sub = ":bar_chart:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
            st.header(page_subtitle + " " + page_icon_sub)

            page_mk1 = "flussi pre intervento"
            st.markdown(page_mk1)

            # 1st Create sankey chart
            label = ['fonte ren', 'fonte fossile', 'tot fabbisogno', 'riscaldamento', 'acs', 'altro'] 
            source = [0,1,2,2,2]
            target = [2,2,3,4,5]
            value = list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_ren']*fattore_corr_nren*m_q)+list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_nren']*fattore_corr_nren*m_q) +list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_res']*fattore_corr_nren* 0.7*m_q) +list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_res']*fattore_corr_nren* 0.13*m_q) +list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_res']*fattore_corr_nren* 0.17*m_q)

            # Data to dict, dict to sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=5)
            data = go.Sankey(link=link, node=node)

            # Plot it!
            fig = go.Figure(data)
            #fig.update_layout(margin=dict(l=0, r=0, t=2, b=2))
            st.plotly_chart(fig, use_container_width=True)
            
            page_mk2 = "flussi Heco solution"
            st.markdown(page_mk2)
            
            # 2nd Create sankey chart
            label = ['fonte ren', 'fonte fossile', 'tot fabbisogno', 'riscaldamento', 'acs', 'altro'] 
            source = [0,1,2,2,2]
            target = [2,2,3,4,5]
            
            value = list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_ren']*fattore_corr_nren*m_q+cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_nren']*fattore_corr_nren*m_q*(1-heco_system))+list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_nren']*fattore_corr_nren*m_q*heco_system) +list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_res']*fattore_corr_nren* 0.7*m_q) +list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_res']*fattore_corr_nren* 0.13*m_q) +list(cons_res.loc[(cons_res.zona_climatica== zona_climatica),'Epgl_res']*fattore_corr_nren* 0.17*m_q)

            # Data to dict, dict to sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=5)
            data = go.Sankey(link=link, node=node)

            # Plot it!
            fig = go.Figure(data)
            #fig.update_layout(margin=dict(l=0, r=0, t=2, b=2))
            st.plotly_chart(fig, use_container_width=True)
            
        
        

