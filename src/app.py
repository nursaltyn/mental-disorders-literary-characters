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
import json
# Sample data

json_file_path = '/content/drive/MyDrive/softpr_sose23/Datasets/characters_disorders/vis_data.json'
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

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
            options=[{'label': country.capitalize(), 'value': country} for country in list(data['country'].keys())],
            value=list(data['country'].keys())[0],
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
    authors = df['country'][selected_country].keys()
    options = [{'label': author, 'value': author} for author in authors]
    return options

# Callback to update the first bar chart (disorders by gender and country)
@app.callback(
    Output('disorders-by-gender-and-country', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_bar_chart_country(selected_country):
    # Create separate DataFrames for males and females
  filtered_df = pd.DataFrame(df['country'][selected_country])

  # Reset the index and move it into a new column
  filtered_df.reset_index(inplace=True)

  # Rename the new column (optional)
  filtered_df.rename(columns={'index': 'disorders'}, inplace=True)

  male, female = [], []
  for ind in filtered_df.index:
    male_interm = 0
    female_interm = 0
    for author in filtered_df.keys():
      try:
        male_interm += filtered_df[author][ind]['male']
        female_interm += filtered_df[author][ind]['female']
      except:
        next
    male.append(male_interm)
    female.append(female_interm)

  filtered_df['male'] = male
  filtered_df['female'] = female
  authors = df['country'][selected_country].keys()

  filtered_df = filtered_df.drop(columns=[col for col in authors])
  melted_df = filtered_df.melt(id_vars=['disorders'], var_name='Gender', value_name='Count')
  male_df = melted_df[melted_df['Gender'] == 'male']
  female_df = melted_df[melted_df['Gender'] == 'female']

  # Define distinct color sequences for males and females
  color_sequence_male = ['#1f77b4', '#aec7e8']  # Blue shades
  color_sequence_female = ['#ff7f0e', '#ffbb78']  # Orange shades

  # Create individual bar charts for males and females with distinct colors
  fig = px.bar(male_df, x='Count', y='disorders', orientation='h', text='Count',
              title=f'Distribution of Disorders by Gender in {selected_country}',
              color='Gender', color_discrete_sequence=color_sequence_male,
              labels={'Gender': 'Legend'})
  fig.update_traces(texttemplate='%{text}', textposition='inside', marker=dict(line=dict(color='navy', width=1)))

  fig2 = px.bar(female_df, x='Count', y='disorders', orientation='h', text='Count',
                title=f'Distribution of Disorders by Gender in {selected_country.capitalize()}',
                color='Gender', color_discrete_sequence=color_sequence_female,
                labels={'Gender': 'Legend'})
  fig2.update_traces(texttemplate='%{text}', textposition='inside', marker=dict(line=dict(color='firebrick', width=1)))

  # Combine the two figures
  fig.add_trace(fig2.data[0])

  # Customize layout
  fig.update_layout(barmode='relative', xaxis_tickangle=-45,
                    xaxis_title='Total count of Cases', yaxis_title='Disorders',
                    paper_bgcolor='white')

  # Adjust the figure size
  fig.update_layout(width=1000, height=600)

  # Show the population pyramid plot
  return fig

# Callback to update the second bar chart (disorders by gender and author within selected country)
@app.callback(
    Output('disorders-by-gender-and-author', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('author-dropdown', 'value')]
)
def update_bar_chart_author(selected_country, selected_author):
    filtered_df = pd.DataFrame(df['country'][selected_country])
    filtered_df.reset_index(inplace=True)
    # Rename the new column (optional)
    filtered_df.rename(columns={'index': 'disorders'}, inplace=True)
    melted_df = filtered_df.melt(id_vars=['disorders'], var_name='author')

    male, female = [], []
    for ind in range(len(melted_df)):
      try:
        male.append(melted_df['value'][ind]['male'])
        female.append(melted_df['value'][ind]['female'])
      except:
        male.append(0)
        female.append(0)

    melted_df['male'] = male
    melted_df['female'] = female
    #delete all rows where the values are both 0
    melted_df = melted_df[(melted_df['male'] != 0) | (melted_df['female'] != 0)]
    melted_df = melted_df.drop(columns = ['value'])
    melted_df = melted_df.melt(id_vars=['author', 'disorders'], var_name='gender', value_name='count')
    melted_df = melted_df[(melted_df['author'] == selected_author)]
    fig = px.bar(melted_df, x='disorders', y='count', color='gender', barmode='group',
                title=f'Distribution of Disorders by Gender and Author in {selected_country.capitalize()} - {selected_author}')


    return fig


# Run the app
if __name__ == '__main__':

    app.run_server(debug=True)