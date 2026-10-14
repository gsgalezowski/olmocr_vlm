# Protokol testu LUMI: OlmOCR dla HTR

## Cel

Sprawdzenie na LUMI-G calkowitego lancucha dla VLM OCR: uruchomienie modelu,
przetworzenie skanu, porownanie z reczna transkrypcja, przygotowanie danych do
dostrajania oraz sprawdzenie importu oficjalnego kodu treningowego OlmOCR.

## Modele

- Pierwszy model: `allenai/olmOCR-2-7B-1025-FP8`.
- Model porownawczy: `reducto/RolmOCR`.
- Oba sa uruchamiane bez narzedzi Kraken i bez klasycznego silnika HTR.

## Material i granice wnioskowania

Do testu technicznego wykorzystano pary JPG/TXT z
`[local source collection]`.
Pliki TXT sa recznymi transkrypcjami stron. Zestaw szesciu stron sluzy tylko do
oceny technicznej. Nie jest to jeszcze finalny, niezalezny podzial wedlug
rekopisu, reki pisarskiej lub zespolu archiwalnego, wiec nie wolno go opisywac
jako wynikow koncowego eksperymentu naukowego.

## Metryki

Skrypty normalizuja tekst do Unicode NFC i licza CER oraz WER przez odleglosc
Levenshteina. Poza wartoscia laczna zostana zapisane wyniki dla kazdej strony,
zeby mozna bylo wykryc strony nietypowe i halucynacje.

## Dane do LoRA

`prepare_olmocr_pilot_data.py` przygotowal 98 niepustych par JPG/TXT w formacie
zgodnym z instrukcja treningowa OlmOCR: jednoplikowy PDF na strone i Markdown z
front matter YAML. Podzial ma charakter techniczny: 81 train, 10 dev, 7
within-corpus check; jedna pusta transkrypcja zostala wykluczona.

## Zasady LUMI

- Centralny kontener ROCm nie jest modyfikowany.
- Wagi, dane robocze i checkpointy maja trafic do `/scratch/project_465003327`.
- Do `/project/project_465003327` trafiaja kod, adapter LoRA, wyniki i logi.
- Kazdy job Slurm zapisuje stdout, stderr, zuzycie pamieci i stan zakonczenia.
- Najpierw weryfikujemy kompatybilnosc zaleznosci i pojedynczy krok LoRA; dopiero
  potem planuje sie wielogodzinne dostrajanie.
