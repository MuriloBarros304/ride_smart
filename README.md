# RideSmart

Projeto final para modelagem e análise de rotas urbanas com grafos. O foco
 é simular um cenário de mobilidade urbana com ponto de origem, destino e
 escolha de ponto de embarque dentro de um raio de caminhada.

## Estrutura

- src/: código-fonte principal
- src/algorithms/: implementações de algoritmos de caminho mínimo
- data/raw/: dados de entrada (opcional)
- data/processed/: saídas geradas (ex.: animações)
- tests/: testes automatizados

## Requisitos

- Python 3.10+
- Dependências listadas em requirements.txt

Instalação das dependências:

```bash
pip install -r requirements.txt
```

## Uso

O script principal gera pontos aleatórios dentro de um raio de caminhada,
 escolhe o melhor ponto de embarque e gera uma animação do algoritmo selecionado.

Exemplo usando um lugar para baixar o grafo:

```bash
python src/main.py \
    --origin-lat -5.8430277 --origin-lon -35.1979797 \
    --dest-lat -5.8121992 --dest-lon -35.2080217 \
    --walk-radius 100 --candidates 10\
    --algorithm dijkstra_heap \
    --output data/processed/dijkstra_animation.html
```
Se usar `--place` toda a cidade será exibida, use latitude e longitude para
 melhores visualizações.

Também é possível usar um arquivo GraphML local:

```bash
python3 src/main.py --graphml caminho/para/grafo.graphml
```

## Algoritmos disponíveis

- Dijkstra simples
- Dijkstra com heap
- A*
...

## Saídas

- Animação HTML com a exploração do algoritmo (padrão em data/processed/).

## Pendências

- Simular trânsito e congestionamentos em horário de pico para rodovias
- Implementar um outro algoritmo de escolha do grupo
- Implementar testes unitários
- Ver se é possível adicionar alguma heurística para otimizar a geração de candidatos
- Melhorar desempenho
