from Modelo.siniestro_dao import SiniestroDAO

class SiniestroController:
    @staticmethod
    def calcular_semaforo(total, tasa_mortalidad, gravedad):
        if total == 0:
            return {"color": "verde", "nivel": "Sin Riesgo Detectado", "desc": "No se registran accidentes en este criterio"}

        if gravedad == "Mortal" or tasa_mortalidad >= 2.0 or total >= 1500:
            return {"color": "rojo", "nivel": "Peligro Crítico", "desc": "Alta siniestralidad o tasa de mortalidad elevada"}
        elif gravedad == "Grave" or tasa_mortalidad >= 0.8 or total >= 400:
            return {"color": "amarillo", "nivel": "Riesgo Moderado", "desc": "Siniestralidad intermedia. Requiere protocolos EPP"}
        else:
            return {"color": "verde", "nivel": "Bajo Riesgo", "desc": "Condiciones operativas estables y baja severidad"}

    @staticmethod
    def obtener_resumen(sector="todos", ubigeo="todos", gravedad="todas", f_ini=None, f_fin=None, pagina=1, tamano=10):
        filtrados = SiniestroDAO.filtrar(sector, ubigeo, gravedad, f_ini, f_fin)
        total_eventos = len(filtrados)

        mortales = len([s for s in filtrados if s["_gravedad_norm"] == "MORTAL"])
        tasa_mortalidad = round((mortales / total_eventos * 100), 2) if total_eventos > 0 else 0.0

        sector_riesgo = "N/A"
        if total_eventos > 0:
            secs = [s["sector"] for s in filtrados]
            sector_riesgo = max(set(secs), key=secs.count)

        semaforo = SiniestroController.calcular_semaforo(total_eventos, tasa_mortalidad, gravedad)

        pagina = max(1, int(pagina))
        tamano = max(1, int(tamano))
        inicio = (pagina - 1) * tamano
        datos_paginados = filtrados[inicio:inicio + tamano]
        total_paginas = max(1, (total_eventos + tamano - 1) // tamano)

        return {
            "datos": datos_paginados,
            "paginacion": {
                "pagina_actual": pagina,
                "total_paginas": total_paginas,
                "total_registros": total_eventos,
                "registros_mostrados": len(datos_paginados)
            },
            "kpis": {
                "total_eventos": f"{total_eventos:,}",
                "tasa_mortalidad": f"{tasa_mortalidad}%",
                "sector_riesgo": sector_riesgo,
                "semaforo": semaforo
            },
            "catalogos": {
                "sectores": sorted(list(SiniestroDAO._sectores_disponibles)),
                "ubigeos": sorted(list(SiniestroDAO._ubigeos_disponibles))
            }
        }

    @staticmethod
    def obtener_rf05(ano="todos", gravedad="todas", sector="todos", ubigeo="todos"):
        filtrados_estrictos = SiniestroDAO.filtrar(sector=sector, ubigeo=ubigeo, gravedad=gravedad, ano=ano)
        data_reg = SiniestroDAO.filtrar(sector=sector, ubigeo="todos", gravedad=gravedad, ano=ano) or SiniestroDAO.listar()
        reg_c = {}
        for s in data_reg:
            reg_c[s["ubigeo"]] = reg_c.get(s["ubigeo"], 0) + 1
        top_reg = sorted(reg_c.items(), key=lambda x: x[1], reverse=True)[:7]

        data_sec = SiniestroDAO.filtrar(sector="todos", ubigeo=ubigeo, gravedad=gravedad, ano=ano) or SiniestroDAO.listar()
        sec_c = {}
        for s in data_sec:
            sec_c[s["sector"]] = sec_c.get(s["sector"], 0) + 1
        top_sec = sorted(sec_c.items(), key=lambda x: x[1], reverse=True)[:6]

        base_sev = filtrados_estrictos if filtrados_estrictos else data_sec
        mortal = len([s for s in base_sev if s["_gravedad_norm"] == "MORTAL"])
        grave = len([s for s in base_sev if s["_gravedad_norm"] == "GRAVE"])
        leve = len([s for s in base_sev if s["_gravedad_norm"] == "LEVE"])

        anos_base = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
        data_tend = SiniestroDAO.filtrar(sector=sector, ubigeo=ubigeo, gravedad="todas", ano="todos")
        tendencia_vals = [len([s for s in data_tend if s.get("ano") == y]) for y in anos_base]

        return {
            "total_filtrado": len(filtrados_estrictos),
            "regiones": {"labels": [r[0] for r in top_reg] if top_reg else ["Sin datos"], "valores": [r[1] for r in top_reg] if top_reg else [0]},
            "sectores": {"labels": [s[0] for s in top_sec] if top_sec else ["Sin datos"], "valores": [s[1] for s in top_sec] if top_sec else [0]},
            "severidad": {"mortal": mortal, "grave": grave, "leve": leve},
            "tendencia": {"anos": anos_base, "valores": tendencia_vals}
        }

    @staticmethod
    def nuevo_siniestro(datos):
        SiniestroDAO.insertar(datos)

    @staticmethod
    def exportar_csv(sector="todos", ubigeo="todos", gravedad="todas", f_ini=None, f_fin=None):
        filtrados = SiniestroDAO.filtrar(sector, ubigeo, gravedad, f_ini, f_fin)
        salida = "Codigo,Fecha,Empresa,Sector_CIIU,UBIGEO,Gravedad,Estado,Ano\n"
        for s in filtrados:
            salida += f'"{s["codigo"]}","{s["fecha"]}","{s["empresa"]}","{s["sector"]}","{s["ubigeo"]}","{s["gravedad"]}","{s["estado"]}",{s["ano"]}\n'
        return salida