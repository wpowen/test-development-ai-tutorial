# Reusable AI eval contract skill

1. 先声明 system under test、decision、risk、dataset slice、Oracle、owner 和 stop state。2. 固定 model/prompt/data/tool/scorer manifest。3. 运行 baseline。4. 注入一个会改变专业决定的 fault。5. 要求 exit 1 并保存 raw evidence。6. 修复后用同一 expected contract 复跑。不得把 Fixture 成功写成 live 或模型成功。
