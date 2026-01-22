import networkx as nx
import plotly.graph_objects as go

class SupplyChainAgent:
    def __init__(self):
        # 1. 지식 베이스 (주요 기업들의 실제 공급망 데이터)
        self.knowledge_base = {
            "NVDA": {
                "Suppliers": ["TSMC", "SK Hynix", "Micron", "Samsung Elec", "Coherent"],
                "Customers": ["Microsoft", "Google", "Amazon", "Meta", "Tesla", "Oracle"],
                "Competitors": ["AMD", "Intel", "Qualcomm", "Cerebras"]
            },
            "AAPL": {
                "Suppliers": ["Foxconn", "TSMC", "Samsung Display", "LG Innotek", "Sony", "Broadcom"],
                "Customers": ["Global Consumers", "Education", "Enterprise"],
                "Competitors": ["Samsung", "Google", "Huawei", "Xiaomi"]
            },
            "TSLA": {
                "Suppliers": ["Panasonic", "CATL", "LG Energy", "Baosteel", "Vale"],
                "Customers": ["Global Drivers", "Hertz", "Uber"],
                "Competitors": ["BYD", "Toyota", "Ford", "Rivian", "Lucid"]
            },
            "MSFT": {
                "Suppliers": ["Nvidia", "AMD", "Intel", "Dell"],
                "Customers": ["Enterprise", "Government", "Gamers (Xbox)"],
                "Competitors": ["Google", "Amazon (AWS)", "Apple", "Sony"]
            },
            "GOOGL": {
                "Suppliers": ["Nvidia", "Broadcom", "Samsung"],
                "Customers": ["Advertisers", "Cloud Users"],
                "Competitors": ["Microsoft", "Meta", "Amazon", "OpenAI"]
            }
        }

    def get_network_graph(self, ticker):
        """
        네트워크 그래프를 그려주는 함수 (에러 수정됨)
        """
        # 데이터 가져오기 (없으면 랜덤 예시 생성)
        data = self.knowledge_base.get(ticker, {
            "Suppliers": ["Supplier A", "Supplier B"],
            "Customers": ["Customer X", "Customer Y"],
            "Competitors": ["Competitor 1"]
        })

        # 그래프 객체 생성
        G = nx.Graph()
        
        # 1. 중심 노드 (검색한 기업)
        G.add_node(ticker, type="Target", color="#FFFFFF", size=40)

        # 2. 주변 노드 추가 (공급사, 고객사, 경쟁사)
        for supplier in data["Suppliers"]:
            G.add_node(supplier, type="Supplier", color="#00CC96", size=20) # 초록색
            G.add_edge(ticker, supplier, relation="Supply")
            
        for customer in data["Customers"]:
            G.add_node(customer, type="Customer", color="#636EFA", size=20) # 파란색
            G.add_edge(ticker, customer, relation="Sales")
            
        for competitor in data["Competitors"]:
            G.add_node(competitor, type="Competitor", color="#EF553B", size=20) # 빨간색
            G.add_edge(ticker, competitor, relation="Competition")

        # 3. 레이아웃 계산 (노드 위치 잡기)
        pos = nx.spring_layout(G, seed=42, k=0.5)

        # 4. Plotly로 시각화 (선 그리기)
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888888'), # 회색 선
            hoverinfo='none',
            mode='lines')

        # 5. Plotly로 시각화 (점 그리기)
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            # 마우스 올렸을 때 뜰 텍스트
            node_text.append(f"<b>{node}</b><br>({G.nodes[node]['type']})")
            node_color.append(G.nodes[node]['color'])
            node_size.append(G.nodes[node]['size'])

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[n for n in G.nodes()], # 노드 이름 표시
            textposition="top center",
            textfont=dict(color='white', size=11), # 글씨 하얗게
            marker=dict(
                showscale=False,
                color=node_color,
                size=node_size,
                line_width=2,
                line_color='#1C1F26'))

        # 6. 최종 차트 생성 (여기서 titlefont 에러 해결!)
        fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                # [수정됨] titlefont -> title=dict(font=...)
                title=dict(
                    text=f'🕸️ {ticker} Value Chain Map',
                    font=dict(size=16, color='white')
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                paper_bgcolor='rgba(0,0,0,0)', # 배경 투명
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        return fig
