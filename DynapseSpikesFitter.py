############### author ####################
# federico corradi & cattaneo roberto
# federico@ini.phys.ethz.ch; cattaroby93@gmail.com
# Fitter signal-spikes
# =========================================

### ========================= import packages ===============================
import numpy as np
from matplotlib import pyplot as plt
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

### ===========================================================================
def sklearn_fit(matrix, target):
    """Apply linear regression and find the coefficients to fit matrix in target
        
It uses the sklearn linear regression algorithm.

Parameters
----------
matrix : numpy matrix of floats. Matrix that encodes spike in a certain way
target : numpy array of floats. Vector of target values

Returns
-------
regr : linear model object. Object used for linear regression
coefficients : list of floats. Contains coefficients of the regression
"""
        
    # Reshape to get an array in format (n, 1) --> required by sklearn for fitting
    target = np.array(target).reshape((-1, 1))
    matrix = np.array(matrix)
        
    # Train the model using the training sets
    # The flow is the following:
        # input signal y --> (n, 1)
        # neuronFireRate X --> (1024, n) [should be transposed to (n, 1024)]
        # We should find a vector v such that <v, X> = y
    regr = linear_model.LinearRegression()
    regr.fit(np.transpose(matrix), target)
    coefficients = regr.coef_
    return regr, coefficients

### ===========================================================================
def sklearn_prevision(regr, matrix):
    """Make a target prevision using the previously found coefficients
        
It uses sklearn coefficients and prevision method

Parameters
----------
regr : linear model object. Object used for linear regression
matrix : numpy matrix of floats. Matrix that encodes spike in a certain way

Returns
-------
prediction : numpy array of floats. Contains the performed prediction
"""
        
    matrix = np.transpose(matrix)
    prediction = regr.predict(matrix)
    return prediction
        
### ===========================================================================
def pseudo_inv_fit(matrix, target):
    """Apply linear regression and find the coefficients to fit matrix in target
        
It uses the pseudo inverse fitting algorithm

Parameters
----------
matrix : numpy matrix of floats. Matrix that encodes spike in a certain way
target : numpy array of floats. Vector of target values

Returns
-------
coefficients : list of floats. Contains coefficients of the regression
"""
        
    # Reshape to get an array in format (n, 1) --> required by sklearn for fitting
    matrix = np.array(matrix)
    target = np.array(target).reshape((-1, 1))
        
    # y = X * b --> linear system where b is the vector we are searching (decoders)
    # b = inv(X'X) X'y ---> b = pseudoinv(X'X) X'y
        # should be equivalent:
        # gamma = X*X'
        # upsilon = Xy
        # b = pseudoinv(gamma)*upsilon
    gamma = np.dot(matrix, matrix.T)
    # Apply regularization adding some Gaussian noise close to 1 in the diagonal
    #gamma = gamma + np.eye(len(gamma)) * np.random.normal(loc = 1, scale = 0.15, size = len(gamma))
    upsilon = np.dot(matrix, target)
    ginv = np.linalg.pinv(gamma)

    # Calculate coefficients
    coefficients = np.dot(ginv,upsilon)
    return coefficients

### ===========================================================================
def pseudo_inv_prevision(coefficients, matrix):
    """Make a target prevision using the previously found coefficients
        
It uses pseudo inverse coefficients and prevision method

Parameters
----------
coefficients : list of floats. Contains coefficients of the regression
matrix : numpy matrix of floats. Matrix that encodes spike in a certain way

Returns
-------
prediction : numpy array of floats. Contains the performed prediction
"""
        
    # i have to traspose it to have (n, 1) shape
    prediction = np.dot(coefficients.T, matrix).T
    return prediction

### ===========================================================================  
def prediction_plot(timeScale, target, prediction, ax = None):
    """Plot the prediction
    
Parameters
----------
timeScale : array_like, floats. Time steps in which firing rate has been calculated
target : numpy array of floats. Vector of target values
prediction : numpy array of floats. Contains the performed prediction 

Returns
-------
fig : figure handle of the created figure, if generated
ax : axis handle of the created plot
handles : list of handles of created line (every plot)
"""
        
    fig = None

    # If no subplot is specified, create new plot
    if ax == None: 
        fig = plt.figure()
        ax = fig.add_subplot(111)

    handles = []

    handle, = ax.plot(timeScale, target,  linestyle = 'None', marker = 'o', color='black')
    handles.append(handle)
    handle, = ax.plot(timeScale, prediction, linestyle = 'None', marker = 'o', color='blue')
    handles.append(handle)
    
    return fig, ax, handles
        
### ===========================================================================  
def prediction_performances(target, prediction):
    """Print the mean square error and r2 score of the prediction

Parameters
----------
target : numpy array of floats. Vector of target values
prediction : numpy array of floats. Contains the performed prediction
"""
    # Print the performances of the fitting
    print("Testing Mean squared error: %.4f" % mean_squared_error(target, prediction))
    print('Testing Variance score: %.4f' % r2_score(target, prediction))

### ===========================================================================  
def av_fireRate_matrix_diff(M1, M2):
    """Calculate indicators that give hints about the difference between two matrices
    
The indicators are:
- nDiffNeuronAv: it tells in average how many neurons have a different firing rate
                    between the matrixes. It is expressed in percentage of the
                    average number of neurons that fire (in the two matrixes)
- diffFiringAv: it tells the average firing rate different between the matrixes.\
                    It is expressed in percentage of the average firing rate of the matrixes

Parameters
----------
M1 : numpy matrix of floats. First matrix for the comparizon
M2 : numpy matrix of floats. Second matrix for the comparizon
"""
    
    # Calculate the distance between matrixes (correspond to the number of differences in the experiment)
    M1 = np.array(M1)
    M2 = np.array(M2)
    diff = np.abs(M1 - M2)
    
    # Calculate the average (in time) of the number of neurons that fires in both matrix
    nNeuronM1 = np.mean((M1 != 0).sum(axis = 0))
    nNeuronM2 = np.mean((M2 != 0).sum(axis = 0))
    nNeuronAv = (nNeuronM1 + nNeuronM2) / 2
    
    # Calculate the average (in time) of the number of differences between the matrixes
    # Note that this result is expressed in percentage with respect to the average
    # number of neurons that fires
    nDiffNeuronAv = np.mean((diff != 0).sum(axis = 0)) / nNeuronAv * 100
    
    # Calculate the average (in time) firing rate in both matrixes -> for only the neurons that fire
    # Just do manually the average and delete the nan (neuron that does not fire)
    firingM1 = np.nanmean(np.true_divide(M1.sum(axis = 0), (M1 != 0).sum(axis = 0)))
    firingM2 = np.nanmean(np.true_divide(M2.sum(axis = 0), (M2 != 0).sum(axis = 0)))
    firingAv = (firingM1 + firingM2) / 2
    
    # Calculate the average (in time) of the firing rate differences between the matrixes
    # Note that this result is expressed in percentage with respect to the average
    # firing rate of both the matrixes
    diffFiringAv = np.nanmean(np.true_divide(diff.sum(axis = 0), (diff != 0).sum(axis = 0))) / firingAv * 100
    
    # Print at screen the results
    print("Firing rate matrix difference : ")
    print("Average different neuron : ", nDiffNeuronAv, "%")
    print("Average difference firing rate : ", diffFiringAv, "%")
    print()