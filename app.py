import os
import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

if os.getenv('ENV') != 'PRODUCTION':
    from dotenv import load_dotenv
    dotenv_path = 'C:\\Users\\gergi\\Downloads\\dashboard\\dashboard\\token.env'
    load_dotenv(dotenv_path)

def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value

username = get_env_var('POSTGRES_USER')
password = get_env_var('POSTGRES_PW')
host = get_env_var('POSTGRES_HOST')
port = get_env_var('POSTGRES_PORT')
database = get_env_var('DB_CLIMATE')
weather_api_key = get_env_var('WEATHER_API_KEY')

connection_string = f'postgresql://{username}:{password}@{host}:{port}/{database}'
engine = create_engine(connection_string)

query = """
SELECT p.city, p.date, p.min_temp_c, p.avg_temp_c, p.avg_humidity, p.daily_chance_of_rain, s.lat, s.lon
FROM prep_forecast_day p
JOIN staging_location s ON p.city = s.city AND p.region = s.region AND p.country = s.country
WHERE p.date >= '2024-06-01' AND p.date <= '2024-06-06';
"""
df = pd.read_sql(query, engine)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Big Cities Temperature Dashboard", style={'color': '#007BFF', 'textAlign': 'center'}), className="text-center my-4")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='city-dropdown',
                options=[{'label': city, 'value': city} for city in df['city'].unique()] + [{'label': 'All', 'value': 'All'}],
                value='All',
                className="mb-4"
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='temperature-map'), width=6),
        dbc.Col(dcc.Graph(id='line-chart'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='humidity-rain-chart'), width=12)
    ])
], fluid=True, style={'backgroundColor': '#F0F0F0'})

@app.callback(
    [Output('temperature-map', 'figure'),
     Output('line-chart', 'figure'),
     Output('humidity-rain-chart', 'figure')],
    Input('city-dropdown', 'value')
)
def update_figures(selected_city):
    if selected_city == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['city'] == selected_city]


    fig_map = px.scatter_geo(filtered_df,
                             lat='lat',
                             lon='lon',
                             color='avg_temp_c',
                             hover_name='city',
                             size='avg_temp_c',
                             projection='natural earth',
                             title=f'Temperature Overview for {selected_city}')
    
    fig_map.update_layout(
        geo=dict(
            showland=True,
            landcolor="whitesmoke",
            oceancolor="lightblue",
            showocean=True
        )
    )

    fig_line = px.line(filtered_df,
                       x='date', y=['min_temp_c', 'avg_temp_c'], color='city',
                       title='Temperature Fluctuations by City',
                       labels={'value': 'Temperature (°C)', 'variable': 'Metric'})
    
    fig_line.update_layout(
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        legend_title='City',
        plot_bgcolor='#F9F9F9',
        paper_bgcolor='#F0F0F0'
    )
    
    fig_humidity_rain = px.line(filtered_df,
                                x='date', y=['avg_humidity', 'daily_chance_of_rain'], color='city',
                                title='Humidity and Daily Chance of Rain by City',
                                labels={'value': 'Value', 'variable': 'Metric'})
    
    fig_humidity_rain.update_layout(
        xaxis_title='Date',
        yaxis_title='Value',
        legend_title='City',
        plot_bgcolor='#F9F9F9',
        paper_bgcolor='#F0F0F0'
    )
    
    return fig_map, fig_line, fig_humidity_rain

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)