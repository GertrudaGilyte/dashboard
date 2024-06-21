import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.express as px
from dash import Dash, html, dcc

dotenv_path = 'C:\\Users\\gergi\\Downloads\\dashboard\\dashboard\\token.env'
load_dotenv(dotenv_path)

username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
database = os.getenv('DB_CLIMATE')

connection_string = f'postgresql://{username}:{password}@{host}:{port}/{database}'
engine = create_engine(connection_string)

query = """
SELECT city, date, min_temp_c, avg_temp_c
FROM prep_forecast_day
WHERE date >= '2024-06-01' AND date <= '2024-06-06';
"""

df = pd.read_sql(query, engine)

fig_min_temp = px.line(df, x='date', y='min_temp_c', color='city', title='Minimum Temperature by City')

fig_min_temp.update_layout(
    xaxis_title='Date',
    yaxis_title='Minimum Temperature (°C)',
    legend_title='City'
)


fig_avg_temp = px.line(df, x='date', y='avg_temp_c', color='city', title='Average Temperature by City')

fig_avg_temp.update_layout(
    xaxis_title='Date',
    yaxis_title='Average Temperature (°C)',
    legend_title='City'
)


app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Temperature Data Dashboard"),
    html.Div([
        dcc.Graph(id='min-temp-graph', figure=fig_min_temp),
        dcc.Graph(id='avg-temp-graph', figure=fig_avg_temp)
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)