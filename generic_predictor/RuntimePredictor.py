"""
Takes feature names and coefficients, and allows the user to predict values
"""
import re


from . import Functions


fetchRe = re.compile(r'^x(\d+)$')
powerRe = re.compile(r'^x(\d+)\^(\d+)$')

class RuntimePredictor:
    """
    Takes feature names and coefficients, and allows the user to predict values
    """

    def __init__(self, featureNames, coefficients, intercept):
        """
        Constructs a chain of lambdas
        """
        self.terms = []
        self.coefficients = coefficients
        self.intercept = intercept
        
        for term in featureNames:
            self.terms.append(processTerm(term))
    
    def predict(self, x):
        result = self.intercept
        for i, term in enumerate(self.terms):
            coef = self.coefficients[i]
            termValue = term(x)
            resultValue = coef * termValue
            result += resultValue
        
        return result


def processTerm(term):
    """
    Processes a feature name into a lambda to calculate that term
    """
    parts = term.split(' ')
    if len(parts) == 1:
        m = fetchRe.match(parts[0])
        n = powerRe.match(parts[0])
        if parts[0] == '1':
            return Functions.one()
        if m != None:
            return Functions.fetch(int(m.group(1)))
        elif n != None:
            a = Functions.fetch(int(n.group(1)))
            return Functions.power(a, int(n.group(2)))
    else:
        result = Functions.one()
        terms = map(processTerm, parts)
        for term in terms:
            result = Functions.mul(term, result)
        return result


        