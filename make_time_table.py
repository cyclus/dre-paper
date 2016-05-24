#!/usr/bin/env python

import os
import pandas as pd

fname = 'scenarios/timing'

names = {
    'base_case': 'basecase',
    'once_through': 'oncethrough',
    'military': 'external',
    'outage': 'outage',
    'tariff': 'tariff',
}

with open(fname) as f:
    lines = f.readlines()

    scenarios = lines[::4]
    scenarios = [s.strip() for s in scenarios]

    timing = lines[1::4]
    count = lambda x: float(x.split()[1].split('m')[0]) * 60 + \
        float(x.split()[1].split('m')[1][:-1])
    timing = [count(t) for t in timing]

    split = lambda x: (names[x[:-4]], 'cbc') if x[-3:] == 'cbc' \
        else (names[x], 'greedy')
    scenarios = [split(x) for x in scenarios]
    index = pd.MultiIndex.from_tuples(scenarios, names=('Scenario', 'Solver'))
    df = pd.DataFrame({'Time (s)': timing}, index=index).sort_index()
    print(df.to_latex())
