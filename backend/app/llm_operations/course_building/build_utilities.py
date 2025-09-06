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
    
    # Course title
    title = draft.get("title")
    
    description = draft.get("description")
    description = description.strip()

    # Sections
    sections_raw = draft.get("sections")

    normalized_sections: List[Dict[str, Any]] = []
    for sec_idx, sec in enumerate(sections_raw, start=1):
        sec_title = sec.get("title")

        lessons_raw = sec.get("lessons")

        normalized_lessons: List[Dict[str, Any]] = []
        for les_idx, les in enumerate(lessons_raw, start=1):

            ltitle = les.get("title")
            ldescription = les.get("description")

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
        
    return title, description, normalized_sections

