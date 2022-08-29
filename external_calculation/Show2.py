import textwrap
import json
from typing import Dict
from extcalc import KeywiseExternalCalculationScript, ValidationObject

import pandas as pd
import numpy as np

def destringify_points(points:'str', delimiter='||')->'numpy.array':
    points = points.split(delimiter)
    return np.array([[float(a.split(',')[0]), float(a.split(',')[1])] for a in points])

class interpolator():
    
    def __init__(self, X, Y):
        if not ((pd.Series(X) - pd.Series(X).shift(1)).dropna() > 0).all():
            raise ValueError('X must be strictly increasing')
            
        if not ((type(X) is np.ndarray) or (type(X) is list)):
            raise TypeError('X must be type "list" or "np.ndarray"')
            
        if not ((type(Y) is np.ndarray) or (type(Y) is list)):
            raise TypeError('Y must be type "list" or "np.ndarray"')
            
        if type(X) is list:
            X = np.array(X)
        if type(Y) is list:
            Y = np.array(Y)
            
        if len(X.shape) != 1:
            raise ValueError('X is not 1 dimensional.')
        if len(Y.shape) != 1:
            raise ValueError('Y is not 1 dimensional.')
        
        if X.shape != Y.shape:
            raise ValueError('X and Y must have same shape.')
        
        self.X = np.array(X)
        self.Y = np.array(Y)
        
        return
    
    def __call__(self):
        return NotImplementedError

class interp1d(interpolator):
    
    def __init__(self, X, Y):
        super().__init__(X, Y)
        self.get_S(X, Y)
    
    def __call__(self, x):
        if hasattr(x, '__iter__'):
            return np.array([self.f(xi, self.X, self.Y) for xi in x], dtype='object')
        return self.f(x, self.X, self.Y)
    
    def get_S(self, X, Y):
        out = []
        for i, (x1, y1) in enumerate(zip(X[:-1], Y[:-1])):
            x2, y2 = X[i+1], Y[i+1]
            m, b = np.dot(np.linalg.inv(np.array([[x1, 1],[x2, 1]])), (np.array([y1, y2])))
            out.append((m,b))
            
        self.S = out
        
    
    def f(self, x, X, Y):
        
        if x>X.max():
            return np.nan
        if x<X.min():
            return np.nan
        if x in X:
            arg = (np.where(X == x))[0][0]
            return Y[arg]
        
        arg = np.where(x >= X)[0][-1]
        m,b = self.S[arg]
        
        out = m*x + b
        if hasattr(out, '__iter__'):
            if len(out.flatten()) != 1:
                raise ValueError('This should be impossible error occurance. We are returning more than one value')
            else:
                out = float(out.flatten()[0])
        return out
    
    
class CubicSpline(interpolator):
    
    def __init__(self, X, Y):
        super().__init__(X, Y)
        self.get_S(X, Y)
    
    def __call__(self, x):
        if hasattr(x, '__iter__'):
            return np.array([self.f(xi, X, Y) for xi in x], dtype='object')
        return self.f(x, self.X, self.Y)
    
    def get_S(self, X, Y):
        # cubic spline
        # we have 4(n-1) coefs, aij. i index the spline arg (from 0...n-2) j is index 0...3

        ### build matrix
        nrows = (4*(len(X)-1))
        mat = np.zeros((nrows, nrows))
        ansmat = np.zeros((nrows, 1))

        row_counter = 0
        # first point in spline
        for i, (xp, yp) in enumerate(zip(X[:-1], Y[:-1])):
            x3, x2, x1, x0 = xp**3, xp**2, xp**1, xp**0
            ansmat[i][0] = yp
            for j, xpp in enumerate([x3, x2, x1, x0]):
                mat[i][int(4*(i)) + j] = xpp
            row_counter += 1

        # second point in spline
        for i, (xp, yp) in enumerate(zip(X[1:], Y[1:])):
            x3, x2, x1, x0 = xp**3, xp**2, xp**1, xp**0
            ansmat[row_counter][0] = yp
            for j, xpp in enumerate([x3, x2, x1, x0]):
                mat[row_counter][int(4*(i)) + j] = xpp
            row_counter+=1

        # first derivatives
        for i, xp in enumerate(X[1:-1]):
            for j, xpp in enumerate([3*xp**2, 2*xp**1, 1, 0, -3*xp**2, -2*xp**1, -1, 0]):
                mat[row_counter][j+(i*4)] = xpp
            row_counter+=1

        # second derivatives
        for i, xp in enumerate(X[1:-1]):
            for j, xpp in enumerate([6*xp**1, 2, 0, 0, -6*xp**1, -2, 0, 0]):
                mat[row_counter][j+(i*4)] = xpp
            row_counter+=1

        # second derivative is zero at edges
        mat[-2][0] = 6*X[0]
        mat[-2][1] = 2
        mat[-1][-4] = 6*X[-1]
        mat[-1][-3] = 2

        ### solve 

        coefs = np.dot(np.linalg.inv(mat), ansmat)

        out = []
        for i in range(len(X)-1):
            out.append(tuple(coefs[i*4:i*4 + 4]))
            
        self.S = out
        return
        
    
    def f(self, x, X, Y):
        if x>X.max():
            return np.nan
        if x<X.min():
            return np.nan
        if x in X:
            arg = (np.where(X == x))[0][0]
            return Y[arg]
        
        arg = np.where(x >= X)[0][-1]
        a3, a2, a1, a0 = self.S[arg]
        
        out = a3*x**3 + a2*x**2 + a1*x**1 + a0
        if hasattr(out, '__iter__'):
            if len(out.flatten()) != 1:
                raise ValueError('This should be impossible error occurance. We are returning more than one value')
            else:
                out = float(out.flatten()[0])
        return out


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
            # self.model = CubicSpline(points[:,0], points[:,1])
            self.model = interp1d(points[:,0], points[:,1])

        try:
            return self.model(samples_for_key[0])
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