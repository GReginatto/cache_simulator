## Simulador de Cache em Python
Gustavo Reginatto e Lucas Schneider Ludwig

## Funcionalidades

# Políticas de Substituição:
- LRU (Least Recently Used)-
- FIFO (First In, First Out)
- Random (Substituição aleatória)

# Relatório de Desempenho: Gera estatísticas de hits e misses, incluindo tipos de misses (compulsórios, capacidade e conflito).

# Visualização Gráfica: Possibilidade de gerar um gráfico de pizza mostrando a distribuição de hits e misses.

# Dependências
numpy
matplotlib

# Instruções de Execução
1 - Instale as dependências:
pip install numpy matplotlib

2 - Execute o simulador:
python cache.py <num_sets> <block_size> <assoc> <policy> <output_mode> <input_file> <show_graph>

3 - Parâmetros
<num_sets>: Número de conjuntos no cache.
<block_size>: Tamanho de cada bloco.
<assoc>: Grau de associatividade do cache.
<policy>: Política de substituição (R para Random, L para LRU, F para FIFO).
<output_mode>: Modo de saída (1 para CSV, 0 para relatório detalhado).
<input_file>: Caminho para o arquivo binário com endereços.
<show_graph>: 0 para não mostrar gráfico, 1 para mostrar gráfico.
