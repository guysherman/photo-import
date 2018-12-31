# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 22:32:18 2018

@author: gsher
"""

# Data Preprocessing Template

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('traindata_greece.csv')
X = dataset.iloc[:, 1:-1].values
y = dataset.iloc[:, 11].values

# Splitting the dataset into the Training set and Test set
from sklearn.cross_validation import train_test_split
X = np.append(arr = np.ones((len(y), 1)).astype(int), values = X, axis = 1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)
X_idtest = range(0, len(y_test))
X_idtrain = range(0, len(y_train))
X_id = range(0, len(y))


"""# Feature Scaling
from sklearn.preprocessing import StandardScaler
sc_X = StandardScaler()

Xs = sc_X.fit_transform(X)

#X_train = sc_X.fit_transform(X_train)
#X_test = sc_X.transform(X_test)
#sc_y = StandardScaler()
#y_train = sc_y.fit_transform(y_train)"""


"""# Fitting Multiple Linear Regression to the Training set
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(X_train, y_train)

# Predicting the Test set results
y_pred = regressor.predict(X_test)


X_idtest = range(0, len(y_test))
X_idtrain = range(0, len(y_train))

# Visualising the Training set results
plt.scatter(X_idtrain, y_train, color = 'red')
plt.plot(X_idtrain, regressor.predict(X_train), color = 'blue')
plt.show()

# Visualising the Test set results
plt.scatter(X_idtest, y_test, color = 'red')
plt.plot(X_idtest, regressor.predict(X_test), color = 'blue')
plt.show()

#import statsmodels.formula.api as sm
regressor_OLS = sm.OLS(endog = y, exog = X).fit()
regressor_OLS.summary()

X_opt = X[:, [0,1,2,3,4,5,6,7,8,9,10]]
regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
regressor_OLS.summary()

X_opt = X[:, [0,1,2,3,4,5,6,7,8,9]]
regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
regressor_OLS.summary()

X_opt = X[:, [0,1,2,3,4,5,6,7,8]]
regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
regressor_OLS.summary()

X_opt = X[:, [0,1,3,4,5,6,7,8]]
regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
regressor_OLS.summary()

X_opt = X[:, [0,1,3,4,5,6,8]]
regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
regressor_OLS.summary()



X_train, X_test, y_train, y_test = train_test_split(X_opt, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

# Predicting the Test set results
y_pred = regressor.predict(X_test)



# Visualising the Training set results
plt.scatter(X_idtrain, y_train, color = 'red')
plt.plot(X_idtrain, regressor.predict(X_train), color = 'blue')
plt.show()

# Visualising the Test set results
plt.scatter(X_idtest, y_test, color = 'red')
plt.plot(X_idtest, regressor.predict(X_test), color = 'blue')
plt.show()

err = np.abs(np.subtract(y_pred, y_test))
print (regressor.intercept_, regressor.coef_)"""


# Visualising the Training set results
# Fitting Polynomial Regression to the dataset
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
poly_reg = PolynomialFeatures(degree = 3)
lin_reg_2 = LinearRegression()
model = make_pipeline(poly_reg, lin_reg_2)
model.fit(X_train, y_train)



#X_poly = poly_reg.fit_transform(X)
#poly_reg.fit(X_poly, y)
#lin_reg_2.fit(X_poly, y)

# Visualising the Polynomial Regression results
plt.scatter(X_idtest, y_test, color = 'red')
plt.plot(X_idtest, model.predict(X_test), color = 'blue')
plt.show()

print(model.steps[1][1].intercept_, model.steps[1][1].coef_)
print(len(model.steps[1][1].coef_))
print(model.steps[0][1].get_feature_names())


import json
modelObj = {
        'featureNames': model.steps[0][1].get_feature_names(),
        'coefficients': model.steps[1][1].coef_.tolist(),
        'intercept': model.steps[1][1].intercept_
        }



with open('model.json', 'w') as modelFile:
    json.dump(modelObj, modelFile, indent=4, separators=(',', ':'), sort_keys=True)

    