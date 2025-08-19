**Project Alpaca JNJ Trading System**

**By Shubhaankar Gupta and Marvin Diaz**

1\. Introduction

Our team implemented a compact, reproducible algorithmic trading system that operates exclusively within Alpaca’s paper trading environment. The purpose is to demonstrate the complete knowledge acquired in the course: authenticated acquisition of market data, systematic transformation of those data into well‑specified trading signals, evaluation of the signals through a deterministic backtest with basic frictions, and execution in a risk‑free setting. To keep the analysis transparent and auditable, we focused on a single, liquid U.S. equity, Johnson & Johnson (ticker: JNJ), and we used daily bars. Throughout, we emphasized methodological soundness and reproducibility over aggressive performance claims so that any reviewer can replicate our process from first principles.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfydNSx2_7iTWF4i2woD7GKaNhmkustkpUFz5_JyAGUP-oP4aPjnuHVOyCRxicIc4ezYrUrxDP8kiYtC8pgaIBJ3vGQ_BMggDEignZHlpxQ5feG1VycuknyU-u63FFI9h_7Ua9d?key=7W1aHaiOWzmimfVOElNCvQ)

2\. Market Data Retrieval

We obtained historical market data from Alpaca’s market data endpoints using the official Python client. Credentials were supplied via operating system environment variables, ensuring that no secrets were embedded in notebooks or repositories. The retrieval procedure requested a contiguous history of daily OHLCV bars for JNJ and validated the response for schema conformity, timestamp monotonicity, and the absence of missing values in critical fields. Timestamps were parsed as UTC and normalized to avoid cross machine inconsistencies. The resulting table formed the canonical dataset for the project, and to enable reproducible analysis independent of network availability, we retained it on disk as a single CSV named \`jnj\_bars.csv\`.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXdIO8SDmqkDVpgzacZ9qNmysDTVpC6r5pyblrcOJZJlUja-rWbT1S7GbmBnABRkLIv9_xX-noD1dsCvWCyALgd2s5dxxHQVb974P2j5G0PjY8EPhkC6J-kVSJ-z1ykquSDHPcFP?key=7W1aHaiOWzmimfVOElNCvQ)

_Image: jnj\_bars.csv_

\


3\. Data Storage Strategy

We adopted a file‑system approach tailored to the modest scale of the dataset and the goal of producing inspectable data. The raw download described above is preserved as \`jnj\_bars.csv\`, which serves as the sole on-disk source for all downstream computations. All engineered features, signals, returns, and equity curves are generated in memory at runtime from this file, and are not written out as additional derivative CSVs. This single source of truth design keeps the project minimal, prevents drift between raw and processed files, and ensures that every new run recomputes the same quantities from the same starting point. The CSV is written with explicit UTC timestamps, sorted chronologically, and saved without hidden index columns so that rolling statistics and lags behave deterministically across systems.

4\. Trading Strategy Development

We developed a z‑score mean‑reversion heuristic constructed from rolling statistics of the closing price. For each date, the rolling mean and rolling standard deviation were computed over a twenty-day window, where the degree of deviation was standardized as the difference between the closing price and the rolling mean divided by the rolling standard deviation. The signal logic is intentionally conservative. When the standardized deviation falls below −1.0, the system regards the asset as temporarily depressed relative to its recent distribution and takes or maintains a long position. When the absolute standardized deviation recedes below 0.5, the system exits to a flat state, which reduces churn in a neighborhood where noise tends to dominate exploitable edges. The base configuration is long‑only so that paper execution does not rely on margin or short sale permissions. Position sizing is fixed at one share per entry, which isolates the contribution of the signal from complications introduced by leverage or volatility targeting.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfi_RtJ0c5Bf_ogRzbLpaBjadVP6f66rEtRHGR25CuTovqCaFtSmnF7h4aXRzBZzvQMWF9sxU0JpnVJT-BDTRSne0RLYZeN-DFXj9p44LQGfCenPaCriRq_uvgmNOi5tx7zoJkefw?key=7W1aHaiOWzmimfVOElNCvQ)

5\. Code Explanation

The code is organized as a linear pipeline to support top‑to‑bottom execution without a hidden state. The configuration section loads dependencies, reads credentials from the environment, and sets key hyperparameters: the rolling window length, the entry and exit thresholds, and the transaction‑cost assumption. The ingestion section requests the historical bars and writes \`jnj\_bars.csv\` as the authoritative raw dataset. The feature‑engineering section computes the rolling mean and standard deviation and derives the standardized deviation; numerical safeguards prevent division by zero and discard warm‑up rows that lack a full history. The signal‑generation section converts standardized deviations into positions encoded as one for long and zero for flat, and it constructs the trade indicator as the first difference of the position series so that non‑zero values correspond to true entries and exits. The backtest section then computes percentage returns on the close, multiplies them by the lagged position to eliminate look ahead, subtracts friction on bars where a trade occurs, and compounds the results into equity curves for the strategy and for buy‑and‑hold. The reporting section calculates risk and performance statistics, annualized Sharpe ratio from daily returns, maximum drawdown measured from the strategy equity curve, cumulative return, and, where the span is sufficient, the compound annual growth rate, and renders a figure comparing the equity paths. Crucially, apart from \`jnj\_bars.csv\`, no further CSVs are persisted; results are reviewed directly within the notebook to maintain a single, authoritative artifact on disk.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXd-v84CzeY53x6aYAZdCU2bqTgBcQhjTxT2UMmjiVzkWpkGqoBb958xPbhJfuun2XYLktX5fq3kmnMHto-E_zUHK7cbgIbkDLJ0njcHxYo38XAmBIpsUgyFGVgUeZm2jxZ_t0-MEA?key=7W1aHaiOWzmimfVOElNCvQ)

6\. Testing and Optimization

Evaluation proceeded by a deterministic backtest that runs entirely offline and therefore produces identical results across executions. Look‑ahead bias was eliminated by lagging positions one bar when computing strategy returns; in other words, decisions recorded at time t affect returns realized at time t+1. We included a simple friction term of five basis points per transition to approximate the combined effects of spreads and slippage. Parameters were probed locally rather than exhaustively: the twenty‑day window was varied within a reasonable band, and the entry and exit thresholds were perturbed to gauge turnover and robustness. The qualitative pattern remained stable. Tighter thresholds increased trading frequency and raised the share of performance absorbed by frictions, while looser thresholds reduced activity and produced behavior closer to buy and hold. The baseline parameters strike a pedagogically useful balance between signal responsiveness and cost discipline. Warm-up periods were excluded from evaluation to avoid artifacts from incomplete rolling statistics, and all computations were vetted for numerical stability.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcXwSIpJ50dFytv4dk_CA9k7inuPMvEimyuyVSVz8MwW0ndksbDoQrA_npX5CIg3LbmyaXlwRu8YboOkgBYotB9SWA8w0o17B5TzJH395trln7jW3fcZPJ-eKkh5hwUqlkLwrCx?key=7W1aHaiOWzmimfVOElNCvQ)

7\. Automation and Scheduling

A daily task scheduled shortly after the market close can refresh the historical bars, recompute engineered features and signals, rerun the backtest, and regenerate plots and metrics for review. Network calls are wrapped in basic error handling with bounded retries to accommodate transient issues and rate limits. The repository remains private, and environment files or other secrets are excluded from version control. The workflow is idempotent: rerunning the job on the same inputs reproduces the same outputs, which simplifies auditing and comparison across dates.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXeEeR2pq69ehT-3-tLGYsDeevzBS-jVxT2BsPuAig7VWP8_LXVkCuOXiKaqgtWuTLePGAVZnvRwqVKkVUmt5pp7REBV4Ny9EZFE_EjrTZNNlq8KKWAWNMawRCHYRrjCxw-KRN3U?key=7W1aHaiOWzmimfVOElNCvQ)

8\. Paper Trading and Monitoring

Paper execution is implemented cautiously to avoid unintended order flow. The executor first inspects the latest research row to determine whether a state transition occurred. If so, it reconciles the desired state implied by the signal with the account’s current position and places at most one market-day order to achieve alignment. This reconciliation step makes the process idempotent and prevents accidental duplication of orders when cells are rerun. Subsequent monitoring of order status, fills, and positions is performed through Alpaca’s paper dashboard, which serves as an independent record of activity and outcome. Because the base strategy is long‑only and uses a single‑share sizing rule, execution risk is intentionally minimal.

9\. Results and Lessons Learned

The notebook reports performance through an equity curve comparison and a small set of standard statistics computed directly from the reconstructed series in memory. Interpreting these outputs in the context of mean‑reversion yields a consistent narrative. The approach tends to add value in range‑bound regimes, where deviations from the rolling mean are informative and reversions are frequent. It tends to underperform during extended trends, where deviations persist and premature contrarian entries are penalized. Including transaction costs is essential, as much of the apparent edge at tight thresholds can be consumed by frictions. The exercise also highlighted the importance of clean sequencing, explicit assumptions, and disciplined artifact management in empirical finance. By maintaining \`jnj\_bars.csv\` as the only on‑disk artifact and recomputing everything else from scratch, we eliminated a common failure mode in student projects, stale or inconsistent intermediate files.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfzWPVEVi9D08jUp0OkXeG2vXd6EqyyjTOrNSHMRdFTQHStnOsHftP0v9EoGaYtAu4hdPalPRMagGtN76nYyZgQs1nvAtUGvPTKqEqfOVFY1yxccio-Gj8e6kzqDpFavERNPh2v?key=7W1aHaiOWzmimfVOElNCvQ)

After backtesting, we took the above decision.

10.  Compliance and Legal Considerations

All experimentation was confined to Alpaca’s paper environment and conducted for educational purposes only. No live orders were submitted, no recommendations were offered, and no attempt was made to circumvent rate limits or usage policies. Authentication material was handled exclusively through environment variables and was never written to the repository or embedded in notebooks. Data were used in accordance with the provider’s terms, and the project refrained from any activity that would require regulatory approvals or customer‑fund protections.

11\. Conclusion

Our submission delivers a coherent pipeline from authenticated market‑data acquisition through feature engineering, signal construction, deterministic backtesting with frictions, and optional paper execution. The emphasis on reproducibility, manifest in environment‑based credentialing, careful time handling, and the single‑artifact storage of \`jnj\_bars.csv\`, ensures that an independent reviewer can replicate the results without ambiguity. Although deliberately simple, the system establishes a defensible baseline on which more sophisticated components, volatility‑aware position sizing, regime filters that suspend trading during persistent trends, or out‑of‑sample parameter selection, can be added without altering the core architecture.
