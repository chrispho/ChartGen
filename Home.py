import sqlite3
from time import sleep

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

from streamlit_drawable_canvas import st_canvas
from PIL import Image

import datetime
from math import *

import models
import utils

qualities = ['Response to authority', 'Independence', 'Interest',
             'Enthusiasm', 'Challenge seeking', 'Ability to apply knowledge',
             'Perseverance', 'Focus', 'Respect for others',
             'Confidence', 'Stamina']


def show_sidebar():
    all_names = models.get_all_full_names()
    all_names.append('Add a New Student')

    with st.sidebar:
        # TODO: Remove logo background
        logo = st.sidebar.image(image='./assets/Mathnasium_Logo.jpg')

        global options
        options = tuple(all_names)
        global student
        student = st.selectbox("Student",
                               range(len(options)),
                               format_func=lambda x: options[x],
                               key='student')

        # st.write(student)
        # st.write(options[student])


def input_results():
    with st.expander('Enter a new assessment'):
        with st.form('new_test_form', clear_on_submit=True):
            test_date = st.date_input(label='Assessment Date',
                                      key='test_date')

            grade = st.number_input(label='Grade',
                                    min_value=0,
                                    max_value=12,
                                    step=1,
                                    key='grade')

            test_number = st.number_input(label='Checkup Number',
                                          min_value=0,
                                          max_value=12,
                                          step=1,
                                          key='test_number')

            test_score = st.number_input(label='Score (%)',
                                         min_value=0,
                                         max_value=100,
                                         step=1,
                                         key='test_score')

            left_col, right_col = st.columns([7, 1])

            with right_col:
                test_submit = st.form_submit_button()
                if test_submit:
                    models.create_results(info=student + 1,
                                          test_date=test_date,
                                          grade=grade,
                                          test_number=test_number,
                                          test_score=test_score)
        if test_submit:
            st.success('Test results successfully added!')
            sleep(1)
            st.experimental_rerun()


def input_info():
    with st.form(key='new_test_form', clear_on_submit=True):
        first_name = st.text_input(label='First Name',
                                   max_chars=255)

        last_name = st.text_input(label='Last Name',
                                  max_chars=255)

        left_col, right_col = st.columns([7, 1])

        with right_col:
            info_submit = st.form_submit_button()

    if info_submit:
        if first_name + ' ' + last_name in models.get_all_full_names():
            st.warning('Student already in database. Are you sure you want to add?')
        else:
            models.create_info(first_name, last_name)
            st.success('Student successfully added!')
            sleep(1)
            st.experimental_rerun()


def generate_projection(domain: [], score: float, x: float, y: float, p: float) -> {}:
    """

    :param domain:
    :param score:
    :param x:
    :param y:
    :param p:
    :return:
    """
    period = 1 - (score / 100)

    target = x + period
    projection = {
        'x': [x],
        'y': [y]
    }
    sample_space = np.arange(x, target, period / 10000)

    if projection['x'][-1] < projection['y'][-1]:
        for s in sample_space:
            projection['x'].append(s)
            var = projection['y'][-1] + p * (target - projection['y'][-1])
            deltacap = 0.000000000000000000001
            if var - projection['y'][-1] > deltacap:
                projection['y'].append(deltacap)
            else:
                projection['y'].append(var)

    elif projection['x'][-1] >= projection['y'][-1]:
        for s in sample_space:
            projection['x'].append(s)
            projection['y'].append((p/5) * (projection['y'][-1] ** 2) + projection['y'][-1])
            if projection['y'][-1] >= domain[1] or projection['y'][-1] >= domain[1]:
                break

    # st.write(projection)
    return projection


def annotating(stroke_color):
    bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])
    # realtime_update = st.sidebar.checkbox("Update in realtime", True)

    # Create a canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=3,
        stroke_color=stroke_color,
        background_image=Image.open(bg_image) if bg_image else None,
        # update_streamlit=realtime_update,
        height=500,
        width=704,
        drawing_mode="freedraw",
        # display_toolbar=st.sidebar.checkbox("Display toolbar", True),
        key="full_app",
    )

def show_results():
    input_results()

    # TODO: Add per-session comment box
    # TODO: Add download button?
    # TODO: Sort sql query by date?
    # TODO: Add annotate button to draw over chart

    query_string = "SELECT date, grade, test_number, test_score FROM results WHERE info_id=" + str(student + 1)
    df = pd.read_sql(sql=query_string, con=sqlite3.connect('database.db'))
    if df.empty:
        st.info('No test results found')
    else:
        # st.write(df)
        past_x = []
        past_y = []
        past_dates = []
        past_test_scores = []
        past_test_nums = []

        for i in df.index:
            current_date = datetime.datetime.strptime(df.at[i, 'date'], '%Y-%m-%d')
            current_grade = df.at[i, 'grade']
            current_test_num = df.at[i, 'test_number']
            current_test_score = df.at[i, 'test_score']

            school_start = None
            if current_date < datetime.datetime(current_date.year, 9, 1):
                school_start = datetime.datetime(current_date.year - 1, 9, 1)
            elif current_date >= datetime.datetime(current_date.year, 9, 1):
                school_start = datetime.datetime(current_date.year, 9, 1)
            delta = current_date - school_start
            time_passed = delta.days / 365.25

            x = current_grade + time_passed
            y = current_test_num + (utils.adjust_score(current_test_score) / 100)

            format_code = '%B %d, %Y'
            formatted_date = current_date.strftime(format_code)

            past_x.append(x)
            past_y.append(y)
            past_dates.append(formatted_date)
            past_test_scores.append(current_test_score)
            past_test_nums.append(current_test_num)

        results = pd.DataFrame({'x': past_x,
                                'y': past_y,
                                'date': past_dates})

        # st.dataframe(results, width=1000)
        left_col, right_col = st.columns([9, 1])
        with left_col:
            if len(past_y) > 1:
                st.metric('Most Recent Score',
                    value=f'{int(past_test_scores[-1])}% on Checkup {past_test_nums[-1]}',
                    delta=f'{int((past_y[-1] - past_y[-2]) * 100)}%')
        with right_col:
            stroke_color = st.color_picker("")


        domain = [max(0, min(floor(results['x'].min()), floor(results['y'].min()))),
                  min(12, max(ceil(results['x'].max()) + 1, ceil(results['y'].max()) + 1))]

        past_tests = alt.Chart(results).encode(
            x=alt.X('x',
                    scale=alt.Scale(domain=domain),
                    axis=alt.Axis(tickMinStep=1)),
            y=alt.Y('y', scale=alt.Scale(domain=domain),
                    axis=alt.Axis(tickMinStep=1)),
            tooltip='date'
        ).properties(
            height=500
        )

        line = pd.DataFrame({
            'x': domain,
            'y': domain
        })

        common_core = alt.Chart(line).mark_line(color='black').encode(
            x=alt.X('x', title='Time'),
            y=alt.Y('y', title='Math Mastery'),
        )

        if past_x[-1] < past_y[-1]:  # if the last test result is above y=x

            vertical_line = alt.Chart(
                pd.DataFrame({'x': [past_x[-1], past_x[-1]],
                              'y': [past_y[-1], past_x[-1]]})
            ).mark_line(strokeDash=[5, 3], opacity=0.75, color='gray').encode(x='x',
                                                                              y='y')
            horizontal_line = alt.Chart(
                pd.DataFrame({'x': [past_x[-1], past_y[-1]],
                              'y': [past_y[-1], past_y[-1]]})
            ).mark_line(strokeDash=[5, 3], opacity=0.75, color='gray').encode(x='x',
                                                                              y='y')

        else:  # if the last test results is below y=x
            vertical_line = alt.Chart(
                pd.DataFrame({'x': [past_x[-1], past_x[-1]],
                              'y': [past_x[-1], past_y[-1]]})
            ).mark_line(strokeDash=[5, 3], opacity=0.75, color='gray').encode(x='x',
                                                                              y='y')
            horizontal_line = alt.Chart(
                pd.DataFrame({'x': [past_y[-1], past_x[-1]],
                              'y': [past_y[-1], past_y[-1]]})
            ).mark_line(strokeDash=[5, 3], opacity=0.75, color='gray').encode(x='x',
                                                                              y='y')
        after_joining = pd.DataFrame(
            generate_projection(domain=domain, score=past_y[-1] % 1, x=past_x[-1], y=past_y[-1], p=0.00005))
        not_joining = pd.DataFrame(
            generate_projection(domain=domain, score=past_y[-1] % 1, x=past_x[-1], y=past_y[-1], p=0.000025))
        future = alt.layer(
            alt.Chart(after_joining).mark_line(strokeDash=[5, 3], color='green').encode(x='x', y='y'),
            alt.Chart(not_joining).mark_line(strokeDash=[5, 3], color='red').encode(x='x', y='y')
        )

        chart = past_tests.mark_point(size=100, filled=True) + past_tests.mark_line() + past_tests.mark_area(
            opacity=0.3) + common_core + vertical_line + horizontal_line + future

        annotating(stroke_color)
        # st.altair_chart(chart, use_container_width=True)


def edit_profile():
    with st.expander('Edit Profile'):
        st.header('Edit Profile')

        with st.form(' '):
            utils.radio_factory(qualities)

            comments = st.text_area(label='Additional Comments',
                                    max_chars=None)
            left_col, right_col = st.columns([9, 1])

            with right_col:
                profile_submit = st.form_submit_button(label='Save')


def show_student_profile():
    edit_profile()
    st.write('display student profile here')


def manage_student():
    with st.form(key='manage_student_form', clear_on_submit=True):

        # Change name, delete student

        left_col, right_col = st.columns([7, 1])

        with right_col:
            manage_submit = st.form_submit_button()

    if manage_submit:
        st.success('Student successfully added!')
        sleep(1)
        st.experimental_rerun()


if __name__ == '__main__':
    if 'student_options' not in st.session_state:
        st.session_state['student_options'] = 'Test Results'

    show_sidebar()

    title = st.title(f'{options[student]}')

    if options[student] == 'Add a New Student':
        input_info()

    else:
        tab1, tab2, tab3 = st.tabs(['Test Results', 'Student Profile', 'Manage Student'])

        with tab1:
            show_results()

        with tab2:
            show_student_profile()

        with tab3:
            manage_student()

    # st.write(st.session_state)
