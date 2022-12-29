# ChartGen

ChartGen is a Python tool for visualizing student test data over time

## Installation

Clone the project

```bash
git clone https://github.com/chrispho/ChartGen
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `requirements.txt`.

```bash
pip install requirements.txt
```

## Usage

This tool is designed to be used in conjunction with the graded assessments from the Mathnasium math tutoring franchise. Students and their respective assessment results can be added into a SQLite3 database with the dropdown UI.

![Example3](/assets/ChartGenExample3.png)

Student performance over time is then displayed in an Altair chart with projected future performance indicated with colored, dotted lines. More data points will result in more accurate prediction of future performance.

![Example1](/assets/ChartGenExample1.png)

Charts can also be manually annotated to aid in explanation to potential students and their parents.

![Example2](/assets/ChartGenExample2.png)
