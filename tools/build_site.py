from __future__ import annotations

import html
import json
import re
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DOCX_FILES = [
    "Ответы Гос 1-19 Эдиториал Дизайн Контент.docx",
    "ГОСЫ 20-38 (2).docx",
    "20-57_исправлено (1).docx",
]

QUESTION_TITLES = {
    1: "Актуальные тенденции эдиториал-дизайна.",
    2: "Основные принципы верстки текста. Сущности и стили. Базовые элементы верстки текста.",
    3: "Основы типографики при работе с текстами.",
    4: "Работа с графикой. Правила визуализации данных. Инфографика.",
    5: "Бильд-редактура. Правила подбора, редактирования и композиционного оформления изображений в верстке текстового контента.",
    6: "Понятие модульной верстки.",
    7: "Верстка посадочных страниц в конструкторе Tilda. Обзор функционала и шаблонов.",
    8: "Правила оформления текста в цифровых носителях. Возможности и функционал современных ресурсов.",
    9: "Работа с текстами в интерфейсах.",
    10: "Контент-стратегия. Отличия от контент-плана и медиа-стратегии.",
    11: "Методы анализа конкурентов и целевой аудитории.",
    12: "Типы и форматы контента. Аудиоконтент. Квизы. Игры.",
    13: "Медиа-контент тестовых цифровых ресурсов. Интерактивный контент. Игры.",
    14: "Принципы работы цифровой редакции.",
    15: "Авторское право при работе с текстами и изображениями.",
    16: "Сторителлинг.",
    17: "Смешанный графический контент. Рекомендации по формированию графического контента цифрового ресурса смешанной направленности. Современные стилистические тенденции проектирования, реализации и интеграции графического контента.",
    18: "Общие правила организации графического контента. Законы колористики, влияющие на восприятия графического контента цифрового ресурса.",
    19: "Общие правила организации графического контента. Правила композиции, влияющие на проектирование и размещение графического контента. Декоративные и функциональные компоненты графического контента.",
    20: "Инструментальная среда реализации графического контента.",
    21: "Виды цифровых ресурсов. Виды контента. Распространённые модели сочетания.",
    22: "3D как элемент графического контента. Типографика как элемент графического контента. Инструменты реализации.",
    23: "Инфографика как элемент графического контента. Инструменты реализации.",
    24: "Иллюстрация как элемент графического контента. Фотография как элемент графического контента.",
    25: "Графический контент цифрового ресурса коммерческой направленности. Рекомендации по формированию графического контента цифрового ресурса коммерческой направленности.",
    26: "Графический контент цифрового ресурса образовательной направленности. Рекомендации по формированию графического контента цифрового ресурса образовательной направленности.",
    27: "Графический контент цифрового ресурса развлекательной направленности. Рекомендации по формированию графического контента цифрового ресурса развлекательной направленности.",
    28: "Зарождение и этапы развития кинематографа.",
    29: "Развитие кинематографа в XX веке. Ключевые режиссеры.",
    30: "Этапы работы над создание фильма.",
    31: "Написание сценария. Поиск идеи.",
    32: "Виды сценариев. Структура сценария.",
    33: "Диалог, ремарка, мизансцена. Адаптация сценария.",
    34: "Съемки. Организация съемок. Поиск локаций. Освещение и работа с ним на съемочной площадке.",
    35: "Виды камер и их особенности. Объективы для видеосъемки. Фокусное расстояние.",
    36: "Оборудование, применяемое для видео и киносъемки. Визуальные эффекты в видео и киносъемке.",
    37: "Композиция кадра. Целостность картины. Ракурс, охват и масштабы в съемках.",
    38: "Виды фильмов. Короткометражные и полнометражные фильмы.",
    39: "Виды фильмов. Рекламный ролик.",
    40: "Виды фильмов. Видеоочерк. Репортаж.",
    41: "Виды фильмов. Игровое кино.",
    42: "Особенности жанров. Система жанров в кинопроизводстве.",
    43: "Общие проблемы режиссуры актуального медиа-контента. Тенденции.",
    44: "Визуальные эффекты и интерактивные пользовательские интерфейсы. Применение Java Script библиотек.",
    45: "Языки описания сценариев. Виды, назначение, размещение в HTML-документе.",
    46: "Возможности HTML-форм для взаимодействия с пользователями. Типы элементов HTML-форм.",
    47: "Программные средства создания HTML-документов. Их виды и особенности.",
    48: "Векторная и растровая анимация (Особенности GIF и HTML5-анимации).",
    49: "Требования к иллюстрациям в Интернет. Особенности графических форматов (JPEG, GIF, PNG, SVG).",
    50: "CSS3-модуль Grid Layout. Основные составляющие компоновки Grid-макета.",
    51: "CSS3-модуль Flexible Box Layout. Основные составляющие компоновки Flexbox-макета.",
    52: "Стандарты HTML-5 и CSS3. Семантическая разметка и мультимедийные возможности.",
    53: "Структура и стилевое оформление Web-документов. Создание и использование каскадных таблиц стилей CSS.",
    54: "Основные понятия языка HTML (тэги и их параметры). Структура HTML-документа.",
    55: "Типовые макеты Web-сайтов.",
    56: "Классификация Web-сайтов.",
    57: "Определение, цели и задачи Web-дизайна.",
    58: "Информационные технологии. Основная терминология: информация, технология, ИТ, ИКТ. Промышленные революции, история развития. Третья промышленная революция и базовые ИТ.",
    59: "Четвертая промышленная революция, Индустрия 4.0, основная цель, принципы, основные технологии. Сквозные цифровые технологии и субтехнологии. Дорожные карты сквозных цифровых технологий. Современные тренды развития сквозных технологий. Цикл Хайпа.",
    60: "Программа «Цифровая экономика Российской Федерации», основные цели. Федеральный проекты программы \"Цифровые технологии\". Новые бизнес-модели цифровой экономики. Категории бизнес-моделей цифровой экономики.",
    61: "Определение, общие принципы построения и цели разработки информационных систем (ИС). Состав и структура информационных систем. Классификация ИС. Свойства ИС. Архитектура и жизненный цикл ИС. Модели жизненного цикла ИС. Комплекс стандартов на проектирование и разработку ИС.",
    62: "Определение, общие принципы построения и цели разработки информационных систем (ИС). Классификация ИС. Третья промышленная революция, назначение, виды и области применения ИС.",
    63: "Четвертая промышленная революция. Фабрики будущего. Умное производство, технологии, информационные системы управления умным производством. Киберфизические системы, определение, главная идея, применение. Умные города.",
    64: "Четвертая промышленная революция и цифровая трансформация предприятий. CALS-технологии, ЕИП, ИС управления жизненным циклом продукта.",
    65: "Четвертая промышленная революция. Классификация современных ИС. ИС управления жизненным циклом продукта. Системы управления корпоративным контентом предприятия.",
    66: "Модели данных. Типы моделей данных. Иерархические системы. Иерархическая модель данных. Сетевые системы. Сетевая модель данных. Реляционная модель данных, определение.",
    67: "Системы управления базами данных (СУБД). Общая классификация СУБД. Классификация СУБД по характеру использования информации, модели данных, способу доступа к данным.",
    68: "Системы управления базами данных (СУБД). Функции СУБД. Независимость данных, архитектура СУБД. Типология СУБД, краткое описание и сравнение типов СУБД. Преимущества и недостатки.",
    69: "Теоретические основы БД. Жизненный цикл БД. Основные этапы ЖЦ БД. Свойства БД. Теоретические основы БД. Типология БД, реляционные и нереляционные (NoSql и NewSql) базы данных, достоинства и недостатки. Требования АCID.",
    70: "Реляционная модель данных, основные понятия, компоненты модели. Реляционная алгебра. Ограничения целостности в реляционных БД. Объектно-связанная модель.",
    71: "Реляционная модель данных. Функциональная зависимость в отношениях. Теория нормальных форм. Особенности реляционной модели.",
    72: "Понятие технологии проектирования ИС. Технологии и методы проектирования ИС. Классификация методов проектирования. Классы технологий проектирования. Методологии проектирования. Регламентация процессов проектирования в отечественных и международных стандартах.",
    73: "Новые технологии проектирования и анализа систем. Основные подходы к управлению организацией; понятия системного, ситуационного директивного и функционального подходов. Процессный подход к организации деятельности организации. Основные элементы процессного подхода.",
    74: "Понятие бизнес-процесса (БП), выделение, классификация, способы описания. Инжиниринг и реинжиниринг БП, основные понятия и характеристики. Определяющие принципы реинжиниринга БП. Основные подходы и этапы реинжиниринга БП.",
    75: "Применение CASE-технологий для анализа бизнес-процессов предметной области. Методики концептуального проектирования IDEF (IDEFO, IDEF3 DFD, IDEF1).",
    76: "Выбор и реализация архитектуры ИС. Распределенная обработка данных. Системы распределенной обработки информации. Распределённые системы обработки данных.",
    77: "Распределенные базы данных. Система управления распределёнными базами данных. Архитектура ИС. Архитектура файл-сервер. Распределение функций в архитектуре клиент-сервер. Однозвенная, двухзвенная, трехзвенная и многозвенные архитектуры.",
    78: "Распределенные базы данных. Архитектура SOA, отличительные особенности.",
    79: "Понятие и особенности канонического проектирования ИС. Стандарты и стадии и канонического проектирования. Стандарты в области информационных систем, международный стандарт ISO/IEC 12207, стандарты комплекса ГОСТ34.",
    80: "Каноническое проектирование ИС. Предпроектное обследование объекта автоматизации. Разработка концепции ИС. Модели деятельности предприятий: модель \"как есть\"(\"as-is\") и модель \"как должно быть\"(\"to-be\"). Разработка проекта ТЭО.",
    81: "Каноническое проектирование ИС. Понятие и содержание технического задания на информационную систему. Содержание эскизного проекта. Технический проект ИС. Разработка проектных решений по системе и ее частям.",
    82: "Каноническое проектирование ИС. Организация разработки рабочего проекта ИС. Разработка и оформление рабочей документации. Внедрение информационной системы. Основы методологии внедрения, сопровождения и эксплуатации ИС: ITIL, ITSM, COBIT.",
    83: "Типовое проектирование ИС. Понятие типового элемента, предпосылки типизации. Объекты типизации. Понятие, виды и особенности типовых проектных решений (ТПР). Основные черты ТПР Методы типового проектирования. Достоинства и недостатки ТПР. Оценка эффективности использования типовых решений.",
    84: "Типовое проектное решение (ТПР). Классы и структура ТПР. Ключевые особенности технологии типового проектирования. Технологии параметрически-ориентированного и модельно-ориентированного проектирования.",
    85: "Каноническое проектирование ИС, модели ЖЦ ИС для канонического проектирования. Методология быстрой разработки приложений (RAD), модель ЖЦ ИС.",
}

STOP_WORDS = {
    "и", "в", "во", "на", "по", "с", "со", "к", "ко", "о", "об", "от", "до", "для", "при", "а", "но",
    "или", "это", "как", "что", "его", "ее", "её", "их", "он", "она", "они", "оно", "из", "за", "над", "под",
    "же", "ли", "не", "да", "то", "у", "без", "между", "через", "также", "быть", "является"
}

CATEGORY_RULES = [
    (range(1, 20), "Editorial и графический контент"),
    (range(20, 28), "Графический контент и цифровые ресурсы"),
    (range(28, 44), "Кино и режиссура"),
    (range(44, 58), "Web, HTML, CSS и интерфейсы"),
    (range(58, 86), "Информационные системы и цифровая экономика"),
]


def read_docx_text(path: Path) -> str:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        xml_text = zf.read("word/document.xml")
    root = ET.fromstring(xml_text)
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", ns):
        parts: list[str] = []
        for node in paragraph.iter():
            if node.tag == f"{{{ns['w']}}}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{{{ns['w']}}}tab":
                parts.append("\t")
            elif node.tag == f"{{{ns['w']}}}br":
                parts.append("\n")
        line = "".join(parts).strip()
        paragraphs.append(line)
    text = "\n".join(paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_title(title: str) -> str:
    title = re.sub(r"^Вопрос\s+", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"^\d+[.)]\s*", "", title).strip()
    title = re.sub(r"\s+", " ", title)
    return title.strip()


def normalize_heading(value: str) -> str:
    value = unicodedata.normalize("NFKC", value.lower().replace("ё", "е"))
    value = re.sub(r"[^a-zа-я0-9]+", " ", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", value).strip()


def title_matches_question(number: int, candidate_title: str) -> bool:
    expected = normalize_heading(QUESTION_TITLES[number])
    candidate = normalize_heading(candidate_title)
    if not candidate:
        return False
    if candidate == expected or candidate.startswith(expected) or expected.startswith(candidate):
        return True

    expected_tokens = [token for token in expected.split() if token not in STOP_WORDS and len(token) > 3]
    candidate_tokens = [token for token in candidate.split() if token not in STOP_WORDS and len(token) > 3]
    if not expected_tokens or not candidate_tokens:
        return False

    overlap = len(set(expected_tokens) & set(candidate_tokens))
    required = max(2, int(min(len(expected_tokens), len(candidate_tokens)) * 0.65))
    return overlap >= required


def split_answers(text: str) -> dict[int, str]:
    pattern = re.compile(r"(?m)^\s*(?:Вопрос\s+)?(\d{1,2})[.)]\s+(.+?)\s*$")
    matches = [
        m
        for m in pattern.finditer(text)
        if 1 <= int(m.group(1)) <= 85
        and "\t" not in m.group(2)
        and title_matches_question(int(m.group(1)), m.group(2))
    ]
    answers: dict[int, str] = {}
    for idx, match in enumerate(matches):
        number = int(match.group(1))
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        body = re.sub(r"\n{3,}", "\n\n", body)
        if body and number not in answers:
            answers[number] = body
    return answers


def category_for(number: int) -> str:
    for numbers, name in CATEGORY_RULES:
        if number in numbers:
            return name
    return "Общее"


def words_for(text: str, limit: int = 9) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text.lower().replace("ё", "е"))
    words = re.findall(r"[a-zа-я0-9]{4,}", normalized, flags=re.IGNORECASE)
    seen: set[str] = set()
    result: list[str] = []
    for word in words:
        if word in STOP_WORDS or word in seen:
            continue
        seen.add(word)
        result.append(word)
        if len(result) == limit:
            break
    return result


def is_section_heading(line: str) -> bool:
    clean = line.strip()
    lower = clean.lower().replace("ё", "е")
    heading_phrases = (
        "определение", "общая теория", "развернутый ответ", "примеры", "краткий вывод",
        "виды", "основные", "требования", "рекомендации", "типичные ошибки",
        "инструменты", "структура", "этапы", "функции", "особенности", "сравнение"
    )
    if len(clean) > 96:
        return False
    if re.match(r"^\d+[.)]\s+", clean):
        return False
    if lower.rstrip(".").startswith(heading_phrases):
        return True
    return not clean.endswith((".", "!", "?", ":", ";", ",")) and len(clean.split()) <= 7


def is_list_line(line: str) -> bool:
    clean = line.strip()
    if not clean or re.match(r"^\d+[.)]\s+", clean) or is_section_heading(clean):
        return False
    if len(clean) > 110:
        return False
    if clean.endswith((",", ";")):
        return True
    if clean[0].islower() and len(clean.split()) <= 7:
        return True
    return False


def clean_list_item(line: str) -> str:
    return html.escape(line.strip().rstrip(" ,;"))


def emphasize_definition(paragraph: str) -> str:
    safe = html.escape(paragraph)
    match = re.match(r"^([^.!?]{2,90}?\s+—\s+это)\b", safe)
    if match:
        head = match.group(1)
        safe = f"<strong>{head}</strong>{safe[len(head):]}"
    return safe


def split_inline_list(line: str) -> tuple[str, list[str]] | None:
    markers = ("К ним относятся:", "включает:", "включают:", "относятся:", "используются:", "выделяют:")
    for marker in markers:
        if marker in line:
            prefix, tail = line.split(marker, 1)
            items = [item.strip().rstrip(".;") for item in tail.split(",") if item.strip()]
            if len(items) >= 3:
                return f"{prefix.strip()} {marker}", items
    return None


def flush_paragraph(buffer: list[str], result: list[str], *, lead: bool = False) -> bool:
    if not buffer:
        return False
    paragraph = " ".join(part.strip() for part in buffer if part.strip())
    paragraph = re.sub(r"\s+", " ", paragraph).strip()
    if paragraph:
        class_name = " class=\"answer-lead\"" if lead else ""
        result.append(f"<p{class_name}>{emphasize_definition(paragraph)}</p>")
    buffer.clear()
    return bool(paragraph)


def flush_numbered_items(items: list[tuple[str, str]], result: list[str]) -> None:
    if not items:
        return
    rendered: list[str] = []
    for _, content in items:
        inline = split_inline_list(content)
        if inline:
            intro, subitems = inline
            rendered.append(
                f"<li>{emphasize_definition(intro)}<ul>"
                + "".join(f"<li>{html.escape(item)}</li>" for item in subitems)
                + "</ul></li>"
            )
        else:
            rendered.append(f"<li>{emphasize_definition(content.strip())}</li>")
    result.append("<ol>" + "".join(rendered) + "</ol>")


def collect_inline_sublist(lines: list[str], start: int) -> tuple[list[str], int]:
    items: list[str] = []
    i = start
    while i < len(lines):
        current = lines[i]
        if re.match(r"^\d+[.)]\s+", current) or is_section_heading(current):
            break
        if not is_list_line(current):
            break
        normalized = current.rstrip(" ,;")
        items.append(normalized)
        i += 1
        if current.endswith("."):
            break
    return items, i


def paragraphs_to_html(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "<p class=\"muted\">Ответ пока не добавлен. Когда появится файл с оставшимися вопросами, данные можно будет обновить.</p>"

    result: list[str] = []
    paragraph: list[str] = []
    paragraph_count = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        numbered_match = re.match(r"^(\d+)[.)]\s+(.+)$", line)
        if numbered_match:
            if flush_paragraph(paragraph, result, lead=paragraph_count == 0):
                paragraph_count += 1
            items: list[tuple[str, str]] = []
            while i < len(lines):
                match = re.match(r"^(\d+)[.)]\s+(.+)$", lines[i])
                if not match:
                    break
                current_number = int(match.group(1))
                current_text_parts = [match.group(2).strip()]
                i += 1
                if current_text_parts[0].endswith(":"):
                    subitems, i = collect_inline_sublist(lines, i)
                    if subitems:
                        current_text_parts.append(", ".join(subitems))
                items.append((str(current_number), " ".join(current_text_parts)))
            flush_numbered_items(items, result)
            continue

        if is_section_heading(line):
            if flush_paragraph(paragraph, result, lead=paragraph_count == 0):
                paragraph_count += 1
            result.append(f"<h4>{html.escape(line.strip().rstrip('.'))}</h4>")
            i += 1
            continue

        if is_list_line(line):
            if flush_paragraph(paragraph, result, lead=paragraph_count == 0):
                paragraph_count += 1
            items: list[str] = []
            while i < len(lines) and is_list_line(lines[i]):
                items.append(f"<li>{clean_list_item(lines[i])}</li>")
                i += 1
            if len(items) == 1:
                result.append(f"<p>{items[0][4:-5]}</p>")
            else:
                result.append("<ul>" + "".join(items) + "</ul>")
            continue

        paragraph.append(line)
        if len(" ".join(paragraph)) > 420:
            flush_paragraph(paragraph, result, lead=paragraph_count == 0)
            paragraph_count += 1
        i += 1

    flush_paragraph(paragraph, result, lead=paragraph_count == 0)
    return "\n".join(result)


def build_questions() -> list[dict[str, object]]:
    answer_map: dict[int, str] = {}
    sources: dict[int, str] = {}
    raw_texts: dict[str, str] = {}
    for name in DOCX_FILES:
        path = ROOT / name
        text = read_docx_text(path)
        raw_texts[name] = text
        for number, answer in split_answers(text).items():
            answer_map[number] = answer
            sources[number] = name

    questions: list[dict[str, object]] = []
    for number in range(1, 86):
        title = QUESTION_TITLES[number]
        answer = answer_map.get(number, "")
        plain = re.sub(r"\s+", " ", answer).strip()
        questions.append(
            {
                "id": number,
                "title": title,
                "category": category_for(number),
                "status": "ready" if answer else "missing",
                "source": sources.get(number, "ожидается файл с ответом"),
                "answer": answer,
                "answerHtml": paragraphs_to_html(answer),
                "keywords": words_for(f"{title} {plain}"),
                "excerpt": plain[:280] + ("..." if len(plain) > 280 else ""),
            }
        )

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "questions.json").write_text(
        json.dumps(questions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (data_dir / "raw-docx-text.json").write_text(
        json.dumps(raw_texts, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return questions


INDEX_HTML = """<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta name=\"description\" content=\"Шпаргалка к ГИА: быстрый поиск по вопросам и ответам ИТ-технологий цифрового контента.\">
  <title>ГОСBOOST — поиск по ответам ГИА</title>
  <link rel=\"stylesheet\" href=\"styles.css\">
  <script src=\"app.js\" defer></script>
</head>
<body>
  <header class=\"hero\">
    <section class=\"hero__content\" id=\"top\">
      <form class=\"search\" role=\"search\" aria-label=\"Поиск по вопросам\">
        <label class=\"search__label\" for=\"searchInput\">Поиск по вопросам</label>
        <div class=\"search__box\">
          <input id=\"searchInput\" name=\"q\" type=\"search\" autocomplete=\"off\" placeholder=\"Например: Grid, авторское право, 39, сценарий...\">
          <button class=\"button\" type=\"submit\">Найти</button>
        </div>
        <p class=\"search__hint\">Поиск работает по номеру, заголовку, ключевым словам и полному тексту ответа.</p>
      </form>
    </section>
  </header>

  <main>
    <section class=\"stats\" aria-label=\"Статистика базы\">
      <article class=\"stat\"><strong id=\"readyCount\">0</strong><span>ответов загружено</span></article>
      <article class=\"stat\"><strong id=\"totalCount\">85</strong><span>вопросов всего</span></article>
      <article class=\"stat\"><strong id=\"missingCount\">0</strong><span>ожидают файл</span></article>
    </section>

    <section class=\"layout\" id=\"questions\">
      <aside class=\"sidebar\" aria-label=\"Фильтры\">
        <div class=\"panel\">
          <h2>Разделы</h2>
          <div class=\"chips\" id=\"categoryFilters\"></div>
        </div>
        <div class=\"panel\">
          <h2>Подсказка</h2>
          <p>Нажми на результат или карточку. Ссылка сохранится в адресе, поэтому можно быстро вернуться к конкретному вопросу.</p>
        </div>
      </aside>

      <section class=\"content\" aria-live=\"polite\">
        <div class=\"resultsbar\">
          <div>
            <p class=\"eyebrow\">Результаты</p>
            <h2 id=\"resultTitle\">Все вопросы</h2>
          </div>
          <button class=\"ghost-button\" id=\"clearSearch\" type=\"button\">Сбросить</button>
        </div>

        <div class=\"results\" id=\"results\"></div>
        <div class=\"answers\" id=\"answers\"></div>
      </section>
    </section>
  </main>

  <button class=\"to-top\" id=\"toTop\" type=\"button\" aria-label=\"Наверх\">↑</button>
</body>
</html>
"""

STYLES_CSS = """:root {
  --bg: #070b16;
  --bg-soft: #0d1426;
  --card: rgba(17, 25, 45, 0.86);
  --card-strong: #111a2f;
  --text: #e8eefc;
  --muted: #9aa8c7;
  --line: rgba(148, 163, 184, 0.18);
  --primary: #8b7cf6;
  --primary-dark: #b7adff;
  --accent: #20d3ff;
  --success: #55d98d;
  --warning: #fbbf24;
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
  --radius: 24px;
  --radius-sm: 14px;
  --container: min(1180px, calc(100vw - 32px));
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at 12% 0%, rgba(139, 124, 246, 0.26), transparent 34rem),
    radial-gradient(circle at 88% 8%, rgba(32, 211, 255, 0.18), transparent 30rem),
    linear-gradient(180deg, #070b16 0%, #0a1020 46%, #0b1224 100%);
  line-height: 1.65;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(to bottom, black, transparent 72%);
}

button,
input {
  font: inherit;
}

a {
  color: inherit;
}

.hero {
  min-height: 220px;
  color: #fff;
  background:
    linear-gradient(135deg, rgba(7, 11, 22, 0.96), rgba(22, 18, 58, 0.92)),
    radial-gradient(circle at 80% 30%, rgba(32, 211, 255, 0.22), transparent 24rem),
    var(--bg);
  border-bottom-left-radius: 34px;
  border-bottom-right-radius: 34px;
  overflow: hidden;
  position: relative;
}

.hero::after {
  content: "";
  position: absolute;
  width: 460px;
  height: 460px;
  right: -120px;
  bottom: -180px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.34), rgba(108, 92, 231, 0.16));
  filter: blur(2px);
}

.hero__content,
.stats,
.layout {
  width: var(--container);
  margin-inline: auto;
}

.hero__content {
  position: relative;
  z-index: 2;
  max-width: 920px;
  padding: 42px 0 64px;
}

.eyebrow {
  margin: 0 0 10px;
  color: var(--primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero .eyebrow {
  color: #78e9ff;
}

h1,
h2,
h3 {
  line-height: 1.08;
  margin: 0;
}

h1 {
  max-width: 880px;
  font-size: clamp(2.3rem, 7vw, 5.6rem);
  letter-spacing: -0.06em;
}

.hero__lead {
  max-width: 760px;
  margin: 26px 0 32px;
  color: rgba(255, 255, 255, 0.78);
  font-size: clamp(1.05rem, 2vw, 1.35rem);
}

.search {
  max-width: 920px;
  padding: 18px;
  border-radius: 26px;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(16px);
}

.search__label {
  display: block;
  margin: 0 0 10px 4px;
  font-weight: 700;
}

.search__box {
  display: flex;
  gap: 10px;
}

.search input {
  min-width: 0;
  flex: 1;
  height: 58px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 18px;
  padding: 0 18px;
  outline: none;
  color: var(--text);
  background: rgba(2, 6, 23, 0.84);
}

.search input::placeholder {
  color: #7786a8;
}

.search input:focus {
  box-shadow: 0 0 0 4px rgba(0, 212, 255, 0.24);
}

.button,
.ghost-button,
.chip,
.to-top {
  border: 0;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.button {
  min-width: 132px;
  height: 58px;
  border-radius: 18px;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  box-shadow: 0 16px 36px rgba(0, 212, 255, 0.24);
}

.button:hover,
.ghost-button:hover,
.chip:hover,
.to-top:hover {
  transform: translateY(-1px);
}

.search__hint {
  margin: 12px 4px 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 22px;
  position: relative;
  z-index: 3;
}

.stat {
  min-height: 112px;
  padding: 22px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: linear-gradient(180deg, rgba(20, 30, 53, 0.96), rgba(13, 20, 38, 0.96));
  box-shadow: var(--shadow);
}

.stat strong {
  display: block;
  font-size: 2.2rem;
  line-height: 1;
}

.stat span {
  color: var(--muted);
  font-weight: 700;
}

.layout {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 22px;
  align-items: start;
  padding: 34px 0 80px;
}

.sidebar {
  position: sticky;
  top: 18px;
  display: grid;
  gap: 16px;
}

.panel,
.resultsbar,
.result-card,
.answer-card {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--card);
  box-shadow: 0 18px 52px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(12px);
}

.panel {
  padding: 20px;
}

.panel h2 {
  margin-bottom: 14px;
  font-size: 1rem;
}

.panel p {
  margin: 0;
  color: var(--muted);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 9px 12px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 999px;
  color: var(--text);
  background: rgba(139, 124, 246, 0.14);
  font-weight: 750;
}

.chip.is-active {
  color: #fff;
  background: var(--primary);
}

.content {
  min-width: 0;
}

.resultsbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px;
  margin-bottom: 18px;
}

.ghost-button {
  padding: 12px 16px;
  border: 1px solid rgba(139, 124, 246, 0.2);
  border-radius: 14px;
  color: var(--primary-dark);
  background: rgba(139, 124, 246, 0.14);
  font-weight: 800;
}

.results {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.result-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 14px;
  align-items: start;
  padding: 16px;
  text-decoration: none;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  height: 42px;
  padding: 0 10px;
  border-radius: 14px;
  color: #fff;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  font-weight: 900;
}

.result-card h3 {
  margin-bottom: 6px;
  font-size: 1.05rem;
}

.result-card p {
  margin: 0;
  color: var(--muted);
  font-size: 0.96rem;
}

.result-card__meta {
  white-space: nowrap;
  color: var(--muted);
  font-size: 0.84rem;
  font-weight: 800;
}

.answers {
  display: grid;
  gap: 18px;
}

.answer-card {
  overflow: hidden;
  scroll-margin-top: 18px;
}

.answer-card.is-highlighted {
  outline: 4px solid rgba(0, 212, 255, 0.32);
}

.answer-card__header {
  padding: 24px;
  background: linear-gradient(135deg, rgba(139, 124, 246, 0.13), rgba(32, 211, 255, 0.08));
  border-bottom: 1px solid var(--line);
}

.answer-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.answer-card h3 {
  font-size: clamp(1.28rem, 3vw, 2rem);
  letter-spacing: -0.03em;
}

.answer-card__body {
  padding: 8px 24px 28px;
  max-width: 82ch;
}

.answer-card__body p {
  margin: 18px 0 0;
}

.answer-card__body .answer-lead {
  margin-top: 22px;
  padding: 18px 20px;
  border-left: 5px solid var(--primary);
  border-radius: 0 18px 18px 0;
  background: rgba(139, 124, 246, 0.12);
  font-size: 1.06rem;
}

.answer-card__body h4 {
  margin: 30px 0 10px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
  color: var(--primary-dark);
  font-size: 1.05rem;
  letter-spacing: 0.02em;
}

.answer-card__body ul,
.answer-card__body ol {
  margin: 14px 0 22px;
  padding: 16px 18px 16px 42px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 18px;
  background: rgba(2, 6, 23, 0.28);
}

.answer-card__body li {
  margin: 8px 0;
  padding-left: 4px;
}

.answer-card__body strong {
  color: #ffffff;
  font-weight: 850;
}

.meta-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 999px;
  color: var(--muted);
  background: rgba(2, 6, 23, 0.34);
  font-size: 0.84rem;
  font-weight: 800;
}

.status-ready {
  color: var(--success);
}

.status-missing {
  color: var(--warning);
}

mark {
  padding: 0 0.16em;
  border-radius: 0.24em;
  background: rgba(255, 214, 10, 0.55);
  color: inherit;
}

.muted {
  color: var(--muted);
}

.empty {
  padding: 28px;
  border: 1px dashed rgba(139, 124, 246, 0.36);
  border-radius: var(--radius);
  color: var(--muted);
  background: rgba(17, 25, 45, 0.68);
}

.to-top {
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 10;
  display: none;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  color: #fff;
  background: var(--primary);
  box-shadow: var(--shadow);
}

.to-top.is-visible {
  display: block;
}

@media (max-width: 900px) {
  :root {
    --container: min(100vw - 24px, 760px);
  }

  .hero {
    min-height: auto;
    border-bottom-left-radius: 28px;
    border-bottom-right-radius: 28px;
  }

  .hero__content {
    padding: 28px 0 44px;
  }

  .stats {
    grid-template-columns: 1fr;
    margin-top: 18px;
  }

  .layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }
}

@media (max-width: 620px) {
  .search__box,
  .resultsbar,
  .answer-card__top {
    flex-direction: column;
  }

  .search {
    padding: 18px;
    border-radius: 24px;
  }

  .search__box {
    gap: 12px;
  }

  .search input {
    width: 100%;
    min-height: 68px;
    height: 68px;
    border-radius: 20px;
    font-size: 17px;
    padding: 0 18px;
  }

  .button {
    width: 100%;
    min-height: 62px;
    height: 62px;
    border-radius: 20px;
    font-size: 17px;
  }

  .result-card {
    grid-template-columns: auto 1fr;
  }

  .result-card__meta {
    grid-column: 1 / -1;
  }

  .answer-card__header,
  .answer-card__body {
    padding-inline: 18px;
  }
}
"""

APP_JS = r"""const state = {
  questions: [],
  query: "",
  category: "all",
};

const els = {
  input: document.querySelector("#searchInput"),
  form: document.querySelector(".search"),
  results: document.querySelector("#results"),
  answers: document.querySelector("#answers"),
  resultTitle: document.querySelector("#resultTitle"),
  clearSearch: document.querySelector("#clearSearch"),
  readyCount: document.querySelector("#readyCount"),
  totalCount: document.querySelector("#totalCount"),
  missingCount: document.querySelector("#missingCount"),
  categoryFilters: document.querySelector("#categoryFilters"),
  toTop: document.querySelector("#toTop"),
};

const normalize = (value) => String(value || "")
  .toLowerCase()
  .replaceAll("ё", "е")
  .normalize("NFKC");

const escapeHtml = (value) => String(value || "").replace(/[&<>'"]/g, (char) => ({
  "&": "\\u0026amp;",
  "<": "\\u0026lt;",
  ">": "\\u0026gt;",
  "'": "\\u0026#039;",
  '"': "\\u0026quot;",
}[char]));

const stripHtml = (value) => {
  const node = document.createElement("div");
  node.innerHTML = value || "";
  return node.textContent || node.innerText || "";
};

function scoreQuestion(question, query) {
  if (!query) return 1;
  const normalizedQuery = normalize(query).trim();
  const tokens = normalizedQuery.split(/\s+/).filter(Boolean);
  const title = normalize(question.title);
  const answer = normalize(question.answer);
  const id = String(question.id);
  const combined = `${id} ${title} ${answer} ${normalize((question.keywords || []).join(" "))}`;
  let score = 0;

  if (id === normalizedQuery) score += 120;
  if (title.includes(normalizedQuery)) score += 80;
  if (answer.includes(normalizedQuery)) score += 38;

  tokens.forEach((token) => {
    if (id === token) score += 80;
    if (title.includes(token)) score += 22;
    if (answer.includes(token)) score += 8;
    if (combined.includes(token)) score += 3;
  });

  return score;
}

function getContext(question, query) {
  const plain = question.answer ? stripHtml(question.answerHtml) : question.excerpt;
  if (!query) return question.excerpt || plain.slice(0, 220);
  const normalizedPlain = normalize(plain);
  const token = normalize(query).split(/\s+/).find((part) => part.length > 2) || normalize(query);
  const index = normalizedPlain.indexOf(token);
  if (index < 0) return question.excerpt || plain.slice(0, 220);
  const start = Math.max(0, index - 115);
  const end = Math.min(plain.length, index + token.length + 165);
  return `${start > 0 ? "..." : ""}${plain.slice(start, end)}${end < plain.length ? "..." : ""}`;
}

function highlight(text, query) {
  const safe = escapeHtml(text);
  const tokens = normalize(query).split(/\s+/).filter((part) => part.length > 1);
  if (!tokens.length) return safe;
  const unique = [...new Set(tokens)].sort((a, b) => b.length - a.length);
  const pattern = unique.map((token) => token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");
  if (!pattern) return safe;
  return safe.replace(new RegExp(`(${pattern})`, "giu"), "<mark>$1</mark>");
}

function filteredQuestions() {
  const withScore = state.questions
    .filter((question) => state.category === "all" || question.category === state.category)
    .map((question) => ({ question, score: scoreQuestion(question, state.query) }))
    .filter((item) => !state.query || item.score > 0)
    .sort((a, b) => b.score - a.score || a.question.id - b.question.id);

  return withScore.map((item) => item.question);
}

function renderStats() {
  const ready = state.questions.filter((question) => question.status === "ready").length;
  els.readyCount.textContent = ready;
  els.totalCount.textContent = state.questions.length;
  els.missingCount.textContent = state.questions.length - ready;
}

function renderCategories() {
  const categories = ["all", ...new Set(state.questions.map((question) => question.category))];
  els.categoryFilters.innerHTML = categories.map((category) => {
    const label = category === "all" ? "Все" : category;
    const active = category === state.category ? " is-active" : "";
    return `<button class="chip${active}" type="button" data-category="${escapeHtml(category)}">${escapeHtml(label)}</button>`;
  }).join("");
}

function renderResults(questions) {
  if (!questions.length) {
    els.results.innerHTML = `<div class="empty">Ничего не найдено. Попробуй другое слово, номер вопроса или часть формулировки.</div>`;
    return;
  }

  els.results.innerHTML = questions.slice(0, 10).map((question) => {
    const context = getContext(question, state.query);
    return `
      <a class="result-card" href="#q-${question.id}" data-id="${question.id}">
        <span class="badge">${question.id}</span>
        <span>
          <h3>${highlight(question.title, state.query)}</h3>
          <p>${highlight(context, state.query)}</p>
        </span>
        <span class="result-card__meta">${question.status === "ready" ? "готов" : "нет ответа"}</span>
      </a>`;
  }).join("");
}

function renderAnswers(questions) {
  els.answers.innerHTML = questions.map((question) => {
    const statusClass = question.status === "ready" ? "status-ready" : "status-missing";
    const statusLabel = question.status === "ready" ? "ответ загружен" : "ожидается ответ";
    const body = question.status === "ready" ? question.answerHtml : `<p class="muted">Ответ пока не добавлен. Заголовок уже есть в базе, поэтому поиск по формулировке будет работать. Когда пришлёшь файл с ответами 58–85, базу можно обновить.</p>`;
    return `
      <article class="answer-card" id="q-${question.id}" data-id="${question.id}">
        <header class="answer-card__header">
          <div class="answer-card__top">
            <span class="badge">${question.id}</span>
            <a class="ghost-button" href="#q-${question.id}" aria-label="Ссылка на вопрос ${question.id}">#${question.id}</a>
          </div>
          <h3>${highlight(question.title, state.query)}</h3>
          <div class="meta-list">
            <span class="meta-pill ${statusClass}">${statusLabel}</span>
            <span class="meta-pill">${escapeHtml(question.category)}</span>
            <span class="meta-pill">Источник: ${escapeHtml(question.source)}</span>
          </div>
        </header>
        <div class="answer-card__body">${state.query ? highlightAnswerHtml(body, state.query) : body}</div>
      </article>`;
  }).join("");
}

function highlightAnswerHtml(html, query) {
  if (!query) return html;
  const wrapper = document.createElement("div");
  wrapper.innerHTML = html;
  const walker = document.createTreeWalker(wrapper, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  const tokens = normalize(query).split(/\s+/).filter((part) => part.length > 1);
  if (!tokens.length) return html;
  const pattern = tokens.map((token) => token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");
  const regex = new RegExp(`(${pattern})`, "giu");
  nodes.forEach((node) => {
    const value = node.nodeValue;
    if (!regex.test(value)) return;
    const span = document.createElement("span");
    span.innerHTML = escapeHtml(value).replace(regex, "<mark>$1</mark>");
    node.replaceWith(...span.childNodes);
  });
  return wrapper.innerHTML;
}

function syncUrl() {
  const params = new URLSearchParams();
  if (state.query) params.set("q", state.query);
  if (state.category !== "all") params.set("category", state.category);
  const next = `${location.pathname}${params.toString() ? `?${params}` : ""}${location.hash}`;
  history.replaceState(null, "", next);
}

function render() {
  const questions = filteredQuestions();
  els.resultTitle.textContent = state.query
    ? `Найдено: ${questions.length}`
    : state.category === "all" ? "Все вопросы" : state.category;
  renderCategories();
  renderResults(questions);
  renderAnswers(questions);
  syncUrl();
}

function jumpToFirstResult() {
  const first = filteredQuestions()[0];
  if (!first) return;
  requestAnimationFrame(() => {
    const card = document.querySelector(`#q-${first.id}`);
    if (!card) return;
    card.scrollIntoView({ behavior: "smooth", block: "start" });
    card.classList.add("is-highlighted");
    setTimeout(() => card.classList.remove("is-highlighted"), 1800);
  });
}

async function init() {
  const response = await fetch("data/questions.json");
  state.questions = await response.json();

  const params = new URLSearchParams(location.search);
  state.query = params.get("q") || "";
  state.category = params.get("category") || "all";
  els.input.value = state.query;

  renderStats();
  render();

  if (location.hash) {
    requestAnimationFrame(() => document.querySelector(location.hash)?.scrollIntoView({ block: "start" }));
  }
}

els.form.addEventListener("submit", (event) => {
  event.preventDefault();
  state.query = els.input.value.trim();
  render();
  jumpToFirstResult();
});

els.input.addEventListener("input", () => {
  state.query = els.input.value.trim();
  render();
});

els.clearSearch.addEventListener("click", () => {
  state.query = "";
  state.category = "all";
  els.input.value = "";
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

els.categoryFilters.addEventListener("click", (event) => {
  const button = event.target.closest("[data-category]");
  if (!button) return;
  state.category = button.dataset.category;
  render();
});

els.results.addEventListener("click", (event) => {
  const link = event.target.closest("[data-id]");
  if (!link) return;
  const id = link.dataset.id;
  requestAnimationFrame(() => {
    const card = document.querySelector(`#q-${id}`);
    card?.classList.add("is-highlighted");
    setTimeout(() => card?.classList.remove("is-highlighted"), 1800);
  });
});

window.addEventListener("scroll", () => {
  els.toTop.classList.toggle("is-visible", window.scrollY > 700);
});

els.toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

init().catch((error) => {
  console.error(error);
  els.answers.innerHTML = `<div class="empty">Не удалось загрузить базу вопросов. Проверь файл data/questions.json.</div>`;
});
"""

README_MD = """# ГОСBOOST

Адаптивная статическая шпаргалка для подготовки к ГИА по профилю «ИТ-технологии создания цифрового контента».

## Что умеет

- поиск по номеру вопроса;
- поиск по заголовку;
- поиск по тексту ответа и контексту;
- подсветка найденных слов;
- быстрый переход к найденному ответу;
- адаптация под телефон, планшет и desktop;
- заготовки для вопросов 58–85, пока нет файла с ответами.

## Как обновить базу

1. Добавить новый DOCX-файл с ответами в корень проекта.
2. Добавить имя файла в список `DOCX_FILES` в `tools/build_site.py`.
3. Запустить `python tools/build_site.py`.

После этого обновятся `data/questions.json` и статические файлы сайта.

## Как открыть

Лучше запускать через локальный сервер, потому что браузер может блокировать загрузку JSON при открытии напрямую из файла.

```bash
python -m http.server 8000
```

Затем открыть `http://localhost:8000/`.
"""


def write_site_files() -> None:
    (ROOT / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (ROOT / "styles.css").write_text(STYLES_CSS, encoding="utf-8")
    (ROOT / "app.js").write_text(APP_JS, encoding="utf-8")
    (ROOT / "README.md").write_text(README_MD, encoding="utf-8")


def main() -> None:
    questions = build_questions()
    write_site_files()
    ready = sum(1 for item in questions if item["status"] == "ready")
    missing = len(questions) - ready
    print(f"Built site: {ready} ready answers, {missing} placeholders, {len(questions)} total questions.")


if __name__ == "__main__":
    main()
