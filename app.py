import dash
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc 

# we of course need plotly and pandas
import plotly.express as px
import pandas as pd
app =dash.Dash

server = app.server