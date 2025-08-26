from enum import Enum

class TemplateName(str, Enum):
    cover = 'cover.md.j2'
    page = 'page.md.j2'
    end = 'end.md.j2'