# Wgranie przez przeciągnięcie do GitHuba

1. Otwórz repozytorium `olmocr_vlm` na GitHubie.
2. Wybierz **Add file → Upload files** (w pustym repozytorium: **uploading an existing file**).
3. Otwórz lokalny folder `D:\olmocr_vlm_github`.
4. Zaznacz **całą zawartość tego folderu** i przeciągnij do formularza. Nie przeciągaj samego folderu nadrzędnego, bo README powinien znaleźć się w katalogu głównym repozytorium.
5. Poczekaj na zakończenie przesyłania. Wpisz opis: `Add LUMI HTR pilot evaluation data and documentation`.
6. Zatwierdź przesłanie (Commit changes / Propose changes, zależnie od ustawień repozytorium).
7. Sprawdź, czy README wyświetla się na stronie głównej i czy folder `results` zawiera cztery katalogi ewaluacji.

GitHub pozwala przesłać przez przeglądarkę do 100 plików naraz, każdy do 25 MiB. Ten folder został sprawdzony pod kątem tych limitów. Nie trzeba przesyłać oddzielnie archiwum ZIP ani stosować Git LFS. Przeglądarkowy upload nie jest mechanizmem filtrowania całej kopii roboczej: przesyłaj tylko przygotowany folder, nie `D:\olmocr_vlm`.

Zawartość jest gotowa technicznie do uploadu. Licencja ponownego wykorzystania pozostaje do wyboru przez autora. Skany, transkrypcje i adaptery są poza tym folderem. Dodanie ich później wymaga zaktualizowania zakresu i praw do danych.

Źródło limitów i procedury: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
