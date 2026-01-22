import numpy as np
import pandas as pd
import plotly.graph_objects as go

class VolatilityAgent:
    def __init__(self):
        pass

    def generate_surface(self, current_price):
        """
        가상의 볼륨 스마일(Volatility Smile) 3D 데이터 생성
        """
        # 1. 행사가는 현재가의 80% ~ 120% 범위
        strikes = np.linspace(current_price * 0.8, current_price * 1.2, 20)
        
        # 2. 만기일은 7일 ~ 365일
        days_to_expiry = np.linspace(7, 365, 20)
        
        # 3. 2D 그리드 만들기 (행사가 x 만기일)
        X, Y = np.meshgrid(strikes, days_to_expiry)
        
        # 4. 내재 변동성(IV) 계산 (Volatility Smile 형태 흉내)
        moneyness = (X - current_price) / current_price
        
        # 기본 변동성 30% + 스마일 효과 (거리의 제곱에 비례) + 시간 효과
        Z = 0.3 + (2.5 * moneyness**2) + (0.1 / np.sqrt(Y/365))

        return X, Y, Z

    def plot_surface(self, current_price):
        """
        3D Surface 차트 그리기 (에러 수정 완료)
        """
        if current_price == 0:
            return go.Figure()

        X, Y, Z = self.generate_surface(current_price)

        fig = go.Figure(data=[go.Surface(
            z=Z, x=X, y=Y,
            colorscale='Viridis',
            opacity=0.9,
            contours = {
                "z": {"show": True, "start": 0.3, "end": 0.8, "size": 0.05}
            },
            # [핵심 수정] colorbar 설정 방식 변경 (titlefont -> title dict)
            colorbar=dict(
                tickfont=dict(color="white"),
                title=dict(
                    text="IV",
                    font=dict(color="white")
                )
            )
        )])

        fig.update_layout(
            title=dict(
                text="🧊 Implied Volatility Surface (3D)",
                font=dict(color="white")
            ),
            scene = dict(
                # [수정] 축 제목 설정도 최신 방식으로 통일
                xaxis=dict(
                    title=dict(text='Strike Price ($)', font=dict(color="white")),
                    tickfont=dict(color="white"),
                    gridcolor='#444'
                ),
                yaxis=dict(
                    title=dict(text='Days to Expiry', font=dict(color="white")),
                    tickfont=dict(color="white"),
                    gridcolor='#444'
                ),
                zaxis=dict(
                    title=dict(text='Implied Volatility (IV)', font=dict(color="white")),
                    tickfont=dict(color="white"),
                    gridcolor='#444'
                ),
            ),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, b=0, t=40),
            height=600
        )
        
        return fig
