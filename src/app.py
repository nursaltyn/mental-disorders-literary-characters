from collections import defaultdict, Counter
import pandas as pd
import dash
from dash import dcc
import dash_core_components as dcc
from dash import html
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

# Sample data

data = {
    'Country': ['Russia', 'Russia', 'Russia', 'France', 'France', 'France', 'France'],
    'Author': ['Dos', 'Dos', 'Tur', 'Dumas', 'Dumas', 'Hugo', 'Hugo'],
    'Disorder': ['Schizo', 'Depr', 'Schizo', 'Schizo', 'Depr', 'Depr', 'Depr'],
    'Male': [10, 20, 15, 25, 2, 1, 18],
    'Female': [5, 15, 8, 18, 1, 20, 10]
}

df = pd.DataFrame(data)

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Layout of the app
app.layout = html.Div([
    html.H1('Distribution of Mental Disorders'),
    html.Div([
        html.Label('Select a Country:'),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in df['Country'].unique()],
            value=df['Country'].unique()[0],
            multi=False
        ),
        html.Label('Select an Author:'),
        dcc.Dropdown(id='author-dropdown')
    ]),
    dcc.Graph(id='disorders-by-gender-and-country'),
    dcc.Graph(id='disorders-by-gender-and-author'),
    # Placeholder div for the interactive plot
    html.Div(id='interactive-plot-container')
])

# Callback to populate author dropdown based on selected country
@app.callback(
    Output('author-dropdown', 'options'),
    [Input('country-dropdown', 'value')]
)
def update_author_dropdown(selected_country):
    authors = df[df['Country'] == selected_country]['Author'].unique()
    options = [{'label': author, 'value': author} for author in authors]
    return options

# Callback to update the first bar chart (disorders by gender and country)
@app.callback(
    Output('disorders-by-gender-and-country', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_bar_chart_country(selected_country):
    filtered_df = df[df['Country'] == selected_country]
    filtered_df = filtered_df.drop(columns=['Author'])
    melted_df = filtered_df.melt(id_vars=['Disorder', 'Country'], var_name='Gender', value_name='Count')

    fig = px.bar(melted_df, x='Disorder', y='Count', color='Gender', barmode='group',
                 title=f'Distribution of Disorders by Gender in {selected_country}')

    return fig

# Callback to update the second bar chart (disorders by gender and author within selected country)
@app.callback(
    Output('disorders-by-gender-and-author', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('author-dropdown', 'value')]
)
def update_bar_chart_author(selected_country, selected_author):
    filtered_df = df[(df['Country'] == selected_country) & (df['Author'] == selected_author)]
    filtered_df = filtered_df.drop(columns=['Country'])
    melted_df = filtered_df.melt(id_vars=['Author', 'Disorder'], var_name='Gender', value_name='Count')

    fig = px.bar(melted_df, x='Disorder', y='Count', color='Gender', barmode='group',
                 title=f'Distribution of Disorders by Gender and Author in {selected_country} - {selected_author}')

    return fig


# Run the app
if __name__ == '__main__':

    app.run_server(debug=True)

