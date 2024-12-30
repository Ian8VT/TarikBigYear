import csv
import plotly.graph_objs as go
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import os


# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path to the CSV file
filenameAggregatedSpecies = os.path.join(script_dir, 'data', 'MyEBirdDataSpeciesSum.csv')


def create_dict_from_csv(filename):
    result_dict = {}
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            key = row[0]
            value = (float(row[1]), int(row[2]))
            result_dict[key] = value
    return result_dict

combined_dict = create_dict_from_csv(filenameAggregatedSpecies)
    
# Extract x and y values along with keys for popups
x_values = []
y_values = []
hover_texts = []

for key, value in combined_dict.items():
    x_values.append(value[1])  # First element for x
    y_values.append(value[0])  # Second element for y
    hover_texts.append(f"{key}<br>Identified in {value[0]}% of Checklists<br>Counted {value[1]} Individuals")

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Specify custom marks for the slider
slider_marks = {i: str(i) for i in range(0, int(max(x_values)), 100)}

app.layout = html.Div([
    dcc.Graph(id='scatter-plot'),
    dcc.RangeSlider(
        id='x-range-slider',
        min=min(x_values),
        max=max(x_values),
        value=[min(x_values), max(x_values)],
        marks=slider_marks,
        step=50
    )
])

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('x-range-slider', 'value')
)
def update_scatter_plot(x_range):
    # Filter x and y values based on the selected range
    filtered_x = [x for x in x_values if x_range[0] <= x <= x_range[1]]
    filtered_y = [y_values[i] for i, x in enumerate(x_values) if x_range[0] <= x <= x_range[1]]
    filtered_hover_texts = [hover_texts[i] for i, x in enumerate(x_values) if x_range[0] <= x <= x_range[1]]

    # Calculate the maximum y value, defaulting to 0 if no values are filtered
    max_y = max(filtered_y) if filtered_y else 0
    # Determine max value on y-axis
    if max_y > 0:
        max_y_rounded = ((max_y // 10) + 1.5) * 10
    else:
        max_y_rounded = 10  # Default to 10 if max_y is 0

    max_x= max(filtered_x) if filtered_x else 0
    if max_x > 0:
        max_x_rounded = ((max_x // 10) + 15) * 10
    else:
        max_x_rounded = 10  # Default to 10 if max_y is 0

    max_marker_size = 15
    fig = go.Figure(data=go.Scatter(
        x=filtered_x,
        y=filtered_y,
        mode='markers',
        marker=dict(
            size=filtered_x,
            sizeref=max(filtered_x) / (max_marker_size ** 2),
        ),
        text=filtered_hover_texts,  # Custom hover text
        hoverinfo='text'  # Show only the text on hover
    ))

    fig.update_layout(
        title='Bird Species Count and Frequency',
        xaxis_title='Count of Individual Birds',
        yaxis_title='% Checklists Species Observed',
        yaxis=dict(range=[0, max_y_rounded]),  # Set y-axis range from 0 to rounded max y
        xaxis=dict(range=[0, max_x_rounded])
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=False)
