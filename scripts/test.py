# Tu lista original de valores
valores = [4, 6, 2]

# Obtener una lista de índices ordenados según los valores
indices_ordenados = sorted(range(len(valores)), key=lambda i: valores[i])

# Imprimir la lista de índices ordenados
print(indices_ordenados)