# Rozliczenie PLGrid / LUMI

## Potwierdzone przez użytkownika metadane

| Pole | Wartość |
|---|---|
| Autor pakietu | Grzegorz Gałęzowski |
| Afiliacja | Uniwersytet Kardynała Stefana Wyszyńskiego w Warszawie / Wydział Nauk Humanistycznych |
| Numer grantu | PLL/2026/019908 |
| ID grantu | pllhistpreproc |
| Zespół naukowy | plggarchiai |
| Typ | Grant testowy LUMI |
| Wnioskodawca | Artur Górak |
| Techniczne konto LUMI | project_465003327 |

## Jak opisać tę pozycję w sekcji Dane badawcze

- Tytuł proponowanego rekordu: **olmocr_vlm: pilot HTR evaluation data and scripts from LUMI**.
- Zakres: dane liczbowe z ewaluacji pilotażu, kod i dokumentacja; nie pełny korpus skanów ani 98 stron treningowych.
- DOI: uzupełnić dopiero rzeczywistym DOI opublikowanego rekordu.
- URL: podać stronę tego rekordu; adres GitHuba sam w sobie nie jest DOI.

Publiczny GitHub nie nadaje automatycznie DOI. W Zenodo można opublikować osobny rekord danych; przy publikacji rejestrowany jest DOI. Dane i dokumentacja w tym pakiecie są udostępniane na CC BY 4.0, kod i konfiguracje na MIT. W opisie rekordu należy zachować ten podział. Nie należy wpisywać DOI artykułu lub modelu bazowego jako DOI tego zestawu.

## Faktyczny opis prac do wykorzystania przy raporcie

W ramach grantu testowego sprawdzono techniczną wykonalność przetwarzania historycznych dokumentów za pomocą modeli OCR/VLM na LUMI-G. Zweryfikowano środowisko GPU AMD MI250X, wykonano pilotażowe porównanie olmOCR-2 i Qwen2.5-VL na sześciu stronach oraz krótkie dostrajanie LoRA na dziesięciu stronach z walidacją na dwóch stronach. Zachowano konfiguracje, skrypty oraz metryki CER/WER. Wyniki wykazały problemy z nadgenerowaniem tekstu i uzasadniają dalszą weryfikację na większym, niezależnym zbiorze. Nie stanowią pełnego benchmarku ani dowodu uogólnionej przewagi modelu. Dwie strony walidacyjne nie są niezależnym końcowym zbiorem testowym.

To fragment merytoryczny, nie gotowy kompletny raport ani ocena satysfakcji użytkownika. Nie dopisano zużycia zasobów, daty zakończenia grantu ani publikacji, których nie potwierdzono. Trzeba je uzupełnić na podstawie Portalu i właściwego zestawienia rozliczeniowego.

## Wymagania i źródła

- Dokumentacja grantu testowego LUMI wskazuje raport w ciągu **14 dni od zakończenia**, według dostępnego wzoru; można go przygotować po polsku lub angielsku. Data zakończenia tego grantu nie została ustalona w pakiecie.
- Ogólna instrukcja rozliczania LUMI opisuje publikacje/deklaracje, opcjonalne wskazanie repozytoriów danych oraz obowiązkową ocenę grantu (minimum 2500 znaków). Szczególnego terminu raportu testowego nie należy zastępować ogólnym terminem miesięcznym.
- Repozytorium wspiera dokumentację wyników, lecz nie zastępuje zgłoszenia raportu ani oceny operatora.

Źródła sprawdzone przy przygotowaniu pakietu (2026-10-14):

1. https://guide.plgrid.pl/pl/portal-for-science/grants/lumi/test
2. https://guide.plgrid.pl/pl/portal-for-science/settlements/grants_lumi
3. https://guide.plgrid.pl/pl/portal-for-science/settlements/acknowledgements
4. https://help.zenodo.org/docs/deposit/create-new-upload/
