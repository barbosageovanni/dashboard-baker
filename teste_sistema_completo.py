#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Testes Completo - Dashboard Baker PostgreSQL
Verifica todas as funcionalidades do sistema após instalação
"""

import sys
import os
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import subprocess
import importlib.util

class TesteSistemaBaker:
    """Classe para testar todas as funcionalidades do sistema"""
    
    def __init__(self):
        self.resultados = {
            'sucessos': 0,
            'falhas': 0,
            'avisos': 0,
            'detalhes': []
        }
        
        # Configuração padrão do banco (pode ser sobrescrita)
        self.db_config = {
            'host': 'localhost',
            'database': 'dashboard_baker',
            'user': 'postgres',
            'password': 'senha123',
            'port': 5432
        }
        
        self.carregar_config_env()
    
    def carregar_config_env(self):
        """Carrega configurações do arquivo .env se existir"""
        if os.path.exists('.env'):
            try:
                with open('.env', 'r', encoding='utf-8') as f:
                    for linha in f:
                        linha = linha.strip()
                        if linha and not linha.startswith('#') and '=' in linha:
                            chave, valor = linha.split('=', 1)
                            if chave == 'DB_HOST':
                                self.db_config['host'] = valor
                            elif chave == 'DB_NAME':
                                self.db_config['database'] = valor
                            elif chave == 'DB_USER':
                                self.db_config['user'] = valor
                            elif chave == 'DB_PASSWORD':
                                self.db_config['password'] = valor
                            elif chave == 'DB_PORT':
                                self.db_config['port'] = int(valor)
                
                self.log_sucesso("Configurações carregadas do arquivo .env")
            except Exception as e:
                self.log_aviso(f"Erro ao carregar .env: {e}")
        else:
            self.log_aviso("Arquivo .env não encontrado, usando configurações padrão")
    
    def log_sucesso(self, mensagem):
        """Log de sucesso"""
        print(f"✅ {mensagem}")
        self.resultados['sucessos'] += 1
        self.resultados['detalhes'].append(('SUCESSO', mensagem))
    
    def log_falha(self, mensagem):
        """Log de falha"""
        print(f"❌ {mensagem}")
        self.resultados['falhas'] += 1
        self.resultados['detalhes'].append(('FALHA', mensagem))
    
    def log_aviso(self, mensagem):
        """Log de aviso"""
        print(f"⚠️ {mensagem}")
        self.resultados['avisos'] += 1
        self.resultados['detalhes'].append(('AVISO', mensagem))
    
    def testar_python(self):
        """Testa versão do Python"""
        print("\n🐍 TESTANDO PYTHON")
        print("-" * 30)
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log_sucesso(f"Python {version.major}.{version.minor}.{version.micro} - Versão adequada")
        else:
            self.log_falha(f"Python {version.major}.{version.minor} - Versão inadequada (mínimo 3.8)")
        
        # Testar pip
        try:
            subprocess.check_output([sys.executable, '-m', 'pip', '--version'], 
                                   stderr=subprocess.STDOUT)
            self.log_sucesso("pip disponível")
        except Exception as e:
            self.log_falha(f"pip não disponível: {e}")
    
    def testar_dependencias(self):
        """Testa se todas as dependências estão instaladas"""
        print("\n📦 TESTANDO DEPENDÊNCIAS")
        print("-" * 30)
        
        dependencias = {
            'streamlit': 'Interface web',
            'pandas': 'Manipulação de dados',
            'plotly': 'Gráficos interativos',
            'psycopg2': 'Conexão PostgreSQL',
            'openpyxl': 'Arquivos Excel'
        }
        
        for lib, descricao in dependencias.items():
            try:
                if lib == 'psycopg2':
                    # psycopg2 pode ser instalado como psycopg2-binary
                    try:
                        import psycopg2
                    except ImportError:
                        import psycopg2_binary as psycopg2
                else:
                    importlib.import_module(lib)
                self.log_sucesso(f"{lib} - {descricao}")
            except ImportError:
                self.log_falha(f"{lib} não encontrado - {descricao}")
    
    def testar_arquivos_sistema(self):
        """Testa se todos os arquivos necessários estão presentes"""
        print("\n📁 TESTANDO ARQUIVOS DO SISTEMA")
        print("-" * 35)
        
        arquivos_obrigatorios = {
            'dashboard_baker_web_corrigido.py': 'Dashboard principal',
            'popular_banco_postgresql.py': 'Script de população',
            'config_banco.py': 'Configurações'
        }
        
        arquivos_opcionais = {
            '.env': 'Configurações de ambiente',
            'requirements_postgresql.txt': 'Lista de dependências',
            'iniciar_dashboard_postgresql.bat': 'Script de inicialização Windows'
        }
        
        # Testar arquivos obrigatórios
        for arquivo, descricao in arquivos_obrigatorios.items():
            if os.path.exists(arquivo):
                self.log_sucesso(f"{arquivo} - {descricao}")
            else:
                self.log_falha(f"{arquivo} não encontrado - {descricao}")
        
        # Testar arquivos opcionais
        for arquivo, descricao in arquivos_opcionais.items():
            if os.path.exists(arquivo):
                self.log_sucesso(f"{arquivo} - {descricao}")
            else:
                self.log_aviso(f"{arquivo} não encontrado - {descricao}")
    
    def testar_postgresql(self):
        """Testa conexão com PostgreSQL"""
        print("\n🐘 TESTANDO POSTGRESQL")
        print("-" * 25)
        
        try:
            # Testar conexão
            conn = psycopg2.connect(**self.db_config)
            self.log_sucesso(f"Conexão PostgreSQL: {self.db_config['host']}:{self.db_config['port']}")
            
            cursor = conn.cursor()
            
            # Testar versão PostgreSQL
            cursor.execute("SELECT version();")
            versao = cursor.fetchone()[0]
            self.log_sucesso(f"Versão PostgreSQL: {versao.split()[1]}")
            
            # Testar se banco dashboard_baker existe
            cursor.execute("SELECT datname FROM pg_database WHERE datname = 'dashboard_baker';")
            if cursor.fetchone():
                self.log_sucesso("Banco 'dashboard_baker' existe")
                
                # Conectar ao banco específico
                cursor.close()
                conn.close()
                
                self.db_config['database'] = 'dashboard_baker'
                conn = psycopg2.connect(**self.db_config)
                cursor = conn.cursor()
                
                # Testar tabela
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_name = 'dashboard_baker';
                """)
                
                if cursor.fetchone():
                    self.log_sucesso("Tabela 'dashboard_baker' existe")
                    
                    # Testar estrutura da tabela
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'dashboard_baker' 
                        ORDER BY ordinal_position;
                    """)
                    colunas = cursor.fetchall()
                    self.log_sucesso(f"Estrutura da tabela: {len(colunas)} colunas")
                    
                    # Testar dados
                    cursor.execute("SELECT COUNT(*) FROM dashboard_baker;")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        self.log_sucesso(f"Dados existentes: {count} registros")
                    else:
                        self.log_aviso("Tabela vazia - use popular_banco_postgresql.py")
                    
                else:
                    self.log_falha("Tabela 'dashboard_baker' não existe")
            else:
                self.log_falha("Banco 'dashboard_baker' não existe")
            
            cursor.close()
            conn.close()
            
        except psycopg2.OperationalError as e:
            self.log_falha(f"Erro de conexão PostgreSQL: {e}")
        except Exception as e:
            self.log_falha(f"Erro PostgreSQL: {e}")
    
    def testar_dashboard_imports(self):
        """Testa se o dashboard pode ser importado sem erros"""
        print("\n📊 TESTANDO DASHBOARD")
        print("-" * 22)
        
        try:
            # Adicionar diretório atual ao path
            sys.path.insert(0, os.getcwd())
            
            # Tentar importar funções principais do dashboard
            if os.path.exists('dashboard_baker_web_corrigido.py'):
                spec = importlib.util.spec_from_file_location(
                    "dashboard_baker", 
                    "dashboard_baker_web_corrigido.py"
                )
                dashboard_module = importlib.util.module_from_spec(spec)
                
                # Não executar o módulo, apenas verificar sintaxe
                with open('dashboard_baker_web_corrigido.py', 'r', encoding='utf-8') as f:
                    codigo = f.read()
                
                # Compilar código para verificar sintaxe
                compile(codigo, 'dashboard_baker_web_corrigido.py', 'exec')
                self.log_sucesso("Dashboard - Sintaxe válida")
                
                # Verificar se funções principais existem no código
                funcoes_esperadas = [
                    'carregar_dados_csv',
                    'processar_status_faturas',
                    'processar_variacoes_tempo',
                    'inserir_cte_banco'
                ]
                
                for funcao in funcoes_esperadas:
                    if funcao in codigo:
                        self.log_sucesso(f"Dashboard - Função '{funcao}' encontrada")
                    else:
                        self.log_aviso(f"Dashboard - Função '{funcao}' não encontrada")
                
                # Verificar correção do erro titlefont
                if 'titlefont' in codigo:
                    self.log_falha("Dashboard - Ainda contém 'titlefont' (deveria ser 'title')")
                else:
                    self.log_sucesso("Dashboard - Erro 'titlefont' corrigido")
                
            else:
                self.log_falha("Dashboard - Arquivo não encontrado")
                
        except SyntaxError as e:
            self.log_falha(f"Dashboard - Erro de sintaxe: {e}")
        except Exception as e:
            self.log_falha(f"Dashboard - Erro: {e}")
    
    def testar_popular_banco(self):
        """Testa script de população do banco"""
        print("\n🗄️ TESTANDO POPULAR BANCO")
        print("-" * 27)
        
        if not os.path.exists('popular_banco_postgresql.py'):
            self.log_falha("Script popular_banco_postgresql.py não encontrado")
            return
        
        try:
            with open('popular_banco_postgresql.py', 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            # Verificar sintaxe
            compile(codigo, 'popular_banco_postgresql.py', 'exec')
            self.log_sucesso("Popular banco - Sintaxe válida")
            
            # Verificar funções principais
            funcoes_esperadas = [
                'conectar_banco',
                'carregar_csv_existente',
                'mapear_dados_csv_para_banco',
                'inserir_registros_banco'
            ]
            
            for funcao in funcoes_esperadas:
                if funcao in codigo:
                    self.log_sucesso(f"Popular banco - Função '{funcao}' encontrada")
                else:
                    self.log_aviso(f"Popular banco - Função '{funcao}' não encontrada")
            
        except SyntaxError as e:
            self.log_falha(f"Popular banco - Erro de sintaxe: {e}")
        except Exception as e:
            self.log_falha(f"Popular banco - Erro: {e}")
    
    def testar_dados_exemplo(self):
        """Testa inserção e recuperação de dados de exemplo"""
        print("\n📊 TESTANDO DADOS DE EXEMPLO")
        print("-" * 29)
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Tentar inserir um registro de teste
            teste_cte = {
                'numero_cte': 99999,
                'destinatario_nome': 'TESTE AUTOMATIZADO',
                'valor_total': 100.00,
                'data_emissao': datetime.now().date(),
                'origem_dados': 'TESTE_SISTEMA'
            }
            
            # Verificar se o registro de teste não existe
            cursor.execute("SELECT id FROM dashboard_baker WHERE numero_cte = %s", 
                         (teste_cte['numero_cte'],))
            
            if cursor.fetchone():
                # Remover registro anterior
                cursor.execute("DELETE FROM dashboard_baker WHERE numero_cte = %s", 
                             (teste_cte['numero_cte'],))
                self.log_sucesso("Registro de teste anterior removido")
            
            # Inserir registro de teste
            cursor.execute("""
                INSERT INTO dashboard_baker (
                    numero_cte, destinatario_nome, valor_total, data_emissao, origem_dados
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                teste_cte['numero_cte'],
                teste_cte['destinatario_nome'],
                teste_cte['valor_total'],
                teste_cte['data_emissao'],
                teste_cte['origem_dados']
            ))
            
            conn.commit()
            self.log_sucesso("Inserção de dados - OK")
            
            # Verificar se foi inserido
            cursor.execute("""
                SELECT numero_cte, destinatario_nome, valor_total 
                FROM dashboard_baker 
                WHERE numero_cte = %s
            """, (teste_cte['numero_cte'],))
            
            resultado = cursor.fetchone()
            if resultado and resultado[0] == teste_cte['numero_cte']:
                self.log_sucesso("Consulta de dados - OK")
            else:
                self.log_falha("Consulta de dados - Falhou")
            
            # Limpar registro de teste
            cursor.execute("DELETE FROM dashboard_baker WHERE numero_cte = %s", 
                         (teste_cte['numero_cte'],))
            conn.commit()
            self.log_sucesso("Limpeza de dados de teste - OK")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.log_falha(f"Teste de dados: {e}")
    
    def testar_csv_exemplo(self):
        """Testa processamento de CSV"""
        print("\n📄 TESTANDO PROCESSAMENTO CSV")
        print("-" * 31)
        
        # Criar CSV de exemplo
        dados_exemplo = {
            'Número Cte': [22001, 22002, 22003],
            'Destinatário - Nome': ['Cliente A', 'Cliente B', 'Cliente C'],
            ' Total ': ['R$ 1.500,00', 'R$ 2.200,50', 'R$ 3.100,75'],
            'Data emissão Cte': ['01/jul/24', '15/jul/24', '30/jul/24'],
            'Fatura': ['F001', '', 'F003'],
            'Data baixa': ['05/jul/24', '', '']
        }
        
        try:
            df_teste = pd.DataFrame(dados_exemplo)
            arquivo_teste = 'teste_csv_temp.csv'
            
            # Salvar CSV temporário
            df_teste.to_csv(arquivo_teste, sep=';', index=False, encoding='cp1252')
            self.log_sucesso("CSV de teste criado")
            
            # Testar carregamento
            df_carregado = pd.read_csv(arquivo_teste, sep=';', encoding='cp1252')
            if len(df_carregado) == 3:
                self.log_sucesso("CSV carregado corretamente")
            else:
                self.log_falha(f"CSV carregado com {len(df_carregado)} registros (esperado: 3)")
            
            # Testar processamento de valores monetários
            df_carregado['Valor_Numerico'] = (
                df_carregado[' Total '].astype(str)
                .str.replace('R$', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.strip()
                .astype(float)
            )
            
            soma_esperada = 6800.25  # 1500 + 2200.50 + 3100.75
            soma_calculada = df_carregado['Valor_Numerico'].sum()
            
            if abs(soma_calculada - soma_esperada) < 0.01:
                self.log_sucesso("Processamento de valores monetários - OK")
            else:
                self.log_falha(f"Processamento monetário - Esperado: {soma_esperada}, Calculado: {soma_calculada}")
            
            # Limpar arquivo temporário
            os.remove(arquivo_teste)
            self.log_sucesso("CSV de teste removido")
            
        except Exception as e:
            self.log_falha(f"Teste CSV: {e}")
            # Tentar remover arquivo mesmo em caso de erro
            try:
                if os.path.exists('teste_csv_temp.csv'):
                    os.remove('teste_csv_temp.csv')
            except:
                pass
    
    def gerar_relatorio_final(self):
        """Gera relatório final dos testes"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        
        total_testes = self.resultados['sucessos'] + self.resultados['falhas'] + self.resultados['avisos']
        
        print(f"✅ Sucessos: {self.resultados['sucessos']}")
        print(f"❌ Falhas: {self.resultados['falhas']}")
        print(f"⚠️ Avisos: {self.resultados['avisos']}")
        print(f"📊 Total: {total_testes}")
        
        if total_testes > 0:
            taxa_sucesso = (self.resultados['sucessos'] / total_testes) * 100
            print(f"📈 Taxa de Sucesso: {taxa_sucesso:.1f}%")
        
        print("\n🎯 AVALIAÇÃO GERAL:")
        
        if self.resultados['falhas'] == 0:
            print("✅ SISTEMA TOTALMENTE FUNCIONAL")
            print("   Todos os testes passaram com sucesso!")
            status = "APROVADO"
        elif self.resultados['falhas'] <= 2:
            print("⚠️ SISTEMA PARCIALMENTE FUNCIONAL")  
            print("   Algumas funcionalidades podem não funcionar.")
            status = "APROVADO COM RESSALVAS"
        else:
            print("❌ SISTEMA COM PROBLEMAS")
            print("   Várias funcionalidades não estão funcionando.")
            status = "REPROVADO"
        
        # Salvar relatório detalhado
        self.salvar_relatorio_detalhado(status)
        
        print(f"\n📄 Relatório detalhado salvo em: relatorio_testes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        return status
    
    def salvar_relatorio_detalhado(self, status):
        """Salva relatório detalhado em arquivo"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"relatorio_testes_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE TESTES - DASHBOARD BAKER POSTGRESQL\n")
                f.write("=" * 60 + "\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Status Final: {status}\n")
                f.write(f"Configuração do Banco: {self.db_config}\n")
                f.write("\n")
                
                f.write("RESUMO DOS RESULTADOS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"✅ Sucessos: {self.resultados['sucessos']}\n")
                f.write(f"❌ Falhas: {self.resultados['falhas']}\n")
                f.write(f"⚠️ Avisos: {self.resultados['avisos']}\n")
                f.write("\n")
                
                f.write("DETALHES DOS TESTES:\n")
                f.write("-" * 30 + "\n")
                
                for tipo, mensagem in self.resultados['detalhes']:
                    emoji = "✅" if tipo == "SUCESSO" else ("❌" if tipo == "FALHA" else "⚠️")
                    f.write(f"{emoji} [{tipo}] {mensagem}\n")
                
                f.write("\n")
                f.write("RECOMENDAÇÕES:\n")
                f.write("-" * 30 + "\n")
                
                if self.resultados['falhas'] == 0:
                    f.write("• Sistema está funcionando perfeitamente\n")
                    f.write("• Execute: streamlit run dashboard_baker_web_corrigido.py\n")
                    f.write("• Acesse: http://localhost:8501\n")
                else:
                    f.write("• Corrija os problemas indicados pelas falhas\n")
                    f.write("• Execute setup_dashboard_postgresql.py se necessário\n")
                    f.write("• Verifique configurações do PostgreSQL\n")
                
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
    
    def executar_todos_testes(self):
        """Executa todos os testes"""
        print("🧪 INICIANDO TESTES COMPLETOS DO SISTEMA")
        print("🎯 Dashboard Baker - Versão PostgreSQL")
        print("=" * 60)
        
        # Executar testes em ordem
        self.testar_python()
        self.testar_dependencias()
        self.testar_arquivos_sistema()
        self.testar_postgresql()
        self.testar_dashboard_imports()
        self.testar_popular_banco()
        self.testar_dados_exemplo()
        self.testar_csv_exemplo()
        
        # Gerar relatório final
        status = self.gerar_relatorio_final()
        
        return status

def main():
    """Função principal"""
    teste = TesteSistemaBaker()
    status = teste.executar_todos_testes()
    
    # Código de saída baseado no status
    if status == "APROVADO":
        sys.exit(0)
    elif status == "APROVADO COM RESSALVAS":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()