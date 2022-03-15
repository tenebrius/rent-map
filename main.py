import pandas as pd
import json

from loc_db import load_loc_db, getCoords

files = [
    'lanjia.json',
    'scrapper_58_db.json',
]


def prepare():
    nItems = []
    for file in files:
        f = open(file, 'r', encoding="utf-8")
        nItems = nItems + json.load(f)


    prices = []
    locs = []
    areas = []
    rates = []
    for item in nItems:
        print(item)
        area = int(round(float(item.pop(0))))
        areas.append(area)
        loc = item.pop(0)
        locs.append(loc)
        price = int(item.pop(0))
        prices.append(price)
        rates.append(round(price / area))
    df = pd.DataFrame({"loc": locs,
                       "price": prices,
                       "area": areas,
                       "rate": rates,
                       })
    len_before_drop = len(df)
    df.drop_duplicates(inplace=True)
    len_after_drop = len(df)

    print("dropped duplicates: ", len_before_drop - len_after_drop)
    print("final count: ", len(df))
    df.to_json("cleaned.json", force_ascii=False)


def median():
    ## remove empty datas

    df = pd.read_json('cleaned.json')
    groupby = df.groupby('loc')
    medians = groupby.agg(median=('rate', 'median'), size=('rate', 'size'))
    medians.to_json("medians.json")
    print("total groups:", len(medians))


def geo():
    df = pd.read_json('medians.json')

    load_loc_db()
    lat = []
    lng = []
    failures = []

    df = df.reset_index()

    for index, row in df.iterrows():
        try:
            coord = getCoords(row["index"] + "深圳市", offlineOnly=False)
            lt = coord["lat"]
            ln = coord["lng"]
            lng.append(lt)
            lat.append(ln)
        except Exception as e:
            raise e
            failures.append([i, e])
            lat.append(pd.NA)
            lng.append(pd.NA)
    if len(failures) > 0:
        print(failures)
    df['lng'] = lng
    df['lat'] = lat
    print("geo done")
    df.to_json("geo.json")


def final():
    df = pd.read_json('geo.json')
    df = df[(df["median"] < 250)]
    print(df.head())
    df.to_json("with_size.json", orient="records", force_ascii=False)
    from matplotlib import font_manager
    # plt.rcParams.update({'font.size': 18})

    # df.to_excel("locs123.xlsx")
    # medians.to_excel("medians123.xlsx")
    # import plotly.graph_objects as go
    # scl = [0, "rgb(150,0,90)"], [0.125, "rgb(0, 0, 200)"], [0.25, "rgb(0, 25, 255)"], \
    #       [0.375, "rgb(0, 152, 255)"], [0.5, "rgb(44, 255, 150)"], [0.625, "rgb(151, 255, 0)"], \
    #       [0.75, "rgb(255, 234, 0)"], [0.875, "rgb(255, 111, 0)"], [1, "rgb(255, 0, 0)"]
    #
    # fig = go.Figure(data=go.Scattergeo(
    #     lat=df['Lat'],
    #     lon=df['Lon'],
    #     text=df['rate'].astype(str) + ' 元/m2',
    #     marker=dict(
    #         color=df['rate'],
    #         colorscale=scl,
    #         reversescale=True,
    #         size=10,
    #         colorbar=dict(
    #             titleside="right",
    #             outlinecolor="rgba(68, 68, 68, 0)",
    #             ticks="outside",
    #             showticksuffix="last",
    #             dtick=0.1
    #         )
    #     )
    # ))
    #
    # fig.update_layout(
    #     geo_scope='asia',
    #     title='Shenzhen Rent Price per meter square',
    # )
    # fig.show()


if __name__ == '__main__':
    # prepare()
    median()
    geo()
    final()
