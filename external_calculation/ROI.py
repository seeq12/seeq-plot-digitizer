import textwrap
import json
from typing import Dict
from extcalc import KeywiseExternalCalculationScript, ValidationObject

import pandas as pd
import numpy as np

def destringify_points(points:'str', delimiter='||')->'numpy.array':
    points = points.split(delimiter)
    return np.array([[float(a.split(',')[0]), float(a.split(',')[1])] for a in points])

def create_boundary_points_from_points(selected_points:'numpy.array(n,2)') -> 'numpy.array(n+1,2)':
    # wrap beginning to end
    return np.concatenate((selected_points, selected_points[0].reshape(1,2)))

def get_boundary_coef(points:'numpy.array(n,2)') -> 'numpy.array(n,5)':

    # boundary lines
    # do this as 5 coeficients (A, B, C, D, E), of the form Ax + By = C, D = xmin, E = xmax
    for i in range(points.shape[0] - 1):
        p1, p2 = points[i], points[i+1]
        difference = p1 - p2
        m = difference[1]/difference[0]

        # point slope formula: y - y1 = m(x - x1)
        # y - mx = -mx1 + y1
        A = -1*m
        B = 1
        C = -1*m*p1[0] + p1[1]

        D = np.min((p1[0], p2[0]))
        E = np.max((p1[0], p2[0]))

        tcoef = np.array([A, B, C, D, E]).reshape(1,5)

        if i == 0:
            boundary_coef = tcoef
        else:
            boundary_coef = np.concatenate((boundary_coef, tcoef))
            
    return boundary_coef


def determine_membership(test_point:'numpy.array(2,)', boundary_coef:'numpy.array(n,5)') -> 'bool':
    test_line_coef = np.array([1, 0, test_point[0]])
    must_be_above = test_point[1]

    intersections = 0

    for boundary_line_c in boundary_coef:
        # build matrix
        mat = np.array([boundary_line_c[:2], test_line_coef[:2]])
        ints = np.array([boundary_line_c[2], test_line_coef[2]])

        # solve
        try:
            soln = np.dot(np.linalg.inv(mat), ints)
        except np.linalg.LinAlgError:
            continue

        # boundary_line_c[3] is min domain, 4 is max domain
        if soln[1]>=must_be_above and (soln[0]>=boundary_line_c[3] and 
                                       soln[0]<=boundary_line_c[4]):
            intersections+=1
        else:
            continue
        
    if np.mod(intersections, 2)==1:
        return True
    else:
        return False

####### Class #######


class ROI(KeywiseExternalCalculationScript):

    def function_definition(self) -> Dict[str, str]:
        """
        Defines the parameters, formula, name, examples and documentation
        for this calculation.

        :return: dictionary containing function details
        """
        parameters = [
            {'Name': 'X', 'Type': 'Signal'},
            {'Name': 'Y', 'Type': 'Signal'},
            {'Name': 'PlotDigitizerStorage', 'Type': 'Signal'},
            {'Name': 'curveSet', 'Type': 'Signal'},
            {'Name': 'curveName', 'Type': 'Signal'},
        ]
        examples = [
            {
                'Formula': '@@functionName@@($X, $Y, "PlotDigitizerStorage".toSignal(), "curveSet".toSignal(), "curveName".toSignal())',
                'Description': 'Condition classifying a 2D region of interest (ROI).'
            }
        ]

        function_details = {
            'Name': 'ROI',
            'Documentation': textwrap.dedent("""
                Condition classifying a 2D region of interest (ROI), as generated by the Plot Digitizer Tool. 
            """).strip(),
            'Formula': 'externalCalculation(@@scriptId@@, $X, $Y, $PlotDigitizerStorage, $curveSet, $curveName)',
            'Parameters': parameters,
            'Examples': examples
        }
        return function_details

# The remainder of the script is setup identically to legacy
# external calculation scripts.

    def compute(self, key: int, samples_for_key: []) -> float:
        
        X, Y, storage_str, curve_set, curve_name = samples_for_key
        
        # return X

        if hasattr(self, 'model'):
            pass
        else:
            print('here1', storage_str)
            storage_dict = json.loads(storage_str)
            points = destringify_points(storage_dict[curve_set][curve_name])
            boundary = create_boundary_points_from_points(points)
            self.model = get_boundary_coef(boundary)
            
        test_point = np.array([X, Y])
        in_out = determine_membership(test_point, self.model)
        if in_out:
            return X
        else:
            return np.nan

    def validate(self, validation_object: ValidationObject):
        """
        Optional method to validate the types and quantity of input
        signals. Called once each time the script is loaded.
        If validation fails, the error raised will be visible in Seeq
        as part of the formula error during formula execution.

        In this example, it asserts that a single input signal is used
        and that this signal is has type 'NUMERIC'.

        ValidationObject offers two methods:
        - get_signal_types() which returns a list of types for the
          input signals
        - get_signal_count() which returns the number of input
          signals defined in the Seeq formula for the given
          script invocation

        :param validation_object: ValidationObject
        :return: return value is not checked, an error should be raised
                 in case of validation errors
        """
        signal_count = validation_object.get_signal_count()
        if signal_count != 5:
            raise ValueError('Invalid number of signals received. Expected to get 5, got {nofsig}'.format(
                nofsig=signal_count))

        signal_types = validation_object.get_signal_types()
        if (signal_types[0] == 'NUMERIC', signal_types[1] == 'NUMERIC', 
            signal_types[2] == 'STRING', signal_types[3] == 'STRING', 
            signal_types[4] == 'STRING'):
            pass
        else:
            raise ValueError('Signal types are incorrect. Expecting (STRING, STRING, STRING, STRING)')

    def compute_output_mode(self) -> str:
        """
        Type of output signal.
        :return: either 'NUMERIC' or 'STRING'
        """
        return 'NUMERIC'