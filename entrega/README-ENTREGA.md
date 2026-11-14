# Entrega — Consolidador de reservas de hotel

Este documento apresenta as correções, a investigação e os resultados de validação do CLI, conforme o [README principal](../README.md).

**Estado da entrega:** quatro defeitos corrigidos e uma pendência que impede a aprovação da suíte completa.

## Defeitos corrigidos

| Arquivo | Causa raiz | Correção | Teste de referência |
| --- | --- | --- | --- |
| [currency_converter.py](../src/onfly_report/services/currency_converter.py) | A expressão `Decimal(str(float(amount) / float(rate)))` dividia pela taxa e convertia os operandos para `float`, invertendo a conversão e comprometendo a precisão decimal. | Usar `amount * rate`, mantendo os valores em `Decimal`. | [test_currency.py](../tests/test_currency.py) |
| [stay_calculator.py](../src/onfly_report/services/stay_calculator.py) | A expressão `(checkout.day - checkin.day) * rooms` subtraía apenas os dias do mês, ignorando o mês e o ano. | Usar `(checkout - checkin).days * rooms`, com diferença não inclusiva entre as datas. | [test_nights.py](../tests/test_nights.py) |
| [status_policy.py](../src/onfly_report/services/status_policy.py) | A condição `status != "CANCELLED"` permitia faturar reservas `NO_SHOW`. | Aceitar somente `status == "CONFIRMED"`, preservando a contagem de todos os status nas reservas lidas. | [test_status_rules.py](../tests/test_status_rules.py) |
| [report_builder.py](../src/onfly_report/services/report_builder.py) | A chave `(item[1]["amount"], item[0])` ordenava os hotéis pelo valor crescente, colocando os menores valores primeiro. | Usar `(-item[1]["amount"], item[0])`, com valor decrescente e desempate por `hotel_id` crescente. | [test_top_hotels.py](../tests/test_top_hotels.py) |

As causas originais foram confirmadas pelo responsável pelo projeto; as correções acima foram conferidas no código atual.

## Investigação e abordagem

A investigação relacionou cada regra de negócio à implementação e aos testes existentes, seguindo o fluxo:

```text
ler CSV → converter tipos → contar status → filtrar CONFIRMED → agregar → serializar
```

A validação foi feita em três etapas:

1. **Conferência das regras:** leitura dos repositórios CSV, da conversão de tipos e dos serviços de status, noites, câmbio e montagem do relatório.
2. **Execução dos testes:** uso da suíte existente, que executa o CLI em subprocesso e verifica o JSON gerado, sem alterar os testes fornecidos.
3. **Conferência dos arquivos fornecidos:** comparação da amostra com os valores publicados no README e da quantidade de reservas do arquivo principal com o total informado pelo CLI.

Os testes adicionais em [test_additional_rules.py](../tests/test_additional_rules.py) cobrem ano bissexto, virada de ano, arredondamento após a soma, half-up, desempate entre hotéis, exclusão de reservas não faturáveis, arquivo sem reservas, ordenação dos meses e leitura de mais de 200 registros.

Também foram conferidos o uso de `Decimal`, a média calculada sobre as noites de quarto e a serialização monetária com duas casas decimais. Os relatórios de conferência foram gerados em arquivos temporários, preservando os relatórios existentes em `output/`.


## Resultados da validação

Última execução registrada: **13/11/2026**, em Windows, com **Python 3.12.10** e **pytest 8.3.4**.

### Testes automatizados

Comando utilizado na validação:

```powershell
python -m pytest -q -p no:cacheprovider --basetemp .cache/pytest-readme
```

As opções adicionais desabilitam o cache do pytest e mantêm os arquivos temporários no projeto, sem mudar a seleção de testes.

```text
FAILED tests/test_additional_rules.py::test_more_than_200_rows
E       assert 200 == 205
1 failed, 13 passed in 2.44s
```

| Conjunto | Aprovados | Falhas |
| --- | ---: | ---: |
| Testes identificados como fornecidos | 5 | 0 |
| Testes adicionais existentes | 8 | 1 |
| **Total** | **13** | **1** |

A falha corresponde ao limite de leitura descrito na seção seguinte. O resultado ainda não atende ao requisito de aprovação da suíte completa.

### Amostra de validação

O relatório de `data/exemplo-validacao.csv` correspondeu aos valores esperados no README:

| Campo | Resultado |
| --- | ---: |
| `total_reservations` | 12 |
| `confirmed_reservations` | 9 |
| `cancelled_reservations` | 2 |
| `no_show_reservations` | 1 |
| `total_room_nights` | 28 |
| `total_amount_brl` | `"7566.00"` |
| `average_nightly_rate_brl` | `"270.21"` |

As duas entradas de `by_month` e os cinco itens de `top_hotels` também conferiram com o README, assim como `report_version = "1.0"` e o offset `-03:00` de `generated_at`.


