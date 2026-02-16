import numpy as np

def summa(A, B):
    return (A + B)
    
def subt(A, B):
    return A - B

def multi(A, B):
    return A @ B
    
def det(A):
    return np.linalg.det(A)


def transp(A):
    return A.T
    
def deg(matrix, n):
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Матрица должна быть квадратной")
    return np.linalg.matrix_power(matrix, n)
    
