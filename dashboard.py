import dash
from dash import dcc
from dash import html
import plotly.express as px
import dash_mantine_components as dmc
import pandas as pd
import numpy as np

app = dash.Dash(__name__)

df = pd.read_csv('data/ml-latest/movies.csv')

#extract year from title
df['year'] = df.title.str.extract('.*\((\d{4})\).*', expand=False)
#drop movies without year
df = df.dropna(subset=['year'])
#convert year to int
df['year'] = pd.to_datetime(df['year'], format='%Y')

#remove year from title
df['title'] = df.title.str.replace('(\(\d\d\d\d\))', '')

#extract genres
df['genres'] = df.genres.str.split('|')
#doesnt work
df = df.dropna(subset=['genres'])
#represent each movie for each genre
df = df.explode('genres')

genres = [{'label': genre, 'value': genre} for genre in df['genres'].unique()]
#insert All at the beginning
genres.insert(0, {'label': 'All', 'value': 'All'})

# Definiere das Layout
app.layout = html.Div(children=[
    html.H1(children='Movie Lens Dashboard'),
    html.Div(children=[
        html.Label('Genres:'),
        dcc.Dropdown(
            id='genre-dropdown',
            options=genres,
            value=['Action'],  # Aktualisiere den Wert zu einer Liste von Genres
            multi=True  # Aktiviere Mehrfachauswahl
        ),
        html.Label('Date Range:'),
        dmc.RangeSlider(
            id="range-slider-callback",
            value=[df['year'].min().year, df['year'].max().year],
            min=df['year'].min().year,
            max=df['year'].max().year,
            step=1,
            marks=[
                {"value": df['year'].min().year, "label": str(df['year'].min().year)},
                {"value": df['year'].max().year, "label": str(df['year'].max().year)},
            ],
            mb=35,
        )
    ], style={'width': '100%', 'display': 'block'}),
    html.Div(children=[
        dcc.Graph(id='bar-chart',style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='bar-chart2',style={'width': '48%', 'display': 'inline-block'}),
    ] ),
    # Erstelle einen Container für die Plots
    html.Div(id='plot-container', children=[]),
])

# Definiere die Callback-Funktion für die Plots
@app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    [dash.dependencies.Input('genre-dropdown', 'value'),
     dash.dependencies.Input('range-slider-callback', 'value')
    ]
)
def update_movie_count_plots(selected_genres, date):
    print(date)
    # Konvertiere die ausgewählten Daten in Datetime-Objekte
    start_date = pd.to_datetime(date[0], format='%Y')
    end_date = pd.to_datetime(date[1], format='%Y')
    if selected_genres.count('All') > 0:
        selected_genres = df['genres'].unique()
    # Filtere das DataFrame nach dem aktuellen Genre und Datum
    filtered_df = df[(df['genres'].isin(selected_genres)) & (df['year'] >= start_date) & (df['year'] <= end_date)]
    
    # Gruppiere nach Jahr und zähle die Filme
    movie_count_by_year = filtered_df.groupby(['genres', 'year'])['movieId'].count().reset_index()
    movie_count_by_year['year'] = movie_count_by_year['year'].dt.year
    # rename column movieId to count
    movie_count_by_year = movie_count_by_year.rename(columns={'movieId': 'count'})

    # Erstelle den Balkendiagramm-Plot
    fig = px.bar(
        movie_count_by_year,
        x='year',
        y='count',
        color='genres',
        hover_data = ['genres', 'count']
    )
        
    # Aktualisiere das Layout des Plots
    fig.update_layout(
        title='Movie Count per Year',
        xaxis_title='Year',
        yaxis_title='Movie Count',
        height=600,
        hovermode='x unified'

    )
    fig.update_traces(hovertemplate="%{y}")
        
    return fig
# Definiere die Callback-Funktion für die Plots
@app.callback(
    dash.dependencies.Output('bar-chart2', 'figure'),
    [dash.dependencies.Input('genre-dropdown', 'value'),
     dash.dependencies.Input('range-slider-callback', 'value')
    ]
)
def update_movie_count_total(selected_genres, date):
    print(date)
    # Konvertiere die ausgewählten Daten in Datetime-Objekte
    start_date = pd.to_datetime(date[0], format='%Y')
    end_date = pd.to_datetime(date[1], format='%Y')
    if selected_genres.count('All') > 0:
        selected_genres = df['genres'].unique()
    # Filtere das DataFrame nach dem aktuellen Genre und Datum
    filtered_df = df[(df['genres'].isin(selected_genres)) & (df['year'] >= start_date) & (df['year'] <= end_date)]
    
    # Gruppiere nach Jahr und zähle die Filme
    movie_count_by_year = filtered_df.groupby(['genres'])['movieId'].count().reset_index()
    # rename column movieId to count
    movie_count_by_year = movie_count_by_year.rename(columns={'movieId': 'count'})

    # Erstelle den Balkendiagramm-Plot
    fig = px.bar(
        movie_count_by_year,
        x='genres',
        y='count',
        color='genres',
        hover_data = ['genres', 'count']
    )
        
    # Aktualisiere das Layout des Plots
    fig.update_layout(
        title='Movie Total Counts',
        xaxis_title='Genre',
        yaxis_title='Movie Count',
        height=600,
        hovermode='x unified'

    )
    fig.update_traces(hovertemplate="%{y}")
        
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)