import streamlit as st
import pandas as pd
from datetime import datetime
import os

def ajustar_linha(line, comprimento=200):
    return line.ljust(comprimento)[:comprimento]

def determinar_dia_semana(data_hora):
    # Extrair o dia da semana da data_hora
    dia_semana = data_hora.weekday()
    dias_semana = ["1", "2", "3", "4", "5", "6", "7"]  # Segunda a Domingo
    frequencia = [" "] * 7
    frequencia[dia_semana] = dias_semana[dia_semana]
    return "".join(frequencia)

def determinar_status(tipo):
    tipo_lower = tipo.lower()
    if "regular" in tipo_lower and "carga" not in tipo_lower:
        return "J"
    else:
        return "F"

def format_timezone_offset(offset_str):
    try:
        offset = float(offset_str)
        hours = int(offset)
        minutes = int(abs(offset - hours) * 60)
        if offset >= 0:
            sign = '+'
        else:
            sign = '-'
            hours = -hours  # tornar horas positivas
        offset_formatted = f"{sign}{hours:02}{minutes:02}"
        return offset_formatted
    except ValueError:
        # Se o offset não for um número, definir como '+0000'
        return '+0000'

def gerar_ssim(csv_path, codigo_iata, output_file=None):
    try:
        # Ler o arquivo CSV
        df = pd.read_csv(csv_path, delimiter=';', encoding='latin1')
        df.columns = df.columns.str.strip()  # Remove espaços nos nomes das colunas

        # Carregar o arquivo de mapeamento de aeroportos
        airport_df = pd.read_csv('airport.csv')
        airport_df['ICAO'] = airport_df['ICAO'].str.strip().str.upper()
        airport_df['IATA'] = airport_df['IATA'].str.strip().str.upper()
        icao_to_iata_airport = dict(zip(airport_df['ICAO'], airport_df['IATA']))

        # Criar o dicionário de mapeamento de timezone
        airport_df['Timezone'] = airport_df['Timezone'].astype(str).str.strip()
        icao_to_timezone = dict(zip(airport_df['ICAO'], airport_df['Timezone']))

        # Carregar o arquivo de mapeamento de aeronaves (arquivo Excel)
        dtype_dict = {'ICAO': str, 'IATA': str}
        aircraft_df = pd.read_excel('ACT TYPE.xlsx', dtype=dtype_dict)
        aircraft_df['ICAO'] = aircraft_df['ICAO'].str.strip().str.upper()
        aircraft_df['IATA'] = aircraft_df['IATA'].str.strip()

        # Criar o dicionário de mapeamento
        icao_to_iata_aircraft = dict(zip(aircraft_df['ICAO'], aircraft_df['IATA']))

        # Converter as colunas de data/hora para datetime
        df['Partida_Prevista_DH'] = pd.to_datetime(df['Partida Prevista'], format="%d/%m/%Y %H:%M")
        df['Chegada_Prevista_DH'] = pd.to_datetime(df['Chegada Prevista'], format="%d/%m/%Y %H:%M")

        # Determinar datas mínima e máxima no CSV
        data_min_date = df['Partida_Prevista_DH'].dt.date.min()
        data_max_date = df['Chegada_Prevista_DH'].dt.date.max()
        data_min = data_min_date.strftime("%d%b%y").upper()
        data_max = data_max_date.strftime("%d%b%y").upper()
        data_emissao = datetime.now().strftime("%d%b%y").upper()

        # Definir o nome do arquivo de saída
        if output_file is None:
            output_file = f"Malha SSIM {codigo_iata} {data_min}.{data_max}{data_emissao}.ssim"

        # Criar o arquivo SSIM
        with open(output_file, 'w') as file:
            numero_linha = 1

            # Linha 1
            numero_linha_str = f"{numero_linha:08}"
            linha_1_conteudo = "1AIRLINE STANDARD SCHEDULE DATA SET"
            espacos_necessarios = 200 - len(linha_1_conteudo) - len(numero_linha_str)
            linha_1 = linha_1_conteudo + (' ' * espacos_necessarios) + numero_linha_str
            file.write(linha_1 + "\n")
            numero_linha += 1

            # Linhas de zeros
            for _ in range(4):
                file.write("0" * 200 + "\n")
                numero_linha += 1

            # Linha 2
            linha_2_conteudo = f"2U{codigo_iata}  0008    {data_min}{data_max}{data_emissao}Created by dnata capacity"
            posicao_p = 72
            espacos_antes_p = posicao_p - len(linha_2_conteudo) - 1
            linha_2 = linha_2_conteudo + (' ' * espacos_antes_p) + 'P'

            # Ajuste conforme solicitado
            numero_linha_str = f" EN08{numero_linha:08}"
            espacos_restantes = 200 - len(linha_2) - len(numero_linha_str)
            linha_2 += (' ' * espacos_restantes) + numero_linha_str
            file.write(linha_2 + "\n")
            numero_linha += 1

            # Linhas de zeros
            for _ in range(4):
                file.write("0" * 200 + "\n")
                numero_linha += 1

            # Inicializar os contadores
            flight_counters = {}
            date_counters = {}

            # Ordenar o DataFrame para garantir a ordem correta
            df_sorted = df.sort_values(by=['Voo', 'Partida_Prevista_DH'])

            # Linhas 3
            for _, row in df_sorted.iterrows():
                partida_prevista_dh = row['Partida_Prevista_DH']
                chegada_prevista_dh = row['Chegada_Prevista_DH']

                frequencia = determinar_dia_semana(partida_prevista_dh)
                status = determinar_status(row['Tipo'])

                # Converter os códigos dos aeroportos de ICAO para IATA
                origem_icao = row['Origem'].strip().upper()
                destino_icao = row['Destino'].strip().upper()
                origem = icao_to_iata_airport.get(origem_icao, origem_icao)
                destino = icao_to_iata_airport.get(destino_icao, destino_icao)

                # Obter o timezone dos aeroportos
                origem_timezone_offset_str = icao_to_timezone.get(origem_icao, '0')  # Padrão '0' se não encontrado
                destino_timezone_offset_str = icao_to_timezone.get(destino_icao, '0')  # Padrão '0' se não encontrado

                # Formatar os timezones
                origem_timezone_formatted = format_timezone_offset(origem_timezone_offset_str)
                destino_timezone_formatted = format_timezone_offset(destino_timezone_offset_str)

                # Extrair horários de partida e chegada
                partida = partida_prevista_dh.strftime("%H%M")
                chegada = chegada_prevista_dh.strftime("%H%M")

                # Converter o código da aeronave de ICAO para IATA
                equipamento_icao = row['Equip'].strip().upper()
                equipamento = icao_to_iata_aircraft.get(equipamento_icao, equipamento_icao)

                # Obter as datas de partida e chegada formatadas
                data_partida = partida_prevista_dh.strftime("%d%b%y").upper()
                data_chegada = chegada_prevista_dh.strftime("%d%b%y").upper()

                # Número do voo
                numero_voo = str(row['Voo']).strip()

                # Número do voo preenchido com zeros à esquerda até 4 dígitos
                numero_voo_padded = numero_voo.zfill(4)

                # Chave para o voo (número do voo)
                flight_key = numero_voo_padded

                # Chave para o voo e data
                flight_date_key = (numero_voo_padded, partida_prevista_dh.date())

                # Atualizar o contador de data para este número de voo
                if flight_key not in date_counters:
                    date_counters[flight_key] = 1
                else:
                    # Incrementa o contador de data apenas se a data atual for diferente da última
                    last_date = date_counters[flight_key + '_last_date']
                    if partida_prevista_dh.date() != last_date:
                        date_counters[flight_key] += 1

                # Atualizar a última data processada para este voo
                date_counters[flight_key + '_last_date'] = partida_prevista_dh.date()

                # Obter o valor do contador de data e formatar com dois dígitos
                date_counter = str(date_counters[flight_key]).zfill(2)

                # Atualizar o contador de ocorrência para este número de voo e data
                if flight_date_key not in flight_counters:
                    flight_counters[flight_date_key] = 1
                else:
                    flight_counters[flight_date_key] += 1

                # Obter o valor do contador de ocorrência e formatar com dois dígitos
                occurrence_counter = str(flight_counters[flight_date_key]).zfill(2)

                # Construir o campo de 8 caracteres
                eight_char_field = f"{numero_voo_padded}{date_counter}{occurrence_counter}"

                # Número do voo para exibição (preenchido com espaços à direita até 5 caracteres)
                numero_voo_display = numero_voo.rjust(5)

                # Número da linha formatado com 8 dígitos
                numero_linha_str = f"{numero_linha:08}"

                # Construção da linha 3
                linha_3 = (
                    f"3 "
                    f"{codigo_iata:<2} "
                    f"{eight_char_field}"
                    f"{status}"
                    f"{data_partida}"
                    f"{data_chegada}"
                    f"{frequencia}"
                    f" "
                    f"{origem:<3}"
                    f"{partida}"
                    f"{partida}"
                    f"{origem_timezone_formatted}"
                    f"  "
                    f"{destino:<3}"
                    f"{chegada}"
                    f"{chegada}"
                    f"{destino_timezone_formatted}"
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
                    f"{numero_linha_str}"
                )

                # Garantir que a linha tenha exatamente 200 caracteres
                linha_3 = linha_3.ljust(200)

                file.write(linha_3 + "\n")
                numero_linha += 1

            # Linhas de zeros
            for _ in range(4):
                file.write("0" * 200 + "\n")
                numero_linha += 1

            # Ajuste para a penúltima linha
            penultima_linha_numero = f"{numero_linha - 1:06}E"
            # A linha anterior já foi escrita no loop, aqui apenas atualizamos o número

            # Linha 5
            numero_linha_str = f"{numero_linha:06}"
            linha_5_conteudo = f"5 {codigo_iata} {data_emissao}"
            espacos_necessarios = 200 - len(linha_5_conteudo) - len(numero_linha_str)
            linha_5 = linha_5_conteudo + (' ' * espacos_necessarios) + numero_linha_str
            file.write(linha_5 + "\n")
            numero_linha += 1

            st.success(f"Arquivo SSIM gerado: {output_file}")

            # Oferecer o arquivo para download
            with open(output_file, 'rb') as f:
                st.download_button(
                    label="Baixar Arquivo SSIM",
                    data=f,
                    file_name=output_file,
                    mime='text/plain'
                )

        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar o arquivo SSIM:\n{e}")

# Interface Streamlit

st.title("Gerador de Arquivo SSIM")

# Carregar a lista de companhias aéreas
airlines_df = pd.read_csv('iata_airlines.csv')

# Opção para selecionar o método de entrada
metodo_selecao = st.radio("Selecione o método para informar o código IATA da companhia aérea:",
                          ("Selecionar por País e Companhia Aérea", "Inserir código IATA manualmente"))

if metodo_selecao == "Selecionar por País e Companhia Aérea":
    # Opções de filtro
    paises = airlines_df['Country / Territory'].dropna().unique()
    paises = sorted(paises)

    pais_selecionado = st.selectbox("Selecione o País / Território:", ["Todos"] + list(paises))

    if pais_selecionado != "Todos":
        airlines_df_filtrado = airlines_df[airlines_df['Country / Territory'] == pais_selecionado]
    else:
        airlines_df_filtrado = airlines_df

    companhias = airlines_df_filtrado['Airline Name'].dropna().unique()
    companhias = sorted(companhias)

    companhia_selecionada = st.selectbox("Selecione a Companhia Aérea:", companhias)

    # Obter o código IATA da companhia selecionada
    codigo_iata = airlines_df_filtrado[airlines_df_filtrado['Airline Name'] == companhia_selecionada]['IATA Designator'].values[0]

    st.write(f"Código IATA selecionado: {codigo_iata}")

elif metodo_selecao == "Inserir código IATA manualmente":
    codigo_iata = st.text_input("Digite o código IATA da companhia aérea (2 caracteres):").upper()

    if not codigo_iata or len(codigo_iata) != 2:
        st.warning("Por favor, insira um código IATA válido de 2 caracteres.")

# Upload do arquivo de malha CSV
csv_file = st.file_uploader("Faça o upload do arquivo de malha CSV:", type=['csv'])

if st.button("Gerar Arquivo SSIM"):
    if not csv_file:
        st.warning("Por favor, faça o upload do arquivo de malha CSV.")
    elif metodo_selecao == "Inserir código IATA manualmente" and (not codigo_iata or len(codigo_iata) != 2):
        st.warning("Por favor, insira um código IATA válido de 2 caracteres.")
    else:
        # Salvar o arquivo CSV no disco
        csv_path = 'malha.csv'
        with open(csv_path, 'wb') as f:
            f.write(csv_file.getbuffer())

        gerar_ssim(csv_path, codigo_iata)
