import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# Load environment variables
dotenv_path = 'C:\\Users\\gergi\\Downloads\\dashboard\\dashboard\\token.env'
load_dotenv(dotenv_path)

# Database connection parameters
username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
database = os.getenv('DB_CLIMATE')
weather_api_key = os.getenv('WEATHER_API')

# Create a connection string and engine
connection_string = f'postgresql://{username}:{password}@{host}:{port}/{database}'
engine = create_engine(connection_string)

# Query to load data into DataFrame
query = """
SELECT city, year_and_week, avg_temp_c, lat, lon
FROM mart_conditions_week;
"""
df = pd.read_sql(query, engine)

# Initialize the Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # This line is added for deployment on Render

# Define the layout with Bootstrap components
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Interactive Temperature Dashboard"), className="text-center my-4")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='city-dropdown',
                options=[{'label': city, 'value': city} for city in df['city'].unique()],
                value='Berlin',
                className="mb-4"
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='temperature-map'), width=6),
        dbc.Col(dcc.Graph(id='line-chart'), width=6)
    ])
], fluid=True, style={'backgroundColor': 'neon green'})

@app.callback(
    [Output('temperature-map', 'figure'),
     Output('line-chart', 'figure')],
    Input('city-dropdown', 'value')
)
def update_figures(selected_city):
    filtered_df = df[df['city'] == selected_city]
    
    # Creating the scatter geo map for the selected city
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
    
    # Creating the line chart for temperature fluctuations
    fig_line = px.line(df[df['city'].isin([selected_city])],
                       x='year_and_week', y='avg_temp_c', color='city',
                       title='Temperature Fluctuations by City')
    
    fig_line.update_layout(
        xaxis_title='Week of the Year',
        yaxis_title='Average Temperature (°C)',
        legend_title='City'
    )
    
    return fig_map, fig_line

if __name__ == '__main__':
    app.run_server(debug=True)
