# Комплект исследования голосовой биометрии

## Файлы

- `voice_biometric_paper.docx` — расширенная рукопись на русском языке.
- `voice_biometric_paper.pdf` — PDF для просмотра и рецензирования.
- `voice_biometric_study.py` — расчёт FAR, FRR, EER, APCER, BPCER и построение русскоязычных графиков.
- `results/` — CSV, JSON и PNG контрольного прогона.

## Как воспроизвести контрольный прогон

```bash
python voice_biometric_study.py --out results
```

Фиксированный seed: `20261108`; по 240 наблюдений на класс. После запуска сравните `results_asv.csv` и `results_pad.csv` с таблицей в рукописи. Дополнительная проверка метрик выполняется командой:

```bash
python - <<'PY'
import numpy as np
from voice_biometric_study import simulate, metrics
base, pad, d = simulate()
assert ((base[['FAR','FRR','APCER','BPCER']] >= 0) & (base[['FAR','FRR','APCER','BPCER']] <= 1)).all().all()
print('metric tests passed')
PY
```

## Откуда брать реальные данные

Для итогового benchmark используйте официальные наборы ASVspoof:

- ASVspoof 2019: <https://www.asvspoof.org/index2019.html>
- ASVspoof 2021 и ключи: <https://www.asvspoof.org/index2021.html>
- Zenodo LA: <https://zenodo.org/record/4837263>
- Zenodo PA: <https://zenodo.org/record/4834716>
- Zenodo DF: <https://zenodo.org/record/4835108>
- baseline-код: <https://github.com/asvspoof-challenge/2021>

ASVspoof 2021 DF архивы очень большие. Для проверки методики достаточно начать с LA/PA training и development, а evaluation оставить для финального запуска. Перед публикацией зафиксируйте дату скачивания, идентификатор Zenodo, хэш файла, версию модели и commit baseline-кода.

## Как заменить пилот на реальные аудиоданные

1. Скачайте архив и ключи с официальной страницы ASVspoof.
2. Распакуйте данные в каталог `data/`.
3. Прочитайте protocol/keys и сформируйте массивы `genuine`, `impostor`, `bona_fide`, `attacks`.
4. Получите `s_ASV` от выбранной ASV-модели и `s_PAD` от PAD-модели.
5. Замените функцию `simulate()` загрузчиком протокола, сохранив интерфейс массивов.
6. Калибруйте пороги только на development, а evaluation используйте один раз.
7. Сохраните CSV, конфигурацию, seed, версии библиотек и commit модели.

Текущие результаты являются воспроизводимым контрольным экспериментом для проверки методики. Они не выдаются за полную оценку ASVspoof 2021.

## Реальный benchmark, включённый в рукопись

В каталог `asvspoof_repo/` загружен открытый репозиторий с полным описанием фактического прогона на ASVspoof 2019 LA и выборке ASVspoof 2021 LA. Аудит таблицы выполнен командой:

```bash
python audit_real_benchmark.py
```

Аудит проверяет диапазоны метрик, наличие всех трёх split и строит `results/fig_real_benchmark.png`. Зафиксированный commit: `78ac594bdec572f9f222b01be6a947a41c2d820c`.

Результаты лучшей модели WavLM frozen layer 3 + MLP:

- ASVspoof 2019 dev: EER 0,27%, FAR 0,26%, FRR 0,27%, n=24 844;
- ASVspoof 2019 eval: EER 2,09%, FAR 7,37%, FRR 0,48%, n=71 237;
- ASVspoof 2021 LA eval: EER 9,05%, FAR 8,02%, FRR 10,26%, n=29 636.

Эти результаты получены на реальных аудиоданных и официальных протоколах, а не на сгенерированных score-распределениях. Контрольный пилот сохраняется отдельно для проверки формул и кода.
