matched_tick_query = """
  select m.datetime, m.price, mv.quantity
  from quote.matched m
  join quote.futurecontractcode fc
  on date(m.datetime) = fc.datetime and fc.tickersymbol = m.tickersymbol
  join quote.matchedvolume mv
  on mv.datetime = m.datetime and mv.tickersymbol = m.tickersymbol
  where fc.futurecode = 'VN30F1M' and m.datetime between %s and %s
  order by m.datetime
"""

VNINDEX_open_close = """
  select open_price.datetime, open_price.price as open, close_price.price as close
  from quote.open open_price
  join quote.close close_price
  on date(close_price.datetime) = date(open_price.datetime) and open_price.tickersymbol = close_price.tickersymbol
  where open_price.tickersymbol = 'VNINDEX' and open_price.datetime between %s and %s
  order by open_price.datetime 
"""

daily_query = """
  select max_price.datetime, open_price.price as open, close_price.price as close, max_price.price as high, min_price.price as low
  from quote.max max_price
  join quote.futurecontractcode fc
  on date(max_price.datetime) = fc.datetime and fc.tickersymbol = max_price.tickersymbol
  join quote.min min_price
  on date(min_price.datetime) = fc.datetime and fc.tickersymbol = min_price.tickersymbol
  join quote.open open_price
  on date(open_price.datetime) = fc.datetime and fc.tickersymbol = open_price.tickersymbol
  join quote.close close_price
  on date(close_price.datetime) = fc.datetime and fc.tickersymbol = close_price.tickersymbol
  where fc.futurecode = 'VN30F1M' and max_price.datetime between %s and %s
  order by max_price.datetime 
"""