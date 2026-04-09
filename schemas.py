import re
from pathlib import Path

from pypdf import PdfReader
from docx import Document

from app.models.schemas import ResumeData


def extract_text_from_pdf(filepath: Path) -> str:
    reader = PdfReader(str(filepath))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def extract_text_from_docx(filepath: Path) -> str:
    doc = Document(str(filepath))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(filepath)
    if suffix in (".docx", ".doc"):
        return extract_text_from_docx(filepath)
    raise ValueError(f"Неподдерживаемый формат: {suffix}")


SKILL_PATTERNS = [
    r"python", r"javascript", r"typescript", r"react", r"vue",
    r"angular", r"node\.?js", r"fastapi", r"django", r"flask",
    r"docker", r"kubernetes", r"aws", r"gcp", r"azure",
    r"postgresql", r"mysql", r"mongodb", r"redis", r"sql",
    r"git", r"ci/cd", r"rest\s?api", r"graphql", r"html",
    r"css", r"sass", r"scss", r"webpack", r"vite",
    r"java", r"kotlin", r"swift", r"go(?:lang)?", r"rust",
    r"c\+\+", r"c#", r"\.net", r"spring", r"rails",
    r"machine\s?learning", r"deep\s?learning", r"tensorflow",
    r"pytorch", r"pandas", r"numpy", r"scikit",
    r"figma", r"photoshop", r"agile", r"scrum", r"jira",
    r"linux", r"nginx", r"celery", r"rabbitmq", r"kafka",
]

EXPERIENCE_PATTERN = re.compile(
    r"(\d{1,2})\+?\s*(?:лет|год|года|years?|г\.)",
    re.IGNORECASE,
)

TITLE_KEYWORDS = [
    "developer", "разработчик", "engineer", "инженер",
    "analyst", "аналитик", "designer", "дизайнер",
    "manager", "менеджер", "lead", "тимлид",
    "devops", "qa", "тестировщик", "architect",
    "data scientist", "ml engineer", "frontend", "backend",
    "fullstack", "full-stack", "full stack",
]


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for pattern in SKILL_PATTERNS:
        if re.search(rf"\b{pattern}\b", text_lower):
            match = re.search(rf"\b({pattern})\b", text_lower)
            if match:
                skill = match.group(1).strip()
                normalized = skill.title() if len(skill) > 3 else skill.upper()
                if normalized not in found:
                    found.append(normalized)
    return found[:20]


def extract_experience_years(text: str) -> int | None:
    matches = EXPERIENCE_PATTERN.findall(text)
    if matches:
        return max(int(m) for m in matches)
    return None


def extract_job_titles(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for keyword in TITLE_KEYWORDS:
        if keyword in text_lower:
            for line in text.split("\n"):
                if keyword in line.lower() and len(line) < 80:
                    title = line.strip().rstrip(".,;:")
                    if title and title not in found:
                        found.append(title)
                        break
    return found[:5]


def extract_education(text: str) -> list[str]:
    edu_keywords = [
        "университет", "институт", "академия", "колледж",
        "university", "institute", "college", "bachelor",
        "master", "бакалавр", "магистр", "phd", "кандидат",
    ]
    text_lower = text.lower()
    found = []
    for line in text.split("\n"):
        line_lower = line.lower().strip()
        for kw in edu_keywords:
            if kw in line_lower and len(line.strip()) < 120:
                clean = line.strip().rstrip(".,;:")
                if clean and clean not in found:
                    found.append(clean)
                break
    return found[:5]


def parse_resume(filepath: Path) -> ResumeData:
    raw_text = extract_text(filepath)

    if not raw_text or len(raw_text) < 20:
        raise ValueError("Не удалось извлечь текст из файла. Проверьте, что файл содержит текст.")

    return ResumeData(
        raw_text=raw_text,
        skills=extract_skills(raw_text),
        experience_years=extract_experience_years(raw_text),
        job_titles=extract_job_titles(raw_text),
        education=extract_education(raw_text),
    )
