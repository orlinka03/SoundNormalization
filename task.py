n, w = map(int, input().split())
price_vol = [list(map(int, input().split())) for _ in range(n)]
res = 0
while w > 0:
    ind = index(max(price_vol, key = lambda x: x[0] / x[1]))
    if w - price_vol[ind][1] > 0:
        w -= price_vol[ind][1]
        res += price_vol[ind][0]
        price_vol[ind][0]
    else:

