# Digital Host-Phage Project

这是一个面向数字宿主-噬菌体系统的科研项目目录，当前处于第一阶段最小可运行模型整理阶段。

第一阶段固定体系为：
- Host: E. coli
- Phage: T7

当前目标是逐步构建一个生长耦合的数字宿主-噬菌体最小可运行模型，并为后续扩展到不同宿主、不同噬菌体和更细化机制预留模块化接口。
当前 phase 1 已形成最小可运行主干，但仍然是规则型、粗粒度、机制简化实现，不应视为真实动力学模型或已完成的基因组驱动建模。

## 当前已实现内容

- 输入层
  - minimal annotation schema
  - annotation alias 支持
  - annotation validation
  - recognition / resource / defense builder
  - fallback trace
  - pipeline labels
- 机制层
  - recognition_match_score
  - adsorption_probability
  - injection_success_probability
  - staged infection progression
  - host takeover
  - phage resource allocation
  - progeny_potential
  - release_readiness
  - latent_period_proxy
  - host defense placeholder
- 结果层
  - infection_outcome
  - failure_cause
  - failure_stage
  - trajectory_label
  - host_remodeling_label
  - stage_reach_label
- 标准输出层
  - `extract_standard_phase1_summary(host_state, phage_state, initial_host_state=None)`

## 当前模型特点

- 宿主和噬菌体都可以通过配置创建，便于切换不同测试体系
- 吸附识别模块显式区分受体类型、受体变体、识别偏好和匹配强度
- 感染流程已拆分为注入、早期表达、复制、晚期装配、裂解五个阶段
- 宿主资源状态会影响感染后续推进强度，并已接入 host takeover 与 phage resource allocation
- 宿主防御当前以阶段性占位模块表示，可在特定感染阶段阻断流程
- 最终结果可显式输出感染结局、失败原因、失败阶段、轨迹标签、宿主重塑标签与阶段到达标签

## 第一阶段封版点

- 当前第一阶段已经形成稳定的规则型、粗粒度、机制简化主干
- 已可闭环区分识别失败、资源受限、防御阻断与成功裂解等典型轨迹
- 标准结果口径已收口到 `extract_standard_phase1_summary(...)`
- 当前已有最小回归测试：[tests/test_phase1_regression.py](tests/test_phase1_regression.py)
- 当前已有字段字典：[phase1_field_dictionary.md](phase1_field_dictionary.md)

## 当前推荐阅读顺序

1. [project_overview.md](project_overview.md)
2. [README.md](README.md)
3. [phase1_summary.md](phase1_summary.md)
4. [phase1_field_dictionary.md](phase1_field_dictionary.md)

## 当前标准测试场景

- receptor matching comparison
- host resource comparison
- host defense comparison
- combined annotation pipeline demo
- stage progression comparison
- standard phase1 summary demo

当前标准输出口径见 `extract_standard_phase1_summary(...)`。
更详细的阶段总结见 [phase1_summary.md](phase1_summary.md)。
当前最小回归测试见 [tests/test_phase1_regression.py](tests/test_phase1_regression.py)。
当前字段字典见 [phase1_field_dictionary.md](phase1_field_dictionary.md)。

## Project Vision / 项目愿景

The long-term goal of this project is to build a digital phage–host interaction system that leverages phage/host genomic sequences and related annotations to infer, simulate, and predict infection success, host defense effects, and other key infection-associated interaction behaviors.

## Author / 作者

Yinfeng Wang (王崟沣)
Ocean University of China

## Copyright / 版权

© 2026 Yinfeng Wang (王崟沣). All rights reserved.

This demo is a phase-1 research prototype for academic presentation and research communication only.
It is not a validated quantitative prediction platform.

## Contact / 联系方式

For collaboration or further development of this project, please contact:
yif_wang1@163.com
