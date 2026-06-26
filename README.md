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

### Como o atraso é calculado matematicamente

Para transformar o modelo determinístico em estocástico, o algoritmo aplica os seguintes passos em cada aresta durante a montagem do grafo:

1. **Tempo Base (Cenário Ideal):** Calcula-se o tempo ideal de percurso dividindo a distância física da via pela sua velocidade máxima permitida.
2. **Fatores de Severidade:** Assume-se um atraso base padrão de 5%. Esse valor é multiplicado por 4 em cenários de horário de pico e por 1.5 caso a via seja classificada como rodovia ou via arterial (sujeitas a maior volume de veículos).
3. **Média Esperada ($\mu$):** Multiplica-se o Tempo Base pelo Fator de Severidade para obter a média do atraso esperado para aquela via específica.
4. **Distribuição Exponencial:** O atraso real $x$ não é um valor fixo. Ele é sorteado utilizando a função densidade de probabilidade de uma distribuição exponencial:
   $$f(x; \lambda) = \lambda e^{-\lambda x}$$
   Onde a taxa de ocorrência $\lambda$ é o inverso da média ($\lambda = \frac{1}{\mu}$). O uso dessa curva garante que a maioria das vias sofra apenas lentidões leves, mas cria uma probabilidade matemática real de ocorrência de engarrafamentos severos, simulando acidentes ou bloqueios imprevisíveis.
5. **Teto de Segurança:** O atraso $x$ é limitado a um teto máximo (ex: 120 minutos) para evitar tendências ao infinito.
6. **Peso Final da Aresta:** O custo final repassado ao algoritmo (Dijkstra ou A*) é a soma do **Tempo Base + Atraso**. Caso o sorteio resulte em um atraso severo em uma via principal, o peso dispara, forçando o algoritmo a recalcular e buscar rotas alternativas mais rápidas pela vizinhança.

## Algoritmos disponíveis

- Dijkstra simples
- Dijkstra com heap
- A*
- SPFA

## Saídas

- Animação HTML com a exploração do algoritmo (padrão em `data/processed/`).
- Resumo de métricas no terminal (Distância percorrida e Tempo estimado de viagem com ou sem atraso).

## Pendências

- Implementar testes unitários
- Melhorar desempenho