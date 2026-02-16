import numpy as np

def summa(A, B):
    return (A + B)
    
def subt(A, B):
    return A - B

def multi(A, B):
    return A * B
    
def det(A):
    return np.linalg.det(A)


def transp(A):
    return A.T
    
def deg(A, n):
    return numpy.linalg.matrix_power(A, n)
    
