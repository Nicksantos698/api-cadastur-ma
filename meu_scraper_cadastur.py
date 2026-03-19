import time
import os
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from supabase import create_client

# --- CONFIGURAÇÕES SUPABASE ---
URL_SUPABASE = "https://zaaoyieedbtqpqmnntmp.supabase.co"
CHAVE_PUBLICA = "sb_publishable__3C7E6EfiL96wCzcbQVv2Q_v5aMP9Rp"
supabase = create_client(URL_SUPABASE, CHAVE_PUBLICA)

# Caminho para Backup
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
caminho_final = os.path.join(desktop, "CADASTUR_MA_TOTAL.xlsx")

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
navegador = uc.Chrome(options=options)

try:
    print("🚀 Robô: Iniciando Extração Total (Sem limites de páginas)...")
    navegador.get("https://cadastur.turismo.gov.br/hotsite/#!/public/capa/entrar")
    aguardar = WebDriverWait(navegador, 30)
    
    # Navegação inicial
    btn_turista = aguardar.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@ng-click, 'souTurista')]")))
    navegador.execute_script("arguments[0].click();", btn_turista)

    time.sleep(5) 
    navegador.execute_script("""
        document.querySelectorAll('.modal, .modal-backdrop, .fade.in').forEach(el => el.remove());
        document.body.classList.remove('modal-open');
        document.body.style.overflow = 'auto';
    """)

    # Preenchimento
    aguardar.until(EC.presence_of_element_located((By.TAG_NAME, "select"))).send_keys("MA")
    campo_local = aguardar.until(EC.presence_of_element_located((By.NAME, "local")))
    campo_local.send_keys("SÃO LUÍS")

    print("\n" + "!"*50)
    print("AÇÃO MANUAL: Selecione São Luís, resolva o Captcha e PESQUISE.")
    print("!"*50 + "\n")

    aguardar.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr.ng-scope")))
    
    todos_os_dados = []
    pagina_atual = 1

    # LOOP INFINITO ATÉ O FIM DAS PÁGINAS
    while True:
        tentativas_na_pagina = 0
        sucesso_pagina = False
        
        while tentativas_na_pagina < 3 and not sucesso_pagina:
            try:
                print(f"📂 Coletando Página {pagina_atual}...")
                time.sleep(4) 

                linhas = navegador.find_elements(By.CSS_SELECTOR, "tbody tr.ng-scope")
                if not linhas:
                    break

                for l in linhas:
                    cols = l.find_elements(By.TAG_NAME, "td")
                    if len(cols) > 6:
                        todos_os_dados.append({
                            "numero_cadastro": cols[0].text,
                            "nome_prestador": cols[1].text,
                            "municipio": cols[3].text,
                            "localidade": cols[4].text,
                            "bairro": cols[5].text,
                            "atividade": cols[6].text,
                            "uf": "MA"
                        })
                sucesso_pagina = True
            except StaleElementReferenceException:
                print(f"⚠️ Erro de carregamento na página {pagina_atual}. Tentando de novo...")
                tentativas_na_pagina += 1
                time.sleep(3)

        # Tentar ir para a próxima página
        try:
            # Localiza o botão "Próximo"
            btn_prox_li = navegador.find_element(By.XPATH, "//li[contains(@class, 'pagination-next')]")
            
            # Verifica se o botão está desativado (fim da lista)
            if "disabled" in btn_prox_li.get_attribute("class"):
                print(f"🏁 Fim das páginas alcançado na página {pagina_atual}!")
                break
            
            # Se não estiver desativado, clica
            btn_prox_clique = btn_prox_li.find_element(By.TAG_NAME, "a")
            navegador.execute_script("arguments[0].click();", btn_prox_clique)
            pagina_atual += 1
        except Exception:
            print("🏁 Não há mais botões de navegação. Finalizando coleta.")
            break

    # ENVIO FINAL
    if todos_os_dados:
        total = len(todos_os_dados)
        pd.DataFrame(todos_os_dados).to_excel(caminho_final, index=False)
        print(f"📄 Backup salvo ({total} registros).")

        print(f"📡 Enviando carga total para o Supabase...")
        try:
            for i in range(0, total, 100):
                bloco = todos_os_dados[i : i + 100]
                supabase.table("empresas_ma").insert(bloco).execute()
                print(f"📤 Bloco enviado ({i + len(bloco)}/{total})")
            print("🏆 TUDO PRONTO! Banco de dados atualizado com sucesso.")
        except Exception as error:
            print(f"❌ Erro no disparo para a nuvem: {error}")

except Exception as e:
    print(f"❌ Erro Crítico: {e}")
finally:
    navegador.quit()
    print("\n🤖 Processo encerrado.")