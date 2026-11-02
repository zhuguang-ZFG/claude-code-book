# R4 衍生物料——执行计划

规格：`docs/superpowers/specs/2026-11-03-r4-derivative-materials.md`

- [ ] Step 1：主控 unslop 审计三生成器（portal/gallery/beginner-reader），出五行方向与改动清单；三 worker 并行——W1 知识卡（`scripts/build_knowledge_cards.py` + `docs/cards/` ×15+索引）、W2 样章页（`scripts/build_sample_chapter.py` + `docs/sample-chapter.html`）、W3 封面草案（`scripts/build_video_covers.py` + `docs/video/chNN/cover-draft.svg` ×5）；工人只写自家脚本与产物，共享文件（账本/README/计划）全留主控
- [ ] Step 2：主控收口——unslop 改动落地并重生成三页；四路产物齐跑幂等复验（重跑零 diff）；五道闸全量 + 译腔复测
- [ ] Step 3：账本第 57 条（zh/en，末尾 `构建器测试 N 项全绿`/`N builder tests green`）+ 本计划勾选
- [ ] Step 4：提交 → 推送 → PR #6 → CI 绿 → 合并 → SHA 纪录；README/docs 侧如涉槽位按 CI 实测对齐
