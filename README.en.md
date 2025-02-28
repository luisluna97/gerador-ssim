# SSIM File Generator

This application converts airline schedule files provided by **ANAC** (Brazil’s National Civil Aviation Agency) through the **SIROS** system into files in the **SSIM** format, which is the standard used in the aviation industry for exchanging flight schedule information.

[SSIM FILE GENERATOR](https://gerador-ssim-me42pp9k4m78esyvgvreyw.streamlit.app/)

## What is SIROS?

SIROS (Air Transport Operations Registration System) is an ANAC system where airlines register their scheduled and non-scheduled flight operations in Brazil. More information can be found on the official website:

[SIROS - ANAC](https://siros.anac.gov.br/SIROS/view/registro/frmConsultaVoos)

## How does the application work?

1. **Data Input:**
   - **Airline Selection Method:**
     - **Select by Country and Airline:** Allows the user to choose the desired country and airline from lists.
     - **Manually Enter IATA Code:** Allows the user to type the 2-letter IATA code of the airline.
   - **Upload CSV Schedule File:**
     - The user uploads a CSV file containing flight data obtained from SIROS.

2. **Processing:**
   - The application converts the CSV data into the SSIM format, performing necessary mappings such as converting airport codes from ICAO (4 letters) to IATA (3 letters) using a separate mapping file, and adjusting flight times.

3. **Data Output:**
   - Generates an SSIM file that complies with industry standards.
   - The generated file can be downloaded directly through the application.

## How to Use the Application?

1. **Access the Online Application:** [SSIM FILE GENERATOR](https://gerador-ssim-me42pp9k4m78esyvgvreyw.streamlit.app/)
2. **Select the Airline Input Method:**
   - **By Country and Airline:** Select the country and then the airline.
   - **Manually Enter IATA Code:** Type the 2-letter IATA code of the airline.
3. **Upload the CSV Schedule File:**
   - The file must be exported from SIROS in CSV format and follow the required format.
4. **Generate the SSIM File:**
   - Click **"Generate SSIM File"** and wait for processing.
5. **Download the Generated File:**
   - Once processing is complete, click **"Download SSIM File"** to save the file.

## CSV File Requirements

- The CSV file must be exported from SIROS.
- It should include the necessary columns such as:
  - **Início**
  - **Origem**
  - **Destino**
  - **Partida Prevista**
  - **Chegada Prevista**
  - **Equip**
  - **Voo**
  - **Tipo**

## Additional Information

- **Data Security:**
  - No data is stored on our servers.
  - All processing is performed in real-time, and data is discarded after use.
  - The "Next Flight" field repeats the current flight, as we cannot extract that information from the SIROS file.
- **Support:**
  - For any questions or issues, please contact luis.luna@ufpe.br.

## About SSIM

SSIM (Standard Schedules Information Manual) is an international standard developed by IATA for exchanging flight schedule information among airlines, airports, and other industry stakeholders.

---

**Note:** This application was developed to streamline the conversion of SIROS data to the SSIM format, facilitating communication and data integration in the aviation sector.
