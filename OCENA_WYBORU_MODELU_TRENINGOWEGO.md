# Ocena wyboru modelu do HTR na LUMI

Data: 2026-09-28

## Decyzja w skrócie

**OlmOCR 2 7B jest najlepszym kandydatem operacyjnym do pierwszego treningu
LoRA na LUMI, ale nie jest jeszcze naukowo dowiedzionym najlepszym modelem dla
polskiego rękopisu historycznego.**

Nie należy teraz rozpoczynać wielotysięcznego treningu wyłącznie na OlmOCR.
Należy najpierw wykonać mały, zamrożony eksperyment porównawczy z tym samym
ground truth dla:

1. `allenai/olmOCR-2-7B-1025` BF16 + LoRA - kandydat główny;
2. `Qwen/Qwen2.5-VL-7B-Instruct` BF16 + LoRA - baza kontrolna;
3. `meta-models/Muse-Glimmer-30B` + LoRA - kandydat warunkowy, tylko po
   potwierdzeniu licencji, pełnych wag, działania vision encoder i treningu
   ROCm na LUMI.

Taki test nie wymaga trzykrotnego ręcznego przygotowania danych. Jedno
kanoniczne archiwum obraz + ręczna transkrypcja + manifest generuje eksporty
dla wszystkich modeli.

## Co wynika z dotychczasowych danych

### OlmOCR

- Powstał jako wyspecjalizowany model document OCR oparty o Qwen2.5-VL-7B.
- Uczył się na zróżnicowanych stronach, w tym historycznych skanach, ale jego
  publicznie opisywany benchmark dotyczy przede wszystkim OCR dokumentów, a nie
  polskiego HTR określonej ręki.
- Ma oficjalny kod treningowy, format PDF + Markdown/YAML, konfigurację LoRA i
  ścieżkę przygotowania checkpointu.
- Został uruchomiony na LUMI MI250X; BF16 model ładuje się, a LoRA tworzy
  5 046 272 parametrów trenowalnych.
- Zero-shot na naszej sześciostronicowej próbce rękopisów jest słaby
  (mediana CER 0.890775) i wykazuje nadgenerowanie. To nie dyskwalifikuje LoRA,
  ale wyklucza twierdzenie, że model jest już dobry dla tego rodzaju pisma.

Wniosek: OlmOCR ma najlepszą obecnie drogę **od danych do powtarzalnego
treningu**, lecz jego przewaga jakościowa dla polskiego rękopisu jest hipotezą
do sprawdzenia.

### Muse Glimmer 30B

Raporty Fireworks wskazywały Muse Glimmer 30B jako kandydat warunkowy:

- w poprzednich testach API miał lepszą medianę niż GLM na nowym materiale
  rękopiśmiennym;
- jest większym modelem multimodalnym i może mieć bogatszą wiedzę wizualno-
  językową;
- dostępne materiały wskazują otwarte wagi i Apache-2.0 oraz możliwość LoRA.

Nie jest jednak obecnie wyborem głównym, ponieważ:

- wynik Fireworks był inferencją usługi, nie treningiem tych samych wag;
- nie wykonano testu na LUMI/ROCm, nie sprawdzono pamięci, Flash Attention,
  formatów obrazu ani stabilnego kodu treningowego;
- 30B oznacza istotnie większe ryzyko środowiskowe, dłuższy trening i większy
  koszt GPU niż model 7B;
- nie ma potwierdzenia, że jego przewaga obejmuje polski rękopis po uczciwym
  podziale według ręki, a nie tylko jeden zestaw stron.

Wniosek: Muse warto sprawdzić jako **challengera**, nie jako podstawę całego
przygotowania danych.

### Qwen2.5-VL-7B-Instruct

To właściwy baseline treningowy, bo OlmOCR 2 jest jego specjalizowanym
dostrojeniem. Porównanie obu na tym samym LoRA odpowie na pytanie kluczowe dla
artykułu: czy preadaptacja OlmOCR do document OCR pomaga, czy przeszkadza przy
transferze na rękopis historyczny.

## Ranking decyzji

| rola | model | decyzja |
| --- | --- | --- |
| pierwszy trening produkcyjny | OlmOCR 2 7B BF16 + LoRA | tak, po teście renderera PDF |
| konieczny baseline | Qwen2.5-VL-7B-Instruct + LoRA | tak |
| challenger | Muse Glimmer 30B + LoRA | najpierw preflight LUMI |
| baseline inferencyjny | RolmOCR | opcjonalnie, nie trenować jako główny model |
| API benchmark | Qwen/Kimi/GLM z Fireworks | porównanie zero-shot, nie baza lokalnego treningu |

## Protokół wyboru przed pełnym treningiem

### Dane

Utwórz jeden zamrożony zestaw pilotowy, np. 300-500 stron, z podziałem według
dokumentu i ręki: 70% train, 15% dev, 15% test. Test pozostaje nietknięty.
Dobierz co najmniej kilka rąk i typów stron; nie mieszaj stron tej samej ręki
między train a test.

### Jednakowe warunki

Każdy model dostaje:

- identyczne obrazy i identyczne transkrypcje;
- tę samą normalizację tekstu;
- tę samą liczbę epok, seedów i budżet aktualizacji;
- LoRA rank 8 jako punkt startowy;
- identyczny dev/test oraz CER, WER, stosunek długości predykcji i analizę
  halucynacji.

Nie porównuje się bezpośrednio wyniku API Fireworks z lokalnym LoRA bez
oznaczenia, że są to odmienne warunki.

### Kryterium wyboru

Wybieramy model dopiero, gdy:

1. przejdzie pełny training smoke test na LUMI;
2. poprawi się względem własnego zero-shot;
3. ma najniższy CER na nietkniętym teście lub wynik statystycznie nieodróżnialny
   od najlepszego przy wyraźnie niższym koszcie;
4. nie wykazuje systematycznego nadgenerowania ani utraty tekstu;
5. można legalnie przechować, opisać i odtworzyć jego wagi oraz adapter.

## Zasada nieodwracalności danych

Nie zapisujemy korpusu tylko jako PDF + Markdown OlmOCR. Zachowujemy jako
źródło kanoniczne:

```text
images/<page_id>.jpg|png|tif
transcripts/<page_id>.txt
metadata/manifest.csv
annotations/<page_id>.xml  # gdy istnieje PAGE XML
```

Eksport `PDF + Markdown/YAML` jest pochodną dla OlmOCR. Dla Qwen i Muse można
z tego samego źródła utworzyć JSONL z `image`, `prompt`, `target`. To gwarantuje
możliwość zmiany modelu bez ponownej transkrypcji, utraty metadanych lub
nieuczciwego porównania.

## Rekomendowane działania w kolejności

1. Naprawić renderer PDF w kontenerze OlmOCR i zakończyć smoke test adaptera.
2. Przygotować kanoniczny manifest oraz pilot 300-500 stron według ręki.
3. Uruchomić OlmOCR i bazowy Qwen2.5-VL-7B na identycznym pilocie.
4. Równolegle zrobić krótkie sprawdzenie Muse 30B na LUMI: pobranie wag,
   ładowanie vision modelu, jeden forward pass, LoRA smoke test i koszt pamięci.
5. Dopiero po tabeli dev/test wybrać model do tysięcy stron.

## Konkluzja

Nie ma dziś podstaw, by ogłosić OlmOCR bezwarunkowo najlepszym modelem dla
polskiego HTR. Jest natomiast najlepiej przygotowanym, otwartym i technicznie
zweryfikowanym kandydatem dla LUMI. Najbezpieczniejsza decyzja badawcza to
traktować go jako model główny w trzywariantowym pilocie, nie jako jedyny model
przed wykonaniem porównania z Qwen2.5-VL i Muse Glimmer 30B.
