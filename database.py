# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 18:28:44 2022

@author: matte
"""

import streamlit as st  # pip install streamlit
from deta import Deta  # pip install deta

import os
#from dotenv import load_dotenv


# Load the environment variables
DETA_KEY = 'c01fh95c_CMHFcnXLnip1W6MHNTu2B8MKW7NzaefJ'

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
heco = deta.Base("Heco_simulation")


def insert_location(location, regione, provincia, tipologia, combustibile, metriquadri, classe_en, comment):
    """Returns the report on a successful creation, otherwise raises an error"""
    return heco.put({"key": location, "regione": regione, "provincia": provincia, "tipologia": tipologia, "combustibile": combustibile, "metriquadri": metriquadri, "classe_en": classe_en, "comment": comment})


def fetch_all_locations():
    """Returns a dict of all locations"""
    res = heco.fetch()
    return res.items


def get_location(location):
    """If not found, the function will return None"""
    return heco.get(location)