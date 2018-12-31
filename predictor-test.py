import generic_predictor

p = generic_predictor.RuntimePredictor(['1', 'x0^2', 'x0 x1', 'x0 x1^2', 'x0 x1 x2'], [1, 2, 3, 4, 5], 10)
dataPoint = [1, 2, 3]
result = p.predict(dataPoint)
print(result)
