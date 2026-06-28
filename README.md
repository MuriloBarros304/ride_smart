# RideSmart

Projeto para modelagem e análise de rotas urbanas usando grafos e simulação simples de tráfego.

**Descrição**

O projeto gera candidatos de ponto de embarque dentro de um raio de caminhada, avalia rotas usando diferentes algoritmos de caminho mínimo e produz visualizações (animações e mapas) para análise.

**Integrantes**

- Henrique Eduardo Costa Da Silva
- João Victor Moura Lucas da Silva
- Murilo de Lima Barros
- Ramon Vinícius Ferreira de Souza

## Estrutura do repositório

- [src/](src/) — código-fonte principal
- [src/algorithms/](src/algorithms/) — algoritmos de caminho mínimo
- [data/processed/](data/processed/) — saídas geradas (ex.: animações, mapas)
- [tests/](tests/) — testes automatizados

## Requisitos

- Python 3.10+
- Dependências listadas em [requirements.txt](requirements.txt)

Instalação das dependências:

```bash
pip install -r requirements.txt
```

## Uso rápido

Exemplo de execução a partir do repositório (ajuste coordenadas conforme necessário):

```bash
python3 src/main.py \
    --origin-lat -5.8430277 --origin-lon -35.1979797 \
    --dest-lat -5.8121992 --dest-lon -35.2080217 \
    --walk-radius 100 --candidates 10 \
    --algorithm dijkstra_heap \
    --traffic off \
    --output data/processed/dijkstra_animation.html
```

- Para usar um grafo local em GraphML: `--graphml caminho/para/grafo.graphml`.
- Para baixar uma área inteira, use a flag `--place "Cidade, País"`.

O arquivo de entrada e parâmetros principais são definidos em [src/main.py](src/main.py).

## Notebook interativo

Há um notebook de exemplo para rodar e visualizar resultados interativamente: [notebook.ipynb](notebook.ipynb).

## Sistema de trânsito (opções)

O parâmetro `--traffic` controla uma simulação simples de variação de peso das arestas:

- `off`: usa apenas distância (metros).
- `normal`: aplica um atraso estocástico leve baseado em velocidade da via.
- `peak`: simula horário de pico com atrasos maiores.

O comportamento exato está implementado no código que monta os pesos das arestas (veja os módulos em `src/`).

## Algoritmos disponíveis

- Dijkstra
- Dijkstra com heap (mais eficiente)
- A*
- SPFA

## Saídas

- Animações HTML e mapas produzidos em [data/processed/](data/processed/).
- Resumo de métricas impresso no terminal (distância e tempo estimado).

## Testes

Execute os testes com:

```bash
pytest -q
```

## Histórico de Pendências

- Implementar testes unitários (parcial)
- Melhorar desempenho