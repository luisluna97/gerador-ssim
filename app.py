import streamlit as st
import pandas as pd
from datetime import datetime
import os

def ajustar_linha(line, comprimento=200):
    return line.ljust(comprimento)[:comprimento]

def determinar_dia_semana(data):
    dias_semana = ["1", "2", "3", "4", "5", "6", "7"]  # Segunda a Domingo
    dia_semana = datetime.strptime(data, "%d/%m/%Y").weekday()
    frequencia = [" "] * 7
    frequencia[dia_semana] = dias_semana[dia_semana]
    return "".join(frequencia)

def determinar_status(tipo):
    return "J" if "regular" in tipo.lower() else "F"

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

        # Carregar o arquivo de mapeamento de aeronaves (arquivo Excel)
        dtype_dict = {'ICAO': str, 'IATA': str}
        aircraft_df = pd.read_excel('ACT TYPE.xlsx', dtype=dtype_dict)
        aircraft_df['ICAO'] = aircraft_df['ICAO'].str.strip().str.upper()
        aircraft_df['IATA'] = aircraft_df['IATA'].str.strip()

        # Criar o dicionário de mapeamento
        icao_to_iata_aircraft = dict(zip(aircraft_df['ICAO'], aircraft_df['IATA']))

        # Determinar datas mínima e máxima no CSV
        df['Data'] = df['Início'].str.split(" ").str[0]  # Extrair a data da coluna "Início"
        data_min_date = datetime.strptime(df['Data'].min(), "%d/%m/%Y")
        data_max_date = datetime.strptime(df['Data'].max(), "%d/%m/%Y")
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

            # Linha 2
            linha_2_conteudo = f"2U{codigo_iata}  0008    {data_min}{data_max}{data_emissao}Created by dnata capacity"
            posicao_p = 72
            espacos_antes_p = posicao_p - len(linha_2_conteudo) - 1
            linha_2 = linha_2_conteudo + (' ' * espacos_antes_p) + 'P'

            numero_linha_str = f"EN08{numero_linha:09}"
            espacos_restantes = 200 - len(linha_2) - len(numero_linha_str)
            linha_2 += (' ' * espacos_restantes) + numero_linha_str
            file.write(linha_2 + "\n")
            numero_linha += 1

            # Linhas de zeros
            for _ in range(4):
                file.write("0" * 200 + "\n")

            # Linhas 3
            for _, row in df.iterrows():
                data = row['Data']
                frequencia = determinar_dia_semana(data)
                status = determinar_status(row['Tipo'])

                # Converter os códigos dos aeroportos de ICAO para IATA
                origem_icao = row['Origem']
                destino_icao = row['Destino']
                origem = icao_to_iata_airport.get(origem_icao.strip().upper(), origem_icao.strip())
                destino = icao_to_iata_airport.get(destino_icao.strip().upper(), destino_icao.strip())

                partida = row['Partida Prevista'][-5:].replace(":", "")  # Apenas números
                chegada = row['Chegada Prevista'][-5:].replace(":", "")  # Apenas números

                # Ajustar o formato dos horários
                partida = partida.zfill(4)
                chegada = chegada.zfill(4)

                # Converter o código da aeronave de ICAO para IATA
                equipamento_icao = row['Equip'].strip().upper()
                equipamento = icao_to_iata_aircraft.get(equipamento_icao, equipamento_icao)

                # Obter a data de chegada do voo e formatar
                data_chegada = datetime.strptime(data, "%d/%m/%Y").strftime("%d%b%y").upper()

                # Número do voo
                numero_voo = str(row['Voo']).strip()
                numero_voo = numero_voo.rjust(5)  # Preencher com espaços à esquerda até 5 caracteres

                # Número da linha formatado com 8 dígitos
                numero_linha_str = f"{numero_linha:08}"

                # Construção da linha 3
                linha_3 = (
                    f"3 "
                    f"{codigo_iata:<2} "
                    f"10020101"
                    f"{status}"
                    f"{data_chegada}"
                    f"{data_chegada}"
                    f"{frequencia}"
                    f" "
                    f"{origem:<3}"
                    f"{partida}"
                    f"{partida}"
                    f"-0300"
                    f"  "
                    f"{destino:<3}"
                    f"{chegada}"
                    f"{chegada}"
                    f"-0300"
                    f"  "
                    f"{equipamento:<3}"
                    f"{' ':53}"
                    f"{codigo_iata:<2}"
                    f"{' ':7}"
                    f"{codigo_iata:<2}"
                    f"{numero_voo}"
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

            # Linha 5
            numero_linha_str = f"{numero_linha:08}"
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
