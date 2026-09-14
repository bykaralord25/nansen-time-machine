import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'data' / 'scenarios' / 'production.json'


def n(v, d=0.0):
    try:
        return float(v) if v is not None else d
    except Exception:
        return d


def candles(r):
    return [x for x in (r.get('data', []) if isinstance(r, dict) else []) if isinstance(x, dict) and x.get('close') is not None]


def last_close(r):
    c = candles(r)
    return n(c[-1]['close'], None) if c else None


def main():
    groups = defaultdict(dict)
    files = list(RAW.glob('*.json'))
    if not files:
        raise SystemExit('No files found in data/raw')

    for p in files:
        obj = json.loads(p.read_text(encoding='utf-8'))
        t = obj['task']
        groups[(t['symbol'], t['snapshot_date'])][t['kind']] = obj['response']

    out = []
    skipped = 0
    for (symbol, day), parts in sorted(groups.items()):
        need = {'historical_flow_summary','ohlcv_context','ohlcv_reveal_7d','ohlcv_reveal_30d'}
        if not need.issubset(parts):
            skipped += 1
            continue

        flowdata = parts['historical_flow_summary'].get('data', [])
        flow = flowdata[0] if flowdata else {}
        entry = last_close(parts['ohlcv_context'])
        c7 = candles(parts['ohlcv_reveal_7d'])
        one = n(c7[1]['close'], None) if len(c7) > 1 else (n(c7[0]['close'], None) if c7 else None)
        seven = last_close(parts['ohlcv_reveal_7d'])
        thirty = last_close(parts['ohlcv_reveal_30d'])
        if not all(x is not None and x > 0 for x in (entry, one, seven, thirty)):
            skipped += 1
            continue

        smart = n(flow.get('smart_trader_net_flow_usd'))
        whale = n(flow.get('whale_net_flow_usd'))
        top = n(flow.get('top_pnl_net_flow_usd'))
        exch = n(flow.get('exchange_net_flow_usd'))
        num = .35*smart + .25*whale + .25*top - .15*exch
        den = .35*abs(smart) + .25*abs(whale) + .25*abs(top) + .15*abs(exch)
        score = max(0, min(100, round(50 + 50*(num/den if den else 0))))
        if score >= 70: label = 'Strong Accumulation'
        elif score >= 57: label = 'Accumulation Bias'
        elif score <= 30: label = 'Distribution Risk'
        elif score <= 43: label = 'Distribution Bias'
        else: label = 'Mixed / Neutral'

        ret7 = (seven/entry - 1)*100
        out.append({
            'id': f'{symbol.lower()}-{day}', 'symbol': symbol, 'name': symbol,
            'chain': 'ethereum', 'date': day, 'entry_price': round(entry,8),
            'future': {'1d':round(one,8),'7d':round(seven,8),'30d':round(thirty,8)},
            'smart_money_netflow': round(smart,2),
            'smart_money_wallets': int(n(flow.get('smart_trader_wallet_count'),0)),
            'whale_netflow': round(whale,2), 'exchange_netflow': round(exch,2),
            'top_pnl_netflow': round(top,2), 'signal': label, 'signal_score': score,
            'answer_note': f'Point-in-time Nansen snapshot. Composite signal: {label} ({score}/100). Over the next 7 days, {symbol} moved {ret7:+.2f}%. Future prices are revealed only after the decision.'
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'Cached responses read: {len(files)}')
    print(f'Production scenarios built: {len(out)}')
    print(f'Skipped: {skipped}')
    print(f'Wrote: {OUT}')
    print('No API requests were made. Credits used: 0')

if __name__ == '__main__':
    main()
