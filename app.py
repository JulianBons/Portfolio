#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 13:15:22 2020

@author: julianbons
"""

import os

import style
import layout 
import pages
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.LITERA])
server = app.server 


app.layout = html.Div([dcc.Location(id='url'), layout.sidebar, layout.content, layout.footer])


@app.callback(
    [Output(f'page-{i}-link', 'active') for i in range(1, 4)],
    [Input('url', 'pathname')],
)

def toggle_active_links(pathname):
    if pathname == '/':
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f'/page-{i}' for i in range(1, 4)]


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_page_content(pathname):
    if pathname in ['/', '/page-1']:
        return pages.page1
    elif pathname == '/page-2':
        return pages.page2
    elif pathname == '/page-3':
        return pages.page3
    elif pathname == '/page-4':
        return pages.page4
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1('404: Not found', className='text-danger'),
            html.Hr(),
            html.P(f'The pathname {pathname} was not recognised...'),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)
    