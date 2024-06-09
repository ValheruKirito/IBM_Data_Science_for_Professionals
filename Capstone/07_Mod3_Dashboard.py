# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_site_options = [{'label': 'All Sites', 'value': 'ALL'}]
for i in spacex_df['Launch Site'].unique():
    launch_site_options.append({'label': i, 'value': i})

# Create a dash application
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        html.H3("Select Launch Site",
            style={'fontsize': 20}),
        html.Div(
            dcc.Dropdown(
                id='site-dropdown',
                options=launch_site_options,
                value='ALL',
                placeholder='Select a Launch Site here',
                searchable=True,
                style={'font-size': 20}
            ),
            style={'fontsize': 20}
        ),
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),

        html.H3("Payload range (Kg):",
            style={'fontsize': 20}),
        # TASK 3: Add a slider to select payload range
        html.Div(
            dcc.RangeSlider(
                id="payload-slider",
                min=0,
                max=10000,
                step=1000,
                value=[min_payload, max_payload],
                allowCross=False,
                updatemode='drag',
                marks={
                    i: {'label': str(i), 'style': {'font-size': '20px'}}
                    for i in range(0, 10001, 2000)
                }
            ),
            style={'padding-bottom': '20px'}
        ),

        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ]
)

# TASK 2:
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def plot_succes_pie(site):
    """
    The function `plot_succes_pie` generates a pie chart showing the distribution
    of successful missions per launch site in a SpaceX dataset.
    
    :param site: The `site` parameter in the `plot_succes_pie` function is used to
    specify the launch site for which you want to plot the successful missions. If
    the `site` is set to 'ALL', the function will plot the successful missions for
    all launch sites combined. If a specific launch
    :return: The function `plot_succes_pie(site)` returns a pie chart figure
    (`fig`) showing the distribution of successful missions per launch site. The
    chart is based on the data in the `spacex_df` DataFrame. If the input `site` is
    'ALL', the pie chart will show successful missions for all launch sites. If a
    specific launch site is provided, the pie chart will display
    """
    if site == 'ALL':
        fig1 = px.pie(
            data_frame=spacex_df,
            values='class',
            names='Launch Site',
            title='Successful Missions per Site'
        )
    else:
        filter_idx = spacex_df['Launch Site'] == site
        filtered = spacex_df[filter_idx]
        counts = filtered.groupby('class', as_index=False).count()
        counts = counts.rename(
            columns={'class': 'Success', 'Unnamed: 0': 'Count'}
        )
        counts['Success'] = counts['Success'].map({0: 'No', 1: 'Yes'})
        fig1 = px.pie(
            data_frame=counts,
            values='Count',
            names='Success',
            title='Portion of Successful Missions'
        )
    fig1.update_layout()
    return fig1

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(
        component_id='success-payload-scatter-chart',
        component_property='figure'
    ),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def plot_scatter_mass_success(site, payl):
    """
    The function `plot_scatter_mass_success` generates a scatter plot or pie chart
    based on the payload mass and launch site data from a SpaceX dataset.
    
    :param site: The `site` parameter in the `plot_scatter_mass_success` function
    is used to specify the launch site for which you want to plot the data. If you
    pass 'ALL' as the value for `site`, a scatter plot will be generated showing
    the relationship between payload mass and mission success for
    :param payl: The `payl` parameter in the `plot_scatter_mass_success` function
    represents a list containing two elements. The first element is the lower bound
    of the payload mass range, and the second element is the upper bound of the
    payload mass range. This range is used to filter the data based on
    :return: The function `plot_scatter_mass_success` returns a plotly figure
    object based on the input parameters `site` and `payl`. If the `site` parameter
    is set to 'ALL', a scatter plot showing the relationship between payload mass
    and mission success is returned. If a specific launch site is provided, a pie
    chart showing the distribution of successful missions per site is returned.
    """
    data = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payl[0]) &
        (spacex_df['Payload Mass (kg)'] <= payl[1])
    ]
    if site == 'ALL':
        fig2 = px.scatter(
            data_frame=data,
            x='Payload Mass (kg)',
            y='class',
            title='Mission success with respect to payload',
            color='Booster Version Category'
        )
    else:
        filtered = data[data['Launch Site'] == site]
        fig2 = px.scatter(
            data_frame=filtered,
            x='Payload Mass (kg)',
            y='class',
            title='Mission success with respect to payload',
            color='Booster Version Category'
        )
    fig2.update_layout()
    return fig2


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
