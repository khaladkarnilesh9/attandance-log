import dash
from dash import dcc, html # dcc for Dash Core Components, html for HTML tags
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta, date
import numpy as np # For data generation if not using CSV

# --- 1. Data Preparation ---
# If you generated 'sample_analytics_data.csv', load it:
try:
    df_original = pd.read_csv('sample_analytics_data.csv')
    df_original['timestamp'] = pd.to_datetime(df_original['timestamp'])
except FileNotFoundError:
    print("sample_analytics_data.csv not found. Generating dummy data...")
    # Fallback to generating dummy data if CSV is not present
    num_records = 2000
    end_date_gen = datetime.now()
    start_date_gen = end_date_gen - timedelta(days=60) # Generate data for 60 days
    timestamps_gen = [start_date_gen + timedelta(seconds=np.random.randint(0, int((end_date_gen - start_date_gen).total_seconds())))
                      for _ in range(num_records)]
    timestamps_gen.sort()
    pages_gen = ['/home', '/products', '/about', '/contact', '/blog/article1', '/blog/article2', '/services', '/pricing']
    page_visits_gen = np.random.choice(pages_gen, num_records, p=[0.25, 0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
    user_ids_gen = [f'user_{np.random.randint(1, 100)}' for _ in range(num_records)]
    df_original = pd.DataFrame({
        'timestamp': timestamps_gen,
        'page': page_visits_gen,
        'user_id': user_ids_gen
    })
    df_original['timestamp'] = pd.to_datetime(df_original['timestamp'])

# Ensure 'date' column exists for easier filtering by DatePickerRange
df_original['date'] = df_original['timestamp'].dt.date

# --- 2. Initialize Dash App ---
# Using a Bootstrap theme for better styling out-of-the-box
# You can install it: pip install dash-bootstrap-components
try:
    import dash_bootstrap_components as dbc
    external_stylesheets = [dbc.themes.BOOTSTRAP]
except ImportError:
    print("dash-bootstrap-components not found. Using default Dash styling.")
    external_stylesheets = []

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Analytics Dashboard"

# --- 3. App Layout ---
app.layout = html.Div(children=[
    html.H1(children='My Web Analytics Dashboard', style={'textAlign': 'center', 'marginBottom': '20px'}),

    # Date Range Picker
    html.Div([
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=df_original['date'].min(),
            max_date_allowed=df_original['date'].max(),
            initial_visible_month=df_original['date'].max(),
            start_date=df_original['date'].max() - timedelta(days=29), # Default to last 30 days
            end_date=df_original['date'].max(),
            display_format='YYYY-MM-DD',
            style={'marginRight': '20px'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),

    # Row for KPIs
    html.Div(className='row', children=[ # Using 'row' class if Bootstrap is available
        html.Div(id='kpi-total-page-views', className='four columns', style={'padding': '10px', 'border': '1px solid #eee', 'textAlign': 'center', 'margin': '5px'}),
        html.Div(id='kpi-unique-visitors', className='four columns', style={'padding': '10px', 'border': '1px solid #eee', 'textAlign': 'center', 'margin': '5px'}),
        html.Div(id='kpi-avg-views-per-day', className='four columns', style={'padding': '10px', 'border': '1px solid #eee', 'textAlign': 'center', 'margin': '5px'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'} if not external_stylesheets else {}), # Basic flex if no bootstrap

    # Row for Charts
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[ # Half width if Bootstrap
            dcc.Graph(id='page-views-over-time-chart')
        ], style={'width': '48%', 'display': 'inline-block'} if not external_stylesheets else {}),
        html.Div(className='six columns', children=[ # Half width if Bootstrap
            dcc.Graph(id='top-pages-chart')
        ], style={'width': '48%', 'display': 'inline-block'} if not external_stylesheets else {}),
    ]),

], style={'padding': '20px'})


# --- 4. Callbacks ---
@app.callback(
    [Output('kpi-total-page-views', 'children'),
     Output('kpi-unique-visitors', 'children'),
     Output('kpi-avg-views-per-day', 'children'),
     Output('page-views-over-time-chart', 'figure'),
     Output('top-pages-chart', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dashboard(start_date_str, end_date_str):
    # Convert string dates from DatePickerRange to datetime.date objects
    start_date = datetime.strptime(start_date_str.split('T')[0], '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str.split('T')[0], '%Y-%m-%d').date()

    # Filter DataFrame based on selected date range
    # Note: df_original['date'] is already datetime.date
    filtered_df = df_original[(df_original['date'] >= start_date) & (df_original['date'] <= end_date)]

    if filtered_df.empty:
        empty_fig = {'data': [], 'layout': {'title': 'No data for selected period'}}
        return "Total Page Views: 0", "Unique Visitors: 0", "Avg Views/Day: 0", empty_fig, empty_fig

    # --- Calculate KPIs ---
    total_page_views = len(filtered_df)
    unique_visitors = filtered_df['user_id'].nunique()

    # Avg Views per Day
    num_days = (end_date - start_date).days + 1
    avg_views_per_day = total_page_views / num_days if num_days > 0 else 0

    kpi_pv_children = [html.H3(f"{total_page_views:,}"), html.P("Total Page Views")]
    kpi_uv_children = [html.H3(f"{unique_visitors:,}"), html.P("Unique Visitors")]
    kpi_avg_children = [html.H3(f"{avg_views_per_day:.1f}"), html.P("Avg Views/Day")]


    # --- Generate Charts ---
    # Page Views Over Time
    page_views_daily = filtered_df.groupby(filtered_df['timestamp'].dt.date)['page'].count().reset_index()
    page_views_daily.columns = ['date', 'views']
    fig_page_views_time = px.line(page_views_daily, x='date', y='views',
                                  title='Page Views Over Time',
                                  labels={'date': 'Date', 'views': 'Page Views'})
    fig_page_views_time.update_layout(margin=dict(l=20, r=20, t=40, b=20))


    # Top Pages
    top_n = 10
    top_pages = filtered_df['page'].value_counts().nlargest(top_n).reset_index()
    top_pages.columns = ['page', 'count']
    fig_top_pages = px.bar(top_pages, x='count', y='page', orientation='h',
                           title=f'Top {top_n} Visited Pages',
                           labels={'page': 'Page URL', 'count': 'Number of Visits'})
    fig_top_pages.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=150, r=20, t=40, b=20)) # Ensure long page names are visible

    return kpi_pv_children, kpi_uv_children, kpi_avg_children, fig_page_views_time, fig_top_pages

# --- 5. Run the App ---
if __name__ == '__main__':
    app.run_server(debug=True) # debug=True allows for hot-reloading
