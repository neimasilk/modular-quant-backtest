"""
NewsSanityChecker for EXP-2025-008

LLM-based "Bullshit Detector" that validates whether extreme price moves
are justified by actual news substance or just market noise/hype.

Different from EXP-005:
- EXP-005: Asked for sentiment (positive/negative) -> Buy/Sell
- EXP-008: Price moves FIRST -> LLM validates substance -> Fade or Follow
"""

import os
import json
from typing import Dict, Optional, Literal
from dotenv import load_dotenv
from openai import OpenAI
import time

load_dotenv()


# ============== PROMPTS ==============

SYSTEM_PROMPT = """You are a skeptical, cynical, and highly experienced senior hedge fund risk manager.
Your job is to protect the portfolio from FOMO, panic selling, and stupid decisions.

Analyze the provided news headline/summary in the context of the stock's recent price move.
Your goal: Determine if the market reaction is JUSTIFIED or if the market is being stupid.

Output STRICTLY in JSON format (no markdown, no explanations outside JSON):
{
    "news_category": "Earnings" | "Macro" | "Product" | "Legal" | "Hype/Rumor" | "Noise" | "Unknown",
    "substance_score": <1-10 integer>,
    "market_reaction_justified": <true or false>,
    "verdict": "FADE" | "FOLLOW" | "IGNORE",
    "reasoning": "<short explanation, max 15 words>"
}

SCORING GUIDE:
- substance_score 1-3: Empty marketing, buzzwords, rumors, no financial impact
- substance_score 4-6: Minor news, some substance but not game-changing
- substance_score 7-10: Hard financial impact, earnings beat, major contracts, regulatory changes

VERDICT GUIDE:
- "FADE": The price move is OVERBLOWN. Trade against it (sell rip, buy dip).
- "FOLLOW": The price move is JUSTIFIED. Go with the flow.
- "IGNORE": The news is irrelevant or unclear. Don't trade based on this.

Be RUTHLESS. Most price moves are overreactions. Default to skepticism."""

USER_PROMPT_TEMPLATE = """Context:
Stock: {ticker}
Price Move: {direction} {percent:.1f}% in recent period.
Recent Volume: {volume_context}

News Headline: "{news_text}"

Question: Is this price move justified by the news, or is the market being stupid?

Analyze and output ONLY the JSON."""


# ============== CHECKER CLASS ==============

class NewsSanityChecker:
    """
    LLM-based validator for extreme price moves.

    Only calls LLM when price moves exceed threshold (saves API costs).
    Returns actionable trading signals: FADE, FOLLOW, or IGNORE.
    """

    # Verdict types
    Verdict = Literal["FADE", "FOLLOW", "IGNORE", "SHORT_SCALP", "BUY_TREND", "BUY_DIP", "HARD_EXIT", "NEUTRAL"]

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        """Initialize SanityChecker with DeepSeek API client."""
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model

        # Cache for results
        self.cache = {}
        self.cache_file = "data/sanity_cache.json"

    def _load_cache(self):
        """Load cache from disk."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
        except Exception:
            self.cache = {}

    def _save_cache(self):
        """Save cache to disk."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception:
            pass

    def check_signal(
        self,
        ticker: str,
        price_change_pct: float,
        news_text: str,
        volume: Optional[float] = None,
        avg_volume: Optional[float] = None,
        use_cache: bool = True,
        verbose: bool = True
    ) -> Dict[str, any]:
        """
        Analyze a price move with news and return trading signal.

        Args:
            ticker: Stock symbol
            price_change_pct: Price change as decimal (e.g., 0.05 for +5%)
            news_text: News headline or summary
            volume: Current volume
            avg_volume: Average volume for comparison
            use_cache: Whether to use cached results
            verbose: Print analysis details

        Returns:
            Dict with:
                - signal: Trading signal (SHORT_SCALP, BUY_TREND, BUY_DIP, HARD_EXIT, NEUTRAL)
                - verdict: Raw LLM verdict (FADE, FOLLOW, IGNORE)
                - substance_score: 1-10 score
                - reasoning: LLM explanation
                - should_trade: Boolean
        """
        # Default response
        default_response = {
            "signal": "NEUTRAL",
            "verdict": "IGNORE",
            "substance_score": 0,
            "reasoning": "Price move below threshold",
            "should_trade": False
        }

        # 1. Skip jika pergerakan kecil (hemat biaya API)
        if abs(price_change_pct) < 0.03:
            if verbose:
                print(f"[{ticker}] Move: {price_change_pct:+.1%} | Below threshold - IGNORE")
            return default_response

        # Check cache
        cache_key = f"{ticker}_{news_text}_{price_change_pct:.2f}"
        if use_cache and cache_key in self.cache:
            if verbose:
                cached = self.cache[cache_key]
                print(f"[{ticker}] Move: {price_change_pct:+.1%} | CACHED: {cached['verdict']} | Score: {cached['substance_score']}/10")
            return self._translate_to_signal(
                price_change_pct,
                self.cache[cache_key]
            )

        # 2. Build volume context
        volume_context = "Normal"
        if volume and avg_volume:
            ratio = volume / avg_volume if avg_volume > 0 else 1
            if ratio > 2:
                volume_context = f"High ({ratio:.1f}x average)"
            elif ratio < 0.5:
                volume_context = f"Low ({ratio:.1f}x average)"

        # 3. Call LLM
        direction = "UP" if price_change_pct > 0 else "DOWN"

        prompt = USER_PROMPT_TEMPLATE.format(
            ticker=ticker,
            direction=direction,
            percent=abs(price_change_pct) * 100,
            volume_context=volume_context,
            news_text=news_text[:500]  # Limit length
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temp for consistent JSON
                max_tokens=200
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            analysis = self._parse_json_response(content)

            if verbose:
                print(f"[{ticker}] Move: {price_change_pct:+.1%} | LLM: {analysis['verdict']} | Score: {analysis['substance_score']}/10")
                print(f"    Category: {analysis['news_category']} | Reason: {analysis['reasoning']}")

            # Cache result
            self.cache[cache_key] = analysis
            if use_cache:
                self._save_cache()

            # Translate to trading signal
            return self._translate_to_signal(price_change_pct, analysis)

        except Exception as e:
            print(f"[{ticker}] Error calling LLM: {e}")
            return default_response

    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON response from LLM."""
        default = {
            "news_category": "Unknown",
            "substance_score": 5,
            "market_reaction_justified": False,
            "verdict": "IGNORE",
            "reasoning": "Parse error"
        }

        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```" in content:
                # Extract content between ```json and ```
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end > start:
                    content = content[start:end].strip()
                elif "```" in content:
                    # Try without json keyword
                    start = content.find("```") + 3
                    end = content.find("```", start)
                    if end > start:
                        content = content[start:end].strip()

            # Parse JSON
            result = json.loads(content)

            # Validate required fields
            for key in default.keys():
                if key not in result:
                    result[key] = default[key]

            return result

        except json.JSONDecodeError:
            # Try to extract values manually
            result = default.copy()
            content_lower = content.lower()

            # Simple keyword matching
            if "fade" in content_lower:
                result["verdict"] = "FADE"
            elif "follow" in content_lower:
                result["verdict"] = "FOLLOW"

            # Extract score if present
            import re
            score_match = re.search(r'substance_score["\s:]+(\d+)', content, re.IGNORECASE)
            if score_match:
                result["substance_score"] = int(score_match.group(1))

            return result

    def _translate_to_signal(self, price_change_pct: float, analysis: Dict) -> Dict:
        """
        Translate LLM analysis to actionable trading signal.

        Decision Matrix:
        - Price UP + Low substance = SHORT_SCALP (sell the rip)
        - Price UP + High substance = BUY_TREND (follow the move)
        - Price DOWN + Low substance = BUY_DIP (overreaction, buy cheap)
        - Price DOWN + High substance = HARD_EXIT (real problems, get out)
        """
        score = analysis.get("substance_score", 5)
        verdict = analysis.get("verdict", "IGNORE")

        # Thresholds
        LOW_SUBSTANCE = 4
        HIGH_SUBSTANCE = 7

        signal = "NEUTRAL"
        should_trade = False

        if price_change_pct > 0:  # Harga NAIK
            if score < LOW_SUBSTANCE:
                # Berita Sampah - Harga naik karena FOMO
                signal = "SHORT_SCALP"
                should_trade = True
            elif score > HIGH_SUBSTANCE:
                # Berita Bagus - Tren sehat
                signal = "BUY_TREND"
                should_trade = True
            else:
                # Moderate - caution
                signal = "TAKE_PROFITS" if verdict == "FADE" else "HOLD"

        elif price_change_pct < 0:  # Harga TURUN
            if score < LOW_SUBSTANCE:
                # Masalah Sepele - Pasar overreacting
                signal = "BUY_DIP"
                should_trade = True
            elif score > HIGH_SUBSTANCE:
                # Masalah Serius - Ini kiamat beneran
                signal = "HARD_EXIT"
                should_trade = True
            else:
                # Moderate - wait and see
                signal = "REDUCE_POSITION" if verdict == "FADE" else "HOLD"

        # Override with explicit verdict
        if verdict == "IGNORE":
            signal = "NEUTRAL"
            should_trade = False
        elif verdict == "FADE" and not should_trade:
            # Fade even if moderate score
            if price_change_pct > 0:
                signal = "SHORT_SCALP"
            else:
                signal = "BUY_DIP"
            should_trade = True

        return {
            "signal": signal,
            "verdict": verdict,
            "substance_score": score,
            "reasoning": analysis.get("reasoning", ""),
            "should_trade": should_trade,
            "news_category": analysis.get("news_category", "Unknown"),
            "reaction_justified": analysis.get("market_reaction_justified", False)
        }

    def analyze_batch(
        self,
        scenarios: list[Dict],
        use_cache: bool = True
    ) -> list[Dict]:
        """
        Analyze multiple scenarios (for batch testing).

        Args:
            scenarios: List of dicts with ticker, price_change_pct, news_text
            use_cache: Whether to use cached results

        Returns:
            List of analysis results
        """
        results = []
        self._load_cache()

        for scenario in scenarios:
            result = self.check_signal(
                ticker=scenario.get("ticker", "UNKNOWN"),
                price_change_pct=scenario.get("price_change_pct", 0),
                news_text=scenario.get("news_text", ""),
                verbose=True
            )
            results.append(result)

            # Rate limiting
            time.sleep(0.5)

        return results


# ============== STANDALONE TEST ==============

def main():
    """Test the SanityChecker with example scenarios."""
    print("=" * 60)
    print("NEWS SANITY CHECKER - EXP-2025-008")
    print("Testing LLM-based Bullshit Detector")
    print("=" * 60)

    try:
        checker = NewsSanityChecker()

        # Test scenarios
        scenarios = [
            {
                "ticker": "XYZ",
                "price_change_pct": 0.08,  # +8%
                "news_text": "XYZ Corporation announces strategic AI initiative to transform business operations"
            },
            {
                "ticker": "ABC",
                "price_change_pct": -0.06,  # -6%
                "news_text": "ABC Factory production halted for 3 days due to local protests"
            },
            {
                "ticker": "NVDA",
                "price_change_pct": 0.12,  # +12%
                "news_text": "NVDA beats earnings estimates by 20%, revenue guidance raised to $50B for next quarter"
            },
            {
                "ticker": "TSLA",
                "price_change_pct": -0.15,  # -15%
                "news_text": "DOJ opens criminal investigation into TSLA accounting practices and EV credits"
            }
        ]

        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60 + "\n")

        results = checker.analyze_batch(scenarios)

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        for i, result in enumerate(results):
            if result["should_trade"]:
                print(f"Scenario {i+1}: {result['signal']} | Score: {result['substance_score']}/10")
            else:
                print(f"Scenario {i+1}: IGNORE | Score: {result['substance_score']}/10")

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure DEEPSEEK_API_KEY is set in .env file")


if __name__ == "__main__":
    main()
