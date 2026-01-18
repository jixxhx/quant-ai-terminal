from fpdf import FPDF
import datetime
import os
import tempfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from agents.valuation_agent import ValuationAgent
from agents.peer_agent import PeerAgent

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(90, 100, 110)
        self.cell(0, 8, 'Quant AI Terminal | Institutional Research', 0, 0, 'R')
        self.ln(6)
        self.set_draw_color(10, 18, 26)
        self.set_line_width(0.4)
        self.line(10, 16, 200, 16)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated {datetime.date.today()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 150, 110)
        self.cell(0, 8, title, 0, 1, 'L')
        self.set_draw_color(0, 150, 110)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, body)
        self.ln()

    def section_kicker(self, text):
        self.set_font('Arial', 'B', 9)
        self.set_text_color(120, 130, 140)
        self.cell(0, 6, text.upper(), 0, 1, 'L')

    def callout_box(self, title, body):
        x = self.get_x()
        y = self.get_y()
        w = 190
        h = 22
        self.set_fill_color(245, 250, 248)
        self.set_draw_color(0, 150, 110)
        self.rect(x, y, w, h, 'DF')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0, 120, 90)
        self.set_xy(x + 6, y + 4)
        self.cell(w - 12, 5, title, 0, 2, 'L')
        self.set_font('Arial', '', 9)
        self.set_text_color(50, 70, 80)
        self.multi_cell(w - 12, 5, body)
        self.set_xy(x, y + h + 4)

    def add_metric_box(self, label, value, w=92, h=16):
        x = self.get_x()
        y = self.get_y()
        self.set_fill_color(14, 20, 28)
        self.set_draw_color(22, 32, 44)
        self.rect(x, y, w, h, 'DF')
        self.set_fill_color(0, 150, 110)
        self.rect(x, y, 2, h, 'F')
        self.set_font('Arial', 'B', 9)
        self.set_text_color(180, 220, 210)
        self.set_xy(x + 6, y + 3)
        self.cell(w - 8, 4, label.upper(), 0, 2, 'L')
        self.set_font('Arial', 'B', 12)
        self.set_text_color(235, 255, 245)
        self.cell(w - 8, 8, str(value), 0, 0, 'L')
        self.set_xy(x + w + 6, y)

def _safe_text(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

def _format_large(num):
    if num is None:
        return "N/A"
    try:
        num = float(num)
    except Exception:
        return "N/A"
    if abs(num) >= 1e12:
        return f"{num/1e12:.2f}T"
    if abs(num) >= 1e9:
        return f"{num/1e9:.2f}B"
    if abs(num) >= 1e6:
        return f"{num/1e6:.2f}M"
    return f"{num:.2f}"

def _plot_price_chart(df, path):
    data = df.tail(180)
    fig, ax = plt.subplots(figsize=(6.8, 3.0), dpi=160)
    fig.patch.set_facecolor("#0B0F14")
    ax.set_facecolor("#0B0F14")
    ax.plot(data.index, data["Close"], color="#00E6A8", linewidth=1.6, label="Close")
    if "SMA_50" in data.columns:
        ax.plot(data.index, data["SMA_50"], color="#7AD7C0", linewidth=1.0, label="SMA 50")
    if "SMA_200" in data.columns:
        ax.plot(data.index, data["SMA_200"], color="#5AA7A0", linewidth=1.0, label="SMA 200")
    ax.grid(True, color="#1F2A36", linewidth=0.5, alpha=0.7)
    ax.tick_params(colors="#B5C0CC", labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#27303C")
    ax.spines["bottom"].set_color("#27303C")
    ax.legend(facecolor="#0B0F14", edgecolor="#27303C", labelcolor="#CFE7DF", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

def _plot_rsi_chart(df, path):
    data = df.tail(180)
    fig, ax = plt.subplots(figsize=(6.8, 2.6), dpi=160)
    fig.patch.set_facecolor("#0B0F14")
    ax.set_facecolor("#0B0F14")
    ax.plot(data.index, data["RSI"], color="#00E6A8", linewidth=1.3, label="RSI(14)")
    ax.axhline(70, color="#FF6B6B", linewidth=0.8, linestyle="--")
    ax.axhline(30, color="#FFD166", linewidth=0.8, linestyle="--")
    ax.set_ylim(0, 100)
    ax.grid(True, color="#1F2A36", linewidth=0.5, alpha=0.7)
    ax.tick_params(colors="#B5C0CC", labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#27303C")
    ax.spines["bottom"].set_color("#27303C")
    ax.legend(facecolor="#0B0F14", edgecolor="#27303C", labelcolor="#CFE7DF", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

def _plot_trend_chart(df, path):
    data = df.tail(180)
    base = data["Close"].iloc[0] if not data.empty else 1
    trend = (data["Close"] / base) * 100
    fig, ax = plt.subplots(figsize=(6.8, 2.6), dpi=160)
    fig.patch.set_facecolor("#0B0F14")
    ax.set_facecolor("#0B0F14")
    ax.plot(data.index, trend, color="#74F2C6", linewidth=1.5, label="Normalized Trend")
    ax.grid(True, color="#1F2A36", linewidth=0.5, alpha=0.7)
    ax.tick_params(colors="#B5C0CC", labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#27303C")
    ax.spines["bottom"].set_color("#27303C")
    ax.legend(facecolor="#0B0F14", edgecolor="#27303C", labelcolor="#CFE7DF", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

def _add_table(pdf, headers, rows, col_widths):
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(10, 18, 26)
    pdf.set_text_color(235, 255, 245)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
    pdf.ln()
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color(40, 60, 70)
    fill = False
    for row in rows:
        pdf.set_fill_color(245, 248, 250) if fill else pdf.set_fill_color(255, 255, 255)
        for i, cell in enumerate(row):
            pdf.cell(col_widths[i], 8, str(cell), 1, 0, 'C', 1)
        pdf.ln()
        fill = not fill

def create_pdf(ticker, summary, analysis_text, filename="report.pdf", price_df=None, peer_df=None):
    try:
        pdf = PDFReport()
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()
        
        # 1. Cover Title
        pdf.set_fill_color(10, 18, 26)
        pdf.rect(0, 0, 210, 50, 'F')
        pdf.set_text_color(235, 255, 245)
        pdf.set_font('Arial', 'B', 24)
        pdf.set_xy(10, 12)
        pdf.cell(0, 10, f"{ticker} Institutional Research", 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(180, 220, 210)
        pdf.set_x(10)
        pdf.cell(0, 8, f"Report Date: {datetime.date.today()}  |  Analyst Desk: Quant AI", 0, 1, 'L')
        pdf.set_fill_color(245, 250, 248)
        pdf.rect(10, 56, 190, 14, 'DF')
        pdf.set_text_color(40, 60, 70)
        pdf.set_font('Arial', 'B', 9)
        pdf.set_xy(12, 60)
        pdf.cell(0, 6, "Executive Overview", 0, 1, 'L')
        pdf.ln(10)
        
        # 2. Build sections and collect TOC entries
        toc_entries = []
        analysis_text = analysis_text or ""
        clean_text = _safe_text(analysis_text)

        # 3. Executive Summary
        pdf.add_page()
        summary_text = clean_text.strip().replace("\n", " ")
        if len(summary_text) > 900:
            summary_text = summary_text[:900].rsplit(" ", 1)[0] + "..."
        toc_entries.append(("Executive Summary", pdf.page_no()))
        pdf.section_kicker("Snapshot")
        pdf.chapter_title("Executive Summary")
        pdf.callout_box("Key Takeaways",
                        "Concise synthesis of valuation, momentum, and catalyst framework.")
        pdf.chapter_body(summary_text or "Summary unavailable.")

        # 4. Key Metrics Summary
        if isinstance(summary, dict):
            pdf.add_page()
            toc_entries.append(("Market Pulse (Key Metrics)", pdf.page_no()))
            pdf.section_kicker("Market Snapshot")
            pdf.chapter_title("Market Pulse (Key Metrics)")
            pdf.add_metric_box("Current Price", f"${summary.get('current_price', 0):.2f}")
            pdf.add_metric_box("RSI (14)", f"{summary.get('rsi', 0):.2f}")
            pdf.ln(20)
            pdf.add_metric_box("200-Day SMA", f"${summary.get('sma_200', 0):.2f}")
            pdf.add_metric_box("AI Signal", summary.get('sentiment', 'N/A'))
            pdf.ln(22)
        
        # 5. Charts
        if isinstance(price_df, pd.DataFrame) and not price_df.empty:
            pdf.add_page()
            toc_entries.append(("Technical Charts", pdf.page_no()))
            pdf.section_kicker("Price Action")
            pdf.chapter_title("Technical Charts")
            with tempfile.TemporaryDirectory() as tmpdir:
                price_path = os.path.join(tmpdir, "price.png")
                rsi_path = os.path.join(tmpdir, "rsi.png")
                trend_path = os.path.join(tmpdir, "trend.png")
                try:
                    _plot_price_chart(price_df, price_path)
                    pdf.image(price_path, x=12, w=186)
                    pdf.ln(6)
                except Exception:
                    pass
                try:
                    if "RSI" in price_df.columns:
                        _plot_rsi_chart(price_df, rsi_path)
                        pdf.image(rsi_path, x=12, w=186)
                        pdf.ln(6)
                except Exception:
                    pass
                try:
                    _plot_trend_chart(price_df, trend_path)
                    pdf.image(trend_path, x=12, w=186)
                    pdf.ln(6)
                except Exception:
                    pass

        # 6. Investment Rationale & Valuation
        pdf.add_page()
        toc_entries.append(("Investment Rationale & Valuation", pdf.page_no()))
        pdf.section_kicker("Thesis")
        pdf.chapter_title("Investment Rationale & Valuation")
        val_agent = ValuationAgent()
        metrics = val_agent.get_fundamentals(ticker)
        if metrics:
            fair = val_agent.calculate_fair_value(metrics)
            curr = metrics.get('Current Price', 0)
            upside = ((fair - curr) / curr) * 100 if curr else 0
            pdf.callout_box("Valuation Summary",
                            f"Intrinsic value ${fair:.2f} vs current ${curr:.2f} "
                            f"({upside:+.1f}% upside).")
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(40, 60, 70)
            pdf.multi_cell(0, 6,
                           f"- Intrinsic value estimate: ${fair:.2f}\n"
                           f"- Current price: ${curr:.2f} | Upside: {upside:+.1f}%\n"
                           f"- Target (analyst mean): ${metrics.get('Target Price (Analyst)', 0):.2f}\n"
                           f"- P/E: {metrics.get('Trailing P/E', 0):.2f} | Forward P/E: {metrics.get('Forward P/E', 0):.2f}\n"
                           f"- Price/Book: {metrics.get('Price/Book', 0):.2f} | PEG: {metrics.get('PEG Ratio', 0):.2f}\n"
                           f"- ROE: {metrics.get('ROE', 0):.2%} | Margin: {metrics.get('Profit Margin', 0):.2%}",
                           0, 'L')
        else:
            pdf.chapter_body("Valuation data unavailable.")

        # 7. Sector / Peer Comparison
        pdf.add_page()
        toc_entries.append(("Sector & Peer Comparison", pdf.page_no()))
        pdf.section_kicker("Benchmarking")
        pdf.chapter_title("Sector & Peer Comparison")
        if peer_df is None:
            try:
                peer_agent = PeerAgent()
                peer_df = peer_agent.fetch_peer_data(ticker)
            except Exception:
                peer_df = None
        if isinstance(peer_df, pd.DataFrame) and not peer_df.empty:
            cols = []
            for col in ["Ticker", "Market Cap (B)", "P/E Ratio", "Forward P/E", "ROE (%)", "Rev Growth (%)"]:
                if col in peer_df.columns:
                    cols.append(col)
            display_df = peer_df.copy()
            if "Market Cap (B)" in display_df.columns:
                display_df["Market Cap (B)"] = display_df["Market Cap (B)"].apply(lambda x: f"{x:.1f}B")
            table_rows = display_df[cols].head(6).values.tolist()
            _add_table(pdf, cols, table_rows, [28, 32, 28, 28, 28, 28][:len(cols)])
        else:
            pdf.chapter_body("Peer comparison data unavailable.")

        # 8. Analyst Notes
        pdf.add_page()
        toc_entries.append(("Analyst Notes", pdf.page_no()))
        pdf.section_kicker("Narrative")
        pdf.chapter_title("Analyst Notes")
        pdf.chapter_body(clean_text)

        # 9. Risk Factors
        pdf.add_page()
        toc_entries.append(("Risk Factors", pdf.page_no()))
        pdf.section_kicker("Risk")
        pdf.chapter_title("Risk Factors")
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(40, 60, 70)
        pdf.multi_cell(0, 6,
                       "- Macro shocks can reverse momentum quickly.\n"
                       "- Liquidity conditions may widen spreads during stress.\n"
                       "- Model signals are probabilistic, not deterministic.",
                       0, 'L')
        
        # 10. Table of Contents (append at end)
        pdf.add_page()
        pdf.set_xy(10, 22)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(0, 150, 110)
        pdf.cell(0, 10, "Table of Contents", 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(40, 60, 70)
        for title, page in toc_entries:
            pdf.cell(0, 7, f"{title} .................................... {page}", 0, 1, 'L')

        # 11. Disclaimer
        pdf.ln(20)
        pdf.set_font('Arial', 'I', 8)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(0, 5, "Disclaimer: This report is generated by Quant AI for informational purposes only.")
        
        # 파일 저장 (경로 문제 해결)
        pdf.output(filename)
        return filename
        
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return None
