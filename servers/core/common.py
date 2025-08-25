def parse_markdown_slides(content: str) -> list:
    """
    解析markdown内容，按YAML front matter切分幻灯片
    """
    slides = []
    current_slide = []
    in_yaml = False
    
    for line in content.splitlines():
        if line.strip() == '---' and not in_yaml:
            # 开始YAML front matter
            if not current_slide:
                in_yaml = True
                current_slide.append(line)
            else:
                # 遇到新的幻灯片分隔符
                slides.append('\n'.join(current_slide))
                current_slide = [line]
                in_yaml = True
        elif line.strip() == '---' and in_yaml:
            # 结束YAML front matter
            current_slide.append(line)
            in_yaml = False
        else:
            current_slide.append(line)
    
    # 添加最后一个幻灯片
    if current_slide:
        slides.append('\n'.join(current_slide))
    
    return slides

def transform_parameters_to_frontmatter(parameters: dict):
    frontmatter = ""
    for key in parameters.keys():
        value = parameters.get(key, "")
        frontmatter += f"{key}: {value}\n"
    return frontmatter.strip()