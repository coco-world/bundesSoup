from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

# Browser starten (sichtbar) und maximieren
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.handelsregister.de/rp_web/welcome.xhtml")
wait = WebDriverWait(driver, 15)

success = False

try:
    # Warten, bis der "Erweiterte Suche"-Button vorhanden ist
    advanced_search = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[@title='Erweiterte Suche']"))
    )
    
    # 1. Versuch: JavaScript Click
    try:
        print("Versuche JavaScript-Klick auf 'Erweiterte Suche'...")
        driver.execute_script("arguments[0].click();", advanced_search)
        print("Erweiterte Suche per JS-Click erfolgreich.")
        success = True
    except Exception as e:
        print(f"JavaScript-Click fehlgeschlagen: {e}")

    # 2. Versuch: Hover + normaler Klick (Fallback)
    if not success:
        try:
            print("Versuche Hover + Klick auf 'Erweiterte Suche'...")
            ActionChains(driver).move_to_element(advanced_search).perform()
            time.sleep(1)  # Hover-Effekt wirken lassen
            advanced_search.click()
            print("Erweiterte Suche per Hover + Klick erfolgreich.")
            success = True
        except Exception as e:
            print(f"Hover + Klick fehlgeschlagen: {e}")

    # 3. Versuch: Direkter JS-Trigger des onclick-Events (Fallback)
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
    
    # Wenn die erweiterte Suche erfolgreich geöffnet wurde:
    if success:
        # Kurze Wartezeit, damit die Maske vollständig geladen ist
        time.sleep(2)
        print("Warte auf das Schlagwort-Textarea...")
        schlagwort_feld = wait.until(EC.presence_of_element_located((By.ID, "form:schlagwoerter")))
        schlagwort_feld.clear()
        schlagwort_feld.send_keys("a")
        print("Schlagwort 'a' eingetragen.")

        # PrimeFaces AJAX-Event (onchange) auslösen
        print("Löse PrimeFaces onchange aus...")
        driver.execute_script(
            "PrimeFaces.ab({s:'form:schlagwoerter',e:'change',f:'form',p:'form:schlagwoerter',u:'form:messagesSuchMaske'});"
        )
        print("PrimeFaces onchange ausgeführt.")

        # ===============================
        # Suchen-Button klicken (mit Fallbacks)
        # ===============================
        try:
            print("Warte auf den Suchen-Button...")
            search_button = wait.until(
                EC.presence_of_element_located((By.ID, "form:btnSuche"))
            )

            # 1. Normaler Klick nach Scroll
            try:
                print("Versuche normalen Klick (nach ScrollIntoView) auf 'Suchen'...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
                time.sleep(1)
                search_button.click()
                print("Suchen-Button normaler Klick erfolgreich.")
            except Exception as e1:
                print("Normaler Klick fehlgeschlagen:", e1)

                # 2. JavaScript-Klick
                try:
                    print("Versuche JS-Klick auf Suchen-Button...")
                    driver.execute_script("arguments[0].click();", search_button)
                    print("Suchen-Button per JS-Klick erfolgreich.")
                except Exception as e2:
                    print("JS-Klick fehlgeschlagen:", e2)

                    # 3. Direkter PrimeFaces-Aufruf
                    try:
                        print("Versuche direkten PrimeFaces-Aufruf für Suchen-Button...")
                        # Entspricht onclick="PrimeFaces.bcn(this,event,[...])"
                        driver.execute_script(
                            "PF('btnSuche').disable();"
                            "PrimeFaces.ab({s:'form:btnSuche',f:'form',u:'form'});"
                        )
                        print("Direkter PrimeFaces-Aufruf erfolgreich.")
                    except Exception as e3:
                        print("Alle Methoden zum Klicken auf Suchen-Button haben versagt:", e3)

        except Exception as e:
            print("Fehler beim Finden/Klicken des Suchen-Buttons:", e)

except Exception as e:
    print(f"Fehler im Ablauf: {e}")

# Optional: Warte, um das Ergebnis zu sehen
time.sleep(5)
driver.quit()
