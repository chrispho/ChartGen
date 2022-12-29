import streamlit as st
from typing import List


def adjust_score(test_score: int) -> int:
    adjusted_score: int = test_score
    # Dictionary of accurate ranges
    ranges = {
        'accurate': [40, 60],
        'close': [25, 75],
        'far': [0, 100]
    }

    ranges['accurate'] = range(ranges['accurate'][0], ranges['accurate'][1]+1)
    ranges['close'] = range(ranges['close'][0], ranges['close'][1] + 1)
    ranges['far'] = range(ranges['far'][0], ranges['far'][1] + 1)

    if test_score in ranges['accurate']:
        adjusted_score = test_score
    elif test_score in ranges['close']:
        adjusted_score = test_score - 1 * (50 - test_score)
    elif test_score in ranges['far']:
        adjusted_score = test_score - 2 * (50 - test_score)

    return adjusted_score


def radio_factory(qualities: List):
    for quality in qualities:
        st.radio(label=quality,
                 options=('1', '2', '3', '4', '5'),
                 horizontal=True
                 )
