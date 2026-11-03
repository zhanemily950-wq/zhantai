#!/usr/bin/env python3
"""展台参数检查。只验证信息完整度，不判断结构安全/审批通过。"""
import argparse
import json
from pathlib import Path


def check(data):
    errors, warnings, info = [], [], []
    if not isinstance(data, dict):
        return ['项目配置根节点必须是 JSON 对象'], warnings, info
    for k, label in [('project_name', '项目名'), ('event_name', '展会名'), ('venue', '展馆名'), ('industry', '行业')]:
        if not str(data.get(k, '')).strip():
            warnings.append(f'{label}未填写 ({k})')
    booth = data.get('booth')
    if not isinstance(booth, dict):
        errors.append('booth 必须是对象')
        booth = {}
    dims = []
    for k, label in [('width_m', '宽度'), ('depth_m', '深度')]:
        v = booth.get(k)
        if v is None:
            warnings.append(f'{label}未填写，不能推导面积或绘制精确平面图')
        elif isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
            errors.append(f'{label}需要正数（米）')
        else:
            dims.append(v)
    if len(dims) == 2:
        info.append(f'按输入尺寸计算的矩形面积 = {dims[0]*dims[1]:.2f}㎡；仍需与展位官方平面图核对')
    sides = booth.get('open_sides', [])
    if not isinstance(sides, list):
        errors.append('open_sides 必须是数组')
    elif not sides:
        warnings.append('开口方向未填写，不能确定主入口和主通道')
    if booth.get('official_height_limit_m') is None:
        warnings.append('限高未知：不得自行设定可施工高度')
    if not booth.get('venue_manual_verified'):
        warnings.append('未确认官方展商手册：展馆规则、报馆与结构审批均待核实')
    brand = data.get('brand', {})
    if not isinstance(brand, dict):
        errors.append('brand 必须是对象')
        brand = {}
    if not brand.get('name'):
        warnings.append('品牌名未填写')
    budget = data.get('budget', {})
    if not isinstance(budget, dict):
        errors.append('budget 必须是对象')
        budget = {}
    v = budget.get('ceiling_cny')
    if v is None:
        warnings.append('预算上限未填写：只能讨论成本驱动，不能承诺总价')
    elif isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
        errors.append('预算上限必须为正数（元）')
    if not data.get('exhibits'):
        warnings.append('展品尺寸/重量/数量未提供，展示台承重与空间需求待核实')
    if not data.get('objectives'):
        warnings.append('参展目标未填写，设计主次难以排序')
    return errors, warnings, info


def main():
    parser = argparse.ArgumentParser(description='检查项目输入完整度，不代表工程审核')
    parser.add_argument('json_file', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.json_file.read_text(encoding='utf-8'))
    except (OSError, ValueError) as err:
        parser.exit(2, f'无法读取项目JSON: {err}\n')
    errors, warnings, info = check(data)
    for msg in info:
        print('[信息]', msg)
    for msg in errors:
        print('[错误]', msg)
    for msg in warnings:
        print('[待核实]', msg)
    print(f'完成：{len(errors)}个错误，{len(warnings)}项待补充。结构安全、消防及展馆审批未由本脚本验证。')
    if errors:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
