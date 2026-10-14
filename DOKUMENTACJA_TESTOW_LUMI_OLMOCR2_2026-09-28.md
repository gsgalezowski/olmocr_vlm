# Dokumentacja testow LUMI-G i OlmOCR 2

Data testow: 28 wrzesnia 2026.

Projekt LUMI: `project_465003327` (lokalna nazwa Slurm: `project_465003327`).
Uzytkownik wykonujacy: `<LUMI_USER>`. Katalog projektu na LUMI:
`/project/project_465003327/olmocr_vlm`.

Dokument jest zapisem testu technicznego i pilota badawczego. Nie przedstawia
wynikow jako reprezentatywnej oceny HTR dla calego korpusu historycznego.

## Cel

Sprawdzono, czy LUMI-G pozwala wykonac kompletny, reprodukowalny proces dla
wzmacnianego OCR/HTR opartego na modelu wizyjno-jezykowym:

1. uruchomienie modeli na AMD MI250X przez ROCm;
2. rozpoznanie skanu i porownanie z reczna transkrypcja;
3. przygotowanie par strona-transkrypcja w formacie oficjalnego treningu
   OlmOCR;
4. dostrojenie LoRA modelu BF16;
5. dekodowanie stron walidacyjnych niewykorzystanych do aktualizacji wag i
   obliczenie CER/WER;
6. zapis artefaktow, logow i checksum do audytu.

Nie uzyto Kraken ani klasycznego silnika HTR.

## Infrastruktura faktycznie uzyta

- LUMI-G, jedno przydzielone GCD AMD Instinct MI250X na zlecenie GPU;
- partycje Slurm: `dev-g` dla preflightu, `small-g` dla inferencji i LoRA,
  `small` dla pobran, ewaluacji oraz przygotowania zaleznosci;
- kontener: `/appl/local/laifs/containers/lumi-multitorch-latest.sif`;
- potwierdzone wersje: PyTorch `2.10.0+rocm7.0`, HIP `7.0.51831`,
  `transformers 5.10.1`, `vllm 0.22.1`, `flash-attn 2.8.3`;
- model treningowy: `allenai/olmOCR-2-7B-1025` w BF16;
- adapter: LoRA r=8, alpha=32, dropout=0.05 dla `q_proj`, `k_proj`, `v_proj`
  i `o_proj`; trenowano 5,046,272 z 8,297,212,928 parametrow (0.0608%).

Centralny kontener LUMI nie byl modyfikowany. Zaleznosci treningowe i wagi
robocze byly na `/scratch/project_465003327/olmocr_vlm`; kod, wyniki, logi i
adaptery byly zapisywane na `/project/project_465003327/olmocr_vlm`.

## Dane wykorzystane faktycznie w testach

Wszystkie strony ze znana transkrypcja pochodzily z lokalnego zasobu:

`[local source collection]`

Byly to skany JPG i recznie przygotowane pliki TXT, po jednym na strone.
Transkrypcje byly traktowane jako ground truth na poziomie strony. Zestaw
zostal przeksztalcony do wymaganej przez OlmOCR formy: jednoplanszowy PDF oraz
plik Markdown z front matter YAML.

| Rola | Liczba stron | Identyfikatory stron | Uwagi |
| --- | ---: | --- | --- |
| Porownanie zero-shot OlmOCR i Qwen | 6 | 2, 12, 33, 55, 71, 94 | Te same JPG/TXT dla obu modeli. |
| Jednostronicowy test RolmOCR i OlmOCR | 1 | 1 | Test zgodnosci modelu i GPU. |
| Korpus przygotowany do pilota LoRA | 98 | strona-transkrypcja | 81 train, 10 dev, 7 kontrola techniczna; jedna pusta transkrypcja wylaczona. |
| Wykonany szybki LoRA train | 10 | 10, 11, 13, 14, 15, 16, 17, 18, 20, 100 | Podzbior techniczny z przygotowanego korpusu. |
| Wykonana szybka walidacja LoRA | 2 | 19, 29 | Nie nalezaly do 10 stron treningowych, ale sluzyly do walidacji podczas treningu; nie sa niezaleznym testem koncowym. |
| Smoke LoRA | 2 train + 1 eval | osobny mini-podzbior | Test lancucha treningowego przed krotszym LoRA 10+2. |

Nie trenowano modelu na pozostalych katalogach roboczych, w tym na danych z
`[local source collection]`. Przeglad tych zasobow wykazal kandydatow
do pozniejszego korpusu, ale ich sciezki i/lub metadane wymagalby osobnej
weryfikacji licencji, kompletnej pary skan-transkrypcja oraz podzialu wedlug
rekopisu przed wlaczeniem do eksperymentu.

## Doslowne polecenia reprodukowalne

Ponizsze komendy sa kanonicznymi komendami wykonanymi przez Slurm. Ich pelna,
doslowna postac, lacznie z `#SBATCH`, znajduje sie w wskazanych plikach.
Skrypty i logi sa czescia archiwum audytowego na LUMI.

```bash
# Polaczenie i kontrola kolejki
ssh lumi
squeue -u <LUMI_USER>
sacct -u <LUMI_USER> -S 2026-09-28

# Kazdy job GPU ladowal ten sam oficjalny kontener LUMI
module purge
module load Local-LAIF lumi-aif-singularity-bindings
singularity run /appl/local/laifs/containers/lumi-multitorch-latest.sif ...

# Wlasciwy trening LoRA
sbatch /project/project_465003327/olmocr_vlm/21_lora_quick12.sbatch

# Ewaluacja stron walidacyjnych, kolejno adapter i baza
sbatch /project/project_465003327/olmocr_vlm/22_lora_heldout_eval.sbatch
sbatch /project/project_465003327/olmocr_vlm/23_base_heldout_eval.sbatch
```

Komenda treningowa z `21_lora_quick12.sbatch`:

```bash
singularity run "$sif" env \
  HF_HOME=/scratch/project_465003327/olmocr_vlm/hf_cache \
  PYTHONPATH="$packages:$root/software/olmocr" \
  python -m olmocr.train.train \
  --config "$root/configs/olmocr_lora_quick12.yaml"
```

Komenda post-treningowego rozpoznania z `22_lora_heldout_eval.sbatch`:

```bash
singularity run "$sif" env PYTHONPATH="$packages:$root/software/olmocr" \
  python "$root/scripts/run_lora_eval.py" \
  --model "$scratch/models/olmocr-2-7b-1025-bf16" \
  --adapter "$scratch/outputs/lora_quick12/lora-quick12-2026-09-28/checkpoint-10" \
  --input-dir "$scratch/data/quick_htr_data/eval" \
  --output-dir "$root/results/lora_quick12_heldout" --page 19 --page 29
```

Model bazowy byl uruchomiony tym samym skryptem i promptem, bez parametru
`--adapter`. Metryki liczono lokalnym skryptem z normalizacja Unicode NFC i
odlegloscia Levenshteina: CER na znakach, WER na tokenach rozdzielonych bialym
znakiem.

## Rejestr wszystkich zlecen Slurm

Tabela obejmuje wszystkie zlecenia utworzone podczas sesji, w tym nieudane i
anulowane proby techniczne. Zlecenia `ga-*` byly wczesniejszymi, niezwiazanymi
z OlmOCR probami i nie wplynely na wyniki opisane ponizej.

| Job ID | Nazwa | Stan | Czas | Znaczenie |
| --- | --- | --- | --- | --- |
| 22403846, 22403847 | `ga-htr-baseline`, `ga-htr-augment` | anulowane | 13:49 | Niezwiazane z VLM/OlmOCR; nie sa czescia analizy. |
| 22403848, 22403929 | `ga-segmenter` | fail/anulowane | 0:47, 10:38 | Niezwiazane z VLM/OlmOCR; nie sa czescia analizy. |
| 22405171 | `olmocr-rocm-check` | completed | 0:09 | Potwierdzil ROCm, PyTorch i widocznosc MI250X. |
| 22405219 | `rolmocr-download` | completed | 0:54 | Pobrano model porownawczy. |
| 22405250 | `rolmocr-one-page` | completed | 1:40 | RolmOCR zero-shot na stronie 1. |
| 22405441 | `olmocr2-download` | completed | 0:19 | Pobrano OlmOCR 2 FP8 do inferencji. |
| 22405464 | `olmocr2-one-page` | completed | 4:13 | OlmOCR zero-shot na stronie 1. |
| 22405783 | `olmocr2-batch6` | completed | 28:05 | OlmOCR zero-shot na 6 parach JPG/TXT. |
| 22405819 | `olmocr2-eval6` | completed | 0:21 | CER/WER dla 6 stron OlmOCR. |
| 22405945, 22406139, 22406361, 22406422, 22406555 | rozne preflighty treningu | fail/anulowane | do 3:08 | Diagnostyka zaleznosci, bez treningu modelu. |
| 22406138, 22406706 | zaleznosci bazowe | completed | 3:38, 2:52 | Przygotowanie kompatybilnego srodowiska treningowego. |
| 22406707 | `olmocr-train-import` | completed | 1:20 | Oficjalny modul `olmocr.train.train` zaimportowany poprawnie. |
| 22407055 | `olmocr-bf16-dl` | completed | 0:27 | Pobrano BF16 OlmOCR 2 do LoRA. |
| 22407056, 22407104, 22413525 | preflight LoRA | failed | do 1:57 | Ujawnily brak Poppler/PYTHONPATH; problem poprawiono. |
| 22413555 | `olmocr-lora-smoke` | completed | 3:04 | Poprawny smoke test LoRA, checkpoint-2. |
| 22413582 | `qwen25vl-download` | completed | 0:28 | Pobrano Qwen2.5-VL 7B. |
| 22413583 | `qwen25vl-batch6` | completed | 8:45 | Qwen na tych samych 6 stronach. |
| 22413584 | `muse30b-preflight` | completed | 0:03 | Sprawdzono metadane konfiguracji Muse-Glimmer-30B; wag nie pobierano. |
| 22413671 | `qwen25vl-eval6` | failed | 0:00 | Bledny interpreter `python` poza kontenerem; ponowiono poprawnie. |
| 22414368 | `qwen25vl-eval6` | completed | 0:26 | CER/WER Qwen na 6 stronach. |
| 22414398 | `olmocr-lora-quick12` | completed | 3:18 | LoRA: 10 train, 2 eval, checkpoint-10. |
| 22414685 | `olmocr-lora-heldout` | completed | 2:16 | Adapter LoRA na stronach 19 i 29. |
| 22414753 | `olmocr-base-heldout` | completed | 3:57 | Baza na stronach 19 i 29. |

## Wyniki istotne dla artykulu

Inferencje porownawcze wykonano wlasna, bezposrednia sciezka oparta na
Transformers, a nie kompletnym rekomendowanym toolkitem olmOCR z mechanizmami
renderowania, korekcji obrotu i ponawiania stron. Wyniki odnosza sie wylacznie
do tej konfiguracji i nie powinny byc przedstawiane jako ocena calego produktu
olmOCR.

### Zero-shot na szesciu stronach

| Model | CER pooled | WER pooled | Interpretacja |
| --- | ---: | ---: | --- |
| `reducto/RolmOCR` na stronie 1 | 0.818829 | 0.929032 | Wynik skrocony i nieadekwatny; odrzucony jako baza. |
| `allenai/olmOCR-2-7B-1025` | 1.698142 | 1.716266 | Dziala na LUMI, lecz bez adaptacji nadgeneruje na czesci rekopisu. |
| `Qwen/Qwen2.5-VL-7B-Instruct` | 1.970521 | 2.601664 | Slabszy od OlmOCR na identycznej probie, duze nadgenerowanie. |

### Efekt LoRA na dwoch stronach walidacyjnych

| Wariant | Strony | CER pooled | Obserwacja |
| --- | --- | ---: | --- |
| OlmOCR 2 BF16 bez adaptera | 19, 29 | 5.264778 | Strona 19: 9639 znakow predykcji wobec 441 referencji, CER 21.034014. |
| OlmOCR 2 BF16 + LoRA, 10 stron, 1 epoka | 19, 29 | 0.964827 | Znaczne ograniczenie nadgenerowania po adaptacji. |

Loss walidacyjny w treningu 10+2 zmienil sie z `1.443940` przed treningiem na
`1.441352` po 10 krokach. Adapter `checkpoint-10` ma 20 MB; SHA-256:

`e0da8ee777bea7334fab2377498e71251890393513cf1cff5438fc4a344660a7`

Zbyt mala liczebnosc (10 stron treningowych, 2 walidacyjne) oraz wykorzystanie
tych samych dwoch stron podczas walidacji treningu nie pozwalaja traktowac
spadku CER jako wyniku niezaleznego testu publikacyjnego. Obserwacja potwierdza
techniczna wykonalnosc procesu i uzasadnia dalsze dostrajanie.

## Dlaczego OlmOCR 2 wybrano do dalszych badan i treningu

1. Jest bezposrednio przeznaczony do OCR dokumentow i zwraca ustrukturyzowany
   Markdown z metadanymi strony, co odpowiada pozniejszej analizie dokumentow.
2. Model i oficjalny kod treningowy zostaly faktycznie uruchomione na LUMI-G:
   przetestowano pobieranie wag, ROCm, render PDF, dataloader, LoRA, optymalizator,
   checkpoint i walidacje. To nie jest wybor oparty tylko na dokumentacji.
3. W kontrolowanym porownaniu zero-shot na tych samych 6 stronach OlmOCR mial
   nizszy CER niz Qwen2.5-VL 7B (`1.698142` wobec `1.970521`).
4. RolmOCR dal niedostateczny wynik na stronie kontrolnej, a Qwen byl slabszy
   na calej probie. Muse-Glimmer-30B sprawdzono tylko konfiguracyjnie, bez
   testu wag ani treningu; nie moze byc przedstawiany jako kandydat porownany
   empirycznie.
5. Adapter LoRA jest bardzo maly wobec modelu bazowego i mozna go trenowac na
   pojedynczym GCD MI250X, co umozliwia kosztowo kontrolowane eksperymenty na
   tysiacach stron bez kopiowania pelnych wag modelu.
6. Krotka walidacja na stronach bez aktualizacji wag wskazala, ze adaptacja
   zmniejsza problem nadgenerowania w tej konfiguracji. Wymaga to potwierdzenia
   na duzym, stalym i niezaleznym zbiorze testowym rozdzielonym wedlug
   rekopisu lub reki pisarskiej.

Proponowane zdanie do komunikacji z tworcami OlmOCR 2:

> We selected olmOCR 2 as the base model because its official training stack
> ran end-to-end on LUMI-G AMD MI250X with BF16 LoRA, and it outperformed a
> Qwen2.5-VL-7B control on the same six manually transcribed historical pages.
> In a small validation pilot, LoRA also substantially reduced severe
> over-generation on pages excluded from gradient training. These pages were
> used for validation and do not constitute an independent final test set.
> The result will be tested on a larger manuscript-disjoint corpus using
> CER/WER.

## Artefakty do zachowania

Lokalnie, w tym katalogu:

- `RESULTS_2026-09-28.md` - skrot wynikow;
- `configs/olmocr_lora_quick12.yaml` - konfiguracja LoRA;
- `scripts/21_lora_quick12.sbatch` - trening;
- `scripts/22_lora_heldout_eval.sbatch` - inferencja adaptera;
- `scripts/23_base_heldout_eval.sbatch` - identyczny baseline;
- `results/*_evaluation/` - metryki CSV i JSON;
- `artifacts/olmocr_lora_quick12_checkpoint-10/` - adapter lokalny;
- `logs/` - logi krotszego treningu.

Na LUMI najpelniejsze archiwum audytowe:

`/project/project_465003327/olmocr_vlm/archives/olmocr_reproducibility_final_20260928T2035.tgz`

SHA-256 archiwum:

`e907df2fbd34ecff2d92734e5ff443d01aaa2f2b69a94d7408e76e31442cf59b`

## Ograniczenia i uczciwe sformulowanie do publikacji

- Test wykorzystuje niewielka i techniczna probke, nie pelny korpus.
- Dwie strony walidacyjne nie sa niezaleznym testem i nie sa wystarczajace do
  wnioskowania statystycznego.
- Metryki strony obejmuja caly output modelu, wraz z Markdown/front matter;
  przed publikacja nalezy ustalic jednolity protokol normalizacji oraz
  usuwania metadanych generatywnych.
- Podzial docelowy powinien zapobiegac przeciekowi wariantow tej samej reki,
  ksiegi albo szablonu miedzy train, dev i test.
- Opis LUMI nalezy przedstawic jako walidacje wykonalnosci i pilot adaptacji,
  nie jako finalne porownanie modeli HTR.
