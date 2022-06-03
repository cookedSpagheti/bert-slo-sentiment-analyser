from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# import logging
# from selenium.webdriver.remote.remote_connection import LOGGER
# LOGGER.setLevel(logging.NOTSET)

import time, os, sys
# nastavi da se muta izpisi iz webdriver-ja (ne dela)
DISABLE_LOGS_PATH = '/dev/null' if sys.platform == 'linux' else 'NUL'     # da bo mutal izpis iz webdriver-ja

# mape za posnetke
MAIN_FOLDER = os.getcwd() + "/" + "komentarji/"
FOLDER_24UR = MAIN_FOLDER + "24ur/"
FOLDER_RTVSLO = MAIN_FOLDER + "RTVSLO/"
FOLDER_SIOLNET = MAIN_FOLDER + "SiolNET/"
FOLDER_ZURNAL24 = MAIN_FOLDER + "zurnal24/"

# za selenium
# previdno pri spreminjanju velikosti okna, predvsem pri širini
WEBDRIVER_HEIGHT = 950  #791
WEBDRIVER_WIDTH = 830   #673

WAIT_TIME = 7   # koliko sekund se caka, ce se stvari ne nalozijo

COMMON_TIMOUT_ERROR_PRINT = f"Cakalni čas ({WAIT_TIME} sekund) je potekel"
DEFAULT_WEBDRIVER_FOLDER = os.getcwd() + "/" + "webdrivers/"


# download linki za webdriver_program (razlicica se mora ujemat s trentnim brskalnikom, ki ga uporabljas):
# EDGE   -> https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
# CHROME -> https://chromedriver.chromium.org/downloads


def teardown_method(driver):
    driver.quit()


def use_edge_browser(path: str = None):
    if path is None:
        try:
            driver = webdriver.Edge(executable_path=DEFAULT_WEBDRIVER_FOLDER + "msedgedriver.exe", service_log_path=DISABLE_LOGS_PATH)
            driver.set_window_size(WEBDRIVER_WIDTH, WEBDRIVER_HEIGHT)  # (533, 879)
            return driver
        except:
            print(f"\n  Preveri, da se Edge webdriver_program nahaja v mapi {DEFAULT_WEBDRIVER_FOLDER}\n")
            exit(-1)
    else:
        try:
            driver = webdriver.Edge(executable_path=path, service_log_path=DISABLE_LOGS_PATH)
            driver.set_window_size(WEBDRIVER_WIDTH, WEBDRIVER_HEIGHT)  # (533, 879)
            return driver
        except:
            print(f"\n  Preveri, da se Edge webdriver_program nahaja v mapi {path}\n")
            exit(-1)


def use_chrome_browser(path: str = None):
    if path is None:
        try:
            driver = webdriver.Chrome(executable_path=DEFAULT_WEBDRIVER_FOLDER + "chromedriver.exe", service_log_path=DISABLE_LOGS_PATH)
            driver.set_window_size(WEBDRIVER_WIDTH, WEBDRIVER_HEIGHT)    # 533, 879
            return driver
        except:
            print(f"\n  Preveri, da se Chrome webdriver_program nahaja v mapi {DEFAULT_WEBDRIVER_FOLDER}\n")
            exit(-1)
    else:
        try:
            driver = webdriver.Chrome(executable_path=path, service_log_path=DISABLE_LOGS_PATH)
            driver.set_window_size(WEBDRIVER_WIDTH, WEBDRIVER_HEIGHT)    # 533, 879
            return driver
        except:
            print(f"\n  Preveri, da se Chrome webdriver_program nahaja v mapi {path}\n")
            exit(-1)


def read_comments_24ur(driver, url: str):
    driver.get(url)

    # s tem bos preveril kk je z komentarji, ce sploh obstajajo za ta clanek
    try:
        WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'KOMENTARJI')]"))
        )
        # driver.find_element(By.XPATH, "//div[contains(text(),'KOMENTARJI')]").click()
        # time.sleep(2)
    except NoSuchElementException:
        print("\n  Ta prispevek nima komentarjev\n")  # lahko je tud spremenjena koda od takrat k sm tole skripto pisal
        return
    except TimeoutException:
        print(COMMON_TIMOUT_ERROR_PRINT)
        return

    # sprejmemo piškotke, drugace ma scroll probleme
    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'button') and contains(text(), 'Strinjam se')]"))  #' Nastavitve piškotkov '
        )
        # time.sleep(2)
        driver.find_element(By.XPATH, "//a[contains(@class,'button') and contains(text(),'Strinjam se')]").click()
        # WebDriverWait(driver, 3).until(
        #     EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'button') and contains(text(), 'Shrani nastavitve')]"))
        # )
        # driver.find_element(By.XPATH, "//a[contains(@class,'button') and contains(text(), 'Shrani nastavitve')]").click()
    except TimeoutException:
        pass


    count = 0
    # nalaganje vseh komentarjev prispevka
    while True:
        try:
            # pocaka se dokler se ne pokaze gumb za vec komentarjev na strani
            WebDriverWait(driver, WAIT_TIME/2).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'NALOŽI VEČ')]"))
            )

            # scroll event do gumba
            load_more_btn = driver.find_element(By.XPATH, "//span[contains(text(),'NALOŽI VEČ')]")
            driver.execute_script("return arguments[0].scrollIntoView();", load_more_btn)
            time.sleep(1)
            driver.execute_script("scrollBy(0,-100);")
            time.sleep(1)
            # driver.execute_script("return arguments[0].scrollIntoView();", load_more_btn)

            # pocaka se da scroll naredi svojo stvar in se klikne na gumb
            try:
                WebDriverWait(driver, WAIT_TIME/2).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'NALOŽI VEČ')]"))
                )
                load_more_btn.click()
                count += 1
            except:
                if count < 47:
                    break

                # ucasih ga zmede ce je prevec komentarjev in se komentarji od zacetka nalozijo
                # zato nalozi se enkrat ampak tokrat enkrat manj kliknemo na gumb
                # cist isto kot zgoraj
                for i in range(count-1):
                    WebDriverWait(driver, WAIT_TIME / 2).until(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'NALOŽI VEČ')]"))
                    )

                    # scroll event do gumba
                    load_more_btn = driver.find_element(By.XPATH, "//span[contains(text(),'NALOŽI VEČ')]")
                    driver.execute_script("return arguments[0].scrollIntoView();", load_more_btn)
                    time.sleep(1)
                    driver.execute_script("scrollBy(0,-100);")
                    time.sleep(1)
                    # driver.execute_script("return arguments[0].scrollIntoView();", load_more_btn)

                    # pocaka se da scroll naredi svojo stvar in se klikne na gumb
                    WebDriverWait(driver, WAIT_TIME / 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'NALOŽI VEČ')]"))
                    )
                    load_more_btn.click()


        # ko zmanjka novih komentarjev, zgine gumb
        except TimeoutException:
            break

    # prever ce obstaja glavn folder za shranjevanje posnetkov
    if not os.path.exists(MAIN_FOLDER):
        os.mkdir(MAIN_FOLDER)

    # se nardi se folder za to funkcijo
    if not os.path.exists(FOLDER_24UR):
        os.mkdir(FOLDER_24UR)

    # dobis ime iz datoteke in jo odres/ustvars
    file_name = url.split('/')[-1].split('.')[0]  # najprej odstrani na zadnji del po /, potem pa se .html da stran
    file = open(FOLDER_24UR + file_name + ".txt", 'w', encoding='utf-8')

    # branje podatkov (lahko bi tud samo iskal elemente, k majo class enak comment__content--body, sam tk je bolj za zih)
    # se kr tk isce drugac so problemi
    print('\n  Pisanje v datoteko...\n')
    for scraped_comment in driver.find_elements(By.XPATH, "//div[contains(@class, 'comment__content--body')]"):
        # scraped_comment = comment_window.find_element(By.XPATH, "//div[contains(@class, 'comment__content--body')]")
        file.write(scraped_comment.text + "\n")

    print(f'  Shranjeno v {file_name}.txt\n')
    file.close()
    return


def read_comments_rtvslo(driver, url: str):
    driver.get(url)

    # pocaka se dokler se ne pokaze gumb na strani
    WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='btn-show-comments']"))
    )
    # se "poscroll-a" do gumba
    komentarji_number = driver.find_element(By.XPATH, "//a[@class='btn-show-comments']")
    driver.execute_script("return arguments[0].scrollIntoView();", komentarji_number)

    # pocaka se dokler se scroll dela svojo stvar in se klikne na gumb
    WebDriverWait(driver, WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@class='btn-show-comments']"))
    )
    komentarji_number.click()

    # klikane na gumb "prikazi več"
    # zgleda da je to samo za to velikost (podobno mobilni napravi), drugace kje po straneh
    # side note: komentar komentarjev se ne bere, ker se nahajajo na drugih straneh
    while True:
        try:
            # pocaka se dokler se ne pokaze gumb na strani
            WebDriverWait(driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Prikaži več')]"))
            )

            # scroll event do gumba
            load_more_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Prikaži več')]")
            # driver.execute_script("return arguments[0].scrollIntoView();", load_more_btn)
            time.sleep(1)
            driver.execute_script("scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # pocaka se da scroll naredi svojo stvar in se klikne na gumb
            WebDriverWait(driver, WAIT_TIME).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Prikaži več')]"))
            )
            load_more_btn.click()

        # ko zmanjka novih komentarjev, zgine gumb
        except TimeoutException:
            break

    # prever ce obstaja glavn folder za shranjevanje posnetkov
    if not os.path.exists(MAIN_FOLDER):
        os.mkdir(MAIN_FOLDER)

    # se nardi se folder za to funkcijo
    if not os.path.exists(FOLDER_RTVSLO):
        os.mkdir(FOLDER_RTVSLO)

    # dobis ime iz datoteke in jo odres/ustvars
    array_list = url.split('/')
    file_name = array_list[-2] + "-" + array_list[-1]     # oni majo na predzadnjo naslov novice, na zadnji pa neko stevilko
    file = open(FOLDER_RTVSLO + file_name + ".txt", 'w', encoding='utf-8')

    # branje podatkov (lahk bi tud samo iskal elemente, k majo class enak comment__content--body, sam tk je bolj za zih)
    print('\n  Pisanje v datoteko...\n')
    for paragraph in driver.find_elements(By.XPATH, "//div[@class='comment']/p"):

        # navadno besedilo
        # for paragraph in comment_window.find_elements(By.XPATH, "//p"):
        text = paragraph.text

        # tuki je zato k so lahko prazni paragrafi, vsaj pomojem
        if text != '':
            file.write(text + "\n")

        # # navadno besedilo2
        # for paragraph in comment_window.find_elements(By.XPATH, "//p/p"):
        #     text = paragraph.text
        #
        #     # tuki je zato k so lahko prazni paragrafi, vsaj pomojem
        #     if text != '':
        #         file.write(text + "\n")
        #
        # # vsak comment posevn text
        # for paragraph in comment_window.find_elements(By.XPATH, "//p/p/em"):    # to je ce je
        #     file.write(paragraph.text + "\n")

    print(f'  Shranjeno v {file_name}.txt\n')
    file.close()


# pocakat mores da se neka stvar nalozi na spletni strani
def read_comments_siolnet(driver, url: str):
    driver.get(url)

    # samo prvic bo tole, pol bodo pa gumbi za strani, AMPAK NI NUJNO
    # ok ja, naprej to nardis, pol pa po straneh beres komentarje
    try:
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='comments__show_all--button']"))
        )
        # se "poscroll-a" do gumba
        show_more_comments = driver.find_element(By.XPATH, "//a[@class='comments__show_all--button']")
        driver.execute_script("return arguments[0].scrollIntoView();", show_more_comments)
        time.sleep(1)
        driver.execute_script("scrollBy(0,-130);")

        # pocaka se dokler se scroll dela svojo stvar in se klikne na gumb
        WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='comments__show_all--button']"))
        )
        show_more_comments.click()
    except:
        time.sleep(1)
        driver.execute_script("scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    # prever ce obstaja glavn folder za shranjevanje posnetkov
    if not os.path.exists(MAIN_FOLDER):
        os.mkdir(MAIN_FOLDER)

    # se nardi se folder za to funkcijo
    if not os.path.exists(FOLDER_SIOLNET):
        os.mkdir(FOLDER_SIOLNET)

    # dobis ime iz datoteke in jo odres/ustvars
    file_name = url.split('/')[-1]  # odstrani na zadnji del po /
    file = open(FOLDER_SIOLNET + file_name + ".txt", 'w', encoding='utf-8')

    print('\n  Pisanje v datoteko...\n')
    while True:
        # mogoce se vec
        # time.sleep(2)   # mal pocakam da res ne bo od iste strani komentarjev bral
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".comments__text"))
        )

        # branje podatkov (lahko bi tud samo iskal elemente, k majo class enak comment__content--body, sam tk je bolj za zih)
        # for scraped_comment in driver.find_elements(By.XPATH, "//p[@class='comments__text']"):
        for scraped_comment in driver.find_elements(By.CSS_SELECTOR, ".comments__text"):
            file.write(scraped_comment.text + "\n")

        # poskusa najt gumb za naslednjo stran
        try:
            WebDriverWait(driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pagination__link--next"))   # //a[@class='pagination__link--next']
            )
        except TimeoutException:
            break

        # se "poscroll-a" do gumba naslednjo stran
        show_more_comments = driver.find_element(By.CSS_SELECTOR, ".pagination__link--next")
        driver.execute_script("return arguments[0].scrollIntoView();", show_more_comments)
        time.sleep(1)
        driver.execute_script("scrollBy(0,-130);")

        # pocaka se dokler se scroll dela svojo stvar in se klikne na gumb
        WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".pagination__link--next"))
        )
        show_more_comments.click()

    print(f'  Shranjeno v {file_name}.txt\n')
    file.close()
    return


# brez podpore, saj je prevec oglasov
def read_comments_zurnal24(driver, url: str):
    print("\n  Ni popolnoma podprt!\n")
    return

    driver.get(url)

    # klik pri komentarjih na PREBERI VEČ
    WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='btn btn--viewall']")) # tuki bodo pomojem problemi
    )
    # se "poscroll-a" do gumba
    show_replies = driver.find_element(By.XPATH, "//a[@class='btn btn--viewall']")
    driver.execute_script("return arguments[0].scrollIntoView();", show_replies)
    time.sleep(5)   # fuul je add-ov, zato se more se mal pocakat preden se lahko klikne
    driver.execute_script("return arguments[0].scrollIntoView();", show_replies)
    time.sleep(1)
    driver.execute_script("scrollBy(0,-100);")

    # pocaka se dokler se scroll dela svojo stvar in se klikne na gumb
    WebDriverWait(driver, WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@class='btn btn--viewall']"))
    )
    show_replies.click()
    time.sleep(20)  # oglas, je lahko tud posnetek


    # prever ce obstaja glavn folder za shranjevanje posnetkov
    if not os.path.exists(MAIN_FOLDER):
        os.mkdir(MAIN_FOLDER)

    # se nardi se folder za to funkcijo
    if not os.path.exists(FOLDER_ZURNAL24):
        os.mkdir(FOLDER_ZURNAL24)

    # dobis ime iz datoteke in jo odres/ustvars
    file_name = url.split('/')[-1]  # odstrani na zadnji del po /
    file = open(FOLDER_ZURNAL24 + file_name + ".txt", 'w', encoding='utf-8')

    # dobi koliko strani komentarjev je
    comment_page_numbers = []
    for string in driver.find_elements(By.XPATH, "//a[@class='pagination__link']"):
        if string != '':
            comment_page_numbers.append(int(string))    # mozno, da bodo tuki problemi

    # branje komentarjev po straneh
    final_page = comment_page_numbers[-1]
    for i in range(final_page - 1):     # -1 drugace, se enkrat klikne na naslednjo stran, ceprav je ni (npr. da sta 2 strani)

        # odpre vse odgovore na spletni strani
        for open_replies in driver.find_elements(By.XPATH, "//span[@class='btn__value']"):
            driver.execute_script("return arguments[0].scrollIntoView();", open_replies)

            # pocaka se dokler se scroll dela svojo stvar in se klikne na gumb
            WebDriverWait(driver, WAIT_TIME).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@class='btn__value']"))
            )
            open_replies.click()

        # shrani vse komentarje
        for scraped_comment in driver.find_elements(By.XPATH, "//span[@class='js_onecommentVisible']"):
            file.write(scraped_comment.text + "\n")

        # gremo na nasledno stran
        next_page_btn = driver.find_element(By.XPATH, "//a[@class='pagination__link']/span[contains(text(),'Naslednja')]")
        driver.execute_script("return arguments[0].scrollIntoView();", next_page_btn)

        # pocaka se dokler se scroll dela svojo stvar in se klikne na gumb
        WebDriverWait(driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='btn__value']"))
        )
        next_page_btn.click()

        time.sleep(6)   # ne vem kako zagotovit, da bo preveril ce so prisotni drugi komentarji



def help_description():
    description = ""

    description += "Pomoc za program scrap-anje komentarjev\n"
    description += " -d    --domain              spletna stran za iskanje komentarjev (default: 24ur)\n"
    description += "                               rtvslo - komentarji iz naslova za RTV SLO\n"
    description += "                               siol - komentarji iz naslova za SiolNET.\n"
    description += "                               24ur - komentarji iz naslova za 24UR.com\n"
    description += " -u    --url                 popolna povezava s komentarji (onemogoci -f zastavico)\n"
    description += " -f    --file                pot datoteke s povezavami za isto spletno stran (onemogoci -u zastavico)\n"
    description += " -wd   --webdriver           ime brskalnika za zagon programa (default: edge)\n"
    description += "                               chrome - Google Chrome\n"
    description += "                               edge - MS Edge\n"
    description += f" -wdf  --webdriver-file      pot programa za webdriver_program (default: {DEFAULT_WEBDRIVER_FOLDER})\n"
    description += " -h    --help                trenutni izpis\n"
    description += "\n"
    description += " EXAMPLE: python scraper.py -u \"https://www.24ur.com/novice/gos...\"\n"

    return description


if __name__ == '__main__':
    # driver.get("https://www.24ur.com/novice/gospodarstvo/znana-veriga-portoroskih-hotelov-ostaja-v-drzavni-lasti.html")

    # TOLE JE OK
    # read_comments_24ur(driver, "https://www.24ur.com/novice/gospodarstvo/znana-veriga-portoroskih-hotelov-ostaja-v-drzavni-lasti.html")
    # read_comments_24ur(driver, "https://www.24ur.com/novice/tujina/putin-finsko-odpoved-nevtralnosti-oznacil-za-napako.html")

    # TO TUDI
    # read_comments_rtvslo(driver, "https://www.rtvslo.si/slovenija/v-nacrtu-resevanje-stanovanjske-krize-dvig-minimalne-place-in-pokojnin-ter-regulacija-cen/627375")
    # read_comments_rtvslo(driver, "https://www.rtvslo.si/sport/sportni-sos/vec-tock-od-doncica-so-dosegli-le-durant-jones-in-wilkins/627359")

    # AGAIN COOL
    # read_comments_siolnet(driver, "https://siol.net/novice/slovenija/ziga-turk-mr-tesla-gre-po-twitter-nomenklatura-pa-v-jok-579321")
    # UNICORN? read_comments_siolnet(driver, "https://siol.net/forum/thread/tarca-ceferin-do-luksuznega-stanovanja-po-ceni-o-kateri-lahko-vecina-le-sanja-78754")
    # read_comments_siolnet(driver, "https://siol.net/novice/svet/ukrajina-situacija-je-mnogo-slabsa-kot-na-zacetku-vojne-vzivo-579346")

    # NO GO, ADDS!
    # read_comments_zurnal24(driver, "https://www.zurnal24.si/svet/trenutek-ko-je-tankovsko-kupolo-odneslo-75-metrov-visoko-386210")

    domain = '24ur'
    url = ''
    file = ''
    webdriver_program = 'edge'
    webdriver_path = None

    # ce je prazno
    if len(sys.argv) == 1:
        print(help_description())
        exit(0)

    # gremo cez inpute
    i = 1
    while i != len(sys.argv):
        if '-d' == sys.argv[i] or '--domain' == sys.argv[i]:
            domain = sys.argv[i+1].lower()

        elif '-u' == sys.argv[i] or '--url' == sys.argv[i]:
            url = sys.argv[i+1]

        elif '-f' == sys.argv[i] or '--file' == sys.argv[i]:
            file = sys.argv[i+1]

        elif '-wd' == sys.argv[i] or '--webdriver_program' == sys.argv[i]:
            webdriver_program = sys.argv[i + 1].lower()

        elif '-wdf' == sys.argv[i] or '--webdriver_program-file' == sys.argv[i]:
            webdriver_path = sys.argv[i+1]

        elif '-h' == sys.argv[i] or '--help' == sys.argv[i]:
            print("\n" + help_description())
            exit(0)

        else:
            print("\n" + help_description())
            exit(0)

        i += 2

    # preveri, da je podan vsaj ena povezava
    if '' == url and '' == file:
        print("\n  Manjka povezava do prispevka s komentarji\n")
        exit(0)

    # nastavi driver
    main_driver = None
    if 'edge' == webdriver_program:
        if webdriver_path is None:
            main_driver = use_edge_browser()
        else:
            main_driver = use_edge_browser(webdriver_path)
    elif 'chrome' == webdriver_program:
        if webdriver_path is None:
            main_driver = use_chrome_browser()
        else:
            main_driver = use_chrome_browser(webdriver_path)


    # preveri ce je podana pot do datoteke s spletnimi stranmi
    if '' != file:
        fd = open(file, 'r')

        for current_url in fd:
            try:
                print(f'\n  Berem povezavo: {current_url}\n')

                if '24ur' == domain:
                    read_comments_24ur(main_driver, current_url)
                elif 'siol' == domain:
                    read_comments_rtvslo(main_driver, current_url)
                elif 'rtvslo' == domain:
                    read_comments_siolnet(main_driver, current_url)
            except:
                print(f"\n  Napaka pri {current_url}\n")

        fd.close()
    else:
        try:
            if '24ur' == domain:
                read_comments_24ur(main_driver, url)
            elif 'siol' == domain:
                read_comments_rtvslo(main_driver, url)
            elif 'rtvslo' == domain:
                read_comments_siolnet(main_driver, url)
        except:
            print(f"\n  Napaka pri {url}\n")


    # se ugasne driver
    teardown_method(main_driver)
