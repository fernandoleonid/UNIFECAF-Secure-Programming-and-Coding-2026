from html import escape
import json
from collections import Counter


def carregar_json(caminho):
    with open(caminho) as f:
        return json.load(f)


def metricas_bandit(caminho):
    data = carregar_json(caminho)
    resultados = data.get("results", [])
    severidades = [r.get("issue_severity", "UNKNOWN") for r in resultados]
    contagem = Counter(severidades)
    return {
        "SAST_Total": len(resultados),
        "SAST_HIGH": contagem.get("HIGH", 0),
        "SAST_MEDIUM": contagem.get("MEDIUM", 0),
        "SAST_LOW": contagem.get("LOW", 0),
        "Arquivos_Afetados": len(set(r.get("filename", "") for r in resultados))
    }

def metricas_sbom(caminho):
    data = carregar_json(caminho)
    components = data.get("components", [])
    
    # Contagem por tipo
    tipos = [c.get("type", "desconhecido") for c in components]
    contagem_tipos = Counter(tipos)
    
    # Contagem por licença (simplificada)
    licencas = []
    sem_licenca = 0
    for c in components:
        lic_list = c.get("licenses", [])
        if not lic_list:
            sem_licenca += 1
            continue
        for lic in lic_list:
            lic_id = lic.get("license", {}).get("id", lic.get("license", {}).get("name", "Não informada"))
            # Limpa nomes muito longos
            licencas.append(lic_id.split("::")[-1].strip() if "::" in lic_id else lic_id)
    
    contagem_licencas = Counter(licencas) if licencas else {"Não informada": len(components)}
    
    return {
        "total_componentes": len(components),
        "por_tipo": dict(contagem_tipos),
        "licencas": dict(contagem_licencas),
        "sem_licenca": sem_licenca
    }


def exibir_cabecalho():
    print("=" * 45)
    print("📊 CONSOLIDADO DE SEGURANÇA & GOVERNANÇA")
    print("=" * 45)


def exibir_secao_sast(caminho="bandit-report.json"):
    try:
        m_sast = metricas_bandit(caminho)
        print("\n🔍 MÉTRICAS SAST (Bandit)")
        print("-" * 30)
        for chave, valor in m_sast.items():
            print(f"  {chave}: {valor}")
        if m_sast["SAST_HIGH"] > 0:
            print("  ⚠️ Priorizar correção de vulnerabilidades HIGH")
        else:
            print("  ✅ Sem vulnerabilidades críticas/altas")
    except FileNotFoundError:
        print("  ⚠️ bandit-report.json não encontrado")


def exibir_secao_sbom(caminho="sbom.json"):
    try:
        m_sbom = metricas_sbom(caminho)
        print("\n📦 MÉTRICAS SBOM (CycloneDX)")
        print("-" * 30)
        print(f"  Total de componentes: {m_sbom['total_componentes']}")

        print("  Tipos:")
        for tipo, qtd in m_sbom['por_tipo'].items():
            print(f"    • {tipo}: {qtd}")

        print("  Licenças encontradas:")
        licencas_ordenadas = sorted(m_sbom['licencas'].items(), key=lambda x: x[1], reverse=True)
        for licenca, qtd in licencas_ordenadas[:10]:
            print(f"    • {licenca}: {qtd}")
        if len(licencas_ordenadas) > 10:
            print(f"    ... e mais {len(licencas_ordenadas) - 10} licenças")

        print(f"  Componentes sem licença: {m_sbom['sem_licenca']}")

        if m_sbom["sem_licenca"] > 0:
            print("  ⚠️ Verificar conformidade antes de distribuir")
        else:
            print("  ✅ SBOM válido e pronto para ingestão em ferramentas SCA")

    except FileNotFoundError:
        print("  ⚠️ sbom.json não encontrado")


def carregar_metricas_relatorio(caminho_bandit="bandit-report.json", caminho_sbom="sbom.json"):
    relatorio = {
        "sast": None,
        "sbom": None,
    }

    try:
        relatorio["sast"] = metricas_bandit(caminho_bandit)
    except FileNotFoundError:
        pass

    try:
        relatorio["sbom"] = metricas_sbom(caminho_sbom)
    except FileNotFoundError:
        pass

    return relatorio


def recomendacao_sast(metricas):
    if not metricas:
        return "Arquivo bandit-report.json não encontrado."
    if metricas["SAST_HIGH"] > 0:
        return "Priorizar correção imediata das vulnerabilidades HIGH."
    return "Sem vulnerabilidades críticas/altas identificadas."


def recomendacao_sbom(metricas):
    if not metricas:
        return "Arquivo sbom.json não encontrado."
    if metricas["sem_licenca"] > 0:
        return "Verificar conformidade de licenças antes da distribuição."
    return "SBOM válido e pronto para ingestão em ferramentas SCA."


def gerar_html_relatorio(relatorio, caminho_saida="relatorio_metricas.html"):
    sast = relatorio["sast"]
    sbom = relatorio["sbom"]
    licencas_ordenadas = []
    tipos_ordenados = []

    if sbom:
        licencas_ordenadas = sorted(sbom["licencas"].items(), key=lambda item: item[1], reverse=True)
        tipos_ordenados = sorted(sbom["por_tipo"].items(), key=lambda item: item[1], reverse=True)

    html = f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Relatório de Segurança e Governança</title>
    <style>
        :root {{
            --bg: #f5f7fb;
            --card: #ffffff;
            --ink: #242149;
            --muted: #5f6380;
            --line: #d9deea;
            --accent: #33DB89;
            --accent-dark: #242149;
            --warn: #9a6700;
            --risk: #b42318;
            --surface: #eef2fb;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            color: var(--ink);
            background: linear-gradient(180deg, #fbfcfe 0%, var(--bg) 100%);
        }}
        .container {{
            max-width: 1120px;
            margin: 0 auto;
            padding: 40px 24px 56px;
        }}
        .hero {{
            background: linear-gradient(135deg, var(--accent-dark) 0%, #312d63 100%);
            color: #ffffff;
            border-radius: 0;
            padding: 36px;
            border-left: 8px solid var(--accent);
            box-shadow: 0 18px 40px rgba(36, 33, 73, 0.14);
        }}
        .hero h1 {{
            margin: 0 0 8px;
            font-size: 2.3rem;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }}
        .hero p {{
            margin: 0;
            color: rgba(255, 255, 255, 0.82);
            font-size: 1rem;
            max-width: 720px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
            margin: 24px 0 32px;
        }}
        .kpi {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 0;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(36, 33, 73, 0.05);
        }}
        .kpi small {{
            display: block;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
            font-size: 0.72rem;
        }}
        .kpi strong {{
            font-size: 2rem;
            color: var(--accent-dark);
        }}
        .section {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 0;
            padding: 24px;
            margin-top: 20px;
            box-shadow: 0 8px 24px rgba(36, 33, 73, 0.05);
        }}
        .tabs {{
            margin-top: 20px;
        }}
        .tab-list {{
            display: flex;
            gap: 8px;
            margin-top: 20px;
            border-bottom: 2px solid var(--accent-dark);
        }}
        .tab-button {{
            border: 1px solid var(--line);
            border-bottom: none;
            background: var(--surface);
            color: var(--muted);
            padding: 12px 18px;
            border-radius: 0;
            font: inherit;
            font-weight: 700;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}
        .tab-button[aria-selected="true"] {{
            background: var(--accent);
            border-color: var(--accent);
            color: var(--accent-dark);
            position: relative;
            top: 2px;
        }}
        .tab-panel {{
            display: none;
        }}
        .tab-panel.is-active {{
            display: block;
        }}
        .section h2 {{
            margin: 0 0 18px;
            font-size: 1.35rem;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }}
        .metric-box {{
            border: 1px solid var(--line);
            border-left: 4px solid var(--accent);
            border-radius: 0;
            padding: 14px 16px;
            background: #fff;
        }}
        .metric-box span {{
            display: block;
            color: var(--muted);
            font-size: 0.85rem;
            margin-bottom: 6px;
        }}
        .metric-box strong {{
            font-size: 1.35rem;
            color: var(--accent-dark);
        }}
        .tag {{
            display: inline-block;
            padding: 6px 10px;
            border-radius: 0;
            font-size: 0.82rem;
            font-weight: 700;
            border: 1px solid currentColor;
        }}
        .tag-risk {{ background: #fff1f3; color: var(--risk); }}
        .tag-warn {{ background: #fff8e8; color: var(--warn); }}
        .tag-ok {{ background: #ebfff4; color: #166534; }}
        ul {{
            margin: 14px 0 0;
            padding-left: 18px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 14px;
            background: #fff;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid var(--line);
        }}
        th {{
            color: var(--accent-dark);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: var(--surface);
        }}
        .footer {{
            margin-top: 24px;
            color: var(--muted);
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class=\"container\">
        <section class=\"hero\">
            <h1>Relatório Consolidado de Segurança e Governança</h1>
            <p>Resumo executivo com métricas de SAST e inventário SBOM gerado automaticamente a partir dos arquivos JSON do projeto.</p>
        </section>

        <section class=\"grid\">
            <article class=\"kpi\">
                <small>Achados SAST</small>
                <strong>{sast['SAST_Total'] if sast else 0}</strong>
            </article>
            <article class=\"kpi\">
                <small>Vulnerabilidades High</small>
                <strong>{sast['SAST_HIGH'] if sast else 0}</strong>
            </article>
            <article class=\"kpi\">
                <small>Componentes SBOM</small>
                <strong>{sbom['total_componentes'] if sbom else 0}</strong>
            </article>
            <article class=\"kpi\">
                <small>Sem Licença</small>
                <strong>{sbom['sem_licenca'] if sbom else 0}</strong>
            </article>
        </section>

        <section class=\"tabs\">
            <div class=\"tab-list\" role=\"tablist\" aria-label=\"Seções do relatório\">
                <button class=\"tab-button\" type=\"button\" role=\"tab\" id=\"tab-sast\" aria-controls=\"panel-sast\" aria-selected=\"true\">SAST</button>
                <button class=\"tab-button\" type=\"button\" role=\"tab\" id=\"tab-sbom\" aria-controls=\"panel-sbom\" aria-selected=\"false\">SBOM</button>
            </div>

            <section class=\"section tab-panel is-active\" id=\"panel-sast\" role=\"tabpanel\" aria-labelledby=\"tab-sast\">
                <h2>SAST | Bandit</h2>
                <p>
                    <span class=\"tag {'tag-risk' if sast and sast['SAST_HIGH'] > 0 else 'tag-ok'}\">{escape(recomendacao_sast(sast))}</span>
                </p>
                <div class=\"metrics\">
                    <div class=\"metric-box\"><span>Total</span><strong>{sast['SAST_Total'] if sast else 0}</strong></div>
                    <div class=\"metric-box\"><span>High</span><strong>{sast['SAST_HIGH'] if sast else 0}</strong></div>
                    <div class=\"metric-box\"><span>Medium</span><strong>{sast['SAST_MEDIUM'] if sast else 0}</strong></div>
                    <div class=\"metric-box\"><span>Low</span><strong>{sast['SAST_LOW'] if sast else 0}</strong></div>
                    <div class=\"metric-box\"><span>Arquivos afetados</span><strong>{sast['Arquivos_Afetados'] if sast else 0}</strong></div>
                </div>
            </section>

            <section class=\"section tab-panel\" id=\"panel-sbom\" role=\"tabpanel\" aria-labelledby=\"tab-sbom\">
                <h2>SBOM | CycloneDX</h2>
                <p>
                    <span class=\"tag {'tag-warn' if sbom and sbom['sem_licenca'] > 0 else 'tag-ok'}\">{escape(recomendacao_sbom(sbom))}</span>
                </p>
                <div class=\"metrics\">
                    <div class=\"metric-box\"><span>Total de componentes</span><strong>{sbom['total_componentes'] if sbom else 0}</strong></div>
                    <div class=\"metric-box\"><span>Sem licença</span><strong>{sbom['sem_licenca'] if sbom else 0}</strong></div>
                    <div class=\"metric-box\"><span>Tipos mapeados</span><strong>{len(sbom['por_tipo']) if sbom else 0}</strong></div>
                    <div class=\"metric-box\"><span>Licenças mapeadas</span><strong>{len(sbom['licencas']) if sbom else 0}</strong></div>
                </div>

                <h3>Componentes por tipo</h3>
                <ul>
                    {''.join(f'<li>{escape(tipo)}: <strong>{qtd}</strong></li>' for tipo, qtd in tipos_ordenados) or '<li>Nenhum dado disponível</li>'}
                </ul>

                <h3>Top 10 licenças</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Licença</th>
                            <th>Quantidade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'<tr><td>{escape(licenca)}</td><td>{qtd}</td></tr>' for licenca, qtd in licencas_ordenadas[:10]) or '<tr><td colspan="2">Nenhum dado disponível</td></tr>'}
                    </tbody>
                </table>
            </section>
        </section>

        <p class=\"footer\">Arquivo gerado automaticamente por gerar_metricas.py.</p>
    </div>
    <script>
        const tabs = document.querySelectorAll('.tab-button');
        const panels = document.querySelectorAll('.tab-panel');

        tabs.forEach(function(tab) {{
            tab.addEventListener('click', function() {{
                const targetId = tab.getAttribute('aria-controls');

                tabs.forEach(function(item) {{ item.setAttribute('aria-selected', 'false'); }});
                panels.forEach(function(panel) {{ panel.classList.remove('is-active'); }});

                tab.setAttribute('aria-selected', 'true');
                document.getElementById(targetId).classList.add('is-active');
            }});
        }});
    </script>
</body>
</html>
"""

    with open(caminho_saida, "w", encoding="utf-8") as arquivo_html:
        arquivo_html.write(html)

    return caminho_saida


def main():
    exibir_cabecalho()
    exibir_secao_sast()
    exibir_secao_sbom()
    caminho_html = gerar_html_relatorio(carregar_metricas_relatorio())
    print(f"\n📄 Relatório HTML gerado em: {caminho_html}")

if __name__ == "__main__":
    main()