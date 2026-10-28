# System Nadzoru Produkcji (SCADA) & DBMS 🏭

Projekt akademicki zrealizowany w ramach przedmiotu Przemysłowe Bazy Danych na Politechnice Śląskiej[cite: 2]. Aplikacja stanowi autorski system zarządzania bazą danych (DBMS) zintegrowany z modułem graficznym SCADA do wizualizacji procesu technologicznego w czasie rzeczywistym[cite: 4].

## Autorzy
* Jakub Kielar[cite: 2]

## Technologie
* **Język:** Python 3.13[cite: 4]
* **Baza danych:** SQLite3 (rozwiązanie bezserwerowe, działa lokalnie)[cite: 4]
* **GUI & Grafika wektorowa:** Tkinter (Canvas)[cite: 4]
* **Obsługa plików:** biblioteka CSV[cite: 4]

## Główne funkcjonalności
* **Baza Danych (Rejestr):** Gromadzenie danych historycznych z czujników (wartość, jednostka, status) w tabeli `Pomiary`[cite: 4].
* **Moduł Zarządzania:** Możliwość ręcznego dodawania i usuwania pomiarów oraz masowy import i eksport danych do plików CSV[cite: 4, 5].
* **Statystyki Live:** Dynamiczne obliczanie wskaźników KPI (całkowita liczba rekordów, średnia wartość, liczba stanów ALARM)[cite: 4, 5].
* **Wizualizacja SCADA (Zbiornik Procesowy ZB-01):** Graficzna reprezentacja obiektu[cite: 6]. 
  * Animowany poziom cieczy i jej kolor reagujący na status pomiaru (Niebieski - OK, Czerwony - ALARM)[cite: 6].
  * Cyfrowy wyświetlacz ostatnich odczytów i wskaźnik binarny (lampka statusu)[cite: 6].

## Jak uruchomić projekt?
Aplikacja nie wymaga instalacji żadnego zewnętrznego serwera baz danych[cite: 9]. Aby ją uruchomić:
1. Upewnij się, że masz zainstalowanego Pythona w systemie.
2. Pobierz plik `PBD.py`[cite: 1] z tego repozytorium.
3. Uruchom skrypt z poziomu terminala poleceniem: `python PBD.py` lub uruchom go w swoim ulubionym środowisku IDE (np. PyCharm, VS Code).
4. Przy pierwszym uruchomieniu aplikacja automatycznie wygeneruje lokalny plik bazy danych `przemyslowa_baza.db`[cite: 1].

## Dokumentacja
Szczegółowy opis architektury, struktury bazy danych oraz przeprowadzonych scenariuszy testowych znajduje się w załączonym pliku `PBD_Kielar_Ładoś.pdf`[cite: 2].
