# Relatório — Atividade Final de AED II: Rede Social Simplificada

**Dupla:** Tiago Ferraz dos Santos e Gabriel da Cruz Geraldo  
**Linguagem:** Python 3 (pasta `py/`)

---

## 1. O que foi feito

Todas as funcionalidades pedidas foram implementadas e testadas com os dados fornecidos:

| Item | Comando | Estrutura usada | Situação |
|---|---|---|---|
| 3.1 | `BUSCAR @usuario` | Tabela hash própria (encadeamento) | Completo |
| 3.2 | `SUGERIR @usuario k` | Grafo (listas de adjacência) + heap própria | Completo |
| 3.3 | `COMUNIDADES` | Grafo + BFS própria | Completo |
| 3.4 | `POSTS_ENTRE data1 data2` | Árvore AVL própria, com rotações e consulta por intervalo podada | Completo |
| 3.5 | `TOP_SEGUIDOS k` / `TOP_CURTIDOS k` | Heap própria (top-k) | Completo |
| 3.6 | `RANKING` | Merge Sort próprio | Completo |
| 3.7 | API de linha de comando (bônus) | Usa só as estruturas acima | Completo |

Não ficou nada incompleto. Não usamos `dict`, `set`, `heapq`, `sorted()`, `list.sort()`, `bisect` nem `collections` no código do projeto; apenas listas simples (índice, `append`, `pop`), classes, strings e tipos primitivos. Até a saída `--json` é gerada por um serializador próprio (`saida_json.py`), justamente para não depender de `dict`.

---

## 2. Como foi feito
O código está na pasta `py/` e é dividido em camadas:

- **Estruturas de dados** (feitas do zero):
  - `tabela_hash.py`: tabela hash com encadeamento (BUSCAR)
  - `heap.py`: heap binária e seleção top-k (SUGERIR, TOP_SEGUIDOS, TOP_CURTIDOS)
  - `arvore_avl.py`: árvore AVL com rotações e busca por intervalo (POSTS_ENTRE)
  - `grafo.py`: grafo com listas de adjacência e BFS (SUGERIR, COMUNIDADES)
  - `ordenacao.py`: Merge Sort (RANKING)
- **Lógica da rede:** `rede_social.py` carrega os CSVs, monta as estruturas e faz as consultas (não imprime nada).
- **Interface:** `comandos.py` valida os parâmetros e formata a saída (texto ou JSON). `saida_json.py` gera o JSON. `main.py` abre o menu interativo ou funciona como API de linha de comando.
- `aedlib.py`: leitura dos arquivos (fornecido, não alterado).

**Como rodar:** `python3 py/main.py` (menu) ou `python3 py/main.py ajuda` (API).

### 2.1 Como rodar

```bash
python3 py/main.py                      # modo interativo (menu de comandos)
python3 py/main.py ajuda                # API: lista os comandos
python3 py/main.py buscar @henrique_nascimento
```

### 2.2 Organização dos arquivos (`py/`)

O código está dividido em três camadas: **estruturas de dados**, **domínio** (a rede social) e **interface** (menu e API).

| Arquivo | Camada | O que faz |
|---|---|---|
| `aedlib.py` | (fornecido) | Lê os três CSVs. Não foi alterado. |
| `tabela_hash.py` | Estrutura | Classe `TabelaHash`: hash polinomial para strings, hash multiplicativo para inteiros, encadeamento, redimensionamento (rehash). |
| `heap.py` | Estrutura | Classe `HeapBinaria` (genérica, recebe a função de comparação) e função `top_k`. |
| `arvore_avl.py` | Estrutura | Classes `NoAVL` e `ArvoreAVL`: inserção com as 4 rotações e `buscar_intervalo` podada. |
| `grafo.py` | Estrutura | Classe `Grafo`: listas de adjacência de saída e de entrada, `amigos_de_amigos` e `componentes_conexos` (BFS). |
| `ordenacao.py` | Estrutura | Função `merge_sort` (estável, recebe a função de comparação). |
| `rede_social.py` | Domínio | Classes `Usuario`, `Post` e `RedeSocial`. Monta todas as estruturas a partir dos CSVs e oferece um método por consulta. **Não imprime nada.** |
| `comandos.py` | Interface | Um `comando_*` por funcionalidade: valida parâmetros, chama a `RedeSocial` e devolve o resultado como texto **e** como JSON. Contém a tabela de comandos e a ajuda. |
| `saida_json.py` | Interface | `ObjetoJSON` (lista ordenada de pares chave/valor) e `para_json` (serializador recursivo). |
| `main.py` | Interface | Ponto de entrada. Sem argumentos abre o modo interativo; com argumentos funciona como API e define o código de saída. |

Fluxo de uma consulta: `main.py` → `comandos.executar()` → `comando_xxx()` valida os parâmetros → método da `RedeSocial` → estrutura de dados → resultado volta para `comandos.py`, que formata como texto ou JSON → `main.py` imprime e devolve o código de saída.

### 2.3 Carga dos dados

`RedeSocial.__init__` faz, uma única vez:

1. **Usuários:** cria um `Usuario` por linha, guarda num vetor (índice interno 0..n-1), cria o vetor `indice_por_id` (id do CSV → índice interno, acesso O(1)) e insere `@usuario → Usuario` na tabela hash.
2. **Seguidores:** para cada linha, adiciona a aresta `seguidor → seguido` no grafo. Linhas com id inexistente, auto-seguir e conexões repetidas são descartadas; para detectar repetição usamos outra `TabelaHash` com chave inteira `origem * n + destino`. Com os dados fornecidos nenhuma linha foi descartada (15.000 arestas).
3. **Posts:** cria um `Post`, soma curtidas e quantidade de posts no autor e insere o post na AVL pela data.

---

## 3. Escolhas tomadas e por quê
- **Tabela hash:** a função de hash é polinomial (`h = h*31 + caractere`, mod tamanho). As colisões são tratadas por encadeamento (uma lista em cada posição). O tamanho é um primo, cerca de 2× o número de usuários (4001), e a tabela dobra se passar de 75% de ocupação.
- **AVL em vez de lista ordenada:** na lista, cada inserção custa O(n). Na AVL, as rotações mantêm a árvore balanceada, então inserir e buscar custam O(log n). A busca por intervalo só desce pelos ramos necessários.
- **Heap de mínimo de tamanho k:** guarda só os k melhores. A raiz é o pior deles e sai quando aparece alguém melhor. O custo é O(n log k) e a memória, O(k).
- **Merge Sort:** é sempre O(n log n) e é estável. No empate, vale a ordem alfabética do @usuario.
- **Grafo:** listas de adjacência ("quem sigo" e "quem me segue"). Gastam bem menos memória que uma matriz 2000×2000 e dão o número de seguidores em O(1).

### 3.1 Tabela hash (BUSCAR)

- **Função de hash para strings:** hash polinomial pelo método de Horner, `h = (h * 31 + ord(c)) mod capacidade`. Todos os caracteres contribuem e a ordem importa (`@ab` ≠ `@ba`). Aplicar o `mod` a cada passo evita números enormes. Usamos 31 por ser primo e um valor clássico para texto.
- **Função de hash para inteiros** (usada só na detecção de conexões repetidas): hash multiplicativo de Knuth, `(k * 2654435761) mod 2³² mod capacidade`, que espalha chaves sequenciais.
- **Colisões:** encadeamento separado. Cada balde é uma lista de pares `[chave, valor]`. Escolhemos encadeamento porque é simples, não sofre com agrupamento (*clustering*) como a sondagem linear e continua funcionando mesmo com fator de carga alto.
- **Tamanho:** capacidade inicial de aproximadamente 2 × número de usuários, arredondada para o próximo **primo** (4001 para 2000 usuários). Primo porque o `mod` por um primo distribui melhor. Se o fator de carga passar de 0,75, a tabela dobra de tamanho (próximo primo) e reinsere tudo.
- **Resultado medido com os dados reais:** 4001 baldes, 2000 chaves, fator de carga 0,50, 2416 baldes vazios, **maior lista com 5 elementos** e 415 chaves que caíram num balde já ocupado. Ou seja, no pior caso a busca compara 5 chaves.

### 3.2 Grafo (SUGERIR e COMUNIDADES)

- **Representação:** listas de adjacência. Guardamos duas: `seguindo[v]` (quem v segue) e `seguidores[v]` (quem segue v). Uma matriz de adjacência teria 2000 × 2000 = 4 milhões de posições para só 15 mil arestas; as listas usam O(V + E) de memória. Ter a lista de entrada deixa "quantos seguidores" em O(1) e permite tratar o grafo como não dirigido nas comunidades sem duplicar arestas.
- **SUGERIR:** para cada amigo `a` que o usuário segue, percorremos quem `a` segue e somamos 1 em `contador[c]`. No fim, `contador[c]` é exatamente o número de conexões em comum. Um vetor booleano marca quem o usuário já segue (exclusão em O(1)), e a lista `tocados` guarda só os candidatos, para não varrer o vetor inteiro. Os k melhores são escolhidos com a heap (seção 3.4). Empate em conexões em comum é desfeito pela ordem alfabética do `@usuario`, para o resultado ser sempre o mesmo.
- **COMUNIDADES:** BFS a partir de cada vértice ainda não visitado; os vizinhos são `seguindo[v]` + `seguidores[v]` (grafo não dirigido). A fila é uma lista com um ponteiro de início, o que evita o `pop(0)`, que custa O(n). Componentes de tamanho 1 são os usuários totalmente isolados (não seguem nem são seguidos); os demais são as comunidades, ordenadas do maior para o menor com o nosso Merge Sort.

### 3.3 Árvore AVL (POSTS_ENTRE)

- **Chave:** a própria data em texto `AAAA-MM-DD`. Nesse formato a ordem alfabética coincide com a cronológica, então não é preciso converter. Cada nó guarda a **lista de posts daquela data** (vários posts por dia), o que deixa a árvore com 669 nós em vez de 20.000.
- **Por que AVL e não uma lista ordenada:** numa lista ordenada, cada inserção precisa deslocar elementos, O(n), e montar o índice com 20.000 posts custaria O(n²). Uma árvore de busca **sem** balanceamento degeneraria numa lista se os posts chegassem em ordem de data (o caso mais comum em dados reais), com altura n. A AVL garante altura O(log n) com as rotações: inserção e busca ficam O(log n) sempre. Com os dados reais a altura ficou **11** para 669 nós (o limite teórico da AVL é cerca de 1,44 · log₂ n ≈ 13,5).
- **Rotações:** depois de inserir, na volta da recursão, recalculamos a altura e o fator de balanceamento (altura esq. − altura dir.) de cada nó do caminho. Os quatro casos (Esquerda-Esquerda, Esquerda-Direita, Direita-Direita, Direita-Esquerda) estão comentados com desenhos no código.
- **Consulta por intervalo sem percorrer a árvore toda:** só descemos à esquerda se a data do nó for maior que o início, e só à direita se for menor que o fim. Exemplo medido: a consulta de janeiro/2025 visitou **37 dos 669 nós**. O resultado sai em ordem cronológica porque é um percurso em ordem.
- **Datas:** validamos o formato e se a data existe (dias do mês e ano bissexto). Datas invertidas são trocadas automaticamente, com um aviso.

### 3.4 Heap (SUGERIR, TOP_SEGUIDOS e TOP_CURTIDOS)

- `HeapBinaria` é guardada num vetor (pai `(i-1)//2`, filhos `2i+1` e `2i+2`) e é genérica: recebe uma função que diz qual elemento deve ficar mais perto da raiz. Com ela dá para ter heap de mínimo ou de máximo sem duplicar código.
- **Para o top-k usamos uma heap de MÍNIMO de tamanho k.** A raiz é sempre o *pior* entre os k melhores vistos até agora. Para cada novo elemento basta comparar com a raiz: se for melhor, ele substitui a raiz (um *sift-down*); se não, é descartado em O(1). No fim retiramos os k elementos (saem do pior para o melhor) e invertemos.
- **Por que mínimo e não máximo:** com uma heap de máximo teríamos que colocar **todos** os n elementos na heap e depois retirar k, usando O(n) de memória. A heap de mínimo de tamanho k usa só O(k) de memória e custa O(n log k), melhor quando k é pequeno (o caso normal: top 5, top 10).
- Se `k` for maior que o número de candidatos, a heap simplesmente nunca enche e devolvemos todos (com aviso).
- Critérios de desempate: TOP_SEGUIDOS por `@usuario` alfabético; TOP_CURTIDOS pelo menor id do post.

### 3.5 Ordenação (RANKING)

- **Merge Sort.** Escolhemos porque é **O(n log n) em todos os casos** (o Quick Sort pode cair para O(n²) no pior caso) e porque é **estável** (o Heap Sort não é). A comparação usada é: maior engajamento primeiro; em empate, `@usuario` em ordem alfabética.
- `engajamento = seguidores × 2 + soma das curtidas dos posts`. As curtidas por usuário são somadas uma única vez na carga, então calcular o engajamento é O(1).
- O ranking fica guardado em cache depois da primeira vez, já que os dados não mudam durante a execução.

### 3.6 Organização da API (bônus)

- As estruturas (`tabela_hash.py`, `heap.py`, `arvore_avl.py`, `grafo.py`, `ordenacao.py`) não sabem nada de terminal nem de JSON.
- `rede_social.py` só devolve objetos (`Usuario`, `Post`, listas), nunca imprime.
- `comandos.py` é a única camada que conhece o formato da saída: cada `comando_*` devolve um `ResultadoComando` com o **texto** e o **JSON** da mesma resposta. Por isso o modo interativo e a API usam exatamente as mesmas funções.
- `main.py` só decide o modo, imprime e define o código de saída (0 em sucesso, 1 em erro).

---

## 4. Complexidade de cada comando

Notação: V = usuários (2.000), E = conexões (15.000), P = posts (20.000), D = datas distintas (669), L = tamanho do `@usuario`, k = parâmetro do comando, m = quantidade de resultados.

| Comando | Complexidade | Justificativa |
|---|---|---|
| Carga dos dados | O(V + E + P log D) | Cada usuário e cada conexão entram em O(1) médio (hash e listas); cada post é inserido na AVL em O(log D). |
| `BUSCAR` | O(L) médio, O(V) no pior caso | Calcular o hash percorre o nome; a lista do balde tem tamanho médio constante (fator de carga ≤ 0,75; máximo medido: 5). Seguindo/seguidores são `len` das listas, O(1). |
| `SUGERIR` | O(V + A + C log k) | O(V) para criar os vetores auxiliares; A = soma dos graus de saída de quem o usuário segue (cada aresta de 2º nível é vista uma vez); C candidatos passam pela heap de tamanho k. |
| `COMUNIDADES` | O(V + E + c log c) | A BFS visita cada vértice uma vez e cada aresta duas (uma por ponta); depois ordenamos os c componentes com Merge Sort. |
| `POSTS_ENTRE` | O(log D + m) | A busca podada desce só pelos ramos que podem ter datas do intervalo: O(log D) para achar as bordas mais os nós dentro do intervalo. |
| `TOP_SEGUIDOS` | O(V log k) | Cada usuário é comparado com a raiz da heap de tamanho k e, se entrar, custa O(log k). |
| `TOP_CURTIDOS` | O(P log k) | Mesmo raciocínio, sobre os posts. |
| `RANKING` | O(V log V) | Merge Sort; mostrar os N primeiros é O(N). A posição de um usuário é encontrada em O(V) no vetor já ordenado. |

---

## 5. Testes feitos manualmente

Ambiente: GitHub Codespaces, Python 3, com os arquivos de dados originais. Cada chamada da API leva cerca de 0,2 s, incluindo a leitura dos três arquivos e a montagem de todas as estruturas.

Além dos testes abaixo, conferimos os resultados com um script à parte (fora do projeto, só para teste) que recalcula tudo de forma "ingênua" com as estruturas prontas do Python e compara: BUSCAR para os 2.000 usuários, SUGERIR (k = 7) para os 2.000 usuários, COMUNIDADES, três intervalos de POSTS_ENTRE, TOP_SEGUIDOS, TOP_CURTIDOS e o RANKING completo. Todos bateram. Também verificamos que a AVL respeita |fator| ≤ 1 em todos os nós.

### 5.1 BUSCAR

```
$ python3 py/main.py buscar @henrique_nascimento
Usuario:          @henrique_nascimento
Nome:             Henrique Nascimento
Data de cadastro: 2022-10-26
Segue:            10
Seguidores:       12
Posts publicados: 8
(código de saída 0)

$ python3 py/main.py buscar henrique_nascimento        # sem o @: também funciona
(mesma saída, código 0)

$ python3 py/main.py buscar @nao_existe                # caso de borda: usuário inexistente
Erro: Usuario @nao_existe nao existe.
(código de saída 1)

$ python3 py/main.py buscar @mariana_gomes             # caso de borda: usuário isolado
Usuario:          @mariana_gomes
Nome:             Mariana Gomes
Data de cadastro: 2020-01-29
Segue:            0
Seguidores:       0
Posts publicados: 13
(código de saída 0)
```

### 5.2 SUGERIR

```
$ python3 py/main.py sugerir @henrique_nascimento 5
Sugestoes para @henrique_nascimento (k = 5, 65 candidatos a distancia 2):
  Pos  Usuario                     Nome                        Em comum
  1.   @andre_martins2             André Martins               2
  2.   @beatriz_moreira3           Beatriz Moreira             2
  3.   @eduarda_rocha5             Eduarda Rocha               2
  4.   @mateus_pereira2            Mateus Pereira              2
  5.   @sofia_freitas              Sofia Freitas               2

$ python3 py/main.py sugerir @andre_barbosa 50         # caso de borda: k maior que os candidatos
Sugestoes para @andre_barbosa (k = 50, 3 candidatos a distancia 2):
  Pos  Usuario                     Nome                        Em comum
  1.   @gabriela_gomes             Gabriela Gomes              2
  2.   @isabela_santos4            Isabela Santos              1
  3.   @pedro_teixeira             Pedro Teixeira              1
  (k maior que o numero de candidatos: mostrando todos os 3)

$ python3 py/main.py sugerir @isabela_pinto 5          # segue alguém, mas não há amigos de amigos novos
Sugestoes para @isabela_pinto (k = 5, 0 candidatos a distancia 2):
  Nenhuma sugestao: nao ha amigos de amigos que ele ainda nao siga.

$ python3 py/main.py sugerir @mariana_gomes 5          # caso de borda: usuário isolado
Sugestoes para @mariana_gomes (k = 5, 0 candidatos a distancia 2):
  Nenhuma sugestao: @mariana_gomes nao segue ninguem.

$ python3 py/main.py sugerir @henrique_nascimento abc  # k não numérico
Erro: O parametro 'k' deve ser um numero inteiro positivo (recebido: 'abc').
(código de saída 1)
```

### 5.3 COMUNIDADES

```
$ python3 py/main.py comunidades
Comunidades (componentes conexos com 2 ou mais usuarios): 18
Usuarios totalmente isolados: 58
Total de componentes (contando cada isolado como 1): 76
Tamanho de cada comunidade, da maior para a menor:
  Comunidade 1: 930 usuarios
  Comunidade 2: 620 usuarios
  Comunidade 3: 310 usuarios
  Comunidade 4: 8 usuarios
  Comunidade 5: 8 usuarios
  Comunidade 6: 8 usuarios
  Comunidade 7: 7 usuarios
  Comunidade 8: 6 usuarios
  Comunidade 9: 6 usuarios
  Comunidade 10: 6 usuarios
  Comunidade 11: 5 usuarios
  Comunidade 12: 5 usuarios
  Comunidade 13: 4 usuarios
  Comunidade 14: 4 usuarios
  Comunidade 15: 4 usuarios
  Comunidade 16: 4 usuarios
  Comunidade 17: 4 usuarios
  Comunidade 18: 3 usuarios
```

Conferência: 930 + 620 + 310 + 8 + 8 + 8 + 7 + 6 + 6 + 6 + 5 + 5 + 4 × 5 + 3 = 1942 usuários em comunidades, mais 58 isolados = 2000.

### 5.4 POSTS_ENTRE

```
$ python3 py/main.py posts-entre 2025-01-01 2025-01-03 --limite 8
Posts entre 2025-01-01 e 2025-01-03: 93 encontrados
  Data        Id     Autor                     Curtidas  Texto
  2025-01-01  403    @quesia_almeida2          1         Prova sabe livro isso viagem faculdade dados código hash heap resolver
  2025-01-01  820    @henrique_araujo3         1         Amanhã isso sol consegui faculdade
  2025-01-01  1704   @joao_ramos3              0         Bom consegui hash dados heap feliz muito
  ...
  ... mostrando 8 de 93 posts.
Total: 93 posts.

$ python3 py/main.py posts-entre 2025-01-03 2025-01-01 --limite 3   # caso de borda: datas invertidas
Aviso: Datas invertidas: a consulta foi feita de 2025-01-01 ate 2025-01-03.
Posts entre 2025-01-01 e 2025-01-03: 93 encontrados
...

$ python3 py/main.py posts-entre 2030-01-01 2030-12-31   # caso de borda: intervalo sem posts
Posts entre 2030-01-01 e 2030-12-31: 0 encontrados
  Nenhum post nesse intervalo.
Total: 0 posts.

$ python3 py/main.py posts-entre 2025-02-30 2025-03-01   # data que não existe
Erro: Data invalida: '2025-02-30'. Use o formato AAAA-MM-DD (ex.: 2025-03-01).
(código de saída 1)
```

Os posts publicados exatamente em `data1` e em `data2` aparecem (intervalo fechado), e a saída sai em ordem cronológica. Os dados vão de 2025-01-01 a 2026-10-31.

### 5.5 TOP_SEGUIDOS e TOP_CURTIDOS

```
$ python3 py/main.py top-seguidos 5
Top 5 usuarios com mais seguidores:
  Pos  Usuario                     Nome                        Seguidores
  1.   @nicolas_mendes             Nicolas Mendes              110
  2.   @mariana_costa              Mariana Costa               109
  3.   @renata_pinto               Renata Pinto                109
  4.   @isabela_freitas3           Isabela Freitas             108
  5.   @larissa_moreira            Larissa Moreira             108

$ python3 py/main.py top-curtidos 5
Top 5 posts mais curtidos:
  Pos  Curtidas  Data        Autor                     Texto
  1.   2988      2025-06-16  @zeca_pinto               De jogo de fim viagem livro café bom árvore cansado estruturas
  2.   1274      2025-01-17  @ursula_martins           Sol café finalmente ontem sabe algoritmo ruim
  3.   789       2026-06-03  @renata_souza2            Dados viagem algoritmo academia
  4.   747       2025-10-04  @mateus_vieira            Fim treino código recomendo muito
  5.   704       2026-05-13  @henrique_teixeira3       Hoje algoritmo bug estudei academia heap sol ruim

$ python3 py/main.py top-seguidos 0                    # k inválido
Erro: O parametro 'k' deve ser maior que zero.
(código de saída 1)
```

Também testamos `top-seguidos 5000` (k maior que o total): devolve os 2000 usuários e avisa.

### 5.6 RANKING

```
$ python3 py/main.py ranking --limite 10 --usuario @henrique_nascimento
Ranking de engajamento (seguidores x 2 + curtidas) - 10 primeiros de 2000 usuarios:
  Pos   Usuario                     Seguidores  Curtidas  Engajamento
  1.    @zeca_pinto                 7           2998      3012
  2.    @ursula_martins             5           1291      1301
  3.    @renata_souza2              7           925       939
  4.    @mateus_vieira              8           755       771
  5.    @henrique_teixeira3         10          712       732
  6.    @andre_ferreira             12          646       670
  7.    @joao_rocha                 7           639       653
  8.    @patricia_barbosa           10          517       537
  9.    @rafael_rocha               6           519       531
  10.   @eduarda_costa              8           508       524
Posicao de @henrique_nascimento: 927o de 2000 (engajamento 30)
```

Conferência da fórmula: @zeca_pinto tem 7 seguidores e 2998 curtidas → 7 × 2 + 2998 = 3012.

### 5.7 Modo interativo

```
$ python3 py/main.py
Usuários carregados: 2000
Conexões carregadas: 15000
Posts carregados: 20000

Comandos disponiveis:
  ...

> BUSCAR @henrique_nascimento
Usuario:          @henrique_nascimento
...
> TOP_SEGUIDOS 3
Top 3 usuarios com mais seguidores:
...
> POSTS_ENTRE 2025-01-01 2025/13/01
Erro: Data invalida: '2025/13/01'. Use o formato AAAA-MM-DD (ex.: 2025-03-01).
> sair
```

No modo interativo os comandos aceitam maiúsculas ou minúsculas e `_` ou `-` (`POSTS_ENTRE` = `posts-entre`). Um erro não encerra o programa.

---

## 6. API de linha de comando (bônus 3.7)

### 6.1 Comandos

| Comando | Parâmetros | O que faz | Exemplo |
|---|---|---|---|
| `buscar` | `@usuario` | Dados do usuário (tabela hash) | `python3 py/main.py buscar @henrique_nascimento` |
| `sugerir` | `@usuario k` | Até k sugestões de quem seguir (grafo + heap) | `python3 py/main.py sugerir @henrique_nascimento 5` |
| `comunidades` | — | Comunidades e usuários isolados (BFS) | `python3 py/main.py comunidades` |
| `posts-entre` | `data1 data2 [--limite N]` | Posts entre duas datas, inclusive (AVL) | `python3 py/main.py posts-entre 2025-03-01 2025-03-31` |
| `top-seguidos` | `k` | k usuários com mais seguidores (heap) | `python3 py/main.py top-seguidos 10` |
| `top-curtidos` | `k` | k posts mais curtidos (heap) | `python3 py/main.py top-curtidos 10` |
| `ranking` | `[--limite N] [--usuario @x]` | Ranking de engajamento (Merge Sort); padrão: 20 primeiros | `python3 py/main.py ranking --limite 20` |
| `ajuda` | — | Lista comandos, parâmetros e exemplos | `python3 py/main.py ajuda` |

Opção geral: `--json` em qualquer comando troca a saída legível por JSON válido.

### 6.2 Regras de erro e códigos de saída

- Sucesso → código de saída **0**.
- Parâmetro faltando, `k` não numérico ou ≤ 0, data mal formatada ou inexistente, usuário inexistente → mensagem clara em `stderr` e código **1** (com `--json`, a mensagem sai como `{"erro": "..."}` em `stdout`, para continuar sendo JSON válido).
- Comando inválido → mensagem de erro, a ajuda completa e código **1**.

### 6.3 Exemplos com a saída obtida

```
$ python3 py/main.py top-seguidos 3 --json
{
  "k": 3,
  "resultado": [
    {
      "posicao": 1,
      "usuario": "@nicolas_mendes",
      "nome": "Nicolas Mendes",
      "seguidores": 110
    },
    {
      "posicao": 2,
      "usuario": "@mariana_costa",
      "nome": "Mariana Costa",
      "seguidores": 109
    },
    {
      "posicao": 3,
      "usuario": "@renata_pinto",
      "nome": "Renata Pinto",
      "seguidores": 109
    }
  ]
}
(código de saída 0; validado com um leitor de JSON)

$ python3 py/main.py buscar @nao_existe --json
{
  "erro": "Usuario @nao_existe nao existe."
}
(código de saída 1)

$ python3 py/main.py xpto
Erro: Comando invalido: 'xpto'.

Comandos disponiveis:

  buscar @usuario
      Dados do usuario (tabela hash)
      Exemplo: python3 py/main.py buscar @ana_silva
  ...
(código de saída 1)
```

### 6.4 Separação entre estruturas e interface

Explicado na seção 3.6: as estruturas e a `RedeSocial` não imprimem nada; `comandos.py` transforma cada resultado em texto e em JSON; `main.py` só escolhe o modo (interativo ou API), imprime e devolve o código de saída. Por isso as mesmas funções atendem o menu e a API, e a API só **usa** as estruturas implementadas por nós.
