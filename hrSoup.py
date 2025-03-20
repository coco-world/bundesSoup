import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

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

# Browser starten und Seite öffnen
driver = create_driver()
driver.get("https://www.handelsregister.de/rp_web/welcome.xhtml")
wait = WebDriverWait(driver, 15)

# 1. Klicke auf den "Erweiterte Suche"-Button
advanced_search = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[@title='Erweiterte Suche']")
))
advanced_search.click()

# 2. Warte, bis das Suchformular sichtbar ist und gebe im Textarea (Firma/Schlagwörter) ein "a" ein
schlagwoerter = wait.until(EC.visibility_of_element_located((By.ID, "form:schlagwoerter")))
schlagwoerter.clear()
schlagwoerter.send_keys("a")

# 3. Wähle in der Rechtsform den Eintrag "eingetragener Verein" aus
#    (In diesem Fall hat das <option>-Element den Wert "3")
rechtsform_select_elem = wait.until(EC.presence_of_element_located((By.ID, "form:rechtsform_input")))
select_rechtsform = Select(rechtsform_select_elem)
select_rechtsform.select_by_value("3")

# 4. Klicke auf den Suchen-Button
search_button = wait.until(EC.element_to_be_clickable((By.ID, "form:btnSuche")))
search_button.click()

# 5. Warte, bis die Ergebnisliste geladen ist (identifiziert durch das <tbody>-Element)
table_body = wait.until(EC.presence_of_element_located(
    (By.ID, "ergebnissForm:selectedSuchErgebnisFormTable_data")
))

# 6. Extrahiere aus jedem Ergebnis den Firmennamen.
#    In diesem Beispiel nehmen wir an, dass der Name in einem <span> mit der Klasse "marginLeft20" steht.
results = []
rows = table_body.find_elements(By.XPATH, "./tr")
for row in rows:
    try:
        # Suche in jedem Resultat nach dem <span>, in dem der Firmenname enthalten ist
        name_element = row.find_element(By.XPATH, ".//span[contains(@class, 'marginLeft20')]")
        name = name_element.text.strip()
        if name:
            results.append(name)
    except Exception as e:
        # Falls ein Eintrag diese Struktur nicht hat, wird er übersprungen.
        continue

# 7. Schreibe die extrahierten Namen in eine CSV-Datei (Spalte "name")
with open("results.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["name"])  # Header
    for name in results:
        writer.writerow([name])

print("Ergebnisse wurden in 'results.csv' gespeichert.")
driver.quit()
