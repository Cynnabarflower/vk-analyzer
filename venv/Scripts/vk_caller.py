GOODS1 = pd.DataFrame({"назв":['яблоки', 'бананы', 'сыр'],
                       "тг":['фрукты', 'фрукты', 'молочные продукты'],
                       "код_пост":['10', '20', '10'],
                       "цена":[100, 50, 500]})

GOODS2 = pd.DataFrame({"назв":['виноград', 'кефир', 'ананасы'],
                       "тг":['фрукты', 'молочные продукты', 'фрукты'],
                       "код_пост":['10', '10', '20'],
                       "цена":[200, 70, 150]})

SUPL = pd.DataFrame({"код_пост":['10', '20'],
                       "пост":['Рога и Копыта', 'Парнас'],
                       "область":['Тверская', 'Воронежская'],
                       "наценка":[15, 10]})

import pandas as pd

purchases = pd.DataFrame(
{
'client' : ['Alice', 'Bob', 'Alice', 'Claudia'],
'item' : ['sweets', 'chock', 'chock', 'juice'],
'quantity' : [4, 5, 3, 2]
}
)

goods = pd.DataFrame(
{
'good': ['sweets', 'chock', 'juice', 'lemons'],
'price': [15, 7, 8, 3]
}
)

discounts = pd.DataFrame(
{
'client' : ['Alice', 'Bob', 'Patricia'],
'discount' : [10, 5, 15]
}
)

def totals(purchases, goods, discounts):
	d = pd.merge(purchases, goods, left_on = 'item', right_on = 'good', how = 'left')
	d = pd.merge(d, discounts, on = 'client', how = 'left')
	d.set_index('item')
	d = d.fillna(0)
	d['sum'] = d['quantity'] * d['price'] * (100 - d['discount'])/100.0
	d = d.fillna(0)
	d = pd.pivot_table(d, index = ['client'], columns = ['good'], values='sum')
	d = d.reindex(goods['good'], axis='columns')
	d = d.fillna(0)
	return d

totals(purchases, goods, discounts)