/**
 * About Page — The Story Behind MeridianFX
 * 
 * Inspirado en SignalIQ con identidad de Stratus Intelligence
 */
import { Panel } from "../components/common";

export function AboutPage(): JSX.Element {
  return (
    <section className="flex flex-col gap-6 max-w-4xl mx-auto">
      {/* Hero */}
      <div className="text-center py-8 border-b border-line">
        <div className="flex items-center justify-center gap-3 mb-4">
          <span className="w-4 h-4 rounded-full bg-meridian inline-block"></span>
          <span className="font-serif text-5xl tracking-wide">
            Meridian<span className="italic text-meridian font-normal">FX</span>
          </span>
        </div>
        <p className="text-xl text-ink-soft font-light">
          Financial Intelligence · Stratus Intelligence
        </p>
        <div className="mt-3 inline-block bg-meridian-soft text-meridian text-xs font-mono font-semibold px-3 py-1 rounded-full">
          v2.0 · 28 de agosto 2026
        </div>
      </div>

      {/* The Story Behind MeridianFX */}
      <Panel title="📖 The Story Behind MeridianFX">
        <div className="space-y-4 text-ink-soft leading-relaxed">
          <p className="text-base">
            <strong className="text-ink">MeridianFX</strong> was born from a fundamental question in quantitative finance: 
            <em className="text-meridian font-medium"> "What separates a market forecast from a decision-ready signal?"</em>
          </p>
          <p className="text-base">
            For years, traders and analysts have relied on models that generate predictions — probabilities, directions, 
            expected returns. But a prediction is not a decision. A decision requires understanding the economic friction: 
            costs, liquidity, slippage, and the regime in which the signal exists.
          </p>
          <p className="text-base">
            <strong className="text-ink">MeridianFX</strong> was developed to bridge that gap. It is not just a forecasting 
            system — it is a <strong className="text-meridian">decision intelligence layer</strong> that applies an 
            <strong className="text-ink"> Economic Filter</strong> to every signal, ensuring that only signals that survive 
            the friction of real markets are presented as actionable.
          </p>
          <div className="bg-panel-2 rounded-xl p-4 border border-line">
            <p className="text-sm font-mono text-ink-soft">
              "MeridianFX doesn't just tell you what might happen. It tells you what is worth acting on."
            </p>
          </div>
        </div>
      </Panel>

      {/* Why MeridianFX */}
      <Panel title="🎯 Why MeridianFX?">
        <div className="space-y-4 text-ink-soft leading-relaxed">
          <p className="text-base">
            Financial markets are complex adaptive systems. Models can capture patterns, but they cannot capture the 
            <strong className="text-ink"> economic friction</strong> that exists between a forecast and a trade.
          </p>
          <p className="text-base">
            <strong className="text-ink">MeridianFX</strong> measures and applies:
          </p>
          <ul className="list-disc list-inside space-y-2 text-base ml-4">
            <li><strong className="text-ink">Net Return</strong> — After spreads, slippage, and fees</li>
            <li><strong className="text-ink">Edge Ratio</strong> — Risk-adjusted return relative to cost</li>
            <li><strong className="text-ink">Minimum Threshold</strong> — Dynamic thresholds per pair based on liquidity</li>
            <li><strong className="text-ink">Regime</strong> — Risk-on / Risk-off market conditions</li>
          </ul>
          <div className="bg-meridian-soft rounded-xl p-4 border border-meridian/20">
            <p className="text-sm text-ink-soft">
              <strong className="text-meridian">Actionability = f(Net Return, Minimum Edge, Probability, Costs, Regime)</strong>
            </p>
          </div>
        </div>
      </Panel>

      {/* Academic Foundation */}
      <Panel title="🔬 Academic Foundation">
        <div className="space-y-4 text-ink-soft leading-relaxed">
          <p className="text-base">
            <strong className="text-ink">MeridianFX</strong> is built on a foundation of academic and quantitative research:
          </p>
          <div className="space-y-3 ml-4">
            <div className="flex items-start gap-3">
              <span className="text-meridian font-mono text-base font-bold min-w-[140px]">Dornbusch (1976)</span>
              <span className="text-base">— Exchange Rate Overshooting. Monetary policy and interest-rate differentials can produce short- and medium-term deviations in exchange rates, supporting macroeconomic drivers in FX analysis.</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-meridian font-mono text-base font-bold min-w-[140px]">White (2000)</span>
              <span className="text-base">— Reality Check for Data Snooping. Highlights the danger of selecting apparently successful trading strategies through repeated experimentation, supporting MeridianFX's emphasis on robust evaluation and avoiding overfitting.</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-meridian font-mono text-base font-bold min-w-[140px]">Platt (1999)</span>
              <span className="text-base">— Probability Calibration. Establishes the importance of transforming model scores into meaningful probabilities, supporting MeridianFX's use of calibrated probabilities rather than raw model confidence.</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-meridian font-mono text-base font-bold min-w-[140px]">Lopez de Prado (2018)</span>
              <span className="text-base">— Financial Machine Learning. Provides a framework for applying machine learning to financial problems while addressing issues such as non-stationarity, overfitting, validation and backtesting.</span>
            </div>
          </div>
          <div className="bg-panel-2 rounded-xl p-4 border border-line mt-3">
            <p className="text-base text-ink-soft">
              The <strong className="text-ink">Economic Filter</strong> in MeridianFX operationalizes these theories by 
              systematically testing whether a forecast can survive real-world friction.
            </p>
          </div>
        </div>
      </Panel>

      {/* Author */}
      <Panel title="👨‍💻 Author">
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <div className="flex-1 space-y-3">
            <div>
              <h3 className="text-xl font-semibold text-ink">Daniel Canedo</h3>
              <p className="text-muted text-sm">ML Engineer · Economist · Quantitative Researcher</p>
            </div>
            <div className="space-y-2 text-ink-soft text-base">
              <div className="flex items-center gap-2">
                <span className="text-meridian">🤖</span>
                <span><strong className="text-ink">ML Engineer</strong> — Anyone AI</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-meridian">🎓</span>
                <span><strong className="text-ink">MSc. Economics</strong> — Yokohama National University</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-meridian">📊</span>
                <span><strong className="text-ink">Economist</strong> — Universidad Católica Boliviana</span>
              </div>
            </div>
            <div className="bg-panel-2 rounded-xl p-4 border border-line mt-2">
              <p className="text-sm text-ink-soft font-mono">
                "This software was designed and built by Daniel Canedo as part of the <strong className="text-meridian">Stratus Intelligence</strong> project."
              </p>
            </div>
          </div>
          <div className="flex-shrink-0 w-32 h-32 rounded-full bg-gradient-to-br from-meridian/20 to-meridian-soft flex items-center justify-center border-4 border-meridian/20">
            <span className="text-4xl font-serif text-meridian">DC</span>
          </div>
        </div>
      </Panel>

      {/* Enterprise */}
      <Panel title="🏢 Stratus Intelligence">
        <div className="space-y-4 text-ink-soft leading-relaxed">
          <div className="flex items-center gap-3">
            <span className="text-2xl">☁️</span>
            <div>
              <h4 className="text-lg font-semibold text-ink">Stratus Intelligence</h4>
              <p className="text-sm text-muted">Enterprise Financial Intelligence</p>
            </div>
          </div>
          <p className="text-base">
            <strong className="text-ink">MeridianFX</strong> is a flagship product of 
            <strong className="text-meridian"> Stratus Intelligence</strong>, an enterprise-grade financial 
            intelligence platform focused on systematic decision-making in currency markets.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-2">
            <div className="bg-panel-2 rounded-lg p-3 text-center border border-line">
              <div className="text-2xl font-serif text-meridian">9</div>
              <div className="text-xs text-muted">Currency Pairs</div>
            </div>
            <div className="bg-panel-2 rounded-lg p-3 text-center border border-line">
              <div className="text-2xl font-serif text-meridian">XGBoost</div>
              <div className="text-xs text-muted">ML Models</div>
            </div>
            <div className="bg-panel-2 rounded-lg p-3 text-center border border-line">
              <div className="text-2xl font-serif text-meridian">Real-Time</div>
              <div className="text-xs text-muted">Market Data</div>
            </div>
          </div>
        </div>
      </Panel>
    </section>
  );
}
