import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import pandas as pd

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
        html.Label('Start Date:'),
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=df['year'].min(),
            max_date_allowed=df['year'].max(),
            initial_visible_month=df['year'].min(),
            date=df['year'].min().date()
        ),
        html.Label('End Date:'),
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=df['year'].min(),
            max_date_allowed=df['year'].max(),
            initial_visible_month=df['year'].max(),
            date=df['year'].max().date()
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    # Erstelle einen Container für die Plots
    html.Div(id='plot-container', children=[]),
])

# Definiere die Callback-Funktion für die Plots
@app.callback(
    dash.dependencies.Output('plot-container', 'children'),  # Verwende einen Container für die Plots
    [dash.dependencies.Input('genre-dropdown', 'value'),
     dash.dependencies.Input('start-date-picker', 'date'),
     dash.dependencies.Input('end-date-picker', 'date')]
)
def update_movie_count_plots(selected_genres, start_date, end_date):
    # Konvertiere die ausgewählten Daten in Datetime-Objekte
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
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
            marker_color='steelblue'
        ))
        
        # Aktualisiere das Layout des Plots
        fig.update_layout(
            title=f'Movie Count for Genre: {genre}',
            xaxis_title='Year',
            yaxis_title='Movie Count',
            height=400
        )
        
        plots.append(html.Div(children=html.Div([
            dcc.Graph(figure=fig)  # Füge den Plot zur Liste der Plots hinzu
        ])))
    return plots

if __name__ == '__main__':
    app.run_server(debug=True)