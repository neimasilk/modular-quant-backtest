"""
Earnings Call LLM Analyzer

Analyzes earnings call transcripts using LLM to extract sentiment signals.

Key Features:
- Management confidence scoring (1-10)
- Quarter-over-quarter comparison
- Red flag detection
- Trading signal generation

Usage:
    analyzer = EarningsCallAnalyzer(api_key=DEEPSEEK_API_KEY)
    analysis = analyzer.analyze_call(ticker='NVDA', transcript=text)
"""

import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI


EARNINGS_ANALYSIS_PROMPT = """You are a senior equity research analyst specializing in management tone analysis for institutional investors.

Analyze this earnings call transcript and extract key sentiment indicators that predict future stock performance.

Transcript (Management Discussion section):
{transcript_text}

Previous Quarter Summary (for comparison):
{prev_quarter_summary}

Tasks:
1. Management Confidence Level (1-10 scale):
   - 1-3: Very defensive, uncertain, risk-focused, declining confidence
   - 4-6: Neutral, mixed signals, cautious optimism
   - 7-10: Confident, growth-focused, optimistic, strong conviction

2. Key Themes Mentioned (rank by emphasis):
   - List top 5 themes (e.g., "AI demand acceleration", "margin expansion", "supply constraints")
   - Note frequency and tone for each theme

3. Red Flags (if any):
   - Defensive language ("challenging", "headwinds", "uncertainty", "pressured")
   - Vague or delayed guidance
   - Excuses or blame shifting
   - Repeated questions about same concerning issue
   - Management avoiding direct answers

4. Quarter-over-Quarter Comparison:
   - Confidence shift: How much has confidence changed vs previous quarter? (-5 to +5)
   - Narrative shift: Describe any major theme changes or new concerns

5. Trading Signal:
   - BULLISH: High confidence (7+) + positive themes + no major red flags + improving QoQ
   - NEUTRAL: Mixed signals, moderate confidence (4-6), or unclear direction
   - BEARISH: Low confidence (<4) OR multiple red flags OR significant confidence decline

Output STRICTLY in JSON format (no additional text):
{{
    "confidence_level": <1-10>,
    "qoq_confidence_change": <-5 to +5>,
    "key_themes": [
        {{"theme": "...", "frequency": "high/medium/low", "tone": "positive/negative/neutral"}}
    ],
    "red_flags": ["...", "..."],
    "narrative_shift": "One sentence describing major changes vs previous quarter",
    "trading_signal": "BULLISH/NEUTRAL/BEARISH",
    "reasoning": "Max 50 words explaining the trading signal",
    "analyst_notes": "Additional context or nuances worth noting"
}}
"""


class EarningsCallAnalyzer:
    """Analyze earnings calls using LLM to extract sentiment signals."""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        """
        Initialize the analyzer.

        Args:
            api_key: DeepSeek API key (or set DEEPSEEK_API_KEY env var)
            model: Model to use (default: deepseek-chat)
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable "
                "or pass api_key parameter"
            )

        self.model = model
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

        # Cache for previous analyses (for QoQ comparison)
        self.analysis_cache = {}

    def analyze_call(self, ticker: str, quarter: str, transcript: str,
                    prev_summary: Optional[Dict] = None) -> Dict:
        """
        Analyze a single earnings call.

        Args:
            ticker: Stock symbol
            quarter: Quarter label (e.g., "2023_Q4")
            transcript: Full transcript text
            prev_summary: Previous quarter analysis for comparison

        Returns:
            Dict with confidence_level, themes, red_flags, signal, etc.
        """
        print(f"\n🤖 Analyzing {ticker} {quarter} earnings call...")

        # Truncate transcript to fit context window (keep first 8000 chars)
        # Focus on management discussion and key Q&A
        transcript_excerpt = self._extract_management_discussion(transcript)[:8000]

        # Format previous summary
        if prev_summary:
            prev_text = f"""Previous Quarter:
- Confidence: {prev_summary.get('confidence_level', 'N/A')}/10
- Signal: {prev_summary.get('trading_signal', 'N/A')}
- Key themes: {', '.join([t['theme'] for t in prev_summary.get('key_themes', [])[:3]])}
"""
        else:
            prev_text = "No previous quarter data available (first analysis)"

        # Build prompt
        prompt = EARNINGS_ANALYSIS_PROMPT.format(
            transcript_text=transcript_excerpt,
            prev_quarter_summary=prev_text
        )

        # Call LLM API
        try:
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior equity research analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for consistent analysis
                max_tokens=1000
            )

            elapsed = time.time() - start_time

            # Extract response
            content = response.choices[0].message.content

            # Parse JSON (handle potential markdown code blocks)
            content = content.strip()
            if content.startswith('```'):
                # Remove markdown code block wrapper
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            analysis = json.loads(content)

            # Add metadata
            analysis['ticker'] = ticker
            analysis['quarter'] = quarter
            analysis['analyzed_at'] = datetime.now().isoformat()
            analysis['llm_call_time'] = round(elapsed, 2)

            # Cache for next quarter comparison
            cache_key = f"{ticker}_{quarter}"
            self.analysis_cache[cache_key] = analysis

            # Print summary
            print(f"  ✅ Confidence: {analysis['confidence_level']}/10")
            print(f"  ✅ Signal: {analysis['trading_signal']}")
            print(f"  ✅ QoQ Change: {analysis['qoq_confidence_change']:+d}")
            print(f"  ⏱️  LLM call: {elapsed:.2f}s")

            if analysis['red_flags']:
                print(f"  ⚠️  Red flags: {len(analysis['red_flags'])}")

            return analysis

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM response as JSON: {e}")
            print(f"Raw response: {content[:200]}...")
            raise

        except Exception as e:
            print(f"❌ LLM API call failed: {e}")
            raise

    def analyze_ticker_history(self, ticker: str, transcripts: List[Dict],
                               save_results: bool = True) -> List[Dict]:
        """
        Analyze historical earnings calls for a ticker.

        Args:
            ticker: Stock symbol
            transcripts: List of transcript dicts from EarningsTranscriptFetcher
            save_results: Save results to JSON file

        Returns:
            List of analysis dicts, one per quarter
        """
        print(f"\n" + "="*60)
        print(f"ANALYZING EARNINGS HISTORY: {ticker}")
        print(f"Total quarters: {len(transcripts)}")
        print("="*60)

        results = []
        prev_analysis = None

        # Sort by date to ensure chronological order
        transcripts_sorted = sorted(transcripts, key=lambda x: x['date'])

        for idx, transcript in enumerate(transcripts_sorted):
            quarter = transcript['quarter']
            text = transcript['text']

            try:
                analysis = self.analyze_call(
                    ticker=ticker,
                    quarter=quarter,
                    transcript=text,
                    prev_summary=prev_analysis
                )

                results.append(analysis)
                prev_analysis = analysis  # For next QoQ comparison

                # Rate limiting (1 call per 2 seconds to be safe)
                if idx < len(transcripts_sorted) - 1:
                    time.sleep(2)

            except Exception as e:
                print(f"⚠️ Failed to analyze {quarter}: {e}")
                continue

        # Save results if requested
        if save_results and results:
            output_dir = f"experiments/active/EXP-2025-010-earnings-call/results"
            os.makedirs(output_dir, exist_ok=True)

            output_file = f"{output_dir}/{ticker}_earnings_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n💾 Results saved to: {output_file}")

        return results

    def _extract_management_discussion(self, transcript: str) -> str:
        """
        Extract the management discussion section from full transcript.

        This typically contains the most important forward-looking statements.
        """
        # Try to find "Prepared Remarks" or "Management Discussion" section
        # For now, just return the first half of the transcript
        # (opening remarks and prepared statements usually come first)

        lines = transcript.split('\n')
        total_lines = len(lines)

        # Take first 60% of transcript (management remarks + early Q&A)
        cutoff = int(total_lines * 0.6)

        return '\n'.join(lines[:cutoff])

    def generate_trading_signals(self, analyses: List[Dict]) -> Dict:
        """
        Generate trading signals from earnings analysis history.

        Decision Logic:
        - BUY: Confidence ≥8, QoQ change ≥2, no red flags
        - STRONG_BUY: Confidence ≥9, QoQ change ≥3
        - SELL: Confidence ≤4 OR QoQ change ≤-3 OR red_flags ≥3
        - HOLD: Everything else

        Args:
            analyses: List of earnings analyses (sorted by date)

        Returns:
            Dict with current signal and supporting data
        """
        if not analyses:
            return {'signal': 'HOLD', 'reason': 'No data'}

        # Get latest analysis
        latest = analyses[-1]

        confidence = latest['confidence_level']
        qoq_change = latest['qoq_confidence_change']
        red_flags = len(latest.get('red_flags', []))
        llm_signal = latest['trading_signal']

        # Decision logic
        if confidence >= 9 and qoq_change >= 3 and red_flags == 0:
            signal = 'STRONG_BUY'
            reason = f"Very high confidence ({confidence}/10), strong improvement ({qoq_change:+d})"

        elif confidence >= 8 and qoq_change >= 2 and red_flags == 0:
            signal = 'BUY'
            reason = f"High confidence ({confidence}/10), improving QoQ ({qoq_change:+d})"

        elif confidence <= 4 or qoq_change <= -3 or red_flags >= 3:
            signal = 'SELL'
            reason = f"Low confidence ({confidence}/10) or declining ({qoq_change:+d}) or {red_flags} red flags"

        elif qoq_change <= -2:
            signal = 'REDUCE'
            reason = f"Confidence declining ({qoq_change:+d})"

        else:
            signal = 'HOLD'
            reason = f"Neutral signals (confidence {confidence}/10, QoQ {qoq_change:+d})"

        return {
            'ticker': latest['ticker'],
            'quarter': latest['quarter'],
            'signal': signal,
            'confidence_level': confidence,
            'qoq_change': qoq_change,
            'red_flags_count': red_flags,
            'llm_raw_signal': llm_signal,
            'reason': reason,
            'generated_at': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    import sys

    print("\n" + "="*60)
    print("EARNINGS CALL ANALYZER - TEST MODE")
    print("="*60)

    # Check for API key
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        print("\n📝 To use this analyzer:")
        print("  1. Get API key from https://platform.deepseek.com/")
        print("  2. Set environment variable: export DEEPSEEK_API_KEY='sk-...'")
        print("  3. Run this script again")
        sys.exit(1)

    # Test with a sample transcript (if available)
    from src.data.earnings_fetcher import EarningsTranscriptFetcher

    fetcher = EarningsTranscriptFetcher()
    transcripts = fetcher.fetch_transcripts('NVDA', quarters=2, source='manual')

    if not transcripts:
        print("\n⚠️ No transcripts found for testing")
        print("Please add manual transcripts first (see earnings_fetcher.py)")
        sys.exit(0)

    # Initialize analyzer
    analyzer = EarningsCallAnalyzer(api_key=api_key)

    # Analyze available transcripts
    results = analyzer.analyze_ticker_history('NVDA', transcripts, save_results=True)

    # Generate trading signal
    if results:
        signal = analyzer.generate_trading_signals(results)
        print("\n" + "="*60)
        print("TRADING SIGNAL")
        print("="*60)
        print(f"Signal: {signal['signal']}")
        print(f"Reason: {signal['reason']}")
        print(f"Confidence: {signal['confidence_level']}/10")
        print(f"QoQ Change: {signal['qoq_change']:+d}")
