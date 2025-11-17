import streamlit as st
import pandas as pd
import sqlite3
import altair as alt 
import numpy as np 

# Configuração da Página
st.set_page_config(
    page_title="Análise FM23",
    layout="wide" 
)

# Título 
st.title("Análise de Jogadores - Football Manager Scouting")

# Carregamento dos Dados 
@st.cache_data
def load_data():
    con = sqlite3.connect("database/fm_database.db")
    df = pd.read_sql_query("SELECT * FROM players", con)
    con.close()

    df['posicao'] = df['posicao'].fillna('Desconhecida')
    df['clube'] = df['clube'].fillna('Sem Clube')
    df['pais'] = df['pais'].fillna('Desconhecido')
    return df

# Carrega os dados
try:
    df_players = load_data()

    st.sidebar.header("Filtros Interativos")

    # Filtros de Seleção 
    
    # Filtro de Texto para Nome
    filtro_nome = st.sidebar.text_input(
        "Buscar por Nome",
        placeholder="Digite o nome do jogador..."
    )

    # Filtro de Seleção para Função (usando sufixo_atual)
    funcoes_unicas = sorted(list(set(
        f.strip() for funcs in df_players['sufixo_atual'].dropna() 
        for f in funcs.split(',') if f.strip()
    )))
    
    filtro_funcao = st.sidebar.multiselect(
        "Função Atual",
        options=funcoes_unicas,
        default=[]
    )   
    
    posicoes_unicas = sorted(df_players['posicao'].dropna().unique())
    filtro_posicao = st.sidebar.multiselect(
        "Posição (posicao)",
        options=posicoes_unicas,
        default=[] 
    )

    clubes_unicos = sorted(df_players['clube'].dropna().unique())
    filtro_clube = st.sidebar.multiselect(
        "Clube (clube)",
        options=clubes_unicos,
        default=[]
    )

    paises_unicos = sorted(df_players['pais'].dropna().unique())
    filtro_pais = st.sidebar.multiselect(
        "País (pais)",
        options=paises_unicos,
        default=[]
    )

    # Filtros de Intervalo (Slider)
    idade_min = int(df_players['idade'].min())
    idade_max = int(df_players['idade'].max())
    filtro_idade = st.sidebar.slider(
        "Idade (idade)",
        min_value=idade_min,
        max_value=idade_max,
        value=(idade_min, idade_max) 
    )

    potencial_min = float(df_players['classificacao_potencial'].min())
    potencial_max = float(df_players['classificacao_potencial'].max())
    filtro_potencial = st.sidebar.slider(
        "Potencial (classificacao_potencial)",
        min_value=potencial_min,
        max_value=potencial_max,
        value=(potencial_min, potencial_max)
    )

    valor_max = int(df_players['valor'].max())
    filtro_valor = st.sidebar.slider(
        "Valor de Mercado (valor)",
        min_value=0,
        max_value=valor_max,
        value=(0, valor_max),
        step=100000,
        format="€ %d"
    )
    
    df_filtered = df_players.copy()
    
    df_filtered = df_players.copy()

    if filtro_nome:
        df_filtered = df_filtered[df_filtered['nome'].str.contains(filtro_nome, case=False, na=False)]
    if filtro_funcao:
        df_filtered = df_filtered[df_filtered['sufixo_atual'].str.contains('|'.join(filtro_funcao), na=False)]
    if filtro_posicao:
        df_filtered = df_filtered[df_filtered['posicao'].isin(filtro_posicao)]
    if filtro_clube:
        df_filtered = df_filtered[df_filtered['clube'].isin(filtro_clube)]
    if filtro_pais:
        df_filtered = df_filtered[df_filtered['pais'].isin(filtro_pais)]

    # Filtros de intervalo (idade, potencial, valor)
    df_filtered = df_filtered[
        (df_filtered['idade'] >= filtro_idade[0]) & (df_filtered['idade'] <= filtro_idade[1])
    ]
    df_filtered = df_filtered[
        (df_filtered['classificacao_potencial'] >= filtro_potencial[0]) & (df_filtered['classificacao_potencial'] <= filtro_potencial[1])
    ]
    df_filtered = df_filtered[
        (df_filtered['valor'] >= filtro_valor[0]) & (df_filtered['valor'] <= filtro_valor[1])
    ]

    # PÁGINA PRINCIPAL 
    st.header("Análise Principal (Resultados Filtrados)")
    st.info(f"Mostrando **{len(df_filtered)}** jogadores de um total de **{len(df_players)}** com base nos filtros aplicados.")
    
    st.dataframe(
    df_filtered.sort_values(by="classificacao_potencial", ascending=False).head(50), 
    height=500,
    column_config={
            "valor": st.column_config.NumberColumn(
                "Valor de Mercado",
                format="€ %d"  
            ),
            "salario": st.column_config.NumberColumn(
                "Salário",
                format="€ %d"  
            ),
            "posicao": st.column_config.TextColumn(
                "Posições", 
                help="Todas as posições que o jogador pode atuar. Veja a aba 'Legendas' para as abreviações."
            ),
            "sufixo_atual": st.column_config.TextColumn(
                "Função (Atual)",  
                help="Melhor função/perfil do jogador (ex: W, FS). Veja a aba 'Legendas'."
            ),
            "sufixo_potencial": st.column_config.TextColumn(
                "Função (Potencial)", 
                help="Melhor função/perfil potencial do jogador (ex: W, FS). Veja a aba 'Legendas'."
            )
        }
    )

    st.markdown("---") 

    # Seções de Análise (em ABAS)
    st.header("Análises Detalhadas")
    tab1, tab2, tab3, tab_evolucao, tab_legenda = st.tabs([
        "Wonderkids", 
        "Melhor custo-benefício", 
        "Fábrica de talentos (Clube/País)",
        "Evolução dos jogadores",
        "Legendas e Informações"     
    ])

    # Aba 1: Wonderkids
    with tab1:
        st.subheader("Jogadores com maior diferença entre Qualidade Atual e Potencial")
        
        idade_brutos = st.slider("Idade Máxima", 15, 25, 21, key="idade_brutos")
        
        df_gap = df_filtered.copy()
        df_gap['gap_potencial'] = df_gap['classificacao_potencial'] - df_gap['classificacao_atual']
        
        df_gap_filtrado = df_gap[df_gap['idade'] <= idade_brutos]
        
        st.dataframe(
            df_gap_filtrado.sort_values(by="gap_potencial", ascending=False).head(20),
            column_order=[
                'nome', 'clube', 'idade', 'gap_potencial', 
                'classificacao_atual', 'classificacao_potencial', 'valor'
            ],
            column_config={
                "gap_potencial": st.column_config.NumberColumn(
                    "Gap Potencial",
                    help="Diferença entre Potencial e Qualidade Atual",
                    format="%.1f"
                )
            }
        )

    # Aba 2: Pechinchas 
    with tab2:
        st.subheader("Gráfico de Custo-Benefício (Qualidade Atual vs. Valor)")
        st.markdown("Procure por jogadores no **canto superior esquerdo** (alta qualidade, baixo valor).")

        df_pechinchas = df_filtered[df_filtered['valor'] > 1000].copy()

        use_log_valor = st.checkbox("Usar escala logarítmica para 'Valor'", value=True)
        scale_type = "log" if use_log_valor else "linear"

        chart = alt.Chart(df_pechinchas).mark_circle(opacity=0.7).encode(
            x=alt.X('valor', title='Valor de Mercado', scale=alt.Scale(type=scale_type)),
            y=alt.Y('classificacao_atual', title='Qualidade Atual'),
            tooltip=['nome', 'clube', 'idade', 'valor', 'classificacao_atual', 'posicao']
        ).interactive() 

        st.altair_chart(chart, use_container_width=True)

    # Aba 3: Clubes que produzem os Wonderkids
    with tab3:
        st.subheader("Quais Clubes e Países produzem os melhores talentos?")
        
        col1, col2 = st.columns(2) 

        with col1:
            st.markdown("#### Top Clubes por Potencial Médio")
            
            min_players_club = st.slider("Nº mínimo de jogadores no clube (para média)", 1, 10, 3, key="min_jog_clube")
            
            club_stats = df_filtered.groupby('clube')['classificacao_potencial'].agg(['mean', 'count'])
            club_stats_filtered = club_stats[club_stats['count'] >= min_players_club]
            
            top_clubs = club_stats_filtered.sort_values(by='mean', ascending=False).head(15)
            top_clubs.columns = ['Potencial Médio', 'Nº de Jogadores']
            st.dataframe(top_clubs.style.format({"Potencial Médio": "{:.1f}"}))

        with col2:
            st.markdown("#### Top Países por contagem de 'Wonderkids'")

            # Define os atributos para um Wonderkid
            potencial_wonderkid = st.slider("Potencial Mínimo (Wonderkid)", 80.0, 100.0, 90.0, step=0.1, key="pot_wk")
            idade_wonderkid = st.slider("Idade Máxima (Wonderkid)", 18, 23, 21, key="idade_wk")

            df_wonderkids = df_filtered[
                (df_filtered['classificacao_potencial'] >= potencial_wonderkid) & 
                (df_filtered['idade'] <= idade_wonderkid)
            ]
            
            country_counts = df_wonderkids['pais'].value_counts().head(15)
            st.bar_chart(country_counts)
    
    # Aba 4: Evolução dos Jogadores
    with tab_evolucao:
        st.subheader("Análise de Evolução do Jogador")
        st.markdown("Use os filtros da sidebar para refinar a lista de jogadores e, em seguida, selecione um jogador abaixo para ver seu histórico.")

        nomes_unicos_filtrados = sorted(df_filtered['nome'].unique())
        
        jogador_selecionado = st.selectbox(
            "Selecione um jogador:",
            options=nomes_unicos_filtrados,
            index=None,
            placeholder="Escolha um jogador para analisar..."
        )

        if jogador_selecionado:
            df_historico = df_players[df_players['nome'] == jogador_selecionado].copy()
            
            df_historico['data_snapshot'] = pd.to_datetime(df_historico['data_snapshot'])
            df_historico = df_historico.sort_values(by="data_snapshot")

            if len(df_historico) < 2:
                st.warning(f"O jogador '{jogador_selecionado}' tem apenas 1 registro. Não é possível mostrar a evolução.")
                st.dataframe(df_historico)
            
            else:
                primeiro_snapshot = df_historico.iloc[0]
                ultimo_snapshot = df_historico.iloc[-1]
                
                delta_atual = ultimo_snapshot['classificacao_atual'] - primeiro_snapshot['classificacao_atual']
                delta_potencial = ultimo_snapshot['classificacao_potencial'] - primeiro_snapshot['classificacao_potencial']
                delta_valor = ultimo_snapshot['valor'] - primeiro_snapshot['valor']

                st.markdown(f"#### Resumo da Evolução de {jogador_selecionado}")
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric(
                    "Qualidade Atual", 
                    f"{ultimo_snapshot['classificacao_atual']:.1f}", 
                    f"{delta_atual:+.1f}"
                )
                col_m2.metric(
                    "Potencial", 
                    f"{ultimo_snapshot['classificacao_potencial']:.1f}", 
                    f"{delta_potencial:+.1f}"
                )
                col_m3.metric(
                    "Valor de Mercado", 
                    f"€ {ultimo_snapshot['valor']:,.0f}", 
                    f"€ {delta_valor:+,.0f}"
                )

                st.markdown("---")
                st.markdown("### Gráfico de Evolução (vs. Tempo)")
                
                df_plot = df_historico.set_index('data_snapshot')
                st.line_chart(df_plot[['classificacao_atual', 'classificacao_potencial']])
                st.markdown("### Evolução do Valor de Mercado")
                st.line_chart(df_plot[['valor']])
                
                st.markdown("---")
    
    # Aba 5: Legendas
    with tab_legenda:
        st.subheader("Legendas")
        st.markdown("Aqui você encontra a explicação dos termos e abreviações usados no dashboard.")
        
        st.markdown("---")

        with st.container(border=True):
                st.markdown("### 💡 Como Pesquisar de Forma Eficiente")
                st.markdown("""
                Você tem duas formas principais para filtrar jogadores pela sua atuação em campo: **Posição** e **Função**. Entender a diferença é a chave para uma boa análise:

                1.  **Filtro de Posição (`posicao`):**
                    * **O que é:** Um filtro **específico e detalhado**.
                    * **O que mostra:** *Todas* as posições literais que o jogador pode atuar (ex: `DC`, `DD`, `DE`, `MA DEC`).
                    * **Quando usar:** Quando você precisa preencher uma vaga muito específica (ex: "Estou procurando apenas por `DC`" ou "Quem pode jogar de `MA DEC`?").

                2.  **Filtro de Função (`Função Atual`):**
                    * **O que é:** Um filtro **amplo e categórico**.
                    * **O que mostra:** O *perfil geral* ou a *faixa do campo* onde o jogador atua (ex: `CB`, `FB`, `W`, `AM`).
                    * **Quando usar:** Quando você quer ver um *grupo* de jogadores (ex: "Quero ver todos os meus zagueiros" ou "Quero ver todos os meus pontas").
                """)
                
                st.info("""
                **Dica (Exemplo):**
                * Se você quer ver **todos os laterais** (direitos e esquerdos) de uma só vez, use o filtro **`Função Atual`** e selecione **`FB`** (Full Back).
                * Se você quer ver **apenas** laterais **direitos**, use o filtro **`Posição`** e selecione **`DD`**.
                """)

                st.markdown("---")
        
        with st.container(border=True):
            st.markdown("### Abreviaturas de Funções (`Função Atual`)")
            st.write("Estas são as abreviações para o **perfil geral** do jogador, indicando seu papel em campo.")
            
            col_func1, col_func2, col_func3 = st.columns(3)
            with col_func1:
                st.markdown("""
                * **AM**: Advanced Midfielder (Meia Avançado)
                * **CB**: Center Back (Zagueiro)
                * **DM**: Defensive Midfielder (Volante)
                * **FB**: Full Back (Lateral)
                """)
            with col_func2:
                st.markdown("""
                * **FS**: Full Striker (Atacante Completo)
                * **GK**: Goalkeeper (Goleiro)
                * **M**: Midfielder (Meia Central)
                """)
            with col_func3:
                st.markdown("""
                * **TS**: Target Striker (Atacante Pivô)
                * **W**: Winger (Ponta)
                * **WB**: Winger Back (Ala)
                """)
        
        st.markdown("---")
        
        # Agrupado em um container para destaque
        with st.container(border=True):
            st.markdown("### Abreviaturas de Posições (`Posições`)")
            st.write("Estas são *todas* as posições que o jogador tem aptidão para jogar (ex: 'MA DEC').")
                
            col_pos1, col_pos2, col_pos3 = st.columns(3)
            with col_pos1:
                st.markdown("""
                * **GR**: Goleiro
                * **DD**: Lateral Direito
                * **DE**: Lateral Esquerdo
                * **DC**: Defensor Central
                """)
            with col_pos2:
                st.markdown("""
                * **DM**: Volante (Meio Defensivo)
                * **MC**: Meia Central
                * **MD**: Meia Direita
                * **ME**: Meia Esquerda
                """)
            with col_pos3:
                st.markdown("""
                * **MA**: Meia Atacante
                * **PL**: Ponta de Lança (Atacante)
                * **D / E / C**: Lado Direito / Esquerdo / Central
                """)
            st.success("**Exemplo:** Um jogador listado como **'MA DEC'** pode atuar como **Meia Atacante** e **Defensor Central**.")

        st.markdown("---")
        
        st.markdown("### Funções de Jogador (`Função (Atual)` / `Função (Potencial)`)")
        st.write("Diz respeito a **melhor função** que o jogador exerce em campo. A abreviação (ex: 'EX', 'CJ') é extraída do dado. **Clique em cada função** para ver os detalhes.")
        
        col_func1, col_func2, col_func3 = st.columns(3)
        
        # --- Coluna 1: Defesa ---
        with col_func1:
            
            # Container para Goleiros
            with st.container(border=True):
                st.markdown("#### Goleiros (GR)")
                
                with st.expander("**GK**: Goleiro (Goalkeeper)"):
                    st.write("Ele joga um futebol simples, sem riscos, e procura encontrar jogadores livres para passar a bola; caso contrário, faz um passe longo. A distribuição do goleiro mudará de acordo com a estratégia da partida:")
                    st.markdown("* **Táticas Cautelosas:** Ele irá 'limpar' a bola (chutão).")
                    st.markdown("* **Táticas Agressivas:** Ele passará a bola para a defesa para iniciar a construção das jogadas.")
                    
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Reflexos, Um a Um, Comando da Área, Comunicação, Primeiro Toque (First Touch), Jogo de Mãos (Handling), Chute (Kicking), Arremesso (Throwing), Jogo Aéreo, Antecipação, Decisões, Posicionamento.")
                    
                    st.markdown("---")
                    st.markdown("**Outras Variações (Instruções/PPMs):**")
                    st.markdown("* **PPM:** Usa longos arremessos para iniciar contra-ataques.")
                    st.markdown("* **PI:** Distribuir para o 'Target Man' (Pivô) ou jogador (se o Chute for bom).")
                    st.markdown("* **PI:** Rolar a bola para os zagueiros (para táticas de posse).")

                    st.markdown("---")
                    st.markdown("**Resumo 'Goleiro':**")
                    st.markdown("* Goleiro 'ortodoxo', não precisa ter um ótimo Primeiro Toque.")
                    st.markdown("* Ainda pode jogar com os pés com a instrução de time 'Sair Jogando da Defesa'.")
                    st.markdown("* Permanece na área de pênalti, raramente se aventura para fora.")
                    st.markdown("* **Exemplo Real:** Kaspar Schmeichel.")

                with st.expander("**SK**: Goleiro Líbero (Sweeper Keeper)"):
                    st.write("O Goleiro Líbero (SK) desempenha duas funções: Goleiro e Líbero de campo. Além de suas tarefas habituais, ele 'varre' a bola ao redor da área de pênalti e inicia contra-ataques com passes diretos para os atacantes.")
                    st.write("É uma escolha popular para quem joga com posse de bola e linha defensiva alta. Ele deve agir como um último defensor, confortável em sair da área e controlar a bola com os pés.")
                    
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Mais cauteloso, mas iniciará contra-ataques se a oportunidade for clara.")
                    st.markdown("* **Support (Apoiar):** Fica um pouco fora da área de pênalti e busca passes de contra-ataque mais arriscados.")
                    st.markdown("* **Attack (Atacar):** O mais arriscado. Avança para longe da área e fica confortável em conduzir a bola com os pés.")
                    
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Todos os atributos do GK, mais: **Compostura**, **Concentração**, **Agilidade**. Para as funções 'Apoiar' e 'Atacar', ele também precisa de **Decisões**, **Excentricidade**, **Sair Jogando (Rushing Out)** e **Aceleração**.")
                    
                    st.markdown("---")
                    st.markdown("**Outras Variações (Instruções/PPMs):**")
                    st.markdown("* **PPM:** Usa longos arremessos para iniciar contra-ataques.")
                    st.markdown("* **PI:** Distribuir para o 'Target Man' (Pivô) ou jogador (se o Chute for bom).")
                    st.markdown("* **PI:** Rolar a bola para os zagueiros (para táticas de posse).")
                    
                    st.markdown("---")
                    st.markdown("**Resumo 'Goleiro Líbero':**")
                    st.markdown("* Tecnicamente proficiente; bom Primeiro Toque, Drible e Chute são necessários além dos atributos típicos de goleiro.")
                    st.markdown("* Ideal para futebol de posse e para contra-atacar a pressão alta do adversário.")
                    st.markdown("* Usado bem quando há jogadores próximos para oferecer opções de passe (ex: Zagueiro Construtor, Armador Recuado).")
                    st.markdown("* Pode sair da área para lançar ataques de trás.")
                    st.markdown("* **Exemplo Real:** Alisson.")
            
            # Container para Zagueiros
            with st.container(border=True):
                st.markdown("#### Zagueiros (DC)")

                with st.expander("**DCD**: Defesa Central Descaido"):
                    st.write("O dever principal é parar o ataque adversário e afastar o perigo. Diferente dos zagueiros centrais padrão, o Zagueiro Aberto é encorajado a ficar aberto e apoiar o meio-campo como um lateral.")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Mais tradicional, dá apoio às áreas laterais, mas de trás.")
                    st.markdown("* **Apoiar:** Disposto a fazer ultrapassagens (overlap/underlap) para criar situações de 2 contra 1, jogando mais como um lateral.")
                    st.markdown("* **Atacar:** Faz ultrapassagens regulares e tem maior tendência a driblar com a bola.")

                with st.expander("**DC**: Defesa Central"):
                    st.write("Seu trabalho principal é parar os jogadores adversários e limpar a bola de uma área perigosa quando necessário. Em táticas mais agressivas, ele também deve ter técnica e compostura para manter a posse e fazer passes simples para os companheiros.")
                    
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Permanece em linha com seu parceiro de defesa, busca quebrar ataques, marcar os atacantes e impedir que a bola entre na área.")
                    st.markdown("* **Bloqueador:** Avança à frente da linha defensiva para fechar os espaços e pressionar os jogadores antes que cheguem à área.")
                    st.markdown("* **Cobrir:** Recua um pouco mais, como um 'líbero', para varrer bolas longas e cobrir espaços nas costas da linha defensiva.")
                    
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Cabeceamento, Marcação, Desarme, Antecipação, Coragem, Concentração, Decisões, Determinação, Posicionamento, Alcance no Ar, Força e Agressividade.")
                    st.markdown("* **Para a função 'Cobrir':** Aceleração é um atributo chave.")
                    
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Chutar Menos (Shoot Less Often), Driblar Menos (Dribble Less), Menos Passes Arriscados (Fewer Risky Passes).")

                    st.markdown("---")
                    st.markdown("**Resumo 'Zagueiro':**")
                    st.markdown("* Defensores 'genéricos' que são uma boa opção para qualquer time.")
                    st.markdown("* Pode jogar a bola saindo da defesa ou pelo ar.")
                    st.markdown("* Instruções de time e mentalidade podem influenciar seu jogo (ex: passes longos se não houver opção curta).")
                    st.markdown("* **Movimentação:** Geralmente não sai da linha defensiva.")

                with st.expander("**LA**: Líbero Avançado"):
                    st.write("O Líbero joga atrás da linha defensiva, com o objetivo de varrer bolas longas, marcar atacantes extras e fazer desarmes, bloqueios e interceptações cruciais.")
                    st.write("Seu atleticismo e leitura de jogo excepcionais permitem cobrir erros defensivos e tomar posse de bolas perdidas. No entanto, ele também avançará para apoiar o meio-campo quando o time tiver a posse.")

                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Support (Apoiar):** O Líbero avança para o meio-campo quando a posse é recuperada e procura lançar bolas para os companheiros de ataque.")
                    st.markdown("* **Attack (Atacar):** O Líbero se aventura muito mais alto no campo para ser uma ameaça de gol de longa distância e armar para os outros.")
                    
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Apoiar:** Cabeceamento, Marcação, Passe, Desarme, Antecipação, Compostura, Concentração, Decisões, Posicionamento, Trabalho em Equipe, Aceleração, Equilíbrio, Alcance no Ar.")
                    st.markdown("* **Atacar:** Todos os de 'Apoiar', mais: **Velocidade (Pace)** e **Fôlego (Stamina)**.")

                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.markdown("* **Apoiar:** Passes Mais Arriscados.")
                    st.markdown("* **Atacar:** Chutar Mais, Passes Mais Arriscados, Avançar Mais e Driblar Mais.")

                    st.markdown("---")
                    st.markdown("**Resumo 'Líbero':**")
                    st.markdown("* Zagueiro central criativo; Passe, Decisões, Visão e Drible são recomendados além dos atributos de defesa.")
                    st.markdown("* Jogador tecnicamente proficiente.")
                    st.markdown("* Pode sair da sua linha defensiva quando leva a bola.")
                    st.markdown("* Para extrair o melhor dele, é melhor não ter armadores à sua frente.")

                with st.expander("**DBL**: Defesa com Bola"):
                    st.write("Seu trabalho principal é parar os adversários, mas ele é encorajado a iniciar passes que quebram a defesa vindo de trás para gerar contra-ataques. Ele tem uma instrução ativa para 'Passes Mais Arriscados' e deve ser confortável com a bola.")
                    st.write("Por padrão, ele tentará trazer a bola para fora da defesa, podendo avançar até o terço final do campo dependendo da transição.")
                    
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Permanece em linha com seu parceiro de defesa.")
                    st.markdown("* **Bloqueador:** Avança à frente da linha defensiva para pressionar.")
                    st.markdown("* **Cobrir:** Recua um pouco mais para varrer bolas longas.")
                    
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Todos os atributos do 'Defesa Central (DC)', mais: **Primeiro Toque**, **Técnica**, **Visão**, **Passe** e **Compostura**.")
                    st.markdown("* **Para a função 'Cobrir':** Aceleração.")

                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Passes Mais Arriscados e/ou Manter Posição.")

                    st.markdown("---")
                    st.markdown("**Resumo 'Zagueiro Construtor':**")
                    st.markdown("* Jogador tecnicamente proficiente; bom primeiro toque, drible, passe, visão são essenciais.")
                    st.markdown("* Pode lançar ataques diagonais profundos (ex: para um Extremo Invertido (EI) com espaço).")
                    st.markdown("* Função arriscada se usada com jogadores com pouca compostura, primeiro toque ou drible.")
                    st.markdown("* Quando pareado com um Goleiro Líbero (SK), pode quebrar a pressão alta adversária.")
                    st.markdown("* **Movimentação:** Função dinâmica que pode sair da linha defensiva para iniciar ataques.")
                    st.markdown("* **Exemplos Reais:** Virgil Van Dijk, Matthijs De Ligt.")

                with st.expander("**DCE**: Defesa Central Eficiente"):
                    st.write("Seu trabalho principal é parar os jogadores adversários e limpar a bola da área perigosa. Ele tenta ganhar a bola sem fazer faltas e sua prioridade é 'limpar' a bola para uma zona segura (ex: chutão).")
                    
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Permanece em linha com seu parceiro de defesa.")
                    st.markdown("* **Bloqueador:** Avança à frente da linha defensiva para pressionar.")
                    st.markdown("* **Cobrir:** Recua um pouco mais para varrer bolas longas.")
                    
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Cabeceamento, Marcação, Desarme, Determinação, Posicionamento, Alcance no Ar e Força.")
                    
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Chutar Menos, Driblar Menos, Passes Mais Diretos, Menos Passes Arriscados e/ou Manter Posição (apenas em 'Defender').")
                    
                    st.markdown("---")
                    st.markdown("**Resumo 'Zagueiro Tradicional':**")
                    st.markdown("* Função ideal para jogadores que não são bons em Passe, Primeiro Toque ou Drible.")
                    st.markdown("* Uma função que joga bolas diretas para o espaço ou para um jogador alvo.")
                    st.markdown("* Ideal para times que querem jogar futebol defensivo, onde limpar a bola é a prioridade.")

            # Container para Laterais 
            with st.container(border=True):
                st.markdown("#### Laterais (DD/DE)")

                with st.expander("**AL**: Ala"):
                    st.write("Uma função versátil, considerada a mais defensiva entre os laterais, mas que ainda avança para dar largura. Complementa seus deveres defensivos com corridas de ultrapassagem para apoiar o meio-campo e o ataque. Funciona muito bem em conjunto com meio-campistas abertos (ex: num 4-4-2).")
                    
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Permanece recuado e faz passes simples para manter a posse, seja pela lateral ou para o meio-campo central. (Instruções: Menos Passes Arriscados, Cruzar da Intermediária e Manter Posição).")
                    st.markdown("* **Apoiar:** Apoia o meio-campo dando largura extra. Procura por cruzamentos e passes em profundidade quando a chance surge.")
                    st.markdown("* **Atacar:** Ultrapassa o meio-campo e busca cruzamentos de primeira para a área. (Instruções: Cruzar Mais e Avançar Mais).")
                    
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Defender:** Marcação, Desarme, Posicionamento, Trabalho em Equipe.")
                    st.markdown("* **Apoiar:** Marcação, Desarme, Antecipação, Concentração, Posicionamento, Trabalho em Equipe, Índice de Trabalho, Fôlego.")
                    st.markdown("* **Atacar:** Cruzamento, Desarme, Antecipação, Posicionamento, Trabalho em Equipe, Índice de Trabalho, Aceleração, Fôlego.")
                    
                    st.markdown("---")
                    st.markdown("**Resumo 'Ala':**")
                    st.markdown("* A função mais versátil do jogo, pode ser moldada com Instruções de Jogador (PIs) e Movimentos Preferidos (PPMs).")
                    st.markdown("* Pode ser usado para manter a posse (ex: 'passes curtos') ou como um 'pivô' de ataque (ex: PPM 'Muda o jogo para o outro flanco') se tiver boa Visão e Passe.")

                with st.expander("**DLE**: Lateral Descomplicado"):
                    st.write("Um jogador que se concentra em seus deveres defensivos e raramente avança. Sua prioridade é afastar o perigo.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Defender'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Defender:** Marcação, Desarme e Força.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Chutar Menos, Driblar Menos, Passes Mais Diretos, Menos Passes Arriscados, Cruzar Menos e Manter Posição.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Lateral Descomplicado':**")
                    st.markdown("* Função ideal para jogadores que não são bons em Passe, Primeiro Toque ou Drible.")
                    st.markdown("* Joga bolas diretas para o espaço ou para um jogador alvo.")
                    st.markdown("* Ideal para táticas defensivas onde limpar a bola é a prioridade.")

                with st.expander("**DL**: Defesa Lateral"):
                    st.write("Uma variação moderna do Lateral, com ênfase muito maior no ataque. São uma combinação de ponta e lateral, sendo uma das posições mais exigentes fisicamente. Devem dar largura ao ataque, mas ter a capacidade de recuar e marcar.")
                    st.write("São ideais para sistemas que não oferecem outra opção de largura, como um 4-4-2 losango ou um 5-3-2.")
                    
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Joga com menos passes arriscados, corre com a bola, cruza da intermediária e mantém a posição.")
                    st.markdown("* **Apoiar:** Corre com a bola e avança mais no campo.")
                    st.markdown("* **Atacar:** Corre aberto com a bola, cruza mais, cruza da linha de fundo e avança mais.")
                    
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Aceleração, Velocidade, Fôlego, Cruzamento, Decisões, Trabalho em Equipe, Índice de Trabalho e Sem Bola.")
                    
                    st.markdown("---")
                    st.markdown("**Resumo 'Defesa Ala Invertido':**")
                    st.markdown("* Mais agressivo que o Ala (AL).")
                    st.markdown("* Bom para times com um jogo de posse agressivo no terço final.")
                    st.markdown("* Mesmo na função 'Defender', eles se posicionam mais alto no campo do que um Ala (AL) em 'Apoiar'.")
                    st.markdown("* Se seus cruzamentos estiverem sendo bloqueados, considere diminuir a função de 'Atacar' para 'Apoiar' para que cruzem de posições ligeiramente mais recuadas.")

                with st.expander("**ALC**: Ala Completo"):
                    st.write("O Ala Completo ama atacar. Embora capaz de cumprir deveres defensivos, sua inclinação natural é impactar o jogo no terço final adversário. Pense em Jordi Alba.")
                    
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Busca combinar seus instintos ofensivos com alguma responsabilidade defensiva para dar equilíbrio.")
                    st.markdown("* **Atacar:** Muito aventureiro. Busca impactar o jogo principalmente no campo adversário. Pode ser pego fora de posição e ser um risco em transições defensivas rápidas.")

                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Cruzamento, Drible, Primeiro Toque, Passe, Desarme, Decisões, Sem Bola, Posicionamento, Trabalho em Equipe, Índice de Trabalho, Aceleração, Velocidade e Fôlego.")
                    
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas (em ambas as funções):**")
                    st.write("Driblar Mais, Correr Aberto, Avançar Mais, Ficar Aberto e Sair da Posição.")

                    st.markdown("---")
                    st.markdown("**Resumo 'Ala Completo':**")
                    st.markdown("* Por ter que sair da Posição, seu jogo é imprevisível.")
                    st.markdown("* Pode cortar para dentro ou ir pela linha lateral. Precisa de boas decisões para fazer a escolha certa.")
                    st.markdown("* Exige um jogador de alto nível, com bons atributos técnicos, mentais e físicos.")

                with st.expander("**DAI**: Defesa Ala Invertido"):
                    st.write("Defensivamente, funciona como um lateral padrão. No entanto, com a posse de bola, em vez de dar largura, o IWB tenta 'flutuar' para dentro (drift inside) e criar espaço para os jogadores ao seu redor, congestionando o meio-campo.")
                    
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Mantém a posição (como um volante central).")
                    st.markdown("* **Apoiar / Atacar:** Pode acabar atacando a entrada da área centralmente, às vezes avançando mais do que um Meia Central (MC) em 'Apoiar'.")
                    
                    st.markdown("---")
                    st.markdown("**Atributs Chave:**")
                    st.write("Marcação, Passe, Desarme, Antecipação, Decisões, Determinação, Posicionamento, Índice de Trabalho, Aceleração, Fôlego.")
                    
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Driblar Mais, Cortar para Dentro com a Bola, Passes Mais Arriscados, Cruzar Menos, Ficar mais Centralizado e Sair da Posição.")
                    
                    st.markdown("---")
                    st.markdown("**Resumo 'Lateral Invertido':**")
                    st.markdown("* Um cruzamento entre um volante (MD) e um Ala (AL).")
                    st.markdown("* Posiciona-se no nível dos volantes quando o time tem a bola.")
                    st.markdown("* **Exemplo Real:** Phillip Lahm (no Bayern de Pep Guardiola).")
                    
                    st.warning("**Importante:** Esta função precisa de requisitos táticos específicos para funcionar. Se o espaço central já estiver ocupado (ex: dois Volantes), ou se não houver alas (MD/ME) para dar largura, o DAI pode reverter para um comportamento de 'Ala' (AL) normal.")

        # --- Coluna 2: Meio-Campo ---
        with col_func2:
            
            # Container para Volantes
            with st.container(border=True):
                st.markdown("#### Volantes (VOL)")
                
                with st.expander("**MD**: Médio Defensivo"):
                    st.write("Seu trabalho principal é proteger a linha defensiva e apoiar os meias mais criativos quando o time tem a posse. Ele segura o jogo enquanto a defesa e o ataque se reorganizam.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Mantém sua posição entre o meio-campo e a defesa e recicla a posse de uma posição recuada. (Instruções: Chutar Menos, Driblar Menos e Manter Posição).")
                    st.markdown("* **Support (Apoiar):** Avança para a linha do meio-campo e apoia as jogadas de ataque.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Desarme (Tackling), Posicionamento, Trabalho em Equipe, Índice de Trabalho, Concentração e Fôlego.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Volante':**")
                    st.markdown("* Um pouco mais criativo que o Trinco (TRI), pode tentar passes mais longos.")
                    st.markdown("* Pode pressionar mais longe do que o Trinco.")
                    st.markdown("* Função 'genérica' que pode ser uma boa opção para jogadores criativos, pois não é tão travada em instruções.")

                with st.expander("**RGA**: Médio Criativo"):
                    st.write("O 'Armador Recuado' opera no espaço entre a defesa e o meio-campo e visa iniciar jogadas de ataque através de passes precisos para jogadores mais avançados. Embora sua principal função seja criativa, ele também tem capacidade defensiva.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Cumpre responsabilidades defensivas extras, mantendo a posição na frente da zaga e raramente apoiando o ataque. (Instruções: Chutar Menos, Manter Posição e Driblar Menos).")
                    st.markdown("* **Apoiar:** Traz a bola para fora da defesa e procura iniciar passes em profundidade. (Instruções: Chutar Menos, Passes Mais Arriscados e Manter Posição).")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Primeiro Toque (First Touch), Passe, Técnica, Compostura, Decisões e Visão.")
                    st.markdown("---")
                    st.markdown("**Resumo Médio Criativo:**")
                    st.markdown("* Tenta passes arriscados ocasionalmente.")
                    st.markdown("* Boa opção para times que querem ditar o jogo de posições recuadas.")
                    st.markdown("* Seu posicionamento é semelhante ao do Volante (DM).")
                    st.markdown("* Precisa de jogadores ao seu redor que lhe deem tempo e espaço para jogar.")

                with st.expander("**MRB**: Médio Recuperador de Bola"):
                    st.write("A principal função do 'Recuperador' é pressionar a oposição e ganhar a bola. É um jogador agressivo que atua na frente da defesa, um 'disruptor' que quebra o jogo adversário.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Procura ganhar a bola no centro do campo e passá-la rapidamente para jogadores mais criativos. (Instruções: Menos Riscos, Manter Posição, Chutar Menos, Driblar Menos e Desarmar com Mais Força).")
                    st.markdown("* **Apoiar:** Tenta ganhar a bola mais alto no campo e apoiar os contra-ataques resultantes. (Instrução: Desarmar com Mais Força).")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Desarme, Agressividade, Coragem, Determinação, Trabalho em Equipe, Índice de Trabalho, Concentração, Fôlego, Posicionamento e Força.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Recuperador':**")
                    st.markdown("* Um 'disruptor'. Quebra as jogadas e tem uma grande área de influência.")
                    st.markdown("* Deve ser usado com cuidado: se jogar como VOL, ele pode sair para pressionar nas laterais, deixando os zagueiros centrais expostos.")

                with st.expander("**TRI**: Trinco"):
                    st.write("Também chamado de 'Carregador de Piano'. Sua principal função é sentar-se no espaço entre a defesa e o meio-campo, interceptando jogadas, ganhando a bola e distribuindo passes simples para jogadores mais criativos.")
                    st.write("Ele não se aventura para longe de sua posição, nem para pressionar alto nem para apoiar o ataque.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Defender'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Desarme, Antecipação, Compostura, Concentração, Decisões e Posicionamento.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Chutar Menos, Driblar Menos, Menos Passes Arriscados e Manter Posição.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Volante Fixo':**")
                    st.markdown("* O volante (DM) mais disciplinado.")
                    st.markdown("* Posiciona-se na frente dos zagueiros e não se afasta.")
                    st.markdown("* Joga passes simples e não faz nada extraordinário.")
                    st.markdown("* Uma das melhores funções para defesas disciplinadas e para isolar atacantes solitários.")

                with st.expander("**PD**: Pivô Defensivo"):
                    st.write("O Pivô Defensivo atua entre a defesa e o meio-campo. Quando o time ataca, os zagueiros centrais avançam um pouco, e o Pivô Defensivo recua, ficando mais fundo que um volante padrão, oferecendo uma saída para reciclar a posse.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Defender'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Primeiro Toque, Passe, Técnica, Antecipação, Compostura, Decisões, Posicionamento e Trabalho em Equipe.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Driblar Menos, Manter Posição.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Volante de Proteção':**")
                    st.markdown("* Uma mistura de Zagueiro Central com Volante.")
                    st.markdown("* Fica perto dos zagueiros na maioria das fases do jogo.")
                    st.markdown("* É uma opção agressiva, boa para times que querem 'sair jogando de trás', pois sua posição na construção da jogada oferece uma saída para o Goleiro Líbero (SK).")

                with st.expander("**OV**: Organizador Móvel (Regista)"):
                    st.write("O 'Regista' é uma versão mais agressiva do Armador Recuado (CJ), ideal para sistemas de posse de bola que pressionam alto. Com total liberdade para ditar o jogo de posições recuadas, ele oferece uma saída criativa dinâmica e imprevisível.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Apoiar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Primeiro Toque, Passe, Técnica, Compostura, Decisões, Sem Bola e Visão.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Sair da Posição (Roam From Position), Passes Mais Arriscados.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Regista':**")
                    st.markdown("* Mais agressivo que um DLP, mas menos 'corredor' que um Segundo Volante (VOL).")
                    st.markdown("* Jogador criativo que não corre tanto com a bola (como o VOL), mas se torna disponível.")
                    st.markdown("* Atua como um jogador de ligação entre a defesa e o ataque.")
                    st.markdown("* **Exemplo Real:** Andrea Pirlo.")
                    st.warning("Cuidado ao usar: um Zagueiro Tradicional e um tempo de jogo alto podem 'ignorar' o Regista, pois a bola passará por cima dele.")

                with st.expander("**CJ**: Construtor de Jogo Recuado"):
                    st.write("O Construtor de Jogo Recuado (CJ) é o coração do time, avançando com a bola para liderar ataques e também voltando para cobrir defensivamente. Ele está sempre oferecendo uma opção de passe e precisa de atributos físicos para manter uma alta intensidade.")
                    st.write("Ele busca a bola em posições recuadas e a leva para frente urgentemente, muitas vezes acampando na entrada da área adversária procurando um chute ou um passe matador.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Apoiar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Drible, Primeiro Toque, Passe, Técnica, Antecipação, Compostura, Decisões, Determinação, Sem Bola, Visão, Índice de Trabalho, Aceleração e Fôlego.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Sair da Posição, Passes Mais Arriscados.")
                    st.markdown("---")
                    st.markdown("**Resumo Construtor de Jogo Recuado:**")
                    st.markdown("* Precisa de ótimas Decisões, Passe, Visão e Sem Bola.")
                    st.markdown("* Se movimenta muito, então precisa de alto Índice de Trabalho e Fôlego.")
                    st.markdown("* A movimentação é sua força no ataque, mas pode ser uma fraqueza na defesa, pois pode deixar o centro do campo desprotegido.")

                with st.expander("**VOL**: Segundo Volante"):
                    st.write("O 'Segundo Volante' é uma mistura de Construtor de Jogo Recuado (CJ), Recuperador de Bolas (BWM) e Meia Área-a-Área (MAA). Ele ajuda o time a defender, mas adora chegar na área adversária, similar a um MAA. É um jogador explosivo que começa em posições recuadas.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** (Sem instruções bloqueadas).")
                    st.markdown("* **Atacar:** (Instrução: Avançar Mais).")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Fôlego, Índice de Trabalho, Determinação, Coragem, Antecipação, Posicionamento, Visão, Decisões, Sem Bola, Desarme, Primeiro Toque, Passe e Compostura.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Segundo Volante':**")
                    st.markdown("* Uma função muito exigente: cobre, defende, cria e pode chegar atrasado na área para finalizar.")
                    st.markdown("* Suas corridas são difíceis de marcar para o adversário.")
                    st.markdown("* Funciona bem ao lado de um Volante Fixo (A) ou Regista (REG).")
                    st.markdown("* Pode operar nos espaços para atrair marcadores.")

            # Container para Meias Centrais
            with st.container(border=True):
                st.markdown("#### Meias Centrais (MC)")
                
                with st.expander("**MC**: Médio Centro"):
                    st.write("Responsável por ser um elo versátil e 'operário' entre a defesa e o ataque. Espera-se que execute uma variedade de tarefas no centro do campo.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Foca em sentar-se mais recuado, parar contra-ataques e controlar o ritmo. (Instrução: Manter Posição).")
                    st.markdown("* **Apoiar:** Busca equilibrar suas responsabilidades defensivas e ofensivas, mantendo-se no centro e tentando passes para o terço final.")
                    st.markdown("* **Atacar:** Avança mais no campo. (Instrução: Avançar Mais).")
                    st.markdown("---")
                    st.markdown("**Atributos Chave (Depende da Customização):**")
                    st.markdown("* **Defender:** Passe, Desarme, Concentração, Trabalho em Equipe, Posicionamento e Agressividade.")
                    st.markdown("* **Apoiar:** Primeiro Toque, Passe, Decisões e Trabalho em Equipe.")
                    st.markdown("* **Atacar:** Primeiro Toque, Passe, Decisões e Sem Bola.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Meia Central':**")
                    st.markdown("* Função 'genérica' e uma das mais personalizáveis do jogo (ex: pode-se criar um 'Recuperador de Bolas' sem o 'Desarmar com Força').")
                    st.markdown("* Uma função subestimada; sua eficácia depende dos atributos do jogador e das funções ao seu redor.")

                with st.expander("**MAA**: Médio Área-a-Área (Box-to-Box)"):
                    st.write("O dinamismo 'non-stop' do Meia Área-a-Área (MAA) permite que ele contribua muito tanto na defesa quanto no ataque.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Apoiar'.")
                    st.markdown("---")
                    st.markdown("**Como atua:**")
                    st.markdown("* **No Ataque:** Sobe para apoiar os atacantes, muitas vezes infiltrando-se 'tardiamente' na área para finalizar cruzamentos, além de ser uma ameaça de chute de longe.")
                    st.markdown("* **Na Defesa:** Pressiona os adversários e ajuda a proteger a linha defensiva.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Passe, Desarme, Decisões, Determinação, Sem Bola, Posicionamento, Índice de Trabalho, Aceleração, Forma Física Natural (Natural Fitness) e Fôlego.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Sair da Posição.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Meia Área-a-Área':**")
                    st.markdown("* Posição muito exigente, requer diligência defensiva e ofensiva.")
                    st.markdown("* Aparece na defesa para ajudar e chega tarde no ataque, mas não é o primeiro a entrar na área.")
                    st.markdown("* **Exemplo Real:** Paul Pogba (na Juventus).")

                with st.expander("**CJA**: Construtor De Jogo Avançado"):
                    st.write("O Construtor De Jogo Avançado opera nos 'buracos' entre o meio-campo e a defesa adversária. Seu objetivo é receber passes e transformar a defesa em ataque instantaneamente.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Fica nos espaços e procura distribuir passes para os companheiros. (Instruções: Chutar Menos e Passes Mais Arriscados).")
                    st.markdown("* **Atacar:** (Instruções: Chutar Menos, Passes Mais Arriscados e Driblar Mais).")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Apoiar:** Primeiro Toque, Passe, Técnica, Compostura, Decisões e Visão.")
                    st.markdown("* **Atacar:** Drible, Primeiro Toque, Equilíbrio, Passe, Técnica, Compostura, Decisões, Sem Bola e Visão.")
                    st.markdown("---")
                    st.markdown("**Resumo Construtor de Jogo Avançado:**")
                    st.markdown("* Função criativa que dita o jogo mais alto no campo.")
                    st.markdown("* Se usado em uma dupla de meio-campo, precisa ser um jogador excepcional (bom Índice de Trabalho, Posicionamento e Desarme) para não perder a posse.")
                    st.markdown("* **Exemplo Real:** Philippe Coutinho (no Liverpool de Klopp).")

                with st.expander("**MEZ**: Mezzala"):
                    st.write("A interpretação moderna do 'Mezzala', que atua como um 'meia-ala'. Ele trabalha os 'meios-espaços' no terço final, criando sobrecargas e sendo uma fonte de criatividade.")
                    st.write("Defesa não é seu foco principal.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Tenta equilibrar ataque e defesa, mas foca no ataque.")
                    st.markdown("* **Atacar:** Deixa as responsabilidades do meio-campo para os companheiros e foca em criar com a bola.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas (em ambas):**")
                    st.write("Avançar Mais, Mover para os Canais, Sair da Posição, Ficar Aberto. (A função Atacar também tem 'Passes Mais Arriscados').")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Sem Bola, Decisões, Imprevisibilidade, Drible, Passe, Visão, Trabalho em Equipe e Antecipação. (Basicamente, precisa de criatividade, controle de bola e atributos mentais).")
                    st.markdown("---")
                    st.markdown("**Resumo 'Mezzala':**")
                    st.markdown("* Meio-ala, meio-ponta-invertido. Dita o jogo dos meios-espaços.")
                    st.markdown("* Muito difícil de marcar por ser imprevisível.")
                    st.markdown("* Idealmente usado em um trio de meio-campo.")
                    st.markdown("* **Risco:** Sua movimentação pode deixar o centro do campo aberto.")
                    st.markdown("* **Exemplo Real:** Andrés Iniesta.")

                with st.expander("**CAR**: Carrilero"):
                    st.write("Uma função de apoio, frequentemente referida como (transportador). É mais usado em formações estreitas (ex: losango) ou sem alas, onde a largura vem dos laterais.")
                    st.write("Ele transporta a bola entre a defesa e o meio-campo, protegendo a zona e garantindo que os flancos sejam cobertos.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Apoiar'.")
                    st.markdown("---")
                    st.markdown("**Diferença do MAA:**")
                    st.write("O Carrilero foca em cobrir as *linhas* (entre defesa e ataque) e os lados, enquanto o MAA foca em ir de *área a área*.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Desarme, Posicionamento, Decisões, Marcação, Aceleração e Força. (Coragem e Determinação também são úteis).")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Ficar Aberto.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Carrilero':**")
                    st.markdown("* Opera pela lateral do campo, mas não se aventura em nenhuma das áreas.")
                    st.markdown("* Joga simples, mantém a bola em movimento e protege os flancos.")
                    st.markdown("* Bom para proteger os 'meios-espaços' deixados por um Extremo Invertido (EI), por exemplo.")

        # --- Coluna 3: Ataque ---
        with col_func3:

            # Container 1: Funções de Ponta (MA D/E)
            with st.container(border=True):
                st.markdown("#### Funções de Ponta (MA D/E)")

                with st.expander("**EX**: Extremo (Ponta)"):
                    st.write("O extremo (Ponta) clássico. Seu objetivo é vencer o adversário pelo lado de fora do campo (na linha lateral) e precisa ser tecnicamente proficiente e rápido.")
                    st.write("Ele 'abraça' a linha lateral quando o time avança, pronto para atacar o espaço e cruzar da linha de fundo.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Tenta passar rapidamente pelo seu marcador e fazer cruzamentos cedo para os atacantes.")
                    st.markdown("* **Atacar:** Corre em direção à defesa no terço final, causando pânico antes de chutar ou tentar um cruzamento/passe decisivo.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Apoiar:** Passe, Trabalho em Equipe e Índice de Trabalho.")
                    st.markdown("* **Atacar:** Cruzamento, Passe, Primeiro Toque, Trabalho em Equipe e Índice de Trabalho.")

                with st.expander("**EI**: Extremo Invertido (Ponta Invertido)"):
                    st.write("Esta função busca 'cortar para dentro' no terço final, criando espaço para a ultrapassagem dos laterais e pressionando os zagueiros.")
                    st.write("Funciona melhor quando o jogador usa o pé oposto ao flanco em que joga (ex: destro na esquerda), permitindo que ele corte para dentro naturalmente.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Fará corridas mais diagonais, cortando pela defesa para tentar passes pelo meio.")
                    st.markdown("* **Atacar:** Vai 'dirigir' para cima da defesa, passar ou tentar a finalização.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Apoiar:** Aceleração, Drible, Cruzamento, Primeiro Toque, Compostura, Decisões, Passe, Visão, Técnica, Agilidade e Sem Bola.")
                    st.markdown("* **Atacar:** Todos os de 'Apoiar', mais: **Finalização**.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Ponta Invertido':**")
                    st.markdown("* Uma função excitante que corre de posições mais recuadas.")
                    st.markdown("* Requer bom Índice de Trabalho, Fôlego, Drible e Finalização.")
                    st.markdown("* Em um 4-1-4-1, um EI(Ataque) pode agir como um segundo atacante chegando na área.")
                
                with st.expander("**AI**: Avançado Interior"):
                    st.write("O Avançado Interior (Focado no gol) tenta cortar das pontas e correr *diretamente* para os zagueiros. Como o EI, funciona melhor com o pé oposto ao flanco.")
                    st.write("Seu movimento pode abrir espaço para laterais ou criar sobrecargas. O 'AI' é mais focado em finalizar do que o 'EI', que é mais criativo.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Corta para dentro e tenta passes para outros ou arrisca chutes de longe. (Instruções: Driblar Mais, Cortar para Dentro, Passes Mais Arriscados e Cruzar Menos).")
                    st.markdown("* **AAtacar:** Corre para cima da defesa e pode chutar, passar ou cruzar. (Instruções: 'Apoiar' + Avançar Mais).")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Apoiar:** Drible, Passe, Técnica, Decisões, Sem Bola, Aceleração, Equilíbrio, Agilidade.")
                    st.markdown("* **Atacar:** Todos os de 'Apoiar', mais: **Compostura** e **Finalização**.")
                    st.markdown("---")
                    st.markdown("**Resumo Avançado Interior:**")
                    st.markdown("* Muito perigoso; usa a bola vindo de posições abertas e move-se para dentro.")
                    st.markdown("* Precisa de Equilíbrio, Agilidade, Drible e 'Sem Bola'.")
                    st.markdown("* Na função 'Atacar', é ótimo para atacar espaços criados por sobrecargas táticas.")

                with st.expander("**CJA**: Construtor de Jogo Avançado"):
                    st.write("O Construtor de Jogo Avançado atua como a fonte primária de criatividade do time, 'flutuando' para dentro para encontrar espaço e criar passes letais.")
                    st.write("Defensivamente, ele ocupa a posição na ponta para cobrir o lateral, mas não se espera que desarme muito.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Flutua para uma posição de Meia Central (MC) quando o time tem a bola, atuando como o criador principal.")
                    st.markdown("* **Atacar:** Flutua para uma posição de Meia Atacante (MAC), entre a defesa e o meio-campo adversário. Pode ser pego fora de posição na defesa.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas (em ambas):**")
                    st.write("Chutar Menos, Cortar para Dentro, Cruzar Menos, Ficar mais Centralizado, Sair da Posição e Passes Mais Arriscados. (Atacar também tem 'Driblar Mais').")

                with st.expander("**PLA**: Ponta de Lança Aberto"):
                    st.write("Um termo alemão para 'Aquele que procura espaços'. Sua principal função é encontrar espaço para operar. Ele assume posições abertas, esperando o momento certo para 'explodir' através da linha defensiva.")
                    st.write("É difícil para os defensores marcarem, pois ele 'flutua' para fora de sua posição. Pode negligenciar deveres defensivos.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Atacar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Antecipação, Compostura, Decisões, Concentração, Determinação, Sem Bola, Índice de Trabalho, Equilíbrio, Fôlego.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Passar Mais Curto, Cruzar Menos, Avançar Mais, Ficar Mais Centralizado, Mover para os Canais e Sair da Posição.")
                    st.markdown("---")
                    st.markdown("**Resumo Ponta de Lança Aberto:**")
                    st.markdown("* **Exemplo Real:** Thomas Müller.")
                    st.markdown("* 'Decisões', 'Antecipação' e 'Sem Bola' são cruciais.")
                    st.markdown("* Para usá-lo bem, você precisa *criar* o espaço para ele (ex: focar o jogo no lado oposto do campo para atrair a marcação).")

                with st.expander("**ARA**: Avançado de Referência Aberto (Pivo de Ponta)"):
                    st.write("O 'Pivô de Ponta' é a principal saída para 'chutões' e bolas longas da defesa. Idealmente posicionado contra um lateral mais baixo e fraco, ele deve segurar a bola e reciclá-la para um companheiro.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Usado para intimidar um lateral fraco, oferecendo passes para companheiros que chegam.")
                    st.markdown("* **Atacar:** Torna-se o ponto focal do ataque, recebendo a bola aberto antes de colocar os outros no jogo.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.markdown("* **Apoiar:** Segurar a Bola, Driblar Menos e Manter Posição.")
                    st.markdown("* **Atacar:** Segurar a Bola, Driblar Menos e Avançar Mais.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Força, Sem Bola, Passe, Equilíbrio, Primeiro Toque, Índice de Trabalho e Trabalho em Equipe.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Pivô de Ponta':**")
                    st.markdown("* Função fantástica para criar espaço.")
                    st.markdown("* Segura a bola, ganha no físico e pode jogar para quem ataca o espaço (ex: um lateral ofensivo, um Mezzala).")
                    st.markdown("* Eficaz na criação de sobrecargas na lateral.")

            # Container 2: Meia Avançado (MA C) 
            with st.container(border=True):
                st.markdown("#### Meia Avançado (MA C)")

                with st.expander("**MO**: Médio Ofensivo"):
                    st.write("O 'Meia Atacante' (MO) opera mais alto no campo, no 'buraco', e sua função é criar chances para si e para os outros no terço final.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Apoiar:** Fica no 'buraco', ajudando a defesa, mas sem se infiltrar muito na área.")
                    st.markdown("* **Atacar:** Procura criar chances para os atacantes e também ser uma ameaça entrando na área. (Instrução: Avançar Mais).")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Apoiar:** Primeiro Toque, Passe, Técnica, Antecipação e Decisões.")
                    st.markdown("* **Atacar:** Todos os de 'Apoiar', mais: **Sem Bola**.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Médio Ofensivo':**")
                    st.markdown("* Função genérica para a posição MA C.")
                    st.markdown("* 'Sem Bola' e 'Decisões' são cruciais.")
                    st.markdown("* Sua posição central permite mudar o lado do jogo e chegar de surpresa na área.")

                with st.expander("**PO**: Pivô Ofensivo"):
                    st.write("O 'Pivô Ofensivo'é o criador principal, um pivô que conecta o meio-campo e o ataque. Ele se atém à sua posição (é estacionário) e o time se move ao seu redor.")
                    st.write("Pense em Juan Roman Riquelme. Ele não se movimenta; ele age como o ponto focal.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Apoiar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Primeiro Toque, Passe, Técnica, Compostura, Decisões, Sem Bola e Visão.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Driblar Menos, Passes Mais Arriscados, Pressão Bloqueada (baixa) e Manter Posição.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Enganche':**")
                    st.markdown("* Um 'armador' estacionário. Precisa de jogadores que correm ao seu redor.")
                    st.markdown("* Não pressiona nem fecha espaços na defesa.")
                    st.markdown("* Uma função de nicho, menos comum no futebol moderno.")

                with st.expander("**N10**: Número 10"):
                    st.write("O Número 10 opera nos 'buracos' entre o meio-campo e a defesa. Similar a um Construtor de Jogo Avançado (CJA), mas se esforça *muito menos* defensivamente. Ele 'flutua' procurando espaço quando o time não tem a posse.")
                    st.write("O time precisa 'carregá-lo' na defesa, mas usá-lo como principal válvula de escape no ataque.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Atacar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Primeiro Toque, Passe, Técnica, Antecipação, Compostura, Decisões, Sem Bola e Visão.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Driblar Mais, Passes Mais Arriscados, Mover para os Canais, Sair da Posição, Pegar Leve.")
                    st.markdown("---")
                    st.markdown("**Resumo Número 10:**")
                    st.markdown("* Uma saída criativa que se movimenta muito (diferente do Enganche).")
                    st.markdown("* Não pressiona e não contribui defensivamente.")
                    st.markdown("* Pode se comportar como um Ponta, um Armador ou um Atacante, tudo em um só.")

                with st.expander("**AS**: Avançado Sombra"):
                    st.write("O Avançado Sombra (AS) é a principal ameaça de gol do time vindo de trás. Geralmente pareado com um atacante que recua (como um Pivô), o AS ataca agressivamente os espaços e as posições de finalização.")
                    st.write("Ele também pressiona os defensores adversários quando está sem a bola.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Atacar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Finalização, Antecipação, Compostura, Decisões, Determinação, Sem Bola, Índice de Trabalho, Fôlego.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Driblar Mais, Passes Mais Arriscados, Avançar Mais, Mover para os Canais.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Segundo Atacante':**")
                    st.markdown("* Um atacante que 'chega' (arrives) da posição de MA C.")
                    st.markdown("* Precisa de um parceiro de ataque que crie espaço para ele (ex: AVR, AR, AC).")
                    st.markdown("* 'Sem Bola' é vital. Ele precisa ser bom na construção e na finalização.")
                    st.markdown("* Pode sofrer contra times com dois volantes (DM) que congestionam seu espaço.")
            
            # Container 3: Funções de Atacante (PL)
            with st.container(border=True):
                st.markdown("#### Funções de Atacante (PL)")
                
                with st.expander("**PLF**: Ponta de Lança Fixo (Matador)"):
                    st.write("O 'Matador' se posiciona 'no ombro' do último zagueiro, procurando quebrar a linha defensiva e atacar bolas em profundidade.")
                    st.write("Seu foco é tão extremo em marcar gols que ele raramente ajuda na construção das jogadas, preferindo ficar centralizado e encontrar oportunidades dentro e ao redor da área.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Atacar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Finalização (Finishing), Primeiro Toque (First Touch), Antecipação, Compostura, Sem Bola (Off The Ball).")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Menos Passes Arriscados, Avançar Mais (Get Further Forward).")
                    st.markdown("---")
                    st.markdown("**Resumo 'Matador':**")
                    st.markdown("* Um atacante 'sem frescuras' (no nonsense).")
                    st.markdown("* Joga simples; seu trabalho é finalizar.")
                    st.markdown("* Funciona bem com um parceiro criativo (AVR, AR e F9).")

                with st.expander("**PL**: Ponta de Lança"):
                    st.write("A principal função do 'Ponta de Lança' é liderar a linha e ser a 'ponta de lança' dos movimentos de ataque. Ele é o ponto focal.")
                    st.write("Ele é o atacante mais avançado de todos, jogando na linha do último zagueiro. Sua função secundária é perseguir bolas longas ou 'chutões' da zaga.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Atacar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Finalização, Antecipação, Compostura, Aceleração, Sem Bola.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Driblar Mais, Avançar Mais, Mover para os Canais.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Atacante Avançado':**")
                    st.markdown("* O mais agressivo dos atacantes.")
                    st.markdown("* Joga melhor contra times que deixam espaço nas costas (linha alta).")
                    st.markdown("* Pode sofrer contra defesas recuadas e congestionadas.")

                with st.expander("**F9**: Falso 9"):
                    st.write("Similar a um Meia Atacante, o 'Falso 9' é um atacante não convencional que 'recua' para o meio-campo, criando problemas para os zagueiros (que não sabem se o seguem ou se mantêm a linha).")
                    st.write("**Exemplos Reais:** Lionel Messi (no Barcelona de Guardiola), Cesc Fàbregas (pela Espanha).")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Apoiar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Primeiro Toque, Passe, Técnica, Compostura, Sem Bola, Visão, Trabalho em Equipe. (Força e Decisões também são vitais).")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Driblar Mais, Passes Mais Arriscados.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Falso 9':**")
                    st.markdown("* A mais criativa das funções de atacante.")
                    st.markdown("* Traz outros jogadores para o jogo, liga o meio-campo ao ataque.")
                    st.markdown("* Precisa de Força (para não ser desarmado) e Decisões (para saber quando recuar ou atacar).")

                with st.expander("**N10**: Número 10"):
                    st.write("O avançado recua para buscar o jogo e também chega de surpresa na área. Ele 'vaga' da posição, tornando-se difícil de marcar.")
                    st.write("Ele se exime de tarefas defensivas.")
                    st.markdown("---")
                    st.markdown("**Função:** Apenas 'Atacar'.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Primeiro Toque, Passe, Técnica, Antecipação, Compostura, Decisões, Sem Bola, Visão.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Driblar Mais, Passes Mais Arriscados, Mover para os Canais, Sair da Posição, Pegar Leve.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Número 10':**")
                    st.markdown("* Seu movimento o torna difícil de marcar.")
                    st.markdown("* Pode formar uma boa dupla com um Ponta de Lança fixo em um sistema de contra-ataque.")

                with st.expander("**AC**: Avançado Completo"):
                    st.write("O 'Avançado Completo' possui as habilidades técnicas de um Pivô (AR), a capacidade de finalização de um PLF e a força de um Pivô (AR).")
                    st.write("Ele é um jogador que 'transcende' as instruções táticas e deve ser deixado para fazer o seu próprio jogo. Um 'faz-tudo'.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Support (Apoiar):** Recua para o espaço, corre para cima da zaga, chuta de longe, cai pelas pontas ou dá passes em profundidade.")
                    st.markdown("* **Attack (Atacar):** Faz tudo o que o 'Apoiar' faz, mas também foca em finalizar.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Quase todos: Drible, Primeiro Toque, Cabeceamento, Chutes de Longe, Passe, Técnica, Finalização, Antecipação, Compostura, Decisões, Sem Bola, Visão, Aceleração, Força...")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas (em ambas):**")
                    st.write("Segurar a Bola, Driblar Mais, Passes Mais Arriscados, Sair da Posição.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Avançado Completo':**")
                    st.markdown("* O atacante 'faz-tudo', exige um jogador de nível mundial.")

                with st.expander("**AT**: Avançado Trabalhador (Atacante Pressionador)"):
                    st.write("A função principal do 'Avançado Trabalhador' é pressionar a linha defensiva, perseguir o homem com a bola, bolas perdidas e, geralmente, não dar tempo para o adversário pensar.")
                    st.write("Ofensivamente, ele mantém o jogo simples. **Exemplo Real:** Jamie Vardy.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Defender:** Fica um pouco mais recuado e pressiona os Volantes (DMs) adversários.")
                    st.markdown("* **Support (Apoiar):** Pressiona a linha de zagueiros centrais.")
                    st.markdown("* **Attack (Atacar):** Pressiona a defesa e, com a bola, joga de forma parecida com um Atacante Avançado (AF).")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Agressividade, Coragem (Bravery), Determinação, Trabalho em Equipe, Índice de Trabalho, Aceleração, Fôlego (Stamina).")
                    st.markdown("---")
                    st.markdown("**Insta (Attack):** 'Avançar Mais', 'Mover para Canais', 'Pressionar Mais', 'Desarmar com Força'.")

                with st.expander("**AVR**: Avançado de Referência Recuado (Pivô)"):
                    st.write("A função principal do 'Pivô Recuado' (AVR) é fazer o link (a ligação) entre o ataque e o meio-campo.")
                    st.write("Ele recua (drops deep) para o espaço e 'segura' (hold up) a bola antes de distribuí-la para os companheiros.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Support (Apoiar):** Traz os companheiros para o jogo antes de atacar a área vindo de trás.")
                    st.markdown("* **Attack (Atacar):** Tenta criar chances para si mesmo, além de jogar para os outros.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.write("Força, Primeiro Toque, Passe, Técnica, Compostura, Decisões, Sem Bola, Trabalho em Equipe.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas (em ambas):**")
                    st.write("Segurar a Bola (Hold Up Ball), Passes Mais Arriscados, Mover para os Canais.")
                    st.markdown("---")
                    st.markdown("**Resumo 'Pivô Recuado':**")
                    st.markdown("* Se assemelha ao Falso 9, mas é menos complicado e usa mais a Força e o posicionamento do que o Drible.")

                with st.expander("**AR**: Avançado de Referência (Pivô)"):
                    st.write("O 'Avançado de Referência' (Pivô) usa seu físico e presença aérea para perturbar a defesa adversária e abrir espaço para seus parceiros de ataque e meias.")
                    st.write("Ele usa a Força para trazer os companheiros para o jogo, em vez de depender da habilidade técnica.")
                    st.markdown("---")
                    st.markdown("**Funções:**")
                    st.markdown("* **Support (Apoiar):** Procura ganhar 'casquinhas' e fazer passes simples de posse.")
                    st.markdown("* **Attack (Atacar):** Lidera a linha e abre espaço para os companheiros se infiltrarem.")
                    st.markdown("---")
                    st.markdown("**Atributos Chave:**")
                    st.markdown("* **Apoiar:** Alcance no Ar e Força.")
                    st.markdown("* **Atacar:** 'Apoiar' + Finalização e Cabeceamento.")
                    st.markdown("---")
                    st.markdown("**Instruções Bloqueadas:**")
                    st.write("Segurar a Bola e Driblar Menos.")
                    st.markdown("---")
                    st.markdown("**Resumo Avançado de Refêrencia 'Pivô':**")
                    st.markdown("* Ótimo para padrões de ataque simples e diretos.")
                    st.markdown("* Pode ser o alvo de cruzamentos e bolas longas dos zagueiros.")
                    st.markdown("* Combina bem com um Segundo Atacante (SS) ou Matador (PLF).") 
    
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.exception(e)
