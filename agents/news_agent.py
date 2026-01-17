import yfinance as yf
import datetime

class NewsAgent:
    def __init__(self):
        # Sentiment Dictionary
        self.positive_words = ["surge", "jump", "gain", "buy", "bull", "growth", "record", "profit", "beat", "up", "high", "positive", "deal", "launch", "approval", "soar", "spike"]
        self.negative_words = ["drop", "fall", "loss", "miss", "bear", "down", "low", "negative", "crash", "plunge", "concern", "risk", "lawsuit", "delay", "fail", "sink", "slump"]

    def _find_key_recursive(self, data, target_keys):
        """
        Recursively searches for keys.
        """
        if isinstance(data, dict):
            # Check current level
            for k in target_keys:
                if k in data and data[k]:
                    return data[k]
            
            # Recursive search
            for k, v in data.items():
                if k in ['thumbnail', 'resolutions', 'images']: continue # Skip images
                found = self._find_key_recursive(v, target_keys)
                if found: return found
                
        elif isinstance(data, list):
            for item in data:
                found = self._find_key_recursive(item, target_keys)
                if found: return found
        return None

    def get_news(self, ticker):
        """
        Fetches news with strict URL cleaning (No Dictionaries, No Images).
        """
        try:
            stock = yf.Ticker(ticker)
            news_list = stock.news
            
            processed_news = []
            total_sentiment = 0
            
            if not news_list:
                return [], 0
            
            for item in news_list:
                # 1. Extract Title
                title = self._find_key_recursive(item, ['title', 'headline', 'name'])
                if not title or not isinstance(title, str): 
                    continue
                
                # 2. Extract Publisher
                publisher = self._find_key_recursive(item, ['publisher', 'source'])
                if isinstance(publisher, dict):
                    publisher = publisher.get('title', 'Unknown')
                if not publisher: publisher = "Market News"

                # 3. Extract Link (THE FIX IS HERE)
                raw_link = self._find_key_recursive(item, ['link', 'url', 'clickThroughUrl'])
                link = None

                # [FIX] Unwrap Dictionary if necessary
                if isinstance(raw_link, dict):
                    # It's a package like {'url': 'https://...', ...}
                    link = raw_link.get('url') or raw_link.get('originalUrl') or raw_link.get('link')
                elif isinstance(raw_link, str):
                    link = raw_link

                # [FIX] Filter out Images and Invalid Links
                if link:
                    link_str = str(link).lower()
                    # Check for image extensions or yahoo image domains
                    if "s.yimg.com" in link_str or link_str.endswith(('.jpg', '.png', '.jpeg', '.webp')):
                        link = None
                
                # Fallback to Quote Page
                if not link: 
                    link = f"https://finance.yahoo.com/quote/{ticker}"
                
                # 4. Extract Date
                ts = self._find_key_recursive(item, ['providerPublishTime', 'pubDate', 'timestamp'])
                if ts:
                    try:
                        if isinstance(ts, (int, float)):
                            date_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
                        else:
                            date_str = "Recent"
                    except:
                        date_str = "Recent"
                else:
                    date_str = "Recent"
                
                # 5. Sentiment Analysis
                score = 0
                title_lower = title.lower()
                
                for word in self.positive_words:
                    if word in title_lower: score += 1
                for word in self.negative_words:
                    if word in title_lower: score -= 1
                
                if score > 0: label = "🟢 POSITIVE"
                elif score < 0: label = "🔴 NEGATIVE"
                else: label = "⚪ NEUTRAL"
                
                total_sentiment += score
                
                processed_news.append({
                    "title": title,
                    "publisher": publisher,
                    "link": link, # Now guaranteed to be a clean string or fallback
                    "date": date_str,
                    "sentiment": label,
                    "score": score
                })
            
            # Normalize Score
            final_score = 0
            if processed_news:
                final_score = max(min(total_sentiment * 10, 100), -100)
            
            return processed_news, final_score
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return [], 0