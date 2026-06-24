# RideSmart

Projeto final para modelagem e análise de rotas urbanas com grafos. O foco é simular um cenário de mobilidade urbana com ponto de origem, destino e escolha de ponto de embarque dentro de um raio de caminhada.

## Estrutura

- `src/`: código-fonte principal
- `src/algorithms/`: implementações de algoritmos de caminho mínimo
- `data/raw/`: dados de entrada (opcional)
- `data/processed/`: saídas geradas (ex.: animações)
- `tests/`: testes automatizados

## Requisitos

- Python 3.10+
- Dependências listadas em `requirements.txt`

Instalação das dependências:

```bash
pip install -r requirements.txt
```

## Uso

O script principal gera pontos aleatórios dentro de um raio de caminhada, escolhe o melhor ponto de embarque e gera uma animação do algoritmo selecionado.

Exemplo de uso com busca dinâmica e trânsito no horário de pico:

```bash
python3 src/main.py \
    --origin-lat -5.8430277 --origin-lon -35.1979797 \
    --dest-lat -5.8121992 --dest-lon -35.2080217 \
    --walk-radius 100 --candidates 10 \
    --algorithm dijkstra_heap \
    --min-angle 25 \
    --traffic peak \
    --output data/processed/dijkstra_animation.html
```

Se usar `--place` toda a cidade será baixada. Para visualizações melhores e mais rápidas, prefira usar as coordenadas de latitude e longitude (que geram um raio dinâmico entre a origem e o destino).

Também é possível usar um arquivo GraphML local:

```bash
python3 src/main.py --graphml caminho/para/grafo.graphml
```

## Sistema de Trânsito Estocástico

O projeto possui um modelo probabilístico para simular as condições reais de tráfego urbano, controlado pela flag `--traffic`. O algoritmo altera dinamicamente os pesos das arestas (ruas) do grafo com base na escolha do usuário:

- **`--traffic off`**: O sistema calcula a **rota física mais curta**. O peso das arestas é estritamente a distância em metros.
- **`--traffic normal`**: O sistema calcula a **rota mais rápida**. O peso passa a ser o tempo ideal de viagem (baseado na velocidade da via) somado a um leve atraso estocástico.
- **`--traffic peak`**: Simula o **horário de pico**. Multiplicadores severos de atraso são aplicados, especialmente em vias expressas e rodovias, forçando os algoritmos a buscarem rotas de fuga por dentro de bairros.

O tempo extra de engarrafamento de cada rua não é fixo; ele é sorteado usando uma **Distribuição Exponencial** baseada em um atraso médio esperado. Isso garante realismo: na maioria das vezes o atraso é pequeno, mas há uma chance matemática de ocorrerem gargalos severos (simulando acidentes ou semáforos quebrados), o que exige recálculos drásticos de rota.

## Algoritmos disponíveis

- Dijkstra simples
- Dijkstra com heap
- A*

## Saídas

- Animação HTML com a exploração do algoritmo (padrão em `data/processed/`).
- Resumo de métricas no terminal (Distância percorrida e Tempo estimado de viagem com ou sem atraso).

## Pendências

- Implementar um outro algoritmo de escolha do grupo
- Implementar testes unitários
- Melhorar desempenho