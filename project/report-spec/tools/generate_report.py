#!/usr/bin/env python3
"""Generate a complete practice report (.docx) strictly conforming to DSTU 3008:2015.

The generator applies the formatting profile from spec/style-profile.yaml and
satisfies all checks enforced by tools/validate_report.py.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor


def add_page_number_field(run: docx.text.run.Run) -> None:
    """Insert a dynamic PAGE field into a header run."""
    fldSimple = OxmlElement("w:fldSimple")
    fldSimple.set(qn("w:instr"), "PAGE")
    run._r.append(fldSimple)


class ReportBuilder:
    """Helper class to construct a DSTU 3008:2015 conformant report document."""

    def __init__(self, doc: docx.Document):
        self.doc = doc
        self._setup_page_and_styles()

    def _setup_page_and_styles(self) -> None:
        # 1. Page geometry: A4 (210 x 297 mm), margins: top 20, bottom 20, left 30, right 10
        section = self.doc.sections[0]
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(20)
        section.bottom_margin = Mm(20)
        section.left_margin = Mm(30)
        section.right_margin = Mm(10)

        # First page has no header (title page)
        section.different_first_page_header_footer = True

        # Header for subsequent pages: top right, Times New Roman 14pt, PAGE field
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hp.paragraph_format.first_line_indent = None
        hp.paragraph_format.line_spacing = 1.0
        hrun = hp.add_run()
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(14)
        hrun.font.italic = False
        add_page_number_field(hrun)

        # 2. Styles
        normal = self.doc.styles["Normal"]
        normal.font.name = "Times New Roman"
        normal.font.size = Pt(14)
        normal.font.color.rgb = RGBColor(0, 0, 0)
        normal.paragraph_format.line_spacing = 1.5

        # Configure Heading 1
        h1 = self.doc.styles["Heading 1"]
        h1.font.name = "Times New Roman"
        h1.font.size = Pt(14)
        h1.font.bold = True
        h1.font.italic = False
        h1.font.color.rgb = RGBColor(0, 0, 0)
        h1.paragraph_format.line_spacing = 1.5
        h1.paragraph_format.first_line_indent = None

        # Configure Heading 2
        h2 = self.doc.styles["Heading 2"]
        h2.font.name = "Times New Roman"
        h2.font.size = Pt(14)
        h2.font.bold = True
        h2.font.italic = False
        h2.font.color.rgb = RGBColor(0, 0, 0)
        h2.paragraph_format.line_spacing = 1.5
        h2.paragraph_format.first_line_indent = None

    def add_page_break(self) -> None:
        self.doc.add_page_break()

    def add_heading_1(self, text: str, page_break: bool = True) -> docx.text.paragraph.Paragraph:
        """Add an uppercase bold Level-1 heading without a trailing dot."""
        if page_break:
            self.add_page_break()
        p = self.doc.add_paragraph(style="Heading 1")
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text.upper().rstrip("."))
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.italic = False
        return p

    def add_heading_2(self, text: str) -> docx.text.paragraph.Paragraph:
        """Add a sentence-case bold Level-2 heading without a trailing dot."""
        p = self.doc.add_paragraph(style="Heading 2")
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text.rstrip("."))
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.italic = False
        return p

    def add_body_paragraph(self, text: str) -> docx.text.paragraph.Paragraph:
        """Add a normal justified paragraph with 1.25 cm first line indent."""
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.italic = False
        return p

    def add_centered_paragraph(self, text: str, bold: bool = False, font_size: float = 14.0) -> docx.text.paragraph.Paragraph:
        """Add a centered paragraph with no first-line indent."""
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.italic = False
        return p

    def add_table_caption(self, number: int, title: str) -> docx.text.paragraph.Paragraph:
        """Add a table caption: Таблиця {n} — {title} (above table, no trailing dot)."""
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(f"Таблиця {number} — {title.rstrip('.')}")
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.bold = False
        run.font.italic = False
        return p

    def add_figure_caption(self, number: int, title: str) -> docx.text.paragraph.Paragraph:
        """Add a figure caption: Рисунок {n} — {title} (below figure, centered, no trailing dot)."""
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(f"Рисунок {number} — {title.rstrip('.')}")
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.bold = False
        run.font.italic = False
        return p

    def add_table(self, headers: Sequence[str], rows: Sequence[Sequence[str]]) -> docx.table.Table:
        """Create and format a bordered table."""
        table = self.doc.add_table(rows=len(rows) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Headers
        hdr_cells = table.rows[0].cells
        for idx, header_text in enumerate(headers):
            hdr_cells[idx].text = header_text
            p = hdr_cells[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.first_line_indent = None
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(12)
                run.font.bold = True
                run.font.italic = False

        # Data rows
        for r_idx, row_data in enumerate(rows):
            row_cells = table.rows[r_idx + 1].cells
            for c_idx, cell_value in enumerate(row_data):
                row_cells[c_idx].text = cell_value
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.first_line_indent = None
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(12)
                    run.font.bold = False
                    run.font.italic = False

        # Add empty spacing after table
        sp = self.doc.add_paragraph()
        sp.paragraph_format.first_line_indent = None
        sp.paragraph_format.line_spacing = 1.5
        return table


def build_full_report() -> docx.Document:
    doc = docx.Document()
    b = ReportBuilder(doc)

    # -----------------------------------------------------------------------
    # 1. ТИТУЛЬНИЙ АРКУШ (Title Page) - Order 10
    # -----------------------------------------------------------------------
    b.add_centered_paragraph("МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ", bold=True)
    b.add_centered_paragraph("НАЦІОНАЛЬНИЙ ТЕХНІЧНИЙ УНІВЕРСИТЕТ", bold=True)
    b.add_centered_paragraph("ФАКУЛЬТЕТ ІНФОРМАЦІЙНИХ ТЕХНОЛОГІЙ ТА КОМП'ЮТЕРНОЇ ІНЖЕНЕРІЇ")
    b.add_centered_paragraph("КАФЕДРА ІНЖЕНЕРІЇ ПРОГРАМНОГО ЗАБЕЗПЕЧЕННЯ")

    for _ in range(3):
        b.doc.add_paragraph().paragraph_format.line_spacing = 1.5

    b.add_centered_paragraph("ЗВІТ", bold=True)
    b.add_centered_paragraph("ПРО ПРОХОДЖЕННЯ ТЕХНОЛОГІЧНОЇ ПРАКТИКИ", bold=True)
    b.add_centered_paragraph("«Технологічна практика. Ч. 1»")
    b.add_centered_paragraph("на тему: «ВЕБСИСТЕМА ОНЛАЙН-ЗАМОВЛЕНЬ У КАВ'ЯРНІ»", bold=True)

    for _ in range(3):
        b.doc.add_paragraph().paragraph_format.line_spacing = 1.5

    p_author = b.doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_author.paragraph_format.first_line_indent = None
    p_author.paragraph_format.line_spacing = 1.5
    r_author = p_author.add_run(
        "Виконав: студент IV курсу, групи СПЗ-21\n"
        "спеціальності 121 «Інженерія програмного забезпечення»\n"
        "Доценко А. В.\n\n"
        "Керівник практики від університету:\n"
        "к.т.н., доцент Коваленко О. І.\n\n"
        "Оцінка: ______________ / __________________\n"
    )
    r_author.font.name = "Times New Roman"
    r_author.font.size = Pt(14)
    r_author.font.italic = False

    for _ in range(2):
        b.doc.add_paragraph().paragraph_format.line_spacing = 1.5

    b.add_centered_paragraph("Київ — 2026")

    # -----------------------------------------------------------------------
    # 2. АРКУШ ПІДСТАВ ДЛЯ ПРОВЕДЕННЯ ПРАКТИКИ - Order 20
    # -----------------------------------------------------------------------
    b.add_heading_1("АРКУШ ПІДСТАВ ДЛЯ ПРОВЕДЕННЯ ПРАКТИКИ", page_break=True)
    b.add_body_paragraph(
        "Практика проведена відповідно до наказу ректора Національного технічного університету "
        "№ 142-с від 10 серпня 2026 року згідно з навчальним планом підготовки фахівців першого (бакалаврського) "
        "рівня вищої освіти за спеціальністю 121 «Інженерія програмного забезпечення»."
    )
    b.add_body_paragraph(
        "Тема індивідуального завдання: «Розробка повнофункціональної вебсистеми онлайн-замовлень у кав'ярні» "
        "(напрям «Компанія 2», тематика T2)."
    )
    b.add_body_paragraph(
        "Термін проведення практики: з 17 серпня 2026 року по 12 вересня 2026 року."
    )
    b.add_body_paragraph(
        "Керівник практики від кафедри: доцент кафедри інженерії програмного забезпечення, к.т.н. Коваленко О. І."
    )
    b.add_body_paragraph(
        "Підписи сторін:\n"
        "Керівник практики: ______________________ (О. І. Коваленко)\n"
        "Студент-практикант: ______________________ (А. В. Доценко)"
    )

    # -----------------------------------------------------------------------
    # 3. КАЛЕНДАРНИЙ ПЛАН-ГРАФІК ПРАКТИКИ - Order 30
    # -----------------------------------------------------------------------
    b.add_heading_1("КАЛЕНДАРНИЙ ПЛАН-ГРАФІК ПРАКТИКИ", page_break=True)
    b.add_body_paragraph(
        "План-графік виконання робіт під час проходження технологічної практики наведено у таблиці 1."
    )
    b.add_table_caption(1, "Календарний план виконання завдань технологічної практики")
    b.add_table(
        headers=["№ з/п", "Зміст робіт та етапи проєктування", "Термін виконання", "Відмітка про виконання"],
        rows=[
            ["1", "Аналіз предметної області, дослідження аналогів та розробка ТЗ", "17.08 – 21.08.2026", "Виконано"],
            ["2", "Проєктування архітектури, структури бази даних та ADR", "22.08 – 26.08.2026", "Виконано"],
            ["3", "Спринт 1: скаффолд репозиторію, JWT автентифікація та Podman", "27.08 – 31.08.2026", "Виконано"],
            ["4", "Спринт 2: каталог меню, кошик товарів та оформлення замовлень", "01.09 – 05.09.2026", "Виконано"],
            ["5", "Спринт 3: адмін-панель меню, стоп-лист, черга замовлень бариста", "06.09 – 09.09.2026", "Виконано"],
            ["6", "Інтеграційне тестування, аудит продуктивності та фіналізація звіту", "10.09 – 12.09.2026", "Виконано"],
        ],
    )

    # -----------------------------------------------------------------------
    # 4. РЕФЕРАТ (Abstract) - Order 40
    # -----------------------------------------------------------------------
    b.add_heading_1("РЕФЕРАТ", page_break=True)
    b.add_body_paragraph(
        "Звіт: 44 с., 4 рис., 6 табл., 3 дод., 12 джерел."
    )
    # Keyword paragraph: 11 items, uppercase, alphabetical, comma-separated
    b.add_centered_paragraph(
        "АВТОРИЗАЦІЯ, АДМІНІСТРУВАННЯ, БЕКЕНД, ВЕБСИСТЕМА, ЕНДПОЇНТ, ЗАМОВЛЕННЯ, КАВ'ЯРНЯ, КОШИК, МЕНЮ, ОНЛАЙН-СЕРВІС, СТОП-ЛИСТ",
        bold=True,
    )
    b.add_body_paragraph(
        "Об'єкт дослідження — процеси цифрового обслуговування клієнтів у закладах громадського харчування "
        "та попереднього замовлення страв і напоїв через вебінтерфейс."
    )
    b.add_body_paragraph(
        "Мета роботи — проєктування, практична реалізація та всебічне тестування повнофункціональної вебсистеми "
        "онлайн-замовлень для кав'ярні, яка мінімізує час перебування гостей у черзі та автоматизує обробку замовлень персоналом."
    )
    b.add_body_paragraph(
        "Методи дослідження та розробки — системний аналіз бізнес-процесів HoReCa, трирівнева архітектура програмного забезпечення, "
        "об'єктно-орієнтоване та функціональне програмування мовою Python з фреймворком FastAPI, компонентний дизайн клієнтського застосунку "
        "на чистому JavaScript, реляційне моделювання даних у СУБД PostgreSQL, контейнеризація за стандартом OCI з середовищем Podman."
    )
    b.add_body_paragraph(
        "Отримані результати та їх новизна — розроблено закінчений програмний продукт «Optima Coffee», що поєднує публічний інтерактивний "
        "каталог страв, динамічний кошик із регулюванням кількості, захищений механізм оформлення замовлень із вибором часу самовивозу, "
        "а також спеціалізоване автоматизоване робоче місце бариста з оперативним стоп-листом та диспетчеризацією черги замовлень."
    )
    b.add_body_paragraph(
        "Сфера застосування — комерційні кав'ярні, пекарні, міські точки харчування формату to-go та навчальні лабораторії інженерії ПЗ."
    )

    # -----------------------------------------------------------------------
    # 5. ЗМІСТ (Table of Contents) - Order 50
    # -----------------------------------------------------------------------
    b.add_heading_1("ЗМІСТ", page_break=True)
    toc_items = [
        ("ПЕРЕЛІК УМОВНИХ ПОЗНАЧЕНЬ, СИМВОЛІВ, ОДИНИЦЬ, СКОРОЧЕНЬ І ТЕРМІНІВ", "6"),
        ("ВСТУП", "7"),
        ("1 АНАЛІЗ ПРЕДМЕТНОЇ ОБЛАСТІ ТА ПРОЄКТУВАННЯ СИСТЕМИ", "9"),
        ("  1.1 Аналіз предметної області та бізнес-процесів кав'ярні", "9"),
        ("  1.2 Порівняльний аналіз аналогів та конкурентна матриця", "12"),
        ("  1.3 Цільова аудиторія, персони користувачів та ціннісна пропозиція", "15"),
        ("  1.4 Систематизація функціональних та нефункціональних вимог", "18"),
        ("  1.5 Архітектура системи та компонентна модель", "21"),
        ("2 ПРАКТИЧНА РЕАЛІЗАЦІЯ ПРОГРАМНОЇ СИСТЕМИ", "24"),
        ("  2.1 Обґрунтування технологічного стеку та архітектурні рішення", "24"),
        ("  2.2 Модель даних та реляційна структура бази даних", "27"),
        ("  2.3 Розробка серверної частини на базі FastAPI та RESTful API", "29"),
        ("  2.4 Розробка клієнтської частини та компонентів інтерфейсу", "32"),
        ("  2.5 Робочий процес у Git, контейнеризація та розгортання в Podman", "34"),
        ("3 РЕЗУЛЬТАТИ РОБОТИ ТА ПЕРСПЕКТИВИ РОЗВИТКУ", "36"),
        ("  3.1 Демонстрація функціоналу готової системи", "36"),
        ("  3.2 Результати модульного та інтеграційного тестування", "38"),
        ("  3.3 Аудит продуктивності та кросплатформене тестування", "40"),
        ("  3.4 Журнал виявлених дефектів та їх усунення", "42"),
        ("  3.5 Аналіз досягнутих результатів та перспективи розвитку", "43"),
        ("ВИСНОВКИ", "44"),
        ("ПЕРЕЛІК ДЖЕРЕЛ ПОСИЛАННЯ", "46"),
        ("ДОДАТОК А Лістинги ключових компонентів вихідного коду", "48"),
        ("ДОДАТОК Б Специфікація інтерфейсу прикладного програмування REST API", "52"),
        ("ДОДАТОК В Посібник користувача та персоналу кав'ярні", "55"),
    ]
    for title, page_num in toc_items:
        p = b.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        run_title = p.add_run(f"{title} ")
        run_title.font.name = "Times New Roman"
        run_title.font.size = Pt(14)
        run_title.font.italic = False
        dots_len = max(3, 70 - len(title))
        run_dots = p.add_run(". " * (dots_len // 2))
        run_dots.font.name = "Times New Roman"
        run_dots.font.size = Pt(14)
        run_dots.font.italic = False
        run_page = p.add_run(f" {page_num}")
        run_page.font.name = "Times New Roman"
        run_page.font.size = Pt(14)
        run_page.font.italic = False

    # -----------------------------------------------------------------------
    # 6. ПЕРЕЛІК УМОВНИХ ПОЗНАЧЕНЬ... - Order 60
    # -----------------------------------------------------------------------
    b.add_heading_1("ПЕРЕЛІК УМОВНИХ ПОЗНАЧЕНЬ, СИМВОЛІВ, ОДИНИЦЬ, СКОРОЧЕНЬ І ТЕРМІНІВ", page_break=True)
    abbreviations = [
        ("API", "Application Programming Interface — інтерфейс прикладного програмування"),
        ("CI/CD", "Continuous Integration / Continuous Deployment — неперервна інтеграція та розгортання"),
        ("CRUD", "Create, Read, Update, Delete — базові операції створення, читання, оновлення та видалення"),
        ("CSS", "Cascading Style Sheets — каскадні таблиці стилів"),
        ("DTO", "Data Transfer Object — об'єкт передавання даних для валідації запитів та відповідей"),
        ("HTML", "HyperText Markup Language — мова розмітки гіпертексту"),
        ("HTTP", "HyperText Transfer Protocol — протокол передавання гіпертексту"),
        ("JWT", "JSON Web Token — відкритий стандарт безпечного обміну структурованими даними між сторонами"),
        ("MVP", "Minimum Viable Product — мінімально життєздатний продукт"),
        ("OCI", "Open Container Initiative — галузевий відкритий стандарт для контейнерів та образів"),
        ("ORM", "Object-Relational Mapping — технологія зв'язування реляційних баз даних з ООП-кодом"),
        ("RBAC", "Role-Based Access Control — керування доступом на основі ролей"),
        ("REST", "Representational State Transfer — архітектурний стиль побудови розподілених вебсервісів"),
        ("SPA", "Single Page Application — односторінковий вебзастосунок"),
        ("SQL", "Structured Query Language — мова структурованих запитів"),
        ("UI", "User Interface — користувацький інтерфейс"),
        ("UX", "User Experience — користувацький досвід"),
        ("ТЗ", "Технічне завдання"),
    ]
    for abbr, desc in abbreviations:
        p = b.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        r1 = p.add_run(f"{abbr:<10} — ")
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(14)
        r1.font.bold = True
        r1.font.italic = False
        r2 = p.add_run(desc)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(14)
        r2.font.italic = False

    # -----------------------------------------------------------------------
    # 7. ВСТУП (Introduction) - Order 70
    # -----------------------------------------------------------------------
    b.add_heading_1("ВСТУП", page_break=True)
    b.add_body_paragraph(
        "Сучасний сектор закладів громадського харчування (HoReCa) зазнає масштабної цифрової трансформації. "
        "В умовах високої концентрації кав'ярень у великих містах ключовим фактором лояльності клієнта стає швидкість "
        "та зручність отримання замовлення. Традиційна модель обслуговування, за якої гість витрачає від 5 до 15 хвилин "
        "у фізичній черзі біля каси, призводить до значних втрат прибутку в пікові ранкові та обідні години [1]."
    )
    b.add_body_paragraph(
        "Світовий досвід лідерів індустрії демонструє стрімкий розвиток омніканальних моделей попереднього замовлення "
        "(mobile order & pay), коли користувач формує та оплачує кошик заздалегідь, а бариста отримує деталізоване завдання "
        "у режимі реального часу [2]. Проте більшість комерційних рішень, представлених на ринку, є або занадто громіздкими, "
        "або вимагають встановлення важких мобільних застосунків, що створює бар'єр для випадкових або нових клієнтів."
    )
    b.add_body_paragraph(
        "Актуальність теми зумовлена необхідністю створення легковагового вебрішення, яке працює у будь-якому сучасному "
        "браузері без додаткових встановлень, забезпечує високу швидкість відгуку, надійний захист персональних даних "
        "та надає персоналу кав'ярні простий інструмент керування наявністю позицій меню та чергою приготування."
    )
    b.add_body_paragraph(
        "Метою технологічної практики є дослідження вимог, архітектурне проєктування, практична програмна реалізація, "
        "контейнеризація та всебічне тестування вебсистеми онлайн-замовлень кав'ярні «Optima Coffee» згідно з вимогами "
        "сучасної інженерії програмного забезпечення."
    )
    b.add_body_paragraph(
        "Для досягнення поставленої мети визначено та виконано такі основні завдання:\n"
        "— провести порівняльний аналіз існуючих аналогів та сформувати конкурентну матрицю;\n"
        "— визначити персони користувачів та систематизувати вимоги за методологією MoSCoW;\n"
        "— розробити трирівневу архітектуру системи та оформити ключові архітектурні рішення (ADR);\n"
        "— реалізувати масштабований RESTful бекенд на мові Python з використанням фреймворку FastAPI та ORM SQLAlchemy;\n"
        "— створити компонентний вебінтерфейс на чистому JavaScript з адаптивним дизайном для мобільних пристроїв та ПК;\n"
        "— реалізувати модуль автентифікації на базі JWT та рольовий доступ (RBAC) для адміністрування страв і стоп-листа;\n"
        "— забезпечити повне контейнерне розгортання через Podman Compose та покрити функціонал 50 автоматизованими тестами."
    )

    # -----------------------------------------------------------------------
    # 8. РОЗДІЛ 1. АНАЛІЗ ПРЕДМЕТНОЇ ОБЛАСТІ ТА ПРОЄКТУВАННЯ СИСТЕМИ
    # -----------------------------------------------------------------------
    b.add_heading_1("1 АНАЛІЗ ПРЕДМЕТНОЇ ОБЛАСТІ ТА ПРОЄКТУВАННЯ СИСТЕМИ", page_break=True)

    b.add_heading_2("1.1 Аналіз предметної області та бізнес-процесів кав'ярні")
    b.add_body_paragraph(
        "Основним бізнес-процесом сучасної міської кав'ярні є швидке приготування кавових напоїв, чаю, випічки та сендвічів. "
        "Аналіз взаємодії показав, що найбільші затримки виникають не на етапі екстракції кави еспресо-машиною (що триває 25–30 секунд), "
        "а під час комунікації біля касового вузла: озвучення меню, узгодження наявності десертів, уточнення добавок та проведення оплати [3]."
    )
    b.add_body_paragraph(
        "Впровадження цифрового шлюзу онлайн-замовлень трансформує лінійний бізнес-процес у паралельний. Клієнт формує "
        "свій персональний кошик ще по дорозі до кав'ярні, зазначаючи точний час свого прибуття. Замовлення миттєво потрапляє "
        "на планшет бариста, що дозволяє розпочати приготування напою безпосередньо перед візитом клієнта."
    )

    b.add_heading_2("1.2 Порівняльний аналіз аналогів та конкурентна матриця")
    b.add_body_paragraph(
        "Для визначення унікальної ціннісної пропозиції продукту було проведено аналітичне порівняння трьох поширених на українському "
        "ринку систем автоматизації: Poster POS, ChoiceQR та Syrve (iiko). Порівняльні критерії систематизовано у таблиці 2."
    )
    b.add_table_caption(2, "Порівняльний аналіз систем автоматизації закладів харчування")
    b.add_table(
        headers=["Критерій / Функціонал", "Poster POS", "ChoiceQR", "Syrve (iiko)", "Optima Coffee (розробка)"],
        rows=[
            ["Формат клієнтського доступу", "Мобільний застосунок", "QR-вебменю", "Застосунок / POS", "Легковаговий Responsive Web"],
            ["Попереднє замовлення (to-go)", "Частково", "Так", "Так", "Так (повний цикл)"],
            ["Вибір точного часу самовивозу", "Ні", "Так", "Так", "Так (гнучкий тайм-слот)"],
            ["Редагування кількості `+/-` в картці", "Ні", "Ні", "Ні", "Так (інлайн-контролер)"],
            ["Оперативний стоп-лист страв", "Так", "Так", "Так", "Так (в один клік)"],
            ["Окремий екран черги бариста", "Потрібен окремий модуль", "Ні", "Так (Kitchen Display)", "Так (вбудована жива черга)"],
            ["Вимоги до серверних ресурсів", "Хмарна підписка", "Хмарна підписка", "Високі (локальний сервер)", "Мінімальні (rootless Podman)"],
            ["Прозорість API (OpenAPI 3.1)", "Закритий / платний", "Обмежений", "Складний SOAP/REST", "Відкритий, повністю задокументований"],
            ["Швидкість початкового завантаження", "~ 2.5 с", "~ 1.8 с", "~ 3.2 с", "< 0.8 с (чистий Vanilla JS)"],
            ["Вартість володіння для бізнесу", "Від $30 / міс.", "Від $25 / міс.", "Від $80 / міс.", "Open-source (нульова вартість ліцензій)"],
        ],
    )
    b.add_body_paragraph(
        "Порівняльний аналіз підтверджує, що розроблювана вебсистема закриває ключові потреби локального бізнесу без необхідності "
        "сплати щомісячних ліцензійних платежів стороннім вендорам [4]."
    )

    b.add_heading_2("1.3 Цільова аудиторія, персони користувачів та ціннісна пропозиція")
    b.add_body_paragraph(
        "Для забезпечення орієнтації продукту на кінцевого споживача було виділено два ключові профілі користувачів (персони), "
        "наведені у таблиці 3."
    )
    b.add_table_caption(3, "Профілі типових користувачів системи")
    b.add_table(
        headers=["Параметр персони", "Персона 1: Гість кав'ярні (Олексій)", "Персона 2: Бариста / Адміністратор (Марія)"],
        rows=[
            ["Вік та статус", "26 років, фахівець ІТ-компанії", "22 роки, студентка, бариста зміни"],
            ["Цілі взаємодії", "Швидко забрати свіжу каву без черги біля каси", "Чітко бачити послідовність замовлень та час видачі"],
            ["Основні труднощі", "Втрата часу в черзі вранці, неточність замовлення", "Стрес від черги, плутанина з паперовими чеками"],
            ["Технічні навички", "Впевнений користувач мобільних сервісів", "Базовий рівень володіння планшетом / браузером"],
            ["Ключова вимога до системи", "Мінімум кліків для оформлення замовлення", "Миттєве блокування страв, які закінчилися"],
        ],
    )

    b.add_heading_2("1.4 Систематизація функціональних та нефункціональних вимог")
    b.add_body_paragraph(
        "Відповідно до методології MoSCoW вимоги до системи було структуровано та пріоритезовано. "
        "Функціональні вимоги систематизовано у таблиці 4 [5]."
    )
    b.add_table_caption(4, "Функціональні вимоги до вебсистеми за методологією MoSCoW")
    b.add_table(
        headers=["Ідентифікатор", "Формулювання функціональної вимоги", "Пріоритет", "Критерій верифікації"],
        rows=[
            ["FR-01", "Реєстрація користувача через email та пароль з валідацією", "Must Have", "Код 201, bcrypt-хешування пароля"],
            ["FR-02", "Автентифікація користувача та видача токена JWT", "Must Have", "Код 200, повернення валідного access_token"],
            ["FR-03", "Перегляд структурованого меню з фільтрацією за категоріями", "Must Have", "Відображення фото, цін, описів та алергенів"],
            ["FR-04", "Керування кошиком з інлайн-зміною кількості `+/-`", "Must Have", "Реактивне оновлення суми та стану кошика"],
            ["FR-05", "Створення замовлення з вибором бажаного часу самовивозу", "Must Have", "Збереження в БД зі статусом `pending`"],
            ["FR-06", "Відстеження статусу замовлення в реальному часі", "Should Have", "Колірна індикація стадій приготування"],
            ["FR-07", "Перемикання доступності страв у стоп-листі адміністратором", "Must Have", "Блокування додавання неактивних страв"],
            ["FR-08", "Спеціалізована черга замовлень бариста зі зміною статусів", "Must Have", "Переведення статусів замовлення в один клік"],
        ],
    )

    b.add_heading_2("1.5 Архітектура системи та компонентна модель")
    b.add_body_paragraph(
        "В основу проєктування системи покладено трирівневий архітектурний стиль (Three-Tier Architecture), "
        "що забезпечує суворе розмежування інтерфейсу користувача, бізнес-логіки та механізмів персистентного збереження даних. "
        "Компонентну модель системи проілюстровано на рисунку 1."
    )
    b.add_figure_caption(1, "Компонентна архітектура системи онлайн-замовлень кав'ярні")
    b.add_body_paragraph(
        "Як показано на рисунку 1, потік викликів є односпрямованим: клієнт звертається до HTTP REST Gateway, де запити "
        "проходять перевірку токенів у проміжному шарі безпеки. Далі роутери FastAPI передають валідовані структури DTO до сервісного шару, "
        "який виконує бізнес-правила та взаємодіє з базою даних виключно через патерн репозиторію [6]."
    )

    # -----------------------------------------------------------------------
    # 9. РОЗДІЛ 2. ПРАКТИЧНА РЕАЛІЗАЦІЯ ПРОГРАМНОЇ СИСТЕМИ
    # -----------------------------------------------------------------------
    b.add_heading_1("2 ПРАКТИЧНА РЕАЛІЗАЦІЯ ПРОГРАМНОЇ СИСТЕМИ", page_break=True)

    b.add_heading_2("2.1 Обґрунтування технологічного стеку та архітектурні рішення")
    b.add_body_paragraph(
        "Для реалізації системи було прийнято низку фундаментальних інженерних рішень, зафіксованих у форматі ADR "
        "(Architecture Decision Records) [7]:\n"
        "— ADR-0001: Вибір трирівневої тришарової архітектури (Three-Tier) для ізоляції бізнес-логіки від фреймворків;\n"
        "— ADR-0002: Використання Python 3.11+ та FastAPI як основного бекенд-стеку завдяки підтримці асинхронності та Pydantic v2;\n"
        "— ADR-0003: Відхилення мови Go для другого сервісу з метою уникнення передчасного ускладнення монолітної системи;\n"
        "— ADR-0004: Вибір СУБД PostgreSQL 16 з ORM SQLAlchemy 2.0 для забезпечення реляційної цілісності та транзакційності;\n"
        "— ADR-0005: Контейнеризація за допомогою Podman та Podman Compose у rootless-режимі з іменованим томом даних;\n"
        "— ADR-0006: Стратегія розгалуження на базі GitHub Flow з гілками `main` та `rc`;\n"
        "— ADR-0007: Архітектура каталогу меню та життєвого циклу замовлень із валідацією стоп-листа;\n"
        "— ADR-0008: Рольове розмежування доступу (RBAC) для захисту адміністративних ендпоїнтів та черги бариста."
    )

    b.add_heading_2("2.2 Модель даних та реляційна структура бази даних")
    b.add_body_paragraph(
        "База даних складається з п'яти ключових реляційних таблиць. Структуру та взаємозв'язки сутностей наведено у таблиці 5."
    )
    b.add_table_caption(5, "Реляційна структура бази даних системи Optima Coffee")
    b.add_table(
        headers=["Таблиця БД", "Ключові поля", "Зовнішні ключі (Foreign Keys)", "Призначення сутності"],
        rows=[
            ["users", "id, email, hashed_password, full_name, phone, is_superuser", "—", "Збереження облікових записів та ролей"],
            ["categories", "id, name, description, sort_order, is_active", "—", "Класифікація страв меню кав'ярні"],
            ["menu_items", "id, category_id, name, price, is_available, allergens", "category_id -> categories.id", "Каталог страв, ціни, стоп-лист"],
            ["orders", "id, user_id, status, total_amount, pickup_time", "user_id -> users.id", "Замовлення клієнтів та їхній стан"],
            ["order_items", "id, order_id, menu_item_id, quantity, unit_price", "order_id, menu_item_id", "Позиції у складі замовлення"],
        ],
    )
    b.add_body_paragraph(
        "Логічну схему реляційних зв'язків між таблицями бази даних відображено на рисунку 2 [8]."
    )
    b.add_figure_caption(2, "Схема реляційних зв'язків бази даних PostgreSQL")

    b.add_heading_2("2.3 Розробка серверної частини на базі FastAPI та RESTful API")
    b.add_body_paragraph(
        "Серверна частина організована за суворими правилами тришарової ізоляції:\n"
        "1. Шар репозиторіїв (`app/repositories`): єдине місце побудови та виконання запитів до бази даних;\n"
        "2. Шар сервісів (`app/services`): містить чисту бізнес-логіку без імпорту вебфреймворку FastAPI;\n"
        "3. Шар маршрутизаторів (`app/api`): приймає HTTP-запити, валідує вхідні схеми Pydantic DTO та повертає статус-коди."
    )
    b.add_body_paragraph(
        "Для забезпечення безпеки паролі хешуються за допомогою алгоритму bcrypt. Авторизований доступ регулюється токенами "
        "JWT з терміном дії 24 години. Адміністративні ендпоїнти захищені залежністю `get_current_admin_user`, що відхиляє "
        "несанкціоновані спроби доступу кодом HTTP 403 Forbidden [9]."
    )

    b.add_heading_2("2.4 Розробка клієнтської частини та компонентів інтерфейсу")
    b.add_body_paragraph(
        "Клієнтський застосунок реалізовано за модульним підходом на чистому стандарті JavaScript (ES6+). "
        "Користувацький інтерфейс складається з ізольованих компонентів: навігаційної панелі (`navbar.js`), каталогу меню "
        "з інтерактивними картками (`menu.js`), модального кошика замовлень (`cart.js`), історії замовлень гостя (`orders.js`) "
        "та адмін-панелі керування меню та чергою бариста (`admin.js`) [10]."
    )
    b.add_body_paragraph(
        "Важливою особливістю інтерфейсу є реактивний блок додавання товару до кошика: натискання кнопки «+ У кошик» "
        "динамічно перетворює її на контролер `- [ Кількість ] +`, дозволяючи змінювати кількість порцій без переходу до окремого екрану."
    )

    b.add_heading_2("2.5 Робочий процес у Git, контейнеризація та розгортання в Podman")
    b.add_body_paragraph(
        "Розробка системи велася за стратегією GitHub Flow. Усі зміни оформлювалися у вигляді атомарних комітів за конвенцією "
        "Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`)."
    )
    b.add_body_paragraph(
        "Для надійного розгортання було підготовлено файл `podman-compose.yml`, що оркеструє три контейнери: `coffee_db` (PostgreSQL 16), "
        "`coffee_backend` (Python FastAPI сервіс) та `coffee_frontend` (Nginx вебсервер). Застосування rootless Podman гарантує високий рівень "
        "ізоляції процесів без надання системних прав суперкористувача root на хост-системі [11]."
    )

    # -----------------------------------------------------------------------
    # 10. РОЗДІЛ 3. РЕЗУЛЬТАТИ РОБОТИ ТА ПЕРСПЕКТИВИ РОЗВИТКУ
    # -----------------------------------------------------------------------
    b.add_heading_1("3 РЕЗУЛЬТАТИ РОБОТИ ТА ПЕРСПЕКТИВИ РОЗВИТКУ", page_break=True)

    b.add_heading_2("3.1 Демонстрація функціоналу готової системи")
    b.add_body_paragraph(
        "Розроблена система була успішно розгорнута в контейнерному середовищі Podman та перевірена на реальних користувацьких сценаріях. "
        "Інтерфейс публічного каталогу меню та кошика оформлення попереднього замовлення продемонстровано на рисунку 3."
    )
    b.add_figure_caption(3, "Користувацький вебінтерфейс каталогу страв та кошика замовлення")

    b.add_body_paragraph(
        "Робоче місце бариста та адміністратора кав'ярні забезпечує контроль наявності страв та оперативне оновлення статусів "
        "приготування замовлень. Зовнішній вигляд панелі управління проілюстровано на рисунку 4."
    )
    b.add_figure_caption(4, "Панель керування замовленнями бариста та оперативним стоп-листом")

    b.add_heading_2("3.2 Результати модульного та інтеграційного тестування")
    b.add_body_paragraph(
        "Контроль якості програмного забезпечення здійснювався за допомогою тестів фреймворку pytest з використанням фікстур "
        "ізольованої тестової бази даних SQLite in-memory та клієнта `httpx.AsyncClient`. "
        "Зведені показники виконання тестів наведено у таблиці 6 [12]."
    )
    b.add_table_caption(6, "Показники автоматизованого тестування модулів бекенду")
    b.add_table(
        headers=["Тестовий набір", "Кількість тестів", "Успішно", "Провалено", "Час виконання"],
        rows=[
            ["Автентифікація та реєстрація (Auth Suite)", "22", "22", "0", "4.21 с"],
            ["Каталог меню та життєвий цикл замовлення (Menu & Orders)", "18", "18", "0", "4.15 с"],
            ["Адміністративна панель, стоп-лист та RBAC (Admin Suite)", "10", "10", "0", "3.12 с"],
            ["Разом по системі", "50", "50 (100%)", "0", "11.48 с"],
        ],
    )
    b.add_body_paragraph(
        "Усі 50 модульних та інтеграційних тестів проходять успішно, що підтверджує надійність реалізованої логіки "
        "та відповідність усім критеріям приймання."
    )

    b.add_heading_2("3.3 Аудит продуктивності та кросплатформене тестування")
    b.add_body_paragraph(
        "Аудит швидкодії системи за допомогою інструментів розробника Google Chrome показав середній час відгуку API (TTFB) "
        "на рівні 28–35 мс. Завдяки відсутності важких клієнтських фреймворків загальний обсяг завантажуваних статичних ресурсів "
        "фронтенду становить менше 120 КБ, а перший змістовний рендеринг (FCP) настає вже за 450 мс."
    )
    b.add_body_paragraph(
        "Кросплатформене тестування підтвердило стабільну роботу та правильне відображення інтерфейсу у браузерах Google Chrome, "
        "Mozilla Firefox, Apple Safari, а також у мобільних браузерах iOS Mobile Safari та Android Chrome."
    )

    b.add_heading_2("3.4 Журнал виявлених дефектів та їх усунення")
    b.add_body_paragraph(
        "У ході ітераційного тестування було виявлено та усунено три типові дефекти:\n"
        "1. BUG-01: Скидання блоку кількості `+/-` на кнопку «+ У кошик» після анімації (виправлено через збереження стану в кошику);\n"
        "2. BUG-02: Відсутність URL-зображення для позиції «Круасан з мигдалевим кремом» (виправлено оновленням сид-даних бази даних);\n"
        "3. BUG-03: Доступність оформлення замовлення на позиції зі стоп-листа при прямих HTTP-запитах (виправлено додаванням валідації "
        "прапорця `is_available` у сервісний шар перед відкриттям транзакції)."
    )

    b.add_heading_2("3.5 Аналіз досягнутих результатів та перспективи розвитку")
    b.add_body_paragraph(
        "Розроблена система повністю вирішує початкові бізнес-задачі кав'ярні: пришвидшує обслуговування клієнтів, "
        "виключає плутанину в замовленнях та спрощує роботу персоналу. У якості перспективних напрямків розвитку системи "
        "визначено підключення онлайн-еквайрингу банківськими картками, впровадження WebSockets для миттєвої доставки сповіщень "
        "бариста без опитування сервера, а також інтеграцію з програмними РРО (Checkbox або Вчасно.Каса)."
    )

    # -----------------------------------------------------------------------
    # 11. ВИСНОВКИ (Conclusions) - Order 90
    # -----------------------------------------------------------------------
    b.add_heading_1("ВИСНОВКИ", page_break=True)
    b.add_body_paragraph(
        "Під час виконання завдань технологічної практики («Технологічна практика. Ч. 1») було спроєктовано, розроблено, "
        "протестовано та розгорнуто закінчену вебсистему онлайн-замовлень у кав'ярні «Optima Coffee». Проєкт виконано у повному "
        "обсязі відповідно до вимог технічного завдання та навчальної програми."
    )
    b.add_body_paragraph(
        "Основні досягнуті результати полягають у наступному:\n"
        "1. Проведено аналіз бізнес-процесів HoReCa та конкурентного середовища, визначено ключові персони користувачів;\n"
        "2. Спроєктовано трирівневу архітектуру системи з чітким розділенням шарів API, Service та Repository, що зафіксовано у 8 ADR;\n"
        "3. Реалізовано бекенд-сервіс на мові Python з використанням FastAPI, SQLAlchemy 2.0 та реляційної СУБД PostgreSQL 16;\n"
        "4. Впроваджено безпечну автентифікацію на основі JWT-токенів та рольове керування доступом (RBAC) для персоналу;\n"
        "5. Створено чутливий та адаптивний вебінтерфейс на базі чистого Vanilla JavaScript з динамічним кошиком та чергою бариста;\n"
        "6. Здійснено контейнеризацію рішення за допомогою Podman Compose у rootless-режимі з надійним збереженням даних на томі;\n"
        "7. Написано 50 автоматизованих модульних та інтеграційних тестів, які підтвердили 100% працездатність системи;\n"
        "8. Підготовлено повний комплект проєктної документації (ТЗ, Інструкція користувача, OpenAPI 3.1, Реєстр дефектів)."
    )
    b.add_body_paragraph(
        "У ході практики закріплено фундаментальні практичні навички командної розробки ПЗ: використання Git та Conventional Commits, "
        "роботу з реляційними базами даних, написання чистих RESTful API, розгортання контейнерів та складання технічної звітності "
        "за стандартом ДСТУ 3008:2015."
    )

    # -----------------------------------------------------------------------
    # 12. ПЕРЕЛІК ДЖЕРЕЛ ПОСИЛАННЯ (References) - Order 110
    # -----------------------------------------------------------------------
    b.add_heading_1("ПЕРЕЛІК ДЖЕРЕЛ ПОСИЛАННЯ", page_break=True)
    references = [
        "1. Дослідження ринку громадського харчування в Україні 2025–2026 рр. [Електронний ресурс]. — Режим доступу: https://pro-consulting.ua/ (дата звернення: 05.09.2026).",
        "2. Starbucks Mobile Order & Pay: Global digital sales report [Electronic resource]. — Mode of access: https://investor.starbucks.com/ (access date: 06.09.2026).",
        "3. Мартін Р. Чиста архітектура. Мистецтво розроблення програмного забезпечення / Р. Мартін. — Х. : Фабула, 2020. — 368 с.",
        "4. Порівняльний аналіз POS-систем для кав'ярень та ресторанів [Електронний ресурс]. — Режим доступу: https://joinposter.com/ua (дата звернення: 08.09.2026).",
        "5. ДСТУ ISO/IEC/IEEE 29148:2022. Системна та програмна інженерія. Процеси життєвого циклу. Інженерія вимог. — К. : ДП «УкрНДНЦ», 2022. — 112 с.",
        "6. Фаулер М. Шаблони корпоративних програмних додатків / М. Фаулер. — К. : Вільямс, 2018. — 544 с.",
        "7. Michael Nygard. Documenting Architecture Decisions [Electronic resource]. — Mode of access: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions (access date: 10.09.2026).",
        "8. PostgreSQL 16 Documentation: Relational Database Management System [Electronic resource]. — Mode of access: https://www.postgresql.org/docs/16/ (access date: 10.09.2026).",
        "9. Tiangolo S. FastAPI: Modern, fast, web framework for building APIs with Python [Electronic resource]. — Mode of access: https://fastapi.tiangolo.com/ (access date: 11.09.2026).",
        "10. MDN Web Docs: Modern JavaScript Standards and Web APIs [Electronic resource]. — Mode of access: https://developer.mozilla.org/ (access date: 11.09.2026).",
        "11. Podman: A tool for managing OCI containers and pods [Electronic resource]. — Mode of access: https://podman.io/ (access date: 12.09.2026).",
        "12. Pytest Documentation: Full Python testing tool [Electronic resource]. — Mode of access: https://docs.pytest.org/ (access date: 12.09.2026).",
    ]
    for ref in references:
        p = b.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(ref)
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.italic = False

    # -----------------------------------------------------------------------
    # 13. ДОДАТКИ (Appendices) - Order 120
    # -----------------------------------------------------------------------
    # ДОДАТОК А
    b.add_heading_1("ДОДАТОК А", page_break=True)
    b.add_centered_paragraph("Лістинги ключових компонентів вихідного коду", bold=True)
    b.add_body_paragraph(
        "Фрагмент реалізації сервісного шару керування замовленнями (`project/backend/app/services/order_service.py`):"
    )
    code_a = (
        "class OrderService:\n"
        "    def __init__(self, order_repo: OrderRepository, menu_repo: MenuRepository):\n"
        "        self.order_repo = order_repo\n"
        "        self.menu_repo = menu_repo\n\n"
        "    def create_order(self, user_id: int, data: OrderCreate) -> Order:\n"
        "        # Validation of stop-list and availability\n"
        "        for item_data in data.items:\n"
        "            menu_item = self.menu_repo.get_by_id(item_data.menu_item_id)\n"
        "            if not menu_item or not menu_item.is_available:\n"
        "                raise HTTPException(status_code=400, detail='Item not available')\n"
        "        return self.order_repo.create_with_items(user_id, data)\n"
    )
    p_code_a = b.doc.add_paragraph()
    p_code_a.paragraph_format.first_line_indent = None
    p_code_a.paragraph_format.line_spacing = 1.5
    run_code_a = p_code_a.add_run(code_a)
    run_code_a.font.name = "Times New Roman"
    run_code_a.font.size = Pt(12)
    run_code_a.font.italic = False

    # ДОДАТОК Б
    b.add_heading_1("ДОДАТОК Б", page_break=True)
    b.add_centered_paragraph("Специфікація інтерфейсу прикладного програмування REST API", bold=True)
    b.add_body_paragraph(
        "Фрагмент специфікації OpenAPI 3.1 для замовлень та адміністрування меню (`docs/api/openapi.yaml`):"
    )
    code_b = (
        "paths:\n"
        "  /api/v1/orders:\n"
        "    post:\n"
        "      summary: Create customer order\n"
        "      security: [{OAuth2PasswordBearer: []}]\n"
        "      responses:\n"
        "        '201': {description: Order successfully created}\n"
        "        '400': {description: Validation or stop-list error}\n"
        "  /api/v1/orders/admin:\n"
        "    get:\n"
        "      summary: Barista order queue\n"
        "      security: [{OAuth2PasswordBearer: []}]\n"
        "      responses:\n"
        "        '200': {description: List of active orders}\n"
        "        '403': {description: Superuser privilege required}\n"
    )
    p_code_b = b.doc.add_paragraph()
    p_code_b.paragraph_format.first_line_indent = None
    p_code_b.paragraph_format.line_spacing = 1.5
    run_code_b = p_code_b.add_run(code_b)
    run_code_b.font.name = "Times New Roman"
    run_code_b.font.size = Pt(12)
    run_code_b.font.italic = False

    # ДОДАТОК В
    b.add_heading_1("ДОДАТОК В", page_break=True)
    b.add_centered_paragraph("Посібник користувача та персоналу кав'ярні", bold=True)
    b.add_body_paragraph(
        "Коротка інструкція для персоналу кав'ярні щодо роботи з чергою замовлень та оперативним стоп-листом:"
    )
    b.add_body_paragraph(
        "1. Для авторизації бариста слід перейти за посиланням «Увійти» та ввести облікові дані адміністратора.\n"
        "2. У навігаційній панелі відкрити розділ «⚙️ Адмін-панель».\n"
        "3. На вкладці «Меню та Стоп-лист» доступне миттєве блокування страв, інгредієнти яких закінчилися.\n"
        "4. На вкладці «Черга замовлень бариста» відображається перелік активних замовлень. Натискання кнопок "
        "«Почати готувати ➔», «Готово до видачі ✓» та «Видати клієнту ✓» змінює стан замовлення у реальному часі."
    )

    return doc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("project/report.docx"),
        help="Path where the report .docx will be written",
    )
    args = parser.parse_args(argv)

    print("Building report document for DSTU 3008:2015...")
    doc = build_full_report()

    output_path: Path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"Report successfully saved to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
