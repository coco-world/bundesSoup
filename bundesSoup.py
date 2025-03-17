import time
import csv
import re
import math
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

def scrape_page(driver):
    """
    Extrahiert von der aktuell geladenen Seite die gewünschten Daten.
    Der HTML-Code wird mit BeautifulSoup geparst.
    """
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    # Suche nach der ul-Liste, die die Ergebnisse enthält
    ul = soup.find("ul", class_="bt-suche-results")
    if not ul:
        print("Keine Ergebnisse gefunden.")
        return []
    
    li_items = ul.find_all("li")
    results = []
    
    for li in li_items:
        table = li.find("table", class_="table")
        if not table:
            continue
        
        # Standardwerte initialisieren
        nachname = ""
        vorname = ""
        fraktion = ""
        emailadresse = ""
        zugehoerig = ""
        
        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue
            header = th.get_text(strip=True)
            value = td.get_text(strip=True)
            
            if header == "Nachname":
                nachname = value
            elif header == "Vorname":
                vorname = value
            elif header == "Fraktion/Gruppe":
                fraktion = value
            elif header == "E-Mail Adresse":
                emailadresse = value
            elif header == "Zugehörig zu":
                zugehoerig = value
        
        retrieval_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results.append({
            "nachname": nachname,
            "vorname": vorname,
            "fraktion": fraktion,
            "emailadresse": emailadresse,
            "zugehoerig": zugehoerig,
            "retrieval_date": retrieval_date
        })
    
    return results

def main():
    driver = create_driver()
    
    # Basis-URL der Suchseite
    url = "https://www.bundestag.de/dokumente/adressbuch?surname=&firstname=&fraction=&email=*%40*&associatedTo=&doSearch"
    print(f"[*] Zugriff auf die Seite: {url}")
    driver.get(url)
    
    # Warten, damit die Seite vollständig geladen wird
    time.sleep(3)
    
    # Auslesen der Gesamtanzahl der Fundstellen aus dem HTML
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    num_fundstellen = None
    # Suche nach dem p-Tag mit der Klasse "bt-fake-label" und dem Text "Anzahl der Fundstellen:"
    p_tags = soup.find_all("p", class_="bt-fake-label")
    for p in p_tags:
        text = p.get_text(strip=True)
        if "Anzahl der Fundstellen:" in text:
            # Beispieltext: "Anzahl der Fundstellen: 1173:"
            match = re.search(r"Anzahl der Fundstellen:\s*(\d+)", text)
            if match:
                num_fundstellen = int(match.group(1))
                break
    
    if num_fundstellen is None:
        print("Anzahl der Fundstellen konnte nicht ausgelesen werden!")
        driver.quit()
        return
    else:
        # Berechne die Seitenzahl (5 Ergebnisse pro Seite)
        pages = math.ceil(num_fundstellen / 5)
        print(f"Anzahl der Fundstellen: {num_fundstellen}. Anzahl der Seiten: {pages}")
    
    all_data = []
    
    # Jetzt wird über alle Seiten iteriert (hier: 'pages' Seiten)
    for page in range(1, pages + 1):
        print(f"Verarbeite Seite {page}")
        time.sleep(3)  # Warten, damit die Seite vollständig geladen wird
        
        # Daten der aktuellen Seite extrahieren
        page_data = scrape_page(driver)
        all_data.extend(page_data)
        
        # Falls nicht die letzte Seite: Next-Button klicken
        if page < pages:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.bt-paginierung__button--next"))
                )
                # Scrolle den Button in den sichtbaren Bereich
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                # Klicke per JavaScript, um den "element not clickable"-Fehler zu umgehen
                driver.execute_script("arguments[0].click();", next_button)
                print("Next-Button geklickt.")
            except Exception as e:
                print("Fehler beim Klicken des Next-Buttons:", e)
                break
    
    driver.quit()
    
    print("Gefundene Datensätze:")
    for entry in all_data:
        print(entry)
    
    # Ergebnisse in eine CSV-Datei schreiben
    csv_fieldnames = ["nachname", "vorname", "fraktion", "emailadresse", "zugehoerig", "retrieval_date"]
    with open("bundestag_adressbuch.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
    
    print("Fertig. Daten wurden in 'bundestag_adressbuch.csv' gespeichert.")

if __name__ == "__main__":
    main()
