import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Browser starten (sichtbar) und maximieren
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.handelsregister.de/rp_web/welcome.xhtml")
wait = WebDriverWait(driver, 15)

success = False

try:
    # ========================================
    # 1) Erweiterte Suche öffnen
    # ========================================
    advanced_search = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[@title='Erweiterte Suche']"))
    )
    
    # 1a) JS-Klick als erste Methode
    try:
        print("Versuche JavaScript-Klick auf 'Erweiterte Suche'...")
        driver.execute_script("arguments[0].click();", advanced_search)
        print("Erweiterte Suche per JS-Click erfolgreich.")
        success = True
    except Exception as e:
        print(f"JavaScript-Click fehlgeschlagen: {e}")

    # 1b) Hover + normaler Klick (Fallback)
    if not success:
        try:
            print("Versuche Hover + Klick auf 'Erweiterte Suche'...")
            ActionChains(driver).move_to_element(advanced_search).perform()
            time.sleep(1)
            advanced_search.click()
            print("Erweiterte Suche per Hover + Klick erfolgreich.")
            success = True
        except Exception as e:
            print(f"Hover + Klick fehlgeschlagen: {e}")

    # 1c) Direkter JS-Trigger (Fallback)
    if not success:
        try:
            print("Versuche direkten JavaScript-Trigger für 'Erweiterte Suche'...")
            driver.execute_script("PF('sidebar1').hide();PrimeFaces.ab({s:'j_idt27',f:'headerForm'});")
            print("Direkter JavaScript-Trigger erfolgreich.")
            success = True
        except Exception as e:
            print(f"Direkter JS-Trigger fehlgeschlagen: {e}")

    if not success:
        print("Alle Methoden zum Öffnen der erweiterten Suche haben nicht funktioniert.")
    
    # ========================================
    # 2) Schlagwort eingeben + onchange auslösen
    # ========================================
    if success:
        time.sleep(2)
        print("Warte auf das Schlagwort-Textarea...")
        schlagwort_feld = wait.until(EC.presence_of_element_located((By.ID, "form:schlagwoerter")))
        schlagwort_feld.clear()
        schlagwort_feld.send_keys("a")
        print("Schlagwort 'a' eingetragen.")

        print("Löse PrimeFaces onchange aus...")
        driver.execute_script(
            "PrimeFaces.ab({s:'form:schlagwoerter',e:'change',f:'form',p:'form:schlagwoerter',u:'form:messagesSuchMaske'});"
        )
        print("PrimeFaces onchange ausgeführt.")

        # ========================================
        # 3) Rechtsform "eingetragener Verein" auswählen
        # ========================================
        print("Warte auf das Rechtsform-Dropdown...")
        rechtsform_elem = wait.until(EC.presence_of_element_located((By.ID, "form:rechtsform_input")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", rechtsform_elem)
        time.sleep(1)
        print("Wähle 'eingetragener Verein' aus dem Dropdown...")
        select_rechtsform = Select(rechtsform_elem)
        select_rechtsform.select_by_value("3")  # Wert "3" entspricht "eingetragener Verein"
        print("Rechtsform 'eingetragener Verein' erfolgreich ausgewählt.")

        # ========================================
        # 4) "Ergebnisse pro Seite" auf 100 setzen
        # ========================================
        print("Warte auf das 'Ergebnisse pro Seite'-Dropdown...")
        ergebnisse_dropdown = wait.until(EC.presence_of_element_located((By.ID, "form:ergebnisseProSeite_input")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ergebnisse_dropdown)
        time.sleep(1)
        print("Setze 'Ergebnisse pro Seite' auf 100...")
        select_ergebnisse = Select(ergebnisse_dropdown)
        select_ergebnisse.select_by_value("100")
        print("Ergebnisse pro Seite auf 100 gesetzt.")

        # ========================================
        # 5) Suchen-Button klicken
        # ========================================
        try:
            print("Warte auf den Suchen-Button...")
            search_button = wait.until(EC.presence_of_element_located((By.ID, "form:btnSuche")))
            try:
                print("Versuche normalen Klick (nach ScrollIntoView) auf 'Suchen'...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
                time.sleep(1)
                search_button.click()
                print("Suchen-Button normaler Klick erfolgreich.")
            except Exception as e1:
                print("Normaler Klick fehlgeschlagen:", e1)
                try:
                    print("Versuche JS-Klick auf den Suchen-Button...")
                    driver.execute_script("arguments[0].click();", search_button)
                    print("Suchen-Button per JS-Klick erfolgreich.")
                except Exception as e2:
                    print("JS-Klick fehlgeschlagen:", e2)
                    try:
                        print("Versuche direkten PrimeFaces-Aufruf für den Suchen-Button...")
                        driver.execute_script(
                            "PF('btnSuche').disable();PrimeFaces.ab({s:'form:btnSuche',f:'form',u:'form'});"
                        )
                        print("Direkter PrimeFaces-Aufruf erfolgreich.")
                    except Exception as e3:
                        print("Alle Methoden zum Klicken auf den Suchen-Button haben versagt:", e3)
        except Exception as e:
            print("Fehler beim Finden/Klicken des Suchen-Buttons:", e)

        # ========================================
        # 6) Ergebnisse auslesen und in CSV schreiben
        # ========================================
        try:
            print("Warte auf die Ergebnisliste...")
            # Warte, bis die Ergebnis-Tabelle vorhanden ist
            results_table = wait.until(
                EC.presence_of_element_located((By.ID, "ergebnissForm:selectedSuchErgebnisFormTable_data"))
            )
            # Alle Zeilen abrufen
            rows = results_table.find_elements(By.XPATH, "./tr")
            print(f"{len(rows)} Ergebniszeilen gefunden.")
            
            data = []
            for row in rows:
                try:
                    # Name: Das <span> mit der Klasse 'marginLeft20'
                    name = row.find_element(By.XPATH, ".//span[contains(@class, 'marginLeft20')]").text.strip()
                except Exception as e:
                    name = ""
                try:
                    # Sitz: Im <td> mit Klasse 'sitzSuchErgebnisse'
                    sitz = row.find_element(By.XPATH, ".//td[contains(@class, 'sitzSuchErgebnisse')]//span").text.strip()
                except Exception as e:
                    sitz = ""
                try:
                    # Status: Im <td> mit text-align: center (das Status-Feld)
                    status = row.find_element(By.XPATH, ".//td[contains(@style, 'text-align: center')]//span").text.strip()
                except Exception as e:
                    status = ""
                
                # Falls mindestens Name vorhanden ist, speichern
                if name:
                    data.append([name, sitz, status])
            
            # CSV schreiben
            print(f"Extrahiere {len(data)} Einträge und schreibe in CSV...")
            with open("ergebnisse.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Name", "Sitz", "Status"])  # Header
                writer.writerows(data)
            print("Ergebnisse wurden in 'ergebnisse.csv' gespeichert.")
        except Exception as e:
            print("Fehler beim Auslesen der Ergebnisse:", e)

except Exception as e:
    print(f"Fehler im Ablauf: {e}")

# Optional: Warte, um das Ergebnis zu überprüfen
time.sleep(5)
driver.quit()
