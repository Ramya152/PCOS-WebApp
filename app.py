import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

pd.set_option('display.max_columns', None)
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSzvFdxiPm9ppZt9BsLm_w2Cg2ZuVkgM3WDRKtlpFqNdJexmz6dTKYe8FXTgWxVFw/pub?output=csv'
df = pd.read_csv(url)
df.head()

#mapping months for correct ordering
#the order of months for sorting purposes
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
             7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

#extracting only month from'Patient Check-Up Date' column
df['Month'] = pd.to_datetime(df['Patient Check-Up Date']).dt.month

#replacing month numbers with their names using the map
df['Month'] = df['Month'].map(month_map)

#setting month column as a categorical type with a specific order for proper sorting
df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)

#extracting year from the 'Patient Check-Up Date' column
df['Year'] = pd.to_datetime(df['Patient Check-Up Date']).dt.year

#minimum and maximum years for the slider
min_year = df['Year'].min()
max_year = df['Year'].max()

# General Stats Visualization:
#count the number of people with and without PCOS
pcos_counts = df["PCOS (Y/N)"].value_counts()

#bar chart showing counts of PCOS and non-PCOS cases
fig1 = px.bar(
    x=["No PCOS", "PCOS"],
    y=pcos_counts.values,
    color=["No PCOS", "PCOS"],
    color_discrete_sequence=["#9370DB", "#FF69B4"],
    title="Count of People With vs Without PCOS",
    labels={"x": "Condition", "y": "Count"}
)

#adding annotations (numbers) above each bar
for i, count in enumerate(pcos_counts.values):
    fig1.add_annotation(
        x=i,  #bar position
        y=count + 10,
        text=str(count),  # showing the count
        showarrow=False,
        font=dict(size=12, color="black"),
        align="center"
    )

#=background color of the chart
fig1.update_layout(
    plot_bgcolor='#f8e8e8', #both light pink
    paper_bgcolor='#f8e8e8'
)

# Visualization 2: Youngest and Oldest PCOS Patients
#data with only PCOS patients
pcos_patients = df[df['PCOS (Y/N)'] == 1]

#youngest and oldest PCOS patients
youngest = pcos_patients.loc[pcos_patients[' Age (yrs)'].idxmin()]
oldest = pcos_patients.loc[pcos_patients[' Age (yrs)'].idxmax()]

#scatter plot showing the relationship between BMI and age for PCOS patients
fig2 = px.scatter(
    pcos_patients,
    x='BMI',
    y=' Age (yrs)',
    title='Relationship Between BMI, Age, and PCOS Prevalence',
    labels={' Age (yrs)': 'Age', 'BMI': 'Body Mass Index'},
    color_discrete_sequence=['pink']
)

#highlighting the youngest PCOS patient with markers
fig2.add_trace(go.Scatter(
    x=[youngest['BMI']],
    y=[youngest[' Age (yrs)']],
    mode='markers+text',
    marker=dict(symbol='star-diamond', size=15, color='purple', line=dict(width=2, color='black')),
    name='Youngest PCOS Patient',
    text=['Youngest PCOS Patient'],  #annotation text
    textposition='top center',
    showlegend=False  #avoiding legend as we are annotating
))

#highlighting the oldest PCOS patient with a marker
fig2.add_trace(go.Scatter(
    x=[oldest['BMI']],
    y=[oldest[' Age (yrs)']],
    mode='markers+text',
    marker=dict(symbol='diamond', size=15, color='purple', line=dict(width=2, color='black')),
    name='Oldest PCOS Patient',
    text=['Oldest PCOS Patient'],
    textposition='top center',
    showlegend=False
))

#same background colors for all vis
fig2.update_layout(
    plot_bgcolor='#f8e8e8',
    paper_bgcolor='#f8e8e8'
)
#mapping hair growth responses (0 = No, 1 = Yes) to readable labels
df['Hair_growth'] = df['hair growth(Y/N)'].map({0: 'No', 1: 'Yes'}).astype('category')
# copy pasted codes from previous exercise so have different dataframes with same info(data with only PCOS patients)
pcos_df = df[df['PCOS (Y/N)'] == 1]

#counting the hair growth responses among PCOS patients
hair_growth_counts = pcos_df['Hair_growth'].value_counts().reset_index()
hair_growth_counts.columns = ['Hair Growth', 'Count']

#pie chart showing the proportion of hair growth responses
pie_fig = go.Figure()
pie_fig.add_trace(go.Pie(
    labels=hair_growth_counts['Hair Growth'],
    values=hair_growth_counts['Count'],
    textinfo='percent+label',  #percentage and label on the slices
    hoverinfo='label+percent+value',
    marker=dict(colors=['purple', 'light pink'], line=dict(color='black', width=2))
))

#annotation to the title area for clarity
pie_fig.add_annotation(
    x=0.5,
    y=1.05,
    showarrow=False,
    font=dict(size=14, color='black'),
    align='center'
)

pie_fig.update_layout(
    plot_bgcolor='#f8e8e8',
    paper_bgcolor='#f8e8e8'
)

#median cycle length for PCOS and non-PCOS groups
median_cl = df.groupby('PCOS (Y/N)')['Cycle length(days)'].median().reset_index(drop=True)

#dataframe for the median values
median_df = pd.DataFrame({
    'PCOS (Y/N)': df['PCOS (Y/N)'].unique(),
    'Median Cycle Length (days)': median_cl
})

#subplots for cycle length comparison
fig_cl = make_subplots(rows=1, cols=2, subplot_titles=("Cycle Length by PCOS", "Median Cycle Length by PCOS"))

#box plot to show variability in cycle lengths
fig_cl.add_trace(go.Box(
    y=df['Cycle length(days)'],
    x=df['PCOS (Y/N)'],
    name="PCOS (Y/N)",
    marker_color='#F4C6D4',
    showlegend=False
), row=1, col=1)

#bar charts for the median cycle lengths
for pcos_status, color in zip(median_df['PCOS (Y/N)'].unique(), ['#D1A4D4', '#F4C6D4']):
    fig_cl.add_trace(go.Bar(
        x=[pcos_status],
        y=median_df[median_df['PCOS (Y/N)'] == pcos_status]['Median Cycle Length (days)'],
        name="Yes" if pcos_status == 1 else "No",
        marker_color=color
    ), row=1, col=2)

#background and axis titles for the subplot
fig_cl.update_layout(
    template='simple_white',
    legend_title_text='PCOS (Yes/No)',
    plot_bgcolor='#F8E8E8',
    paper_bgcolor='#F8E8E8'
)
fig_cl.update_xaxes(title_text="PCOS (Y/N)", row=1, col=1)
fig_cl.update_yaxes(title_text="Cycle Length", row=1, col=1)
fig_cl.update_xaxes(title_text="PCOS (Y/N)", row=1, col=2)
fig_cl.update_yaxes(title_text="Median Cycle Length", row=1, col=2)

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server
#app's layout
app.layout = html.Div(
    style={'backgroundColor': '#f8e8e8', 'padding': '20px'},  #background color and padding
    children=[
        html.H1("PCOS Data Visualization", style={'textAlign': 'center', 'color': '#333333'}),  #page title
        dcc.Tabs(  # Tabs for navigation
            style={'backgroundColor': '#f8e8e8'},  #background color for tabs
            children=[
                dcc.Tab(  # Tab 1: General Stats
                    label='General Stats',
                    style={'backgroundColor': '#f8e8e8'},
                    children=[
                        html.Div([dcc.Graph(id='general-stats-graph', figure=fig1),  #bar chart for PCOS counts
                                  html.P("The majority of the dataset shows individuals without PCOS. "
                                         "This suggests a need to focus on the specific factors affecting the smaller group with PCOS.")
                                  ]),
                        html.Div([
                            dcc.Graph(id='causes-graph'),  #monthly trends bar chart
                            html.P("This bar chart reveals monthly trends in PCOS cases across different age groups."),
                            html.Div([
                                html.Label("Select Year:"),
                                dcc.Slider(
                                    id='year-slider',
                                    min=min_year,
                                    max=max_year,
                                    value=min_year,
                                    marks={year: str(year) for year in range(min_year, max_year + 1)},  #year slider
                                    step=None
                                )
                            ], style={'padding': '20px'})
                        ]),
                        html.Div([dcc.Graph(id='general-stats-graph2', figure=fig2),  #scatter plot for age and BMI
                                  html.P(
                                      f"The youngest PCOS patient is {youngest[' Age (yrs)']} years old with a BMI of {youngest['BMI']:.2f}. "
                                      f"The oldest patient is {oldest[' Age (yrs)']} years old with a BMI of {oldest['BMI']:.2f}. "
                                      "The plot highlights these patients with markers."
                                  )]),
                    ]
                ),

                dcc.Tab(  # Tab 2: Effects
                    label='Effects',
                    style={'backgroundColor': '#f8e8e8'},
                    children=[
                        html.Div([
                            html.H2("Effects of PCOS on Cycle Length"),
                            html.P("Explore the relationship between PCOS and cycle length."),
                            dcc.Graph(id='pcos-cycle-length-graph', figure=fig_cl),  #cycle length box plot
                            html.P("The box plot shows variability in cycle lengths between individuals with and without PCOS. "
                                   "Interestingly, the median cycle length is the same for both groups. However, the highest and lowest values differ significantly, "
                                   "indicating greater abnormalities for PCOS individuals.")
                        ], style={'padding': '20px'}),
                        html.Div([
                            html.Label("Select X-Axis Metric:"),  #dropdown for metric selection
                            dcc.Dropdown(
                                id='x-axis-dropdown',
                                options=[
                                    {'label': 'Pulse Rate (bpm)', 'value': 'Pulse rate(bpm) '},
                                    {'label': 'Weight (Kg)', 'value': 'Weight (Kg)'},
                                    {'label': 'Cycle Length (days)', 'value': 'Cycle length(days)'},
                                    {'label': 'FSH (mIU/mL)', 'value': 'FSH(mIU/mL)'},
                                ],
                                value='Pulse rate(bpm) ',  #default selection
                                style={'width': '40%'}
                            )
                        ], style={'padding': '10px'}),
                        html.Div([dcc.Graph(id='bmi-pulse-tsh-graph', figure=fig2)]),  #subplots for effects
                        html.Div([ html.H2('Proportion of Hair Growth Responses Among PCOS Patients'),
                                  dcc.Graph(id='effects-pie-chart', figure=pie_fig)
                      ])  #pie chart for hair growth
                    ]
                )
            ]
        )
    ]
)

age_group_mapping = {'Teen': 1, 'Young Adult': 2, 'Middle-aged Adult': 3, 'Senior Adult': 4}
df['Age Group Num'] = df['Age Group'].map(age_group_mapping)
color_mapping = {
    1: 'blue',
    2: 'violet',
    3: 'light pink',
    4: 'purple'}

#callback for Interactive BMI-Pulse-TSH plot based on dropdown selections
@app.callback(
    Output('bmi-pulse-tsh-graph', 'figure'),
    Input('x-axis-dropdown', 'value')
)
def update_bmi_pulse_tsh(x_axis):

    #two subplots in a single row
    fig2 = make_subplots(
        rows=1,
        cols=2,
        specs=[[{}, {}]],
        subplot_titles=(f'TSH vs {x_axis}', f'BMI vs {x_axis}')
    )

    #plot 1 (TSH vs Selected Value)
    fig2.add_trace(
        go.Scatter(
            x=df[x_axis],
            y=df['TSH (mIU/L)'],
            mode='markers',
            marker=dict(color=df['Age Group Num'].map(color_mapping)),
            hovertemplate=f'Age Group: %{{customdata[0]}}<br>{x_axis}: %{{x}}<br>TSH: %{{y}}<extra></extra>',
            customdata=df[['Age Group']],
            showlegend=False
        ),
        row=1, col=1
    )

    #plot 2 (BMI vs Selected Value)
    fig2.add_trace(
        go.Scatter(
            x=df[x_axis],
            y=df['BMI'],
            mode='markers',
            marker=dict(color=df['Age Group Num'].map(color_mapping)),
            hovertemplate=f'Age Group: %{{customdata[0]}}<br>{x_axis}: %{{x}}<br>BMI: %{{y}}<extra></extra>',
            customdata=df[['Age Group']],
            showlegend=False
        ),
        row=1, col=2
    )

    fig2.update_layout(title=f'{x_axis} vs TSH and BMI by Age Group', showlegend=True)

    #legend items for age groups
    for age, color in color_mapping.items():
        fig2.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(color=color),
                name=f'Age Group {age}',
                showlegend=True
            )
        )
    fig2.update_layout(plot_bgcolor='#f8e8e8', paper_bgcolor='#f8e8e8')
    return fig2



#callback for the Third Visualization
@app.callback(
    Output('causes-graph', 'figure'),
    Input('year-slider', 'value')
)
def update_general_stats(selected_year):
    filtered_df = df[(df['PCOS (Y/N)'] == 1) & (df['Year'] == selected_year)]
    counts = filtered_df.groupby(['Month', 'Age Group', 'PCOS (Y/N)']).size().reset_index(name='Count')
    colors = {'Young Adult': 'purple', 'Other Age Groups': 'lightpink'}
    fig = px.bar(
        counts,
        x='Month',
        y='Count',
        color='Age Group',
        title=f'Number of PCOS Cases per Month by Age Group - {selected_year}',
        labels={'Count': 'Number of PCOS Cases', 'Month': 'Month'},
        color_discrete_map=colors,
        barmode='stack'
    )
    fig.update_layout(plot_bgcolor='#f8e8e8', paper_bgcolor='#f8e8e8')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
