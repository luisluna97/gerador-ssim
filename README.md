# Gerador de Arquivo SSIM

Esta aplicação converte arquivos de malha aérea fornecidos pela **ANAC** (Agência Nacional de Aviação Civil) através do sistema **SIROS** em arquivos no formato **SSIM**, padrão utilizado pela indústria aeronáutica para troca de informações de horários de voos.

[GERADOR DE ARQUIVO SSIM](https://gerador-ssim-me42pp9k4m78esyvgvreyw.streamlit.app/)

## **O que é o SIROS?**

O SIROS (Sistema de Registro de Operações de Transporte Aéreo) é um sistema da ANAC onde as companhias aéreas registram suas operações de voos regulares e não regulares no Brasil. Mais informações podem ser encontradas no site oficial:

[SIROS - ANAC](https://siros.anac.gov.br/SIROS/view/registro/frmConsultaVoos)

## **Como funciona a aplicação?**

1. **Entrada de Dados:**
   - **Método de Seleção da Companhia Aérea:**
     - **Selecionar por País e Companhia Aérea:** Permite que o usuário selecione o país e a companhia aérea desejada a partir de listas.
     - **Inserir código IATA manualmente:** Permite que o usuário digite diretamente o código IATA de 2 letras da companhia aérea.
   - **Upload do Arquivo de Malha CSV:**
     - O usuário faz o upload do arquivo CSV contendo os dados de voos obtidos do SIROS.

2. **Processamento:**
   - A aplicação converte os dados do arquivo CSV para o formato SSIM, realizando mapeamentos necessários, como códigos de aeroportos e aeronaves.

3. **Saída de Dados:**
   - Gera um arquivo SSIM compatível com os padrões da indústria.
   - O arquivo gerado pode ser baixado diretamente através da aplicação.

## **Como utilizar a aplicação?**

1. **Acesse a aplicação online:** [GERADOR DE ARQUIVO SSIM](https://gerador-ssim-me42pp9k4m78esyvgvreyw.streamlit.app/)

2. **Selecione o método para informar a companhia aérea:**
   - **Por País e Companhia Aérea:** Selecione o país e, em seguida, a companhia aérea.
   - **Código IATA Manualmente:** Digite o código IATA de 2 letras da companhia aérea.

3. **Faça o upload do arquivo de malha CSV:**
   - O arquivo deve estar no formato CSV e seguir o padrão fornecido pelo SIROS.

4. **Gerar o Arquivo SSIM:**
   - Clique em **"Gerar Arquivo SSIM"**.
   - Aguarde o processamento.

5. **Baixar o Arquivo Gerado:**
   - Após o processamento, um botão para download aparecerá.
   - Clique em **"Baixar Arquivo SSIM"** para salvar o arquivo no seu computador.

## **Requisitos do Arquivo CSV:**

- O arquivo deve ser exportado do SIROS no formato CSV.
- Deve conter as colunas necessárias para o processamento, como:
  - **Início**
  - **Origem**
  - **Destino**
  - **Partida Prevista**
  - **Chegada Prevista**
  - **Equip**
  - **Voo**
  - **Tipo**

## **Informações Adicionais:**

- **Segurança dos Dados:**
  - Nenhum dado enviado é armazenado em nossos servidores.
  - Todo o processamento é realizado em tempo real e os dados são descartados após o uso.
  - O campo "Voo seguinte" apenas repete o voo atual, pois não conseguimos extrair tal informação na malha disponibilizada pela ANAC.

- **Suporte:**
  - Em caso de dúvidas ou problemas, entre em contato com luis.luna@ufpe.br.

## **Sobre o SSIM:**

O **SSIM** (Standard Schedules Information Manual) é um padrão internacional desenvolvido pela **IATA** (International Air Transport Association) para o intercâmbio de informações de horários de voos entre companhias aéreas, aeroportos e outros stakeholders da indústria.

---

**Nota:** Esta aplicação foi desenvolvida para facilitar o processo de conversão de dados do SIROS para o formato SSIM, agilizando a comunicação e a integração de informações no setor aeronáutico.

