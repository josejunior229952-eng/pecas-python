# Controle de Produção e Qualidade — Peças Fabricadas

Este é um sistema de linha de comando (CLI) desenvolvido em Python para gerenciar o cadastro, a avaliação de qualidade e o armazenamento de peças em uma linha de produção.

## 🛠️ Funcionamento

O programa permite o registro de peças, avaliando automaticamente se cada item atende aos critérios de qualidade exigidos. Se aprovada, a peça é encaminhada para uma caixa de armazenamento.

### Critérios de Qualidade
Para ser aprovada, uma peça deve atender simultaneamente a:
- **Peso:** Entre 95,0g e 105,0g.
- **Cor:** Deve ser "azul" ou "verde".
- **Comprimento:** Entre 10,0cm e 20,0cm.

### Logística de Armazenamento
- Peças aprovadas são organizadas em caixas.
- Cada caixa tem capacidade máxima de **10 peças**.
- O sistema fecha automaticamente uma caixa ao atingir o limite e abre uma nova na próxima aprovação.

### Funcionalidades
1. **Cadastrar nova peça:** Entrada de dados e validação imediata.
2. **Listar peças:** Visualização de itens aprovados (agrupados por caixa) e reprovados (com motivos).
3. **Remover peça:** Exclusão por ID, com atualização automática da ocupação das caixas.
4. **Listar caixas fechadas:** Detalhamento das caixas que já completaram o lote.
5. **Gerar relatório final:** Resumo estatístico da produção e motivos de falhas.

---

## 🚀 Como rodar o programa

### Pré-requisitos
- Python 3.6 ou superior instalado.
- Terminal ou Prompt de Comando.

### Passo a Passo

1. **Clone ou baixe o repositório** para sua máquina local.

2. **Instale as dependências:**
   O projeto utiliza a biblioteca `colorama` para uma interface colorida e amigável.
   ```bash
   pip install colorama
   ```
   *Nota: Você também pode usar o arquivo de requerimentos (se disponível): `pip install -r requeriments.txt`.*

3. **Execute a aplicação:**
   No diretório do projeto, execute o comando:
   ```bash
   python app.py
   ```

---

## 📝 Exemplos de Entradas e Saídas

### Exemplo 1: Peça Aprovada
**Entrada:**
- **Descrição:** Engrenagem A1
- **Peso (g):** 100
- **Cor:** azul
- **Comprimento (cm):** 15

**Saída:**
```text
  ✔  Peça #1 APROVADA e armazenada na Caixa #1!
  📦  Nova caixa #1 aberta automaticamente.
```

### Exemplo 2: Peça Reprovada
**Entrada:**
- **Descrição:** Pino B2
- **Peso (g):** 90
- **Cor:** vermelho
- **Comprimento (cm):** 25

**Saída:**
```text
  ✖  Peça #2 REPROVADA pelos seguintes motivos:
       • Peso 90.0g fora do intervalo [95.0g – 105.0g]
       • Cor 'vermelho' não aprovada (aceitas: azul, verde)
       • Comprimento 25.0cm fora do intervalo [10.0cm – 20.0cm]
```

---

## 📋 Relatório de Produção (Exemplo)
O relatório final exibe estatísticas como:
- Percentual de aprovação.
- Gráfico simples de motivos de reprovação.
- Ocupação visual das caixas usando barras de progresso (ex: `[████░░░░░░]`).
