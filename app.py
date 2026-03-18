from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st


SIROS_URL = "https://siros.anac.gov.br/siros/registros/registros/registros.csv"
DAY_COLUMNS = [
    ("Seg", "1"),
    ("Ter", "2"),
    ("Qua", "3"),
    ("Qui", "4"),
    ("Sex", "5"),
    ("Sab", "6"),
    ("Dom", "7"),
]
REQUIRED_COLUMNS = [
    "Cod. Empresa",
    "Empresa",
    "No Voo",
    "Equip.",
    "Seg",
    "Ter",
    "Qua",
    "Qui",
    "Sex",
    "Sab",
    "Dom",
    "Quant. Assentos",
    "No SIROS",
    "Situacao SIROS",
    "Data Registro",
    "Inicio Operacao",
    "Fim Operacao",
    "Natureza Operacao",
    "No Etapa",
    "Cod. Origem",
    "Arpt Origem",
    "Cod Destino",
    "Arpt Destino",
    "Horario Partida",
    "Horario Chegada",
    "Tipo Servico",
    "Objeto Transporte",
    "Codeshare",
]


def sanitize_column_name(name):
    replacements = {
        "Ã³": "o",
        "Ã“": "O",
        "Ã£": "a",
        "Ãƒ": "A",
        "Ã¢": "a",
        "Ã‚": "A",
        "Ã¡": "a",
        "Ã": "A",
        "Ã©": "e",
        "Ã‰": "E",
        "Ã­": "i",
        "Ã": "I",
        "Ãº": "u",
        "Ãš": "U",
        "Ã§": "c",
        "Ã‡": "C",
        "Âº": "o",
        "Âª": "a",
        "Ã´": "o",
        "Ã”": "O",
    }
    sanitized = name.strip()
    for old, new in replacements.items():
        sanitized = sanitized.replace(old, new)
    return sanitized


def ajustar_linha(line, comprimento=200):
    return line.ljust(comprimento)[:comprimento]


def normalizar_texto(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def format_timezone_offset(offset_value):
    try:
        offset = float(offset_value)
        hours = int(offset)
        minutes = int(abs(offset - hours) * 60)
        sign = "+" if offset >= 0 else "-"
        return f"{sign}{abs(hours):02}{minutes:02}"
    except (ValueError, TypeError):
        return "+0000"


def normalizar_numero_voo(value):
    numero = "".join(char for char in normalizar_texto(value) if char.isdigit())
    return numero or normalizar_texto(value)


def construir_frequencia(df):
    frequency_parts = []
    for column, digit in DAY_COLUMNS:
        values = df[column].fillna("").astype(str).str.strip()
        frequency_parts.append(np.where((values != "") & (values != "0"), digit, " "))
    return pd.Series(["".join(parts) for parts in zip(*frequency_parts)], index=df.index)


def formatar_frequencia_ssim(value):
    if pd.isna(value):
        return " " * 7

    frequencia = str(value)
    if len(frequencia) >= 7:
        return frequencia[:7]

    return frequencia.ljust(7)


def determinar_status(objeto_transporte, tipo_servico, assentos):
    texto = " ".join(
        [
            normalizar_texto(objeto_transporte).upper(),
            normalizar_texto(tipo_servico).upper(),
        ]
    )

    if "CARGA" in texto:
        return "F"

    try:
        if pd.notna(assentos) and float(assentos) == 0:
            return "F"
    except (ValueError, TypeError):
        pass

    return "J"


def converter_horario_utc_para_local(time_value, tz_offset):
    horario = normalizar_texto(time_value)
    if not horario:
        return "0000"

    try:
        utc_dt = datetime.strptime(horario, "%H:%M")
        local_dt = utc_dt + timedelta(hours=float(tz_offset))
        return local_dt.strftime("%H%M")
    except (ValueError, TypeError):
        return "0000"


@st.cache_data(show_spinner=False)
def carregar_aeroportos():
    airport_df = pd.read_csv("airport.csv")
    airport_df["ICAO"] = airport_df["ICAO"].fillna("").astype(str).str.strip().str.upper()
    airport_df["IATA"] = airport_df["IATA"].fillna("").astype(str).str.strip().str.upper()
    airport_df["Timezone"] = (
        airport_df["Timezone"].replace("\\N", "0").fillna("0").astype(float)
    )

    return {
        "icao_to_iata": dict(zip(airport_df["ICAO"], airport_df["IATA"])),
        "icao_to_timezone": dict(zip(airport_df["ICAO"], airport_df["Timezone"])),
    }


@st.cache_data(show_spinner=False)
def carregar_aeronaves():
    aircraft_df = pd.read_excel("ACT TYPE.xlsx", dtype={"ICAO": str, "IATA": str})
    aircraft_df["ICAO"] = aircraft_df["ICAO"].fillna("").astype(str).str.strip().str.upper()
    aircraft_df["IATA"] = aircraft_df["IATA"].fillna("").astype(str).str.strip().str.upper()
    return dict(zip(aircraft_df["ICAO"], aircraft_df["IATA"]))


@st.cache_data(show_spinner=False)
def carregar_companhias():
    airlines_df = pd.read_csv("iata_airlines.csv")
    airlines_df["ICAO code"] = (
        airlines_df["ICAO code"].fillna("").astype(str).str.strip().str.upper()
    )
    airlines_df["IATA Designator"] = (
        airlines_df["IATA Designator"].fillna("").astype(str).str.strip().str.upper()
    )
    return dict(zip(airlines_df["ICAO code"], airlines_df["IATA Designator"]))


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_base_siros():
    df = pd.read_csv(
        SIROS_URL,
        sep=";",
        encoding="utf-8-sig",
        skiprows=1,
        dtype=str,
    )
    if len(df.columns) != len(REQUIRED_COLUMNS):
        raise ValueError(
            f"Quantidade inesperada de colunas na fonte SIROS: {len(df.columns)}"
        )

    df.columns = REQUIRED_COLUMNS

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Colunas obrigatorias ausentes na fonte SIROS: {', '.join(missing_columns)}"
        )

    for column in REQUIRED_COLUMNS:
        df[column] = df[column].fillna("").astype(str).str.strip()

    df = df[REQUIRED_COLUMNS].copy()

    df["Inicio Operacao DT"] = pd.to_datetime(df["Inicio Operacao"], errors="coerce")
    df["Fim Operacao DT"] = pd.to_datetime(df["Fim Operacao"], errors="coerce")
    df = df[
        df["Inicio Operacao DT"].notna()
        & df["Fim Operacao DT"].notna()
        & (df["No Voo"] != "")
        & (df["Cod. Origem"] != "")
        & (df["Cod Destino"] != "")
    ].copy()

    aeroportos = carregar_aeroportos()
    aeronaves = carregar_aeronaves()
    companhias = carregar_companhias()

    df["Cod. Empresa"] = df["Cod. Empresa"].str.upper()
    df["Cod. Origem"] = df["Cod. Origem"].str.upper()
    df["Cod Destino"] = df["Cod Destino"].str.upper()
    df["Equip."] = df["Equip."].str.upper()

    df["Cliente IATA"] = df["Cod. Empresa"].map(companhias).fillna("")
    df["Origem IATA"] = df["Cod. Origem"].map(aeroportos["icao_to_iata"]).fillna("")
    df["Destino IATA"] = df["Cod Destino"].map(aeroportos["icao_to_iata"]).fillna("")
    df["Origem TZ"] = (
        df["Cod. Origem"].map(aeroportos["icao_to_timezone"]).fillna(0.0).astype(float)
    )
    df["Destino TZ"] = (
        df["Cod Destino"].map(aeroportos["icao_to_timezone"]).fillna(0.0).astype(float)
    )
    df["Equipamento SSIM"] = df["Equip."].map(aeronaves).fillna(df["Equip."]).str[:3]

    df["Base Origem"] = df["Origem IATA"].where(
        df["Origem IATA"].str.len() == 3, df["Cod. Origem"]
    )
    df["Base Destino"] = df["Destino IATA"].where(
        df["Destino IATA"].str.len() == 3, df["Cod Destino"]
    )

    df["Frequencia SSIM"] = construir_frequencia(df)
    df["Assentos Num"] = pd.to_numeric(df["Quant. Assentos"], errors="coerce")
    df["Status SSIM"] = [
        determinar_status(objeto, tipo, assentos)
        for objeto, tipo, assentos in zip(
            df["Objeto Transporte"], df["Tipo Servico"], df["Assentos Num"]
        )
    ]
    df["Partida Local"] = [
        converter_horario_utc_para_local(horario, tz)
        for horario, tz in zip(df["Horario Partida"], df["Origem TZ"])
    ]
    df["Chegada Local"] = [
        converter_horario_utc_para_local(horario, tz)
        for horario, tz in zip(df["Horario Chegada"], df["Destino TZ"])
    ]
    df["Numero Voo SSIM"] = df["No Voo"].map(normalizar_numero_voo)
    df["Etapa SSIM"] = df["No Etapa"].replace("", "1").str.zfill(2)
    df["Flight Sort"] = pd.to_numeric(df["Numero Voo SSIM"], errors="coerce")
    df["Etapa Sort"] = pd.to_numeric(df["Etapa SSIM"], errors="coerce").fillna(99)

    return df


def construir_opcoes_clientes(df):
    client_rows = (
        df[["Cod. Empresa", "Empresa", "Cliente IATA"]]
        .drop_duplicates()
        .sort_values(["Empresa", "Cod. Empresa"])
    )

    options = {}
    for row in client_rows.itertuples(index=False):
        codigo = normalizar_texto(row[0])
        empresa = normalizar_texto(row[1])
        iata = normalizar_texto(row[2]) or "--"
        options[codigo] = f"{empresa} ({iata}/{codigo})"

    return options


def construir_opcoes_aeroportos(df):
    airport_rows = pd.concat(
        [
            df[["Base Origem", "Arpt Origem"]].rename(
                columns={"Base Origem": "Aeroporto", "Arpt Origem": "Nome"}
            ),
            df[["Base Destino", "Arpt Destino"]].rename(
                columns={"Base Destino": "Aeroporto", "Arpt Destino": "Nome"}
            ),
        ],
        ignore_index=True,
    )

    airport_rows = airport_rows[
        (airport_rows["Aeroporto"] != "") & airport_rows["Nome"].notna()
    ].drop_duplicates()
    airport_rows = airport_rows.sort_values(["Aeroporto", "Nome"])

    options = {}
    for row in airport_rows.itertuples(index=False):
        options[row[0]] = f"{row[0]} | {normalizar_texto(row[1])}"

    return options


def filtrar_registros(df, cliente_codigo, aeroportos_selecionados, data_inicio, data_fim):
    data_inicio_ts = pd.Timestamp(data_inicio)
    data_fim_ts = pd.Timestamp(data_fim)

    mask = df["Cod. Empresa"].eq(cliente_codigo)
    mask &= df["Fim Operacao DT"].ge(data_inicio_ts)
    mask &= df["Inicio Operacao DT"].le(data_fim_ts)

    if aeroportos_selecionados:
        mask &= df["Base Origem"].isin(aeroportos_selecionados) | df["Base Destino"].isin(
            aeroportos_selecionados
        )

    filtered = df.loc[mask].copy()
    if filtered.empty:
        return filtered

    filtered["SSIM Start DT"] = filtered["Inicio Operacao DT"].clip(lower=data_inicio_ts)
    filtered["SSIM End DT"] = filtered["Fim Operacao DT"].clip(upper=data_fim_ts)
    filtered = filtered[filtered["SSIM Start DT"] <= filtered["SSIM End DT"]].copy()

    filtered["SSIM Start"] = filtered["SSIM Start DT"].dt.strftime("%d%b%y").str.upper()
    filtered["SSIM End"] = filtered["SSIM End DT"].dt.strftime("%d%b%y").str.upper()

    return filtered


def gerar_ssim(df, codigo_iata, output_file=None):
    if df.empty:
        raise ValueError("Nenhum registro disponivel para gerar o SSIM.")

    data_min = df["SSIM Start DT"].min().strftime("%d%b%y").upper()
    data_max = df["SSIM End DT"].max().strftime("%d%b%y").upper()
    data_emissao = datetime.now().strftime("%d%b%y").upper()
    data_emissao2 = datetime.now().strftime("%Y%m%d").upper()

    if output_file is None:
        output_file = f"{codigo_iata} {data_emissao2} {data_min}-{data_max}.ssim"

    lines = []
    numero_linha = 1

    linha_1_conteudo = "1AIRLINE STANDARD SCHEDULE DATA SET"
    linha_1 = linha_1_conteudo + (" " * (200 - len(linha_1_conteudo) - 8)) + f"{numero_linha:08}"
    lines.append(linha_1)
    numero_linha += 1

    for _ in range(4):
        lines.append("0" * 200)
        numero_linha += 1

    linha_2_conteudo = (
        f"2L{codigo_iata}  0008    {data_min}{data_max}{data_emissao}Created by dnata capacity"
    )
    posicao_p = 72
    espacos_antes_p = max(posicao_p - len(linha_2_conteudo) - 1, 0)
    linha_2 = linha_2_conteudo + (" " * espacos_antes_p) + "P"
    numero_linha_str = f" EN08{numero_linha:08}"
    linha_2 += " " * (200 - len(linha_2) - len(numero_linha_str)) + numero_linha_str
    lines.append(linha_2)
    numero_linha += 1

    for _ in range(4):
        lines.append("0" * 200)
        numero_linha += 1

    flight_date_counter = {}
    df_sorted = df.sort_values(
        by=["Flight Sort", "Numero Voo SSIM", "SSIM Start DT", "Etapa Sort"]
    )

    for _, row in df_sorted.iterrows():
        numero_voo = normalizar_texto(row["Numero Voo SSIM"]) or "0"
        etapa = normalizar_texto(row["Etapa SSIM"]) or "01"

        if numero_voo not in flight_date_counter:
            flight_date_counter[numero_voo] = 0
        if etapa == "01":
            flight_date_counter[numero_voo] += 1

        date_counter = flight_date_counter[numero_voo]
        numero_voo_padded = numero_voo.zfill(4)
        eight_char_field = f"{numero_voo_padded}{str(date_counter).zfill(2)}{etapa}"
        numero_voo_display = numero_voo.rjust(5)

        origem = normalizar_texto(row["Origem IATA"]) or normalizar_texto(row["Base Origem"])
        destino = normalizar_texto(row["Destino IATA"]) or normalizar_texto(row["Base Destino"])
        origem_tz = format_timezone_offset(row["Origem TZ"])
        destino_tz = format_timezone_offset(row["Destino TZ"])
        equipamento = normalizar_texto(row["Equipamento SSIM"])[:3]

        linha_3 = (
            f"3 "
            f"{codigo_iata:<2} "
            f"{eight_char_field}"
            f"{normalizar_texto(row['Status SSIM'])}"
            f"{normalizar_texto(row['SSIM Start'])}"
            f"{normalizar_texto(row['SSIM End'])}"
            f"{formatar_frequencia_ssim(row['Frequencia SSIM'])}"
            f" "
            f"{origem:<3}"
            f"{normalizar_texto(row['Partida Local'])}"
            f"{normalizar_texto(row['Partida Local'])}"
            f"{origem_tz}"
            f"  "
            f"{destino:<3}"
            f"{normalizar_texto(row['Chegada Local'])}"
            f"{normalizar_texto(row['Chegada Local'])}"
            f"{destino_tz}"
            f"  "
            f"{equipamento:<3}"
            f"{' ':53}"
            f"{codigo_iata:<2}"
            f"{' ':7}"
            f"{codigo_iata:<2}"
            f"{numero_voo_display}"
            f"{' ':28}"
            f"{' ':6}"
            f"{' ':5}"
            f"{' ':9}"
            f"{numero_linha:08}"
        )
        lines.append(ajustar_linha(linha_3))
        numero_linha += 1

    for _ in range(4):
        lines.append("0" * 200)
        numero_linha += 1

    linha_5_conteudo = f"5 {codigo_iata} {data_emissao}"
    numero_linha_str = f"{numero_linha + 1:06}"
    numero_linha_str2 = f"{numero_linha:06}E"
    linha_5 = linha_5_conteudo + (
        " " * (200 - len(linha_5_conteudo) - len(numero_linha_str) - len(numero_linha_str2))
    )
    linha_5 += numero_linha_str2 + numero_linha_str
    lines.append(linha_5)

    return output_file, "\n".join(lines)


def main():
    st.set_page_config(page_title="Gerador de Arquivo SSIM", page_icon="âœˆï¸", layout="wide")
    st.title("Gerador de Arquivo SSIM")
    st.caption("Fonte: SIROS")

    col_refresh, col_info = st.columns([1, 4])
    with col_refresh:
        if st.button("Atualizar base"):
            carregar_base_siros.clear()
            st.rerun()
    with col_info:
        st.info("Base publica do SIROS")

    with st.spinner("Carregando base do SIROS..."):
        try:
            df = carregar_base_siros()
        except Exception as exc:
            st.error(f"Erro ao carregar a base do SIROS: {exc}")
            return

    if df.empty:
        st.warning("A fonte do SIROS nao retornou registros utilizaveis.")
        return

    clientes = construir_opcoes_clientes(df)
    cliente_codigo = st.selectbox(
        "Companhia aerea",
        options=list(clientes.keys()),
        format_func=lambda value: clientes[value],
    )

    client_df = df[df["Cod. Empresa"] == cliente_codigo].copy()
    aeroportos = construir_opcoes_aeroportos(client_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        aeroportos_selecionados = st.multiselect(
            "Aeroportos",
            options=list(aeroportos.keys()),
            default=[],
            format_func=lambda value: aeroportos[value],
            help="Se nenhum aeroporto for selecionado, todos os aeroportos da companhia entram no SSIM.",
        )
    with col2:
        min_date = client_df["Inicio Operacao DT"].min().date()
        max_date = client_df["Fim Operacao DT"].max().date()
        default_start = max(min_date, min(date.today(), max_date))
        data_inicio = st.date_input(
            "Data inicial",
            value=default_start,
            min_value=min_date,
            max_value=max_date,
        )
    with col3:
        default_end = min(max_date, default_start + timedelta(days=30))
        data_fim = st.date_input(
            "Data final",
            value=default_end,
            min_value=min_date,
            max_value=max_date,
        )

    if data_inicio > data_fim:
        st.error("A data inicial nao pode ser maior que a data final.")
        return

    filtered = filtrar_registros(df, cliente_codigo, aeroportos_selecionados, data_inicio, data_fim)

    resolved_iata = normalizar_texto(client_df["Cliente IATA"].iloc[0]) if not client_df.empty else ""
    if resolved_iata:
        st.caption(f"Codigo IATA da companhia para o SSIM: `{resolved_iata}`")
        codigo_iata = resolved_iata
    else:
        codigo_iata = st.text_input(
            "Codigo IATA da companhia",
            max_chars=2,
            help="Preenchimento manual usado apenas quando nao houver mapeamento ICAO -> IATA.",
        ).upper()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registros na base", f"{len(df):,}")
    with col2:
        st.metric("Registros da companhia", f"{len(client_df):,}")
    with col3:
        st.metric("Registros filtrados", f"{len(filtered):,}")
    with col4:
        st.metric("Aeroportos disponiveis", len(aeroportos))

    preview_columns = [
        "Empresa",
        "Cliente IATA",
        "No Voo",
        "Base Origem",
        "Base Destino",
        "SSIM Start",
        "SSIM End",
        "Frequencia SSIM",
        "Partida Local",
        "Chegada Local",
        "Status SSIM",
    ]

    if not filtered.empty:
        preview_df = filtered[preview_columns].head(50).rename(
            columns={
                "Cliente IATA": "IATA",
                "Base Origem": "Aeroporto Origem",
                "Base Destino": "Aeroporto Destino",
            }
        )
        st.dataframe(preview_df, use_container_width=True)
    else:
        st.warning("Nenhum registro encontrado com os filtros selecionados.")

    if st.button("Gerar Arquivo SSIM", type="primary", use_container_width=True):
        if not codigo_iata or len(codigo_iata) != 2:
            st.error("Nao foi possivel determinar um codigo IATA valido para a companhia.")
            return

        if filtered.empty:
            st.error("Nao ha registros para gerar o SSIM com os filtros atuais.")
            return

        try:
            output_file, ssim_content = gerar_ssim(filtered, codigo_iata)
        except Exception as exc:
            st.error(f"Erro ao gerar o SSIM: {exc}")
            return

        st.success(f"Arquivo SSIM gerado: {output_file}")

        ssim_lines = ssim_content.splitlines()
        flight_lines = [line for line in ssim_lines if line.startswith("3 ")]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Linhas SSIM", len(ssim_lines))
        with col2:
            st.metric("Linhas de voo", len(flight_lines))
        with col3:
            st.metric(
                "Validacao 200 chars",
                "OK" if all(len(line) == 200 for line in ssim_lines) else "Falha",
            )

        st.download_button(
            label="Baixar Arquivo SSIM",
            data=ssim_content.encode("utf-8"),
            file_name=output_file,
            mime="text/plain",
        )

        st.code("\n".join(ssim_lines[:20]), language="text")


if __name__ == "__main__":
    main()

