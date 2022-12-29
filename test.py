import sqlite3
from datetime import datetime
from math import floor, ceil

import altair as alt
import altair_viewer
import pandas as pd

import models

if __name__ == '__main__':
    alt.renderers.enable('altair_viewer')

    student = 'Test Testing'
    query_string = 'SELECT * FROM results, info WHERE info_id=1'
    df = pd.read_sql(sql=query_string, con=sqlite3.connect('database.db'),
                     columns=['test_number', 'test_score', 'date'])

    df2 = df.loc[:, ~df.columns.isin(['id', 'info_id'])]

    print(df2)

    results_x = []
    results_y = []
    for i in df2.index:
        current_date = datetime.strptime(df2.at[i, 'date'], '%Y-%m-%d')
        current_grade = df2.at[i, 'grade']
        current_test_num = df2.at[i, 'test_number']
        current_test_score = (df2.at[i, 'test_score']/100)

        if current_date < datetime(current_date.year, 9, 1):
            school_start = datetime(current_date.year-1, 9, 1)
        else:
            school_start = datetime(current_date.year, 9, 1)

        delta = current_date - school_start
        time_passed = delta.days / 365.25

        x = current_grade + time_passed
        y = current_test_num + current_test_score

        results_x.append(x)
        results_y.append(y)

    print(results_x)
    print(results_y)
    results = pd.DataFrame({'x': results_x,
                            'y': results_y})

    print(results)

    chart = alt.Chart(results).mark_point().encode(
        x=alt.X('x', scale=alt.Scale(domain=[floor(results['x'].min())-1, ceil(results['x'].max())+1])),
        y=alt.Y('y', scale=alt.Scale(domain=[results['y'].min() - 1, results['y'].max() + 1]))
    ).configure_axis(
        grid=False,
        format='0f'
    )

    altair_viewer.show(chart)
