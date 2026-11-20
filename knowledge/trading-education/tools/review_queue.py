#!/usr/bin/env python3
"""Build evidence-location review queue from real extracted source metadata.
No source text is copied into the public repository; no automated factual
validation is claimed. Reviewers must inspect original images and statements.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'integration/extraction-state.json'
QUEUE=ROOT/'integration/visual-and-knowledge-review-queue.md'
def main():
    state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'files':{}}
    records=list(state.get('files',{}).items())
    out=['# The Market Mind — 图表与知识核验队列','',
         '> 自动生成的待办清单，不代表任何原件图表或知识已经核验。','',
         '## 核验标准','',
         '- 逐页打开原件；检查蜡烛实体、影线、颜色、坐标轴、时间周期、成交量、标注与上下文',
         '- 原文每条技术定义标明页码/幻灯片、前提、反例、适用市场和局限',
         '- 对照至少一个独立可靠来源；不一致处保留分歧和待核状态',
         '- 形成原创英语教学内容前，确认没有直接复制原文或图表',
         '- 只有完成视觉检查才可将 visual_review_complete 改为 true；事实核验和课程融合分别验收','']
    for sha,v in records:
        name=v.get('source_name','Unknown')
        out.extend([f'## {name}',f'- Git blob SHA: `{sha}`',
                    f'- 提取状态：`{v.get("extraction_status","unknown")}`',
                    f'- 文本块：{v.get("text_blocks","未提取")}',
                    f'- 图片记录：{v.get("images_found","未提取")}',
                    f'- 视觉核验：{v.get("visual_review_complete",False)}',
                    f'- 事实核验：{v.get("fact_checked",False)}',
                    f'- 课程融合：{v.get("integrated_into_lesson",False)}'])
        d=v.get('details',{})
        if 'pages' in d:
            out.append(f'- 逐页复核范围：PDF 第1—{d["pages"]}页')
            if d.get('pages_without_extractable_text'):
                out.append(f'- 需OCR或人工识别的页面：{d["pages_without_extractable_text"]}')
        if d.get('xml_parts_read'):
            out.append(f'- 需逐张核验的幻灯片/XML部分：{len(d["xml_parts_read"])}')
        out.extend(['- 待补证据：原件页码、图像判读、术语定义、对照来源、反例、风险说明',''])
    QUEUE.write_text('\n'.join(out)+'\n',encoding='utf-8')
    print(f'Generated review queue for {len(records)} sources')
if __name__=='__main__':main()
