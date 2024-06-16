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
    df = pd.read_csv(r'C:\Users\Admin\Desktop\RPO_2_semmestr\dashbord\pythonProject\data.csv', sep=';', parse_dates=['Date and time'], date_format="%Y-%m-%dT%H:%M:%S%z")
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
dcc.Upload(
        id='upload-data',
        children=html.Div(['Перетащите CSV файл сюда или ', html.A('нажмите здесь', style={'display':'inline-block'}), ' для загрузки']),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.H2("Первые 10 строк исходной таблицы данных для предпросмотра"),
    dash_table.DataTable(
        id='preview-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.head(10).to_dict('records'),
        style_cell={'whiteSpace': 'normal'},
        style_header={'fontWeight': 'bold'},
        style_table={'overflowX': 'auto'}
    ),
    dcc.DatePickerRange(
        id='date-picker',
        start_date=df['Date and time'].min(),
        end_date=df['Date and time'].max()
    ),
    dcc.Dropdown(
        id='analysis-parameter-dropdown',
        options=[
            {'label': 'GHI', 'value': 'ghi'},
            {'label': 'DNI', 'value': 'dni'},
            {'label': 'DHI', 'value': 'dhi'}
        ],
        placeholder="Выберите параметр анализа"
    ),
    dcc.Graph(id='line-graph'),
    dcc.Graph(id='bar-graph'),  # Столбчатая диаграмма
    dcc.Graph(id='histogram-graph'),  # Гистограмма
    dcc.Graph(id='pie-chart'),  # Круговая диаграмма
    dcc.Graph(id='scatter-3d')   # 3D scatter plot
])

@app.callback(
    Output('line-graph', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('analysis-parameter-dropdown', 'value')]
)
def update_line_graph(start_date, end_date, parameter):
    try:
        filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]
    except Exception as e:
        print(f"Ошибка при фильтрации данных: {e}")
        return go.Figure()

    if parameter:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=filtered_df['Date and time'], y=filtered_df[parameter], mode='lines', name=parameter))
        fig.update_layout(title=f'Линейный график {parameter}', xaxis_title='Дата и время', yaxis_title='Мощность')
        return fig
    else:
        return go.Figure()


@app.callback(
    Output('bar-graph', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('analysis-parameter-dropdown', 'value')]
)
def update_bar_graph(start_date, end_date, parameter):
    try:
        filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]
    except Exception as e:
        print(f"Ошибка при фильтрации данных: {e}")
        return go.Figure()

    if parameter:
        # Пример агрегации по дням для выбранного параметра
        daily_radiation = filtered_df.groupby(filtered_df['Date and time'].dt.date)[parameter].sum()  # Группировка по дате

        fig = go.Figure()
        fig.add_trace(go.Bar(x=daily_radiation.index, y=daily_radiation.values, name=parameter))
        fig.update_layout(title=f'Столбчатая диаграмма {parameter} по дням', xaxis_title='Дата',
                          yaxis_title='Суммарное значение')
        return fig
    else:
        return go.Figure()

@app.callback(
    Output('histogram-graph', 'figure'),
    [Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
    Input('analysis-parameter-dropdown', 'value')]
    )
def update_histogram_graph(start_date, end_date, parameter):
    try:
        filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]
    except Exception as e:
        print(f"Ошибка при фильтрации данных: {e}")
        return go.Figure()

    if parameter:
        fig = px.histogram(filtered_df, x=parameter, nbins=10)
        fig.update_layout(title=f'Гистограмма {parameter}', xaxis_title=parameter, yaxis_title='Частота')
        return fig
    else:
        return go.Figure()


@app.callback(
    Output('pie-chart', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('analysis-parameter-dropdown', 'value')]
)
def update_pie_chart(start_date, end_date, parameter):
    try:
        filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]
    except Exception as e:
        print(f"Ошибка при фильтрации данных: {e}")
        return go.Figure()

    if parameter:
        total_values = {
            'ghi': filtered_df['ghi'].sum(),
            'dni': filtered_df['dni'].sum(),
            'dhi': filtered_df['dhi'].sum()
        }
        selected_value = total_values.pop(parameter)

        # Вычисляем общую сумму остальных параметров
        other_values_sum = sum(value for value in total_values.values())

        # Вычисляем процентное соотношение выбранного параметра к сумме остальных
        percentage_of_selected = (selected_value / other_values_sum) * 100

        # Формируем значения для круговой диаграммы
        values = [percentage_of_selected] + list(total_values.values())
        names = ['% Выбранного параметра к остальным'] + list(total_values.keys())

        fig = go.Figure(data=[go.Pie(labels=names, values=values, hole=.5)])
        fig.update_traces(hovertemplate='%{label}<br>%{value} (<i>%{percent}</i>)')  # Добавляем hovertemplate
        fig.update_layout(title_text='Процентное соотношение выбранного параметра радиации к сумме остальных параметров')
        return fig
    else:
        return go.Figure()

@app.callback(
    Output('scatter-3d', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('analysis-parameter-dropdown', 'value')]
)
def update_scatter_3d_plot(start_date, end_date, parameter):
    try:
        filtered_df = df[(df['Date and time'] >= start_date) & (df['Date and time'] <= end_date)]
    except Exception as e:
        print(f"Ошибка при фильтрации данных: {e}")
        return go.Figure()

    if parameter:
        fig = go.Figure(data=[go.Scatter3d(
            x=filtered_df['ghi'],
            y=filtered_df['dni'],
            z=filtered_df['dhi'],
            mode='markers',
            marker=dict(
                size=8,
                line=dict(
                    color='rgba(204, 204, 204, 1.0)',
                    width=0.5
                ),
                opacity=0.8
            )
        )])
        fig.update_layout(
            scene=dict(
                xaxis_title='GHI',
                yaxis_title='DNI',
                zaxis_title='DHI',
                aspectratio=dict(x=1, y=1, z=0.7)
            )
        )
        fig.update_layout(title_text='Точечный 3D график - 3D scatter plot ')
        return fig
    else:
        return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)