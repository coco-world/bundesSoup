import time
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # Für die Element-Suche
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def create_driver():
    """Erzeugt und konfiguriert einen Headless-Chrome-Webdriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Browserfenster unsichtbar
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, wie Gecko) Chrome/112.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=chrome_options)

def main():
    driver = create_driver()
    
    # Basisseite mit der Liste der Buchstaben (z. B. A-Z)
    base_url = "https://www.europarl.europa.eu/meps/de/full-list"
    print(f"[*] Zugriff auf: {base_url}")
    driver.get(base_url)
    
    # Warten, bis das Element mit der Buchstabenliste geladen ist
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.erpl_list-letters"))
    )
    time.sleep(2)
    
    # Buchstaben extrahieren: Nur die LI-Elemente mit einem Link (a-Tag) werden übernommen.
    letter_elements = driver.find_elements(By.CSS_SELECTOR, "ul.erpl_list-letters li.erpl_letter a")
    # Erstelle eine Liste von (Buchstabe, URL)-Tupeln
    letter_links = [(elem.get_attribute("title"), elem.get_attribute("href")) for elem in letter_elements]
    
    print(f"[*] Buchstaben gefunden: {[letter for letter, _ in letter_links]}")
    
    all_data = []
    
    # Für jeden Buchstaben den jeweiligen Link öffnen
    for letter, letter_url in letter_links:
        print(f"\n[*] Verarbeite Buchstabe {letter}: {letter_url}")
        driver.get(letter_url)
        # Warten, bis der Container mit den MEP-Karten geladen ist
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.erpl_member-list"))
        )
        time.sleep(2)
        
        # Alle MEP-Karten auf dieser Seite finden
        mep_cards = driver.find_elements(By.CSS_SELECTOR, "div.erpl_member-list-item a.erpl_member-list-item-content")
        links = [elem.get_attribute("href") for elem in mep_cards if elem.get_attribute("href")]
        print(f"[*] {len(links)} MEPs für Buchstabe {letter} gefunden.")
        
        # Für jeden gefundenen MEP-Link wird die Detailseite aufgerufen und ausgelesen
        for idx, link in enumerate(links, start=1):
            print(f"[*] {letter} - Bearbeite {idx}/{len(links)}: {link}")
            driver.get(link)
            
            # Warten, bis das Namenselement auf der Detailseite sichtbar ist
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.sln-member-name"))
            )
            time.sleep(2)
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            
            # Felder extrahieren
            name_elem = soup.find("span", class_="sln-member-name")
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            group_elem = soup.find("h3", class_="erpl_title-h3 mt-1 sln-political-group-name")
            group = group_elem.get_text(strip=True) if group_elem else ""
            
            role_elem = soup.find("p", class_="sln-political-group-role")
            role = role_elem.get_text(strip=True) if role_elem else ""
            
            email_elem = soup.find("a", class_="link_email")
            email = email_elem.get("href").replace("mailto:", "") if email_elem and email_elem.get("href") else ""
            
            twitter_elem = soup.find("a", class_="link_twitt")
            twitter = twitter_elem.get("href") if twitter_elem else ""
            
            insta_elem = soup.find("a", class_="link_instagram")
            insta = insta_elem.get("href") if insta_elem else ""
            
            # Das Land und weitere Infos stehen im gleichen Container, hier wird der Text vor dem Bindestrich genutzt
            country_elem = soup.find("div", class_="erpl_title-h3 mt-1 mb-1")
            country_text = country_elem.get_text(strip=True) if country_elem else ""
            country = country_text.split("-")[0].strip() if "-" in country_text else country_text
            
            time_elem = soup.find("time", class_="sln-birth-date")
            birth = time_elem.get("datetime") if time_elem else ""
            
            birthplace_elem = soup.find("span", class_="sln-birth-place")
            birthplace = birthplace_elem.get_text(strip=True) if birthplace_elem else ""
            
            retrieval_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            all_data.append({
                "letter": letter,
                "name": name,
                "group": group,
                "role": role,
                "email": email,
                "twitter": twitter,
                "insta": insta,
                "country": country,
                "birth": birth,
                "birthplace": birthplace,
                "retrieval_date": retrieval_date
            })
    
    driver.quit()
    
    # Ergebnisse in eine CSV-Datei schreiben
    csv_fieldnames = ["letter", "name", "group", "role", "email", "twitter", "insta", "country", "birth", "birthplace", "retrieval_date"]
    with open("europarl_meps.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
    
    print("Fertig. Daten wurden in 'europarl_meps.csv' gespeichert.")

if __name__ == "__main__":
    main()
