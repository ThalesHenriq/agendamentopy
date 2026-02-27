import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import json
import os
from dataclasses import dataclass
from typing import List, Optional
import calendar

# Configuração da página
st.set_page_config(
    page_title="Sistema de Agendamento",
    page_icon="📅",
    layout="wide"
)

# Classe para representar um agendamento
@dataclass
class Agendamento:
    id: str
    nome_cliente: str
    email: str
    telefone: str
    data: str
    hora: str
    servico: str
    profissional: str
    observacoes: str
    status: str  # "confirmado", "cancelado", "concluído"

class GerenciadorAgendamentos:
    def __init__(self, arquivo_dados="agendamentos.json"):
        self.arquivo_dados = arquivo_dados
        self.servicos = {
            "Corte de Cabelo": 30,
            "Barba": 20,
            "Corte + Barba": 45,
            "Coloração": 60,
            "Hidratação": 40,
            "Manicure": 30,
            "Pedicure": 30
        }
        self.profissionais = ["João", "Maria", "Carlos", "Ana"]
        self.horario_inicio = 8  # 8:00
        self.horario_fim = 18  # 18:00
        self.intervalo_minutos = 30
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega os agendamentos do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                self.agendamentos = [Agendamento(**a) for a in dados]
        else:
            self.agendamentos = []
    
    def salvar_dados(self):
        """Salva os agendamentos no arquivo JSON"""
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            dados = [a.__dict__ for a in self.agendamentos]
            json.dump(dados, f, indent=4, ensure_ascii=False)
    
    def adicionar_agendamento(self, agendamento: Agendamento):
        """Adiciona um novo agendamento"""
        self.agendamentos.append(agendamento)
        self.salvar_dados()
    
    def verificar_disponibilidade(self, data: str, hora: str, profissional: str) -> bool:
        """Verifica se o horário está disponível para o profissional"""
        for agendamento in self.agendamentos:
            if (agendamento.data == data and 
                agendamento.hora == hora and 
                agendamento.profissional == profissional and
                agendamento.status == "confirmado"):
                return False
        return True
    
    def obter_horarios_disponiveis(self, data: str, profissional: str) -> List[str]:
        """Retorna lista de horários disponíveis para uma data e profissional"""
        if not data:
            return []
        
        horarios = []
        hora_atual = datetime.strptime(f"{data} {self.horario_inicio}:00", "%Y-%m-%d %H:%M")
        hora_fim = datetime.strptime(f"{data} {self.horario_fim}:00", "%Y-%m-%d %H:%M")
        
        while hora_atual <= hora_fim:
            hora_str = hora_atual.strftime("%H:%M")
            if self.verificar_disponibilidade(data, hora_str, profissional):
                horarios.append(hora_str)
            hora_atual += timedelta(minutes=self.intervalo_minutos)
        
        return horarios
    
    def cancelar_agendamento(self, agendamento_id: str):
        """Cancela um agendamento"""
        for agendamento in self.agendamentos:
            if agendamento.id == agendamento_id:
                agendamento.status = "cancelado"
                self.salvar_dados()
                return True
        return False
    
    def concluir_agendamento(self, agendamento_id: str):
        """Marca um agendamento como concluído"""
        for agendamento in self.agendamentos:
            if agendamento.id == agendamento_id:
                agendamento.status = "concluído"
                self.salvar_dados()
                return True
        return False
    
    def buscar_agendamentos(self, data_inicio=None, data_fim=None, status=None, profissional=None):
        """Busca agendamentos com filtros"""
        resultados = self.agendamentos.copy()
        
        if data_inicio:
            resultados = [a for a in resultados if a.data >= data_inicio]
        if data_fim:
            resultados = [a for a in resultados if a.data <= data_fim]
        if status:
            resultados = [a for a in resultados if a.status == status]
        if profissional:
            resultados = [a for a in resultados if a.profissional == profissional]
        
        return sorted(resultados, key=lambda x: (x.data, x.hora))

# Inicialização do gerenciador
if 'gerenciador' not in st.session_state:
    st.session_state.gerenciador = GerenciadorAgendamentos()

# Interface principal
st.title("📅 Sistema de Agendamento")
st.markdown("---")

# Menu lateral
with st.sidebar:
    st.header("Menu")
    opcao = st.radio(
        "Selecione uma opção:",
        ["Novo Agendamento", "Visualizar Agendamentos", "Gerenciar", "Relatórios"]
    )
    
    st.markdown("---")
    st.subheader("Informações")
    st.info(f"Total de agendamentos: {len(st.session_state.gerenciador.agendamentos)}")

# Conteúdo principal baseado na opção selecionada
if opcao == "Novo Agendamento":
    st.header("📝 Novo Agendamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Cliente *")
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone *")
        
        data = st.date_input(
            "Data do Agendamento *",
            min_value=datetime.now().date(),
            format="DD/MM/YYYY"
        )
    
    with col2:
        profissional = st.selectbox(
            "Profissional *",
            options=st.session_state.gerenciador.profissionais
        )
        
        servico = st.selectbox(
            "Serviço *",
            options=list(st.session_state.gerenciador.servicos.keys())
        )
        
        # Obter horários disponíveis
        horarios_disponiveis = st.session_state.gerenciador.obter_horarios_disponiveis(
            data.strftime("%Y-%m-%d") if data else "",
            profissional
        )
        
        hora = st.selectbox(
            "Horário *",
            options=horarios_disponiveis if horarios_disponiveis else ["Sem horários disponíveis"]
        )
    
    observacoes = st.text_area("Observações")
    
    # Botão de agendamento
    if st.button("Agendar", type="primary", use_container_width=True):
        if nome and telefone and data and hora and profissional and servico:
            if hora != "Sem horários disponíveis":
                # Criar novo agendamento
                novo_agendamento = Agendamento(
                    id=f"AGR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    nome_cliente=nome,
                    email=email,
                    telefone=telefone,
                    data=data.strftime("%Y-%m-%d"),
                    hora=hora,
                    servico=servico,
                    profissional=profissional,
                    observacoes=observacoes,
                    status="confirmado"
                )
                
                st.session_state.gerenciador.adicionar_agendamento(novo_agendamento)
                st.success("✅ Agendamento realizado com sucesso!")
                st.balloons()
            else:
                st.error("❌ Horário não disponível!")
        else:
            st.error("❌ Por favor, preencha todos os campos obrigatórios (*)")

elif opcao == "Visualizar Agendamentos":
    st.header("📋 Agendamentos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_data_inicio = st.date_input("Data Início", value=None)
    with col2:
        filtro_data_fim = st.date_input("Data Fim", value=None)
    with col3:
        filtro_status = st.selectbox(
            "Status",
            options=["Todos", "confirmado", "cancelado", "concluído"]
        )
    
    # Aplicar filtros
    agendamentos_filtrados = st.session_state.gerenciador.buscar_agendamentos(
        data_inicio=filtro_data_inicio.strftime("%Y-%m-%d") if filtro_data_inicio else None,
        data_fim=filtro_data_fim.strftime("%Y-%m-%d") if filtro_data_fim else None,
        status=None if filtro_status == "Todos" else filtro_status
    )
    
    if agendamentos_filtrados:
        # Converter para DataFrame para exibição
        dados_exibicao = []
        for a in agendamentos_filtrados:
            dados_exibicao.append({
                "ID": a.id,
                "Cliente": a.nome_cliente,
                "Data": datetime.strptime(a.data, "%Y-%m-%d").strftime("%d/%m/%Y"),
                "Hora": a.hora,
                "Serviço": a.servico,
                "Profissional": a.profissional,
                "Status": a.status
            })
        
        df = pd.DataFrame(dados_exibicao)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Detalhes do agendamento selecionado
        st.subheader("Detalhes do Agendamento")
        agendamento_id = st.selectbox(
            "Selecione um agendamento para ver detalhes",
            options=[a.id for a in agendamentos_filtrados],
            format_func=lambda x: f"{x} - {next((a.nome_cliente for a in agendamentos_filtrados if a.id == x), '')}"
        )
        
        if agendamento_id:
            agendamento = next((a for a in agendamentos_filtrados if a.id == agendamento_id), None)
            if agendamento:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Cliente:**", agendamento.nome_cliente)
                    st.write("**Telefone:**", agendamento.telefone)
                    st.write("**E-mail:**", agendamento.email or "Não informado")
                    st.write("**Data:**", datetime.strptime(agendamento.data, "%Y-%m-%d").strftime("%d/%m/%Y"))
                with col2:
                    st.write("**Hora:**", agendamento.hora)
                    st.write("**Serviço:**", agendamento.servico)
                    st.write("**Profissional:**", agendamento.profissional)
                    st.write("**Status:**", agendamento.status)
                
                st.write("**Observações:**", agendamento.observacoes or "Sem observações")
    else:
        st.info("Nenhum agendamento encontrado com os filtros selecionados.")

elif opcao == "Gerenciar":
    st.header("⚙️ Gerenciar Agendamentos")
    
    # Lista de agendamentos ativos
    agendamentos_ativos = [a for a in st.session_state.gerenciador.agendamentos if a.status == "confirmado"]
    
    if agendamentos_ativos:
        for agendamento in agendamentos_ativos:
            with st.expander(f"{agendamento.nome_cliente} - {agendamento.data} {agendamento.hora}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Serviço:** {agendamento.servico}")
                    st.write(f"**Profissional:** {agendamento.profissional}")
                
                with col2:
                    if st.button(f"✅ Concluir", key=f"conc_{agendamento.id}"):
                        st.session_state.gerenciador.concluir_agendamento(agendamento.id)
                        st.rerun()
                
                with col3:
                    if st.button(f"❌ Cancelar", key=f"cancel_{agendamento.id}"):
                        st.session_state.gerenciador.cancelar_agendamento(agendamento.id)
                        st.rerun()
    else:
        st.info("Nenhum agendamento ativo no momento.")

elif opcao == "Relatórios":
    st.header("📊 Relatórios")
    
    # Estatísticas gerais
    total_agendamentos = len(st.session_state.gerenciador.agendamentos)
    confirmados = len([a for a in st.session_state.gerenciador.agendamentos if a.status == "confirmado"])
    concluidos = len([a for a in st.session_state.gerenciador.agendamentos if a.status == "concluído"])
    cancelados = len([a for a in st.session_state.gerenciador.agendamentos if a.status == "cancelado"])
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", total_agendamentos)
    with col2:
        st.metric("Confirmados", confirmados)
    with col3:
        st.metric("Concluídos", concluidos)
    with col4:
        st.metric("Cancelados", cancelados)
    
    # Gráfico de serviços mais solicitados
    st.subheader("Serviços Mais Solicitados")
    servicos_count = {}
    for a in st.session_state.gerenciador.agendamentos:
        servicos_count[a.servico] = servicos_count.get(a.servico, 0) + 1
    
    if servicos_count:
        df_servicos = pd.DataFrame(
            list(servicos_count.items()),
            columns=["Serviço", "Quantidade"]
        ).sort_values("Quantidade", ascending=False)
        
        st.bar_chart(df_servicos.set_index("Serviço"))
    
    # Exportar dados
    st.subheader("Exportar Dados")
    if st.button("Exportar para CSV"):
        dados_export = []
        for a in st.session_state.gerenciador.agendamentos:
            dados_export.append({
                "ID": a.id,
                "Cliente": a.nome_cliente,
                "Email": a.email,
                "Telefone": a.telefone,
                "Data": a.data,
                "Hora": a.hora,
                "Serviço": a.servico,
                "Profissional": a.profissional,
                "Status": a.status,
                "Observações": a.observacoes
            })
        
        df_export = pd.DataFrame(dados_export)
        csv = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"agendamentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Rodapé
st.markdown("---")
