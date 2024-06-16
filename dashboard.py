import app
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from dash.dash_table.Format import Group
import plotly.graph_objects as go




# Загрузка и обработка данных
try:
    df = pd.read_csv(r'C:\Users\Admin\Desktop\RPO_2_semmestr\dashbord\pythonProject\data.csv', sep=';')
except Exception as e:
    print(f"Ошибка при загрузке данных: {e}")
    raise

# Проверка наличия всех необходимых столбцов
required_columns = ['Date and time', 'ghi', 'dni', 'dhi']
for column in required_columns:
    if column not in df.columns:
        print(f"Отсутствует обязательный столбец: {column}")
        raise ValueError(f"Отсутствует обязательный столбец: {column}")

# Преобразование столбца 'Date and time' в datetime
try:
    df['Date and time'] = pd.to_datetime(df['Date and time'])
except Exception as e:
    print(f"Ошибка при преобразовании столбца 'Date and time' в datetime: {e}")
    raise

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.DatePickerRange(
        id='date-picker',
        start_date=df['Date and time'].min(),
        end_date=df['Date and time'].max()
    ),
    dcc.Graph(id='line-graph'),
    dcc.Graph(id='bar-graph'),  # Столбчатая диаграмма
    dcc.Graph(id='histogram-graph'),  # Гистограмма
])


@app.callback(
    Output('line-graph', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_line_graph(start_date, end_date):
    try:
        filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]
    except Exception as e:
        print(f"Ошибка при фильтрации данных: {e}")
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_df['Date and time'], y=filtered_df['ghi'], mode='lines', name='GHI'))
    fig.add_trace(go.Scatter(x=filtered_df['Date and time'], y=filtered_df['dni'], mode='lines', name='DNI'))
    fig.add_trace(go.Scatter(x=filtered_df['Date and time'], y=filtered_df['dhi'], mode='lines', name='DHI'))
    fig.update_layout(title='Линейный график солнечной радиации', xaxis_title='Дата и время', yaxis_title='Мощность')
    return fig


@app.callback(
    Output('bar-graph', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_bar_graph(start_date, end_date):
    try:
        filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]

        # Проверка на наличие данных для агрегации
        if len(filtered_df) == 0:
            print("Нет данных для агрегации.")
            return go.Figure()

        # Пример агрегации по дням
        daily_radiation = filtered_df.groupby(filtered_df['Date and time'].dt.date)['ghi'].sum()  # Группировка по дате

        fig = go.Figure()
        fig.add_trace(go.Bar(x=daily_radiation.index, y=daily_radiation.values, name='Горячая точка'))
        fig.update_layout(title='Столбчатая диаграмма солнечной радиации по дням', xaxis_title='Дата',
                          yaxis_title='Суммарная мощность GHI')
        return fig
    except Exception as e:
        print(f"Ошибка при создании столбчатой диаграммы: {e}")
        return go.Figure()

    #создание гистограммы
@app.callback(
    Output('histogram-graph', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_histogram_graph(start_date, end_date):
    try:
        filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]
    except Exception as e:
        print(f"Ошибка при фильтрации данных: {e}")
        return go.Figure()

    fig = px.histogram(filtered_df, x='ghi', nbins=10)
    fig.update_layout(title='Гистограмма солнечной радиации', xaxis_title='Мощность GHI', yaxis_title='Частота')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)