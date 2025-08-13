import re, json, ast
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory

def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s[:80]  # keep it short-ish

def _validate_draft(draft: Dict[str, Any]) -> Tuple[str, Optional[str], List[Dict[str, Any]]]:
    """
    Expected shape:
    {
      "title": "Course Title",
      "sections": [
        {
          "title": "Section Title",
          "position": Optional[int],
          "lessons": [
            {
              "title": "Lesson Title",
              "description": "Lesson Description",
            }
          ]
        }
      ]
    }

    Returns:
      (title, description, sections)
      where sections = [
        {
          "title": str,
          "lessons": [{"title": str, "description": str, "position": int}]
        }, ...
      ]
    """
    if not isinstance(draft, dict):
        raise TypeError("draft must be a dict.")

    # Course title
    title = draft.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("draft.title must be a non-empty string.")
    title = title.strip()
    
    description = draft.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("draft.description must be a non-empty string.")
    description = description.strip()

    # Sections
    sections_raw = draft.get("sections")
    if not isinstance(sections_raw, list) or not sections_raw:
        raise ValueError("draft.sections must be a non-empty list.")

    normalized_sections: List[Dict[str, Any]] = []
    for sec_idx, sec in enumerate(sections_raw, start=1):
        if not isinstance(sec, dict):
            raise ValueError(f"section #{sec_idx} must be an object.")
        sec_title = sec.get("title")
        if not isinstance(sec_title, str) or not sec_title.strip():
            raise ValueError(f"section #{sec_idx} missing non-empty 'title'.")

        lessons_raw = sec.get("lessons")
        if not isinstance(lessons_raw, list) or not lessons_raw:
            raise ValueError(f"section #{sec_idx} 'lessons' must be a non-empty list.")

        normalized_lessons: List[Dict[str, Any]] = []
        for les_idx, les in enumerate(lessons_raw, start=1):
            if not isinstance(les, dict):
                raise ValueError(f"section #{sec_idx} lesson #{les_idx} must be an object.")

            ltitle = les.get("title")
            if not isinstance(ltitle, str) or not ltitle.strip():
                raise ValueError(f"section #{sec_idx} lesson #{les_idx} missing non-empty 'title'.")

            ldescription = les.get("description")
            if not isinstance(ldescription, str):
                raise ValueError(f"section #{sec_idx} lesson #{les_idx} body must be a string ('description').")

            normalized_lessons.append({
                "title": ltitle.strip(),
                "description": ldescription.strip(),
                "position": les_idx,
            })

        normalized_sections.append({
            "title": sec_title.strip(),
            "position": sec_idx,
            "lessons": normalized_lessons,
        })
        
    print("Draft validated")
    return title, description, normalized_sections

