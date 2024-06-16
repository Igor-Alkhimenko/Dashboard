import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Загрузка и обработка данных
df = pd.read_csv(r'C:\Users\Admin\Desktop\RPO_2_semmestr\dashbord\pythonProject\data.csv', sep=';')
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.DatePickerRange(
        id='date-picker',
        start_date=pd.to_datetime(df['Date and time'].min()),
        end_date=pd.to_datetime(df['Date and time'].max())
    ),
    dcc.Graph(id='graph'),
])


@app.callback(
    Output('graph', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_graph(start_date, end_date):
    filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]

    fig = px.line(filtered_df, x='Date and time', y=['ghi', 'dni', 'dhi'], title='Анализ солнечной радиации')
    fig.update_traces(mode='lines+markers')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)