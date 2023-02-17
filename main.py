import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from pages import login_page, matches_page
import login


# Función para loggear con steam
def steam_login():
    boton_steam = driver.find_element(*login_page.PROVIDER_BUTTON)
    boton_steam.click()
    input_user = wait.until(EC.presence_of_element_located(login_page.USERNAME_INPUT))
    input_user.send_keys(login.username)
    input_pw = wait.until(EC.presence_of_element_located(login_page.PASSWORD_INPUT))
    input_pw.send_keys(login.password)
    boton_login = driver.find_element(*login_page.LOGIN_BUTTON)
    boton_login.click()
    boton_login2 = wait.until(EC.presence_of_element_located(login_page.SECOND_LOGIN_BUTTON))
    boton_login2.click()


# proceso de análisis de partidas
def process_matches():
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")  # bs4 parsea el html para obtener los datos
    partidas = soup.find_all("div", {"class": "match columns"})  # obtiene la lista de partidas
    stats = soup.find_all("div", {"class": "stats columns"})  # obtiene las estadísticas de cada partida
    i = 0

    for partida in partidas:
        equipo1 = partida.find("div", {"class": "team centered-mobile columns medium-3 small-12 right"}).text.strip()
        puntaje1 = partida.find("div", {"class": "score columns medium-1 small-5 right"}).text.strip()

        equipo2 = partida.find("div", {"class": "team centered-mobile columns medium-3 small-12 left"}).text.strip()
        puntaje2 = partida.find("div", {"class": "score columns medium-1 small-5 left"}).text.strip()

        my_team_won = False  # se va a verificar si el equipo del jugador ganó. Se parte asumiendo que no.

        avatar = partida.find_all(class_="avatar")  # La partida donde aparezca el avatar del usuario corresponde al
        # equipo en el que este jugó.
        for element in avatar:
            imgs = element.find_all("img")
            if len(imgs) == 2 and "winner" in imgs[0]["class"]:  # Si aparecen dos imágenes en el equipo entonces es
                # que es el equipo. Si el avatar está acompañado de "winner", es que el equipo del jugador ganó.
                my_team_won = True

        print(equipo1 + " " + puntaje1 + " vs " + equipo2 + " " + puntaje2)
        if my_team_won:
            print('GANASTE')
        else:
            print('PERDISTE')

        # extraigo los datos
        date = stats[i].find(class_="columns medium-2 medium-offset-1 small-12").text
        mapa = stats[i].find(class_="columns medium-2 small-12").text
        stats_data = stats[i].find_all("small", class_="muted-text bold")
        kad = stats_data[3].parent.text

        # Limpiamos la información
        date = date.replace("\n", "").replace("Fecha", "").strip()
        mapa = mapa.replace("\n", "").replace("Mapa", "").strip()
        kad = kad.replace("\n", "").replace("K/A/D", "").strip()

        print("Fecha:", date)
        print("Mapa:", mapa)
        print("K/A/D:", kad)
        print("\n\n\n")
        i = 1 + i
        # Voy a querer el winrate, por lo que necesito conocer cuántas veces jugué un mapa y cuántas veces lo gané.
        maps[mapa]["played"] += 1
        if my_team_won:
            maps[mapa]["won"] += 1


# Declado los mapas que se juegan en GC y los que pueden llegar a estar en el historial.
maps = {
    "de_inferno": {"played": 0, "won": 0},
    "de_dust2": {"played": 0, "won": 0},
    "de_overpass": {"played": 0, "won": 0},
    "de_nuke": {"played": 0, "won": 0},
    "de_mirage": {"played": 0, "won": 0},
    "de_vertigo": {"played": 0, "won": 0},
    "de_ancient": {"played": 0, "won": 0},
    "de_cbble_classic": {"played": 0, "won": 0},
    "de_tuscan": {"played": 0, "won": 0},
    "de_cache": {"played": 0, "won": 0},
    "de_anubis": {"played": 0, "won": 0}
}

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
wait = WebDriverWait(driver, 60)
driver.get("https://gamersclub.com.br/my-matches")

steam_login()

time.sleep(4)

# recién en este punto llegamos a la página de my-matches
driver.refresh()  # esto es para que desaparezca un overlay, que cambia, entonces no lo puedo cerrar con selenium cómodamente.

# Espero a que aparezcan las partidas
matches = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".match")))

# Encontrar todos los botones de la página
buttons = driver.find_elements(By.CSS_SELECTOR, "#myMatchesPagination .btn-group button[data-page]")

if len(buttons) > 0:  # Puede llegar a no haber botones si se jugaron menos de 10 partidas.
    buttons = buttons[1:]  # Eliminar solo el primer elemento, que es el botón que dice PRIMERA
    b = 3

    for button in buttons:  # Cada botón que se itera es cada página de partidas.
        process_matches()  # Procesamos las partidas en la página actual.

        # Hacemos scroll hacia abajo para ir a la siguiente página de partidas.
        scroll = driver.find_element(By.TAG_NAME, 'html')
        time.sleep(4)
        for j in range(6):
            scroll.send_keys(Keys.PAGE_DOWN)
        scroll.send_keys(Keys.PAGE_UP)
        j = 0
        time.sleep(5)

        # El path del botón cambia entre estos 2.
        try:
            boton = driver.find_element(matches_page.BUTTON1)
        except:
            boton = driver.find_element()

        boton.click()
        wait.until(EC.staleness_of(button))  # Esperamos a que el botón anterior desaparezca.
        html = driver.page_source  # Obtenemos el nuevo HTML de la siguiente página.
        b = b + 1

else:
    process_matches()  # Si no hay botones, procesamos solo la página 1.

# iteramos por cada mapa obtenido. Si se jugó, se imprime el winrate.
for map_name, stats in maps.items():
    if stats['played'] != 0:
        winrate = stats['won'] / stats['played'] * 100
        print(f"{map_name}: Jugados: {stats['played']} - Ganados: {stats['won']} - Winrate: {winrate:.2f}%")

driver.quit()
