__author__ = 'akashjeez'

'''
Install Below Python Modules Before Run this Python Script.
>>> pip install dash plotly pandas --upgrade
'''

import os, json, re, dash, warnings, pandas
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

warnings.filterwarnings("ignore")

app = dash.Dash(__name__, external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'])

server = app.server

app.config['suppress_callback_exceptions'] = True

def load_dataset():
	BASE_URL = "https://covid.ourworldindata.org/data"
	covid_data = pandas.read_csv(f"{BASE_URL}/ecdc/full_data.csv")
	population_data = pandas.read_csv(f"{BASE_URL}/ecdc/locations.csv")
	new_df = pandas.merge(covid_data, population_data, on = 'location', how = 'left')
	new_df.drop(['countriesAndTerritories', 'population'], axis = 1, inplace = True)
	new_df = new_df[ new_df.population_year == 2020.0]
	new_df['population_year'] = new_df['population_year'].astype(int)
	return new_df

'''
# Dataset Columns: 
date, location, new_cases, new_deaths, total_cases, total_deaths, continent, population_year,
'''

new_df = load_dataset()

year, month, day = dt.today().strftime('%Y-%m-%d').split('-')

app.layout = html.Div( children = [
	html.H3(children = "CoronaVirus | Data Analysis using Python Pandas & Dash!"),

	dcc.Tabs(id = 'tabs', value = 'tab-1', children = [
		dcc.Tab(label = 'By Country', value = 'tab-1', children = [
			html.Label("Select Countries"),
			dcc.Dropdown(
				id = 'country-dropdown',
				options = [{'label': i, 'value': i} for i in new_df.location.unique()],
			    value = ['India', 'United States'], multi = True
			),
			html.Label("Choose Date Range"),
			dcc.DatePickerRange(
				id = 'date-picker-1',
				end_date = dt(int(year), int(month), int(day)),
				display_format = 'DD-MMM-YYYY'
			),
			html.Div(id = 'output-graph-1'),
		]),
		dcc.Tab(label = 'By continent', value = 'tab-2', children = [
			html.Label("Select Continents"),
			dcc.Dropdown(
				id = 'continent-dropdown',
				options = [{'label': i, 'value': i} for i in new_df.continent.unique()],
			    value = ['Asia'], multi = True
			),
			html.Label("Choose Date Range"),
			dcc.DatePickerRange(
				id = 'date-picker-2',
				end_date = dt(int(year), int(month), int(day)),
				display_format = 'DD-MMM-YYYY'
			),
			html.Div(id = 'output-graph-2'),
		]),
	]),

	html.Br(), html.Br(),
	html.Div(children = [
		html.B(children = "References"),
		html.Br(),
		html.A(" => Python Pandas", href = 'https://pandas.pydata.org/', target = '_blank'),
		html.Br(),
		html.A(" => Python Dash", href = 'https://dash.plotly.com/', target = '_blank'),
		html.Br(),
		html.A(" => Coronavirus Source Data", href = "https://ourworldindata.org/coronavirus-source-data", target = '_blank'),
		html.Br(),
		html.A(" => Developed by Akashjeez", href = 'https://akashjeez.herokuapp.com', target = '_blank'),
	])
])


@app.callback(Output('output-graph-1', 'children'), [Input('country-dropdown', 'value'),
	Input('date-picker-1', 'start_date'), Input('date-picker-1', 'end_date') ])
def update_data_1(value, start_date, end_date):
	if start_date and end_date:
		start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d').strftime('%Y-%m-%d')
		end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d').strftime('%Y-%m-%d')
		dataset = new_df[ (new_df.location.isin(value)) & (new_df.date >= start_date) & (new_df.date <= end_date) ]
		stats = f"Total Cases: { dataset.sum(axis = 0)[2] } | Total Deaths: { dataset.sum(axis = 0)[3] }"
	else:
		dataset = new_df[ new_df.location.isin(value) ]
		temp = dataset[ dataset.date ==  sorted(dataset.date.unique())[-1] ].sum(axis = 0)
		stats = f"New Cases: {temp[2]} | New Deaths: {temp[3]} | Total Cases: {temp[4]} | Total Deaths: {temp[5]}"

	return html.Div(children = [
		html.Br(),
		html.H6(children = stats, style = { 'textAlign': 'center' }),
		dcc.Graph(
			id = 'graph-output-1',
			figure = {
				'data': [
					{'x': dataset['date'], 'y': dataset['total_cases'], 'type': 'line', 'name': 'Total Cases'},
					{'x': dataset['date'], 'y': dataset['total_deaths'], 'type': 'line', 'name': 'Total Deaths'},
					{'x': dataset['date'], 'y': dataset['new_cases'], 'type': 'line', 'name': 'New Cases'},
					{'x': dataset['date'], 'y': dataset['new_deaths'], 'type': 'line', 'name': 'New Deaths'},
				],
	            'layout': {
	                'title': f"COVID-19 | Country: {value}",
	                'xaxis': { 'title': 'Date' },
	                'yaxis': { 'title': 'Count' }
	            }
	        }
	    ),
	    html.Br(),
	    dash_table.DataTable(
			id = 'table-output', 
			style_as_list_view = True, style_cell = {'padding': '5px'},
			style_header = {'backgroundColor': 'white', 'fontWeight': 'bold' },
			columns = [{'name': i, 'id': i, 'selectable': True} for i in dataset.columns],
			data = dataset.to_dict('records'),
			sort_action = 'native', sort_mode = 'multi', page_action = 'native',
			page_current =  0, page_size = 10, export_format = 'xlsx', export_headers = 'display',
		)
	])

@app.callback(Output('output-graph-2', 'children'), [Input('continent-dropdown', 'value'),
	Input('date-picker-2', 'start_date'), Input('date-picker-2', 'end_date') ])
def update_data_1(value, start_date, end_date):
	if start_date and end_date:
		start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d').strftime('%Y-%m-%d')
		end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d').strftime('%Y-%m-%d')
		dataset = new_df[ (new_df.continent.isin(value)) & (new_df.date >= start_date) & (new_df.date <= end_date) ]
		stats = f"Total Cases: { dataset.sum(axis = 0)[2] } | Total Deaths: { dataset.sum(axis = 0)[3] }"
	else:
		dataset = new_df[ new_df.continent.isin(value) ]
		temp = dataset[ dataset.date ==  sorted(dataset.date.unique())[-1] ].sum(axis = 0)
		stats = f"New Cases: {temp[2]} | New Deaths: {temp[3]} | Total Cases: {temp[4]} | Total Deaths: {temp[5]}"

	return html.Div(children = [
		html.Br(),
		html.H6(children = stats, style = { 'textAlign': 'center' }),
		dcc.Graph(
			id = 'graph-output-2',
			figure = {
				'data': [
					{'x': dataset['date'], 'y': dataset['total_cases'], 'type': 'line', 'name': 'Total Cases'},
					{'x': dataset['date'], 'y': dataset['total_deaths'], 'type': 'line', 'name': 'Total Deaths'},
					{'x': dataset['date'], 'y': dataset['new_cases'], 'type': 'line', 'name': 'New Cases'},
					{'x': dataset['date'], 'y': dataset['new_deaths'], 'type': 'line', 'name': 'New Deaths'},
				],
	            'layout': {
	                'title': f"COVID-19 | Continent: {value}",
	                'xaxis': { 'title': 'Date' },
	                'yaxis': { 'title': 'Count' }
	            }
	        }
	    ),
	    html.Br(),
	    dash_table.DataTable(
			id = 'table-output', 
			style_as_list_view = True, style_cell = {'padding': '5px'},
			style_header = {'backgroundColor': 'white', 'fontWeight': 'bold' },
			columns = [{'name': i, 'id': i, 'selectable': True} for i in dataset.columns],
			data = dataset.to_dict('records'),
			sort_action = 'native', sort_mode = 'multi', page_action = 'native',
			page_current =  0, page_size = 10, export_format = 'xlsx', export_headers = 'display',
		),
		html.Br(), html.Br(),
		html.P(children = f" {value} Continent(s) Countries are { ', '.join(list(dataset.location.unique())) }"),
	])


if __name__ == '__main__':
	app.run_server(port = 8050, debug = True)
