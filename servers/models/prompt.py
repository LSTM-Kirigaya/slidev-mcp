from enum import Enum

class PromptName(str, Enum):
    outline_generate = 'outline_generate.j2'
    slidev_generate_with_specific_outlines = 'slidev_generate_with_specific_outlines.j2'
    slidev_generate = 'slidev_generate.j2'
    user_info = 'user_info.j2'