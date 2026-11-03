#!/usr/bin/env python3
"""安全创建展台项目工作区：不会覆盖既有项目。"""
import argparse
import json
import re
import shutil
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def safe_name(raw):
    out = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', raw).strip().strip('.')
    if not out or out in {'.', '..'}:
        raise ValueError('需要有效的项目名称')
    return out


def init_project(name, output):
    dest = output / safe_name(name)
    if dest.exists():
        raise FileExistsError(f'项目目录已存在，未覆盖: {dest}')
    dest.mkdir(parents=True)
    (dest / 'references').mkdir()
    (dest / 'renders').mkdir()
    (dest / 'drawings').mkdir()
    data = json.loads((ASSETS / '项目配置模板.json').read_text(encoding='utf-8'))
    data['project_name'] = name
    (dest / 'project.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    mappings = {
        '项目需求表.md': '01-客户需求.md',
        '展台效果图提示词模板.md': '04-效果图提示词.md',
        '报价清单模板.csv': '05-材料BOM与预算.csv',
    }
    for src, target in mappings.items():
        shutil.copyfile(ASSETS / src, dest / target)
    for name_, content in {
        '02-方案方向对比.md': '# 方案方向对比\n\n待补：预算优先 / 平衡型 / 旗舰型\n',
        '03-平面分区与动线.md': '# 平面分区与动线\n\n待补：展位几何、开口、分区与动线\n',
        '06-落地风险与待确认.md': '# 落地风险与待确认\n\n待补：风险等级、来源、责任人、确认状态\n',
        '07-修改记录.md': '# 修改记录\n\n- V01：新建项目，待确认输入\n',
    }.items():
        (dest / name_).write_text(content, encoding='utf-8')
    return dest


def main():
    parser = argparse.ArgumentParser(description='初始化展台设计项目目录')
    parser.add_argument('--name', required=True, help='项目名称，如 客户-上海宠物展-6x6')
    parser.add_argument('--output', type=Path, default=Path('./projects'), help='目标上级目录')
    args = parser.parse_args()
    try:
        path = init_project(args.name, args.output.expanduser())
    except (FileExistsError, ValueError) as ex:
        parser.exit(2, f'错误: {ex}\n')
    print(f'已创建项目目录: {path.resolve()}')
    print('请先填写 project.json、01-客户需求.md，然后运行 validate_brief.py。')


if __name__ == '__main__':
    main()
