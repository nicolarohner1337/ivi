import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
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

genre_colors = {}
for genre in df['genres'].unique():
    genre_colors[genre] = 'rgb({}, {}, {})'.format(*np.random.randint(0, 255, 3))

# Definiere das Layout
app.layout = html.Div(children=[
    html.H1(children='Movie Lens Dashboard'),
    html.Div(children=[
        html.Label('Genres:'),
        dcc.Dropdown(
            id='genre-dropdown',
            options=[{'label': genre, 'value': genre} for genre in df['genres'].unique()],
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
        ),
        dmc.Text(id="range-slider-output"),
    ], style={'width': '48%', 'display': 'inline-block'}),
    # Erstelle einen Container für die Plots
    html.Div(id='plot-container', children=[]),
])

# Definiere die Callback-Funktion für die Plots
@app.callback(
    dash.dependencies.Output('plot-container', 'children'),  # Verwende einen Container für die Plots
    [dash.dependencies.Input('genre-dropdown', 'value'),
     dash.dependencies.Input('range-slider-callback', 'value')
    ]
)
def update_movie_count_plots(selected_genres, date):
    print(date)
    # Konvertiere die ausgewählten Daten in Datetime-Objekte
    start_date = pd.to_datetime(date[0], format='%Y')
    end_date = pd.to_datetime(date[1], format='%Y')
    
    plots = []  # Erstelle eine leere Liste für die Plots
    
    # Iteriere über die ausgewählten Genres
    for genre in selected_genres:
        # Filtere das DataFrame nach dem aktuellen Genre und Datum
        filtered_df = df[(df['genres'] == genre) & (df['year'].between(start_date, end_date))]
        
        # Gruppiere nach Jahr und zähle die Filme
        movie_count_by_year = filtered_df.groupby('year')['movieId'].count()
        
        # Erstelle den Balkendiagramm-Plot
        fig = go.Figure(go.Bar(
            x=movie_count_by_year.index,
            y=movie_count_by_year.values,
            marker_color=genre_colors[genre]
        ))
        
        # Aktualisiere das Layout des Plots
        fig.update_layout(
            title=f'Movie Count for Genre: {genre}',
            xaxis_title='Year',
            yaxis_title='Movie Count',
            height=400,
            hovermode='x unified'
        )
        
        plots.append(html.Div(children=html.Div([
            dcc.Graph(figure=fig)  # Füge den Plot zur Liste der Plots hinzu
        ])))
    return plots

if __name__ == '__main__':
    app.run_server(debug=True)