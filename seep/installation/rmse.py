import numpy as np

class FuncaoObjetivo:
    def __init__(self, h_medido):
        self.h_medido = h_medido

    def calcular_rmse(self, h_modelo):
        erro = h_modelo - self.h_medido
        rmse = np.sqrt(np.mean(erro**2))

        return rmse
    