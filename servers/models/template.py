from enum import Enum

class Theme(str, Enum):
    academic = "academic"
    default = "default"
    penguin = "penguin"

class TemplateName(str, Enum):
    cover = 'cover.md.j2'
    page = 'page.md.j2'
    end = 'end.md.j2'