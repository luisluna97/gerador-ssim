# SSIM File Generator

Streamlit application that generates SSIM files from the public SIROS data source.

## Overview

The current version no longer depends on a CSV uploaded by the user. The app reads directly from the public SIROS dataset.

The user selects:

1. Airline
2. One or more airports for that airline
3. Start date
4. End date

After that, the app generates the SSIM file and provides a download button.

## How it works

1. The Streamlit app loads the public SIROS dataset.
2. It maps airline, airport, equipment and timezone data.
3. API times, received in UTC, are converted to each airport local time.
4. The SSIM validity period is built from `Inicio Operacao` and `Fim Operacao`.
5. SSIM frequency is built from the `Seg` to `Dom` columns.
6. The final SSIM output keeps the same file structure already used by the project.

## Available filters

- Airline
- Multi-select airports
- Start date
- End date

If no airport is selected, the app uses all airports for the selected airline within the chosen period.

## Main mapping

- `Cod. Empresa` -> selected airline
- `Cod. Origem` / `Cod Destino` -> IATA airport via `airport.csv`
- `Equip.` -> SSIM equipment via `ACT TYPE.xlsx`
- `Seg` ... `Dom` -> SSIM frequency
- `Inicio Operacao` / `Fim Operacao` -> SSIM date range
- `Horario Partida` / `Horario Chegada` -> local SSIM times
- `Quant. Assentos` + `Objeto Transporte` / `Tipo Servico` -> `J` or `F` status

## Access

Use the published application at:

`https://gerador-ssim-me42pp9k4m78esyvgvreyw.streamlit.app/`

## Main files

- `app.py`: Streamlit app and SSIM generation logic
- `airport.csv`: ICAO/IATA and timezone mapping
- `ACT TYPE.xlsx`: aircraft mapping
- `iata_airlines.csv`: airline ICAO -> IATA mapping
- `CHANGELOG.md`: version history

## History

See [CHANGELOG.md](CHANGELOG.md).

## Support

For operational questions or future enhancements, use the current GitHub repository.
