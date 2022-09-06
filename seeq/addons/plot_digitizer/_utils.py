import pandas as pd
import numpy as np

import json


def stringify_selected_points(df:'pandas.DataFrame', delimiter="||"):
	value = ''
	for x, y in zip(df.real_x.values, df.real_y.values):
		value+='{},{}{}'.format(x,y, delimiter)
	value = value[:-1*len(delimiter)]
	return value

def destringify_points(points:'str', delimiter='||')->'numpy.array':
	points = points.split(delimiter)
	return np.array([[float(a.split(',')[0]), float(a.split(',')[1])] for a in points])

def curvesets_to_json(curve_sets:'dict')->'str':
	return json.dumps(curve_sets)
	
def json_to_curvesets(curve_sets:'str[JSON]')->'dict':
	return json.loads(curve_sets)