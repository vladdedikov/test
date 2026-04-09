SYSTEM_INTERVIEWER = """Ты — опытный HR-интервьюер и карьерный консультант.
Ты проводишь mock-собеседование, чтобы помочь кандидату подготовиться.
Твоя задача — задавать релевантные вопросы и оценивать ответы.

Правила:
- Задавай один вопрос за раз
- Вопросы должны быть конкретными и профессиональными
- Адаптируй сложность под уровень кандидата
- Будь доброжелательным, но объективным
- Отвечай на русском языке"""


BASELINE_QUESTION = """Проведи собеседование. Задай один вопрос кандидату."""


def build_question_prompt(
    resume_text: str,
    job_description: str,
    question_type: str,
    question_number: int,
    total_questions: int,
    chat_history: str = "",
) -> str:
    history_block = ""
    if chat_history:
        history_block = f"\n\n## Предыдущий диалог:\n{chat_history}"

    return f"""## Резюме кандидата:
{resume_text[:3000]}

## Описание вакансии:
{job_description[:2000]}
{history_block}

## Задание:
Сгенерируй вопрос #{question_number} из {total_questions} для mock-собеседования.
Тип вопроса: {question_type}.

Типы вопросов:
- behavioral: вопросы о прошлом опыте и поведении (STAR-формат)
- technical: проверка технических знаний и навыков
- situational: гипотетические рабочие ситуации

Требования:
- Вопрос должен учитывать навыки из резюме и требования вакансии
- Найди пробелы между резюме и вакансией — задавай вопросы по ним
- Не повторяй предыдущие вопросы
- Формулируй чётко, в 1-3 предложения

Верни ТОЛЬКО текст вопроса, без нумерации и пояснений."""


def build_evaluation_prompt(
    question: str,
    answer: str,
    job_description: str,
) -> str:
    return f"""## Вопрос интервьюера:
{question}

## Ответ кандидата:
{answer}

## Описание вакансии:
{job_description[:1500]}

## Задание:
Оцени ответ кандидата и верни результат строго в JSON-формате:

{{
  "score": <число от 1 до 5>,
  "strengths": ["сильная сторона 1", "сильная сторона 2"],
  "improvements": ["что улучшить 1", "что улучшить 2"],
  "comment": "краткий комментарий к ответу (1-2 предложения)"
}}

Критерии оценки:
- 5: отличный ответ с конкретными примерами, цифрами, чёткой структурой
- 4: хороший ответ с примерами, но не хватает деталей
- 3: средний ответ, общие фразы, мало конкретики
- 2: слабый ответ, не по теме или очень поверхностный
- 1: ответ отсутствует или полностью нерелевантный

Верни ТОЛЬКО JSON, без пояснений и markdown."""


QUESTION_TYPE_SEQUENCE = {
    "mixed": [
        "behavioral",
        "technical",
        "situational",
        "technical",
        "behavioral",
        "technical",
        "situational",
        "behavioral",
        "technical",
        "situational",
    ],
    "behavioral": ["behavioral"] * 10,
    "technical": ["technical"] * 10,
}


def get_question_type(interview_type: str, question_number: int) -> str:
    sequence = QUESTION_TYPE_SEQUENCE.get(interview_type, QUESTION_TYPE_SEQUENCE["mixed"])
    idx = (question_number - 1) % len(sequence)
    return sequence[idx]


def build_report_prompt(
    resume_text: str,
    job_description: str,
    qa_pairs: list[dict],
) -> str:
    qa_text = ""
    for i, pair in enumerate(qa_pairs, 1):
        qa_text += f"\nВопрос {i}: {pair['question']}\n"
        qa_text += f"Ответ: {pair['answer']}\n"
        qa_text += f"Оценка: {pair.get('score', '—')}/5\n"

    return f"""## Резюме кандидата:
{resume_text[:2000]}

## Вакансия:
{job_description[:1500]}

## Вопросы и ответы:
{qa_text}

## Задание:
Сформируй итоговый отчёт по собеседованию в JSON-формате:

{{
  "overall_score": <число от 1 до 5>,
  "competencies": [
    {{"name": "Коммуникация", "score": <1-5>}},
    {{"name": "Технические навыки", "score": <1-5>}},
    {{"name": "Решение проблем", "score": <1-5>}},
    {{"name": "Релевантный опыт", "score": <1-5>}},
    {{"name": "Мотивация", "score": <1-5>}}
  ],
  "summary": "общий вывод о кандидате (3-4 предложения)",
  "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3"],
  "improvements": ["зона роста 1", "зона роста 2", "зона роста 3"]
}}

Верни ТОЛЬКО JSON."""
