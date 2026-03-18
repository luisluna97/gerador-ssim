# Gerador de Arquivo SSIM

Aplicacao Streamlit para gerar arquivos SSIM a partir da base publica do SIROS.

## Visao geral

Na versao atual, a fonte de dados nao e mais um CSV enviado pelo usuario. O app consome diretamente a base publica do SIROS.

O usuario seleciona:

1. Companhia aerea
2. Um ou mais aeroportos da companhia
3. Data inicial
4. Data final

Depois disso, o app gera e libera o download do arquivo SSIM.

## Como funciona

1. O Streamlit carrega a base publica do SIROS.
2. O app mapeia companhia, aeroportos, equipamento e timezone.
3. Os horarios da API, recebidos em UTC, sao convertidos para horario local do aeroporto.
4. O periodo SSIM e montado a partir de `Inicio Operacao` e `Fim Operacao`.
5. A frequencia SSIM e montada a partir das colunas `Seg` a `Dom`.
6. O output mantem a estrutura SSIM ja usada pelo projeto.

## Filtros disponiveis

- Companhia aerea
- Multisselecao de aeroportos
- Data inicial
- Data final

Se nenhum aeroporto for selecionado, o app usa todos os aeroportos da companhia no periodo filtrado.

## Mapeamento principal

- `Cod. Empresa` -> companhia selecionada
- `Cod. Origem` / `Cod Destino` -> aeroporto IATA via `airport.csv`
- `Equip.` -> equipamento SSIM via `ACT TYPE.xlsx`
- `Seg` ... `Dom` -> frequencia SSIM
- `Inicio Operacao` / `Fim Operacao` -> vigencia do voo no SSIM
- `Horario Partida` / `Horario Chegada` -> horarios locais no SSIM
- `Quant. Assentos` + `Objeto Transporte` / `Tipo Servico` -> status `J` ou `F`

## Acesso

Use a aplicacao publicada em:

`https://gerador-ssim-me42pp9k4m78esyvgvreyw.streamlit.app/`

## Arquivos principais

- `app.py`: app Streamlit e motor de geracao SSIM
- `airport.csv`: mapeamento ICAO/IATA e timezone
- `ACT TYPE.xlsx`: mapeamento de equipamento
- `iata_airlines.csv`: mapeamento ICAO -> IATA da companhia
- `CHANGELOG.md`: historico de versoes

## Historico

Veja [CHANGELOG.md](CHANGELOG.md).

## Suporte

Para duvidas operacionais ou evolucao do projeto, use o repositorio atual no GitHub.

