# Refatoração: núcleo genérico + app VPython de balão

Copie as pastas `src/` e `tests/` deste pacote para a **raiz** do seu repositório, mantendo a organização. A cópia é incremental: não substitui sua pasta `solutions/` nem outros exemplos.

## Principais arquivos

- `src/relative_movement/physics_core.py` — **novo lugar do núcleo físico geral**; não importa VPython. Aceita qualquer quantidade de objetos com aceleração constante, nomes livres (exceto `ground`) e referenciais móveis.
- `src/relative_movement/balloon/physics_core.py` — **shim de compatibilidade** para imports antigos. Quando migrar outros módulos, você pode apagar esse arquivo.
- `src/relative_movement/balloon/apps/vpython/vpython.app.py` — aplicação completa do exemplo do balão, usando o novo núcleo e os widgets compartilhados.
- `src/common/vpython/cards.py` — cards com escape de HTML e conversão segura de expressões matemáticas delimitadas por `\(...\)`, `\[...\]`, `$...$` ou `$$...$$`. Conteúdo comum é escapado.
- `src/common/vpython/parameter_panel.py` — formulário reutilizável, com grupos, limites, valores finitos, passos, inteiros, aplicar e restaurar padrões.
- `tests/test_physics_core.py` — testes unitários do núcleo, sem VPython.
- Arquivos `__init__.py` — garantem importação dos pacotes Python na árvore `src/`.

## Importação nova

```python
from relative_movement.physics_core import PointMass, SimulationEngine, GRAVITY
```

## Executar

No repositório original, com o ambiente do projeto (`uv`) e as dependências VPython instaladas:

```bash
uv run python src/relative_movement/balloon/apps/vpython/vpython.app.py
```

Para a solução analítica exibida no card, também é necessário `latex2mathml`:

```bash
uv add latex2mathml
```

**Importante:** o arquivo `.tex` esperado continua sendo:

```text
src/relative_movement/balloon/apps/vpython/solutions/ballon_problem_enunciation.tex
```

Caso o seu arquivo `.tex` contenha um documento LaTeX completo, o card renderiza a matemática nos delimitadores reconhecidos, mas **não é um compilador de documentos LaTeX**. Comandos estruturais como `\documentclass` ou `\section` fora dos delimitadores aparecem como texto.

## Testes

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Decisões físicas

- O eixo `y` é orientado para cima. A aceleração é constante por objeto.
- Um snapshot contém `abs_y`, `abs_v`, `abs_a`, `rel_y`, `rel_v`, `rel_a`, `energies`.
- `ground` é um referencial fixo na origem, não um objeto da simulação.
- `energies.kinetic` usa a velocidade relativa e `energies.potential` usa `m*g*(y-y_ref)`; `energies.mechanical` é a soma **instantânea**, e não necessariamente conservada em referenciais não inerciais ou objetos com forças externas.
- O chão físico e as dimensões da caixa pertencem apenas ao exemplo VPython. O núcleo genérico não implementa colisões.
- No exemplo, o tempo do impacto é calculado analiticamente e a simulação termina no primeiro contato descendente.

## Limites

A aplicação usa VPython e não foi executada com uma janela gráfica neste ambiente; as validações incluídas são estáticas e de lógica. A renderização MathML final depende também do suporte do navegador do VPython. O aplicativo continua restrito a celular e balão; **o que foi generalizado é o núcleo físico**, como solicitado.
