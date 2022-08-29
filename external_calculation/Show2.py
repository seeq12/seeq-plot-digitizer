import textwrap
import json
from typing import Dict
from extcalc import KeywiseExternalCalculationScript, ValidationObject
from scipy.interpolate import interp1d, CubicSpline

import pandas as pd
import numpy as np

def destringify_points(points:'str', delimiter='||')->'numpy.array':
    points = points.split(delimiter)
    return np.array([[float(a.split(',')[0]), float(a.split(',')[1])] for a in points])


####### Class #######


class Show2(KeywiseExternalCalculationScript):

    def function_definition(self) -> Dict[str, str]:
        """
        Defines the parameters, formula, name, examples and documentation
        for this calculation.

        :return: dictionary containing function details
        """
        parameters = [
            {'Name': 'X', 'Type': 'Signal'},
            {'Name': 'PlotDigitizerStorage', 'Type': 'Signal'},
            {'Name': 'curveSet', 'Type': 'Signal'},
            {'Name': 'curveName', 'Type': 'Signal'},
        ]
        examples = [
            {
                'Formula': '@@functionName@@($X, "PlotDigitizerStorage".toSignal(), "curveSet".toSignal(), "curveName".toSignal())',
                'Description': 'Show digitized plot.'
            }
        ]

        function_details = {
            'Name': 'Show2',
            'Documentation': textwrap.dedent("""
                Show digitized plot (scalar model storage).
            """).strip(),
            'Formula': 'externalCalculation(@@scriptId@@, $X, $PlotDigitizerStorage, $curveSet, $curveName)',
            'Parameters': parameters,
            'Examples': examples
        }
        return function_details

# The remainder of the script is setup identically to legacy
# external calculation scripts.

    def compute(self, key: int, samples_for_key: []) -> float:
        
        X, storage_str, curve_set, curve_name = samples_for_key
        storage_dict = json.loads(storage_str)
        # return X

        if hasattr(self, 'model'):
            pass
        else:
            points = destringify_points(storage_dict[curve_set][curve_name])
            arg_order = np.argsort(points[:,0])
            points = points[arg_order, :]
            self.model = CubicSpline(points[:,0], points[:,1], extrapolate=False)
            # self.model = interp1d(points[:,0], points[:,1])

        try:
            return self.model(samples_for_key[0]).item()
        except ValueError:
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
        if signal_count != 4:
            raise ValueError('Invalid number of signals received. Expected to get 4, got {nofsig}'.format(
                nofsig=signal_count))

        signal_types = validation_object.get_signal_types()
        if (signal_types[0] == 'NUMERIC', signal_types[1] == 'STRING', signal_types[2] == 'STRING', signal_types[3] == 'STRING'):
            pass
        else:
            raise ValueError('Signal types are incorrect. Expecting (STRING, STRING, STRING, STRING)')

    def compute_output_mode(self) -> str:
        """
        Type of output signal.
        :return: either 'NUMERIC' or 'STRING'
        """
        return 'NUMERIC'