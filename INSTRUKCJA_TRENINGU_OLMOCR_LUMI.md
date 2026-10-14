# Instrukcja treningu OlmOCR dla HTR na LUMI

## 1. Cel i decyzja modelowa

Cel: dostrojenie modelu `allenai/olmOCR-2-7B-1025` do rozpoznawania konkretnego
pisma recznego na podstawie skanow stron i wykonanych recznie transkrypcji.
Podejscie podstawowe to **LoRA w BF16**, nie trening modelu od zera. Model BF16
sluzy do uczenia; po pozytywnej ewaluacji mozna scalic adapter z wagami i
utworzyc wariant FP8 do wydajnego rozpoznawania.

Nie stosujemy Kraken. RolmOCR moze wystapic jedynie jako baseline porownawczy.

## 2. Co zostalo juz sprawdzone

- LUMI-G udostepnia AMD MI250X; jedno zadanie `--gpus=1` ma jeden GCD i 64 GiB.
- Oficjalny OlmOCR 2 wykonuje inferencje na tym GPU.
- Oficjalny kod `olmocr.train.train` importuje sie w przygotowanej warstwie.
- Model BF16 zostal pobrany na `/scratch/project_465003327`.
- Pelne ladowanie 8,3 mld parametrow i utworzenie LoRA (5 046 272 trenowalnych
  parametrow) powiodlo sie na jednym GCD.
- Bloker do usuniecia przed treningiem: kontener nie ma polecen `pdfinfo` i
  `pdftoppm`, ktorych upstreamowy renderer PDF uzywa. Nalezy dodac Poppler do
  obrazu/warstwy projektu albo zastosowac przetestowany renderer Pythonowy.

Szczegoly testu: `RESULTS_2026-09-28.md`.

## 3. Organizacja danych i dyskow

| Lokalizacja | Zawartosc |
| --- | --- |
| lokalny dysk | zrodla skanow, transkrypcje, kontrola jakosci |
| `/project/project_465003327/olmocr_vlm` | kod, konfiguracje, manifesty, logi, wyniki i finalne adaptery |
| `/scratch/project_465003327/olmocr_vlm` | wagi BF16, dane robocze, cache, checkpointy, renderowane strony |

`/scratch` jest przestrzenia robocza; po kazdym zakonczonym eksperymencie trzeba
skopiowac adapter, konfiguracje, manifest, metryki i logi do `/project` oraz na
dysk lokalny. Nie przechowujemy jedynej kopii wyniku na `/scratch`.

## 4. Przygotowanie materialu

### 4.1 Zasady danych

Kazda para treningowa musi miec:

1. jeden obraz jednej strony;
2. jedna reczna transkrypcje tej samej strony;
3. stabilny identyfikator strony, rekopisu, jednostki archiwalnej i reki;
4. informacje o jezyku, obrocie i ewentualnej tabeli/diagramie.

Nie wolno trenowac na predykcjach OCR jako etykietach. Tekst musi byc reczna
transkrypcja albo uprzednio zweryfikowana korekta. Puste, uszkodzone i
niedopasowane pary wyklucza sie z manifestu z podaniem przyczyny.

### 4.2 Podzial naukowy

Podzial wykonuje sie **wedlug rekopisu/reki**, nie losowo wedlug stron. Strony
tego samego dokumentu lub tej samej reki nie moga trafic jednoczesnie do train i
test. Zalecany uklad dla tysiecy stron:

| zbior | udzial | rola |
| --- | ---: | --- |
| train | 70-80% | aktualizacja adaptera |
| dev | 10-15% | dobor epoki, learning rate i rank LoRA |
| test-in-domain | 10-15% | finalna ocena nowych stron tych samych rak |
| test-cross-hand | osobny | generalizacja na inne rece/dokumenty |

Tworzymy niezmienny `manifest.csv` z kolumnami: `page_id`, `document_id`,
`hand_id`, `source_path`, `transcript_path`, `sha256_image`, `sha256_text`,
`split`, `exclusion_reason`. Manifest dostaje numer wersji i hash.

### 4.3 Format OlmOCR

OlmOCR oczekuje pary jednostronicowy PDF + Markdown o tej samej nazwie:

```text
train/000123.pdf
train/000123.md
```

```markdown
---
primary_language: pl
is_rotation_valid: true
rotation_correction: 0
is_table: false
is_diagram: false
---
Ręczna transkrypcja strony...
```

Skrypt `prepare_olmocr_pilot_data.py` realizuje ten eksport dla obecnej probki.
Przed produkcja trzeba rozszerzyc go o manifest, SHA-256 i podzial wedlug reki.

## 5. Kontrola jakosci przed transferem

1. Sprawdz liczbe obrazow, transkrypcji i kompletnych par.
2. Waliduj UTF-8, usuń BOM, znormalizuj tekst do Unicode NFC.
3. Zidentyfikuj puste teksty, duplikaty, uszkodzone PDF/JPG i nadmiernie krotkie
   lub dlugie transkrypcje.
4. Losowo zrecenzuj co najmniej 1-2% par wizualnie.
5. Zapisz raport czyszczenia oraz liste wykluczen.
6. Zamroz manifest przed pierwszym treningiem; zmiana danych oznacza nowa wersje.

## 6. Konfiguracja LUMI

Login: `ssh lumi`; konto Slurm: `project_465003327`; uzytkownik: `<LUMI_USER>`.

Kontener:

```bash
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
```

Warstwa Pythona utworzona podczas testu:

```text
/scratch/project_465003327/olmocr_vlm/train_python_compatible
```

Przy wywolaniu Singularity zmienne musza zostac przekazane **wewnatrz**
polecenia, np.:

```bash
singularity run "$SIF" env \
  PYTHONPATH="$packages:$root/software/olmocr" \
  HF_HOME=/scratch/project_465003327/olmocr_vlm/hf_cache \
  python -m olmocr.train.train --config "$config"
```

Nie instalujemy pakietow do centralnego obrazu. Wersje, hash kodu OlmOCR i
`pip freeze` zapisywane sa dla kazdego eksperymentu.

## 7. Naprawa renderera PDF

Przed ponowieniem LoRA wykonaj osobny job walidacyjny na 2 PDF-ach. Musi on
udowodnic, ze z poziomu kontenera dzialaja renderowanie i odczyt rozmiaru strony.

Akceptowalne rozwiazania:

1. warstwa projektu z Poppler (`pdfinfo`, `pdftoppm`) widoczna w `PATH` kontenera;
2. kontrolowana modyfikacja forkowanego `olmocr.data.renderpdf`, wykorzystujaca
   `pypdf` i `pypdfium2`, z testem obrazowym porownanym z Popplerem.

Nie kontynuuj treningu dopoki job walidacyjny nie zwroci poprawnego PNG dla
wszystkich stron kontrolnych.

## 8. Etapy treningu

### Etap A: smoke test

- 2 strony train, 1 strona eval;
- `lora_rank=8`, batch 1, 1 epoka, gradient accumulation 1;
- zapis adaptera i loss;
- cel: potwierdzenie calego lancucha, nie pomiar jakosci.

Akceptacja: brak OOM, poprawne renderowanie, niepusty checkpoint LoRA, skonczenie
Slurm `COMPLETED`.

### Etap B: pilot metodyczny

- 100-300 stron train i 20-50 dev, rozdzielonych wedlug reki;
- porownaj rank LoRA 8 i 16 oraz 2 learning rates (`1e-5`, `2e-5`);
- 2-5 epok, checkpoint po epoce;
- wybierz konfiguracje po dev CER/WER, nie po stracie treningowej.

### Etap C: trening glowny

- tysiace stron w train, zamrozony dev i test;
- zaczynaj od wybranej konfiguracji z Etapu B;
- batch 1 na GCD, `gradient_accumulation_steps` 8-32 zalezne od dlugosci tekstow;
- LoRA rank 8 jako punkt startowy; rank 16 tylko gdy dev wyraznie zyskuje;
- checkpoint po kazdej epoce, `save_total_limit=3`;
- limit czasu jobu 4-12 h oraz mozliwosc wznowienia z checkpointu.

Przy tysiacach stron lepiej uzyc kilku powtarzalnych jobow z resume niz jednego
niekontrolowanego zadania wielodniowego.

## 9. Minimalna konfiguracja LoRA

Punktem wyjscia jest `configs/olmocr_lora_smoke.yaml`. Dla produkcji zmieniamy
wylacznie sciezki danych, nazwe eksperymentu, liczbę epok i akumulacje:

```yaml
model:
  name: /scratch/project_465003327/olmocr_vlm/models/olmocr-2-7b-1025-bf16
  torch_dtype: bfloat16
  use_lora: true
  lora_rank: 8
  lora_alpha: 32
  lora_target_modules: [q_proj, k_proj, v_proj, o_proj]
training:
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 16
  gradient_checkpointing: true
  learning_rate: 2e-5
  save_strategy: epoch
  evaluation_strategy: epoch
```

Nie trenuj FP8 bezposrednio jako domyslnej konfiguracji. Oficjalny proces
OlmOCR trenuje BF16, a FP8 jest etapem optymalizacji po treningu.

## 10. Monitorowanie i automatyzacja

Kazdy job ma zapisywac:

- stdout/stderr do `/project/.../logs`;
- numer jobu, konfiguracje, manifest i commit kodu;
- stan `sacct`, czas, RAM, przydzial GPU;
- loss treningowy i dev loss po epoce;
- checkpoint/adaptor w `/scratch`, a po sukcesie kopie w `/project`.

Monitorowanie bez stalego komputera:

```bash
ssh lumi 'squeue -u <LUMI_USER>'
ssh lumi 'sacct -j JOBID --format=JobID,State,ExitCode,Elapsed,MaxRSS'
```

Job po sukcesie treningu powinien automatycznie uruchamiac inferencje na test
oraz skrypt metryk przez zaleznosc Slurm `--dependency=afterok:JOBID`.

## 11. Ewaluacja

### 11.1 Protokol

1. Generuj predykcje tylko dla testu niewidzialnego w treningu i doborze hiperparametrow.
2. Zapisz surowy tekst modelu bez recznej korekty.
3. Policz CER i WER po jawnie opisanej normalizacji NFC.
4. Podaj wyniki laczne, mediane stron, kwartyle oraz wyniki dla kazdej reki.
5. Osobno ocen test-in-domain i test-cross-hand.
6. Zrecenzuj jakosciowo reprezentatywne bledy: opuszczenia, halucynacje,
   rozwijanie skrotow, cyfry, nazwy wlasne, interpunkcja i zmiana kolejnosci.

Sam niski loss nie jest dowodem poprawnego HTR. Nalezy kontrolowac stosunek
dlugosci predykcji do referencji; duze odchylenie ujawnia nadgenerowanie lub
opuszczenia, ktore CER/WER laczne moga maskowac.

### 11.2 Baselines i publikacja

W artykule porownujemy co najmniej:

1. OlmOCR BF16/FP8 bez dostrojenia;
2. OlmOCR + LoRA po wybranej epoce;
3. opcjonalnie RolmOCR jako VLM baseline.

Dla kazdego wariantu raportujemy dane, podzial wedlug reki, parametry LoRA,
sprzet, wersje oprogramowania, czas i zuzycie GPU oraz metryki per strona.

## 12. Po treningu

1. Zachowaj najlepszy adapter i checkpoint wybrany na dev.
2. Scal adapter zgodnie z `prepare_olmocr_checkpoint.py`.
3. Wykonaj test BF16 na zbiorze testowym.
4. Dopiero po zachowaniu wyniku BF16 wykonaj opcjonalna kwantyzacje FP8 i
   ponow test, aby potwierdzic brak istotnej degradacji.
5. Skopiuj do `/project` i lokalnie: adapter, config, manifest, metryki, logi,
   wersje pakietow, predykcje i tabele do artykulu.

## 13. Kryteria decyzji

- **Przechodzimy dalej:** smoke test poprawny, dev CER spada wobec modelu bazowego,
  brak nadgenerowania w probie jakosciowej.
- **Zmiana hiperparametrow:** dev pogarsza sie lub roznica miedzy epokami wskazuje
  przeuczenie.
- **Zmiana danych/metody:** brak poprawy na wielu seedach, bledne pary,
  zbyt mieszane rece lub test nie jest niezalezny.
- **Nie publikujemy wniosku ogolnego:** gdy podzial nie jest wedlug reki lub
  liczba niezaleznych dokumentow jest za mala.

## 14. Checklist przed glownym wsadem

- [ ] Renderer PDF dziala wewnatrz kontenera.
- [ ] Manifest i hashe sa zamrozone.
- [ ] Train/dev/test nie dziela tej samej reki lub dokumentu.
- [ ] Smoke test zapisal adapter.
- [ ] Pilot wybral rank, learning rate i epoke na dev.
- [ ] Test pozostaje nietkniety do koncowej oceny.
- [ ] Wyniki i logi maja automatyczna kopie poza `/scratch`.
