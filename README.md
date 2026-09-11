# Chomyk / ChomikDownloader

Skrypt został napisany w Pythonie 3.5.2 i służy do pobierania plików z Chomikuj.pl  

Dostępne parametry:  
 * __-u__ użytkownik  
 * __-p__ hasło  
 * __-i__ plik/folder do pobrania  
 * __-d__ ścieżka pobierania plików (domyślnie katalog skryptu)  
 * __-o__ katalog docelowy do zapisu plików (domyślnie katalog skryptu)
 * __-t__ maksymalna ilość wątków (domyślnie 5)  

Przykład: _./chomyk.py -u mojchomik -p mojehaslo -i http://chomikuj.pl/mojchomik/filmy_

## Instalacja

Wymagania: Python 3.5+

```bash
git clone https://github.com/michalsarna/ChomikDownloader.git
cd ChomikDownloader
pip3 install -r requirements.txt

# Jeśli pojawi się błąd "externally managed environment" (macOS z systemowym Pythonem):
pip3 install -r requirements.txt --break-system-packages
```

Uruchomienie:

```bash
python3 chomyk.py -u mojchomik -p mojehaslo -i http://chomikuj.pl/mojchomik/filmy
```


![Screenshot](https://raw.githubusercontent.com/blackberrymamba/ChomikDownloader/master/screenshot-001.png)
