import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup


# Function to interact with Bing Chat


def search_bing(query):
    options = Options()
    options.add_argument(
        "--user-data-dir=C:\\Users\DELL\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default")
    options.add_argument("--lang=en")

    driver = webdriver.Edge(options=options)
    driver.get("https://www.bing.com/search?q=Bing+AI&showconv=1&sydconv=1")
    time.sleep(10)

    search_box = driver.find_element(
        By.XPATH, "/html/body/div[1]/cib-serp//cib-action-bar//div/div[2]/div[2]")



    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(5)
    results = driver.page_source
    driver.quit()

    return results

# Function to parse Bing Chat response


def parse_response(html):
    soup = BeautifulSoup(html, "html.parser")
    response_elements = soup.find_all(
        "div", {"class": "content"})

    # Initialize an empty list to store the scraped responses
    scraped_responses = []

    for element in response_elements:
        # Extract the text from the element and add it to the list
        response_text = element.get_text().strip()
        scraped_responses.append(response_text)

    # Join the scraped responses into a single string (you can adjust this based on your requirement)
    final_response = "\n".join(scraped_responses)

    return final_response


# Function to authenticate with Google Sheets
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope)
    client = gspread.authorize(creds)
    return client


# Main function
def main():
    # Authenticate with Google Sheets
    gs_client = authenticate_google_sheets()

    # Open the Google Sheet (replace 'YourSheetName' with the actual name of your sheet)
    sheet = gs_client.open_by_url(
        "1https://docs.google.com/spreadsheets/d/1Ci51Di-w7FaR1DnzSXsL-rS0tQUxEcJRuoaXvYeIKqA/edit?usp=sharing").sheet1

    # Read search queries from Google Sheets (assuming they are in column A starting from row 2)
    queries = sheet.col_values(1)[1:]  # Ignore the header row

    # Scrape responses and write them back to Google Sheets
    for query in queries:
        response = search_bing(query)
        scraped_response = parse_response(response)

        # Write the scraped response to Google Sheets (in column B next to the corresponding query)
        # Adding 2 to account for the header row and 0-indexing
        row_number = queries.index(query) + 2
        sheet.update_cell(row_number, 2, scraped_response)


if __name__ == "__main__":
    main()
