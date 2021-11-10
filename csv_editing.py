import re

import pandas as pd


def merge(f1, f2, f3):
    f1_name = re.findall(r"/(.*)\.csv", f1)[0]
    f2_name = re.findall(r"/(.*)\.csv", f2)[0]
    f3_name = re.findall(r"/(.*)\.csv", f3)[0]
    f1 = pd.read_csv(f1)
    f2 = pd.read_csv(f2)
    f3 = pd.read_csv(f3)

    output = pd.merge(f1, f2, on="Date", how="inner")
    output = output[["Close_x", "Date", "Close_y", "Volume_x", "Volume_y"]]
    output = output.rename(columns={
        "Close_x": f"Close_{f1_name}", "Close_y": f"Close_{f2_name}",
        "Volume_x": f"Volume_{f1_name}", "Volume_y": f"Volume_{f2_name}",
    })

    output = pd.merge(output, f3, on="Date", how="inner")
    output = output[
        [f"Close_{f1_name}", f"Close_{f2_name}", "Close", "Date", "Volume", f"Volume_{f1_name}", f"Volume_{f2_name}"]
    ]
    return output.rename(columns={"Close": f"Close_{f3_name}", "Volume": f"Volume_{f3_name}"})


if __name__ == '__main__':
    merge('data/AIR.PA.csv', 'data/BA.csv', 'data/LMT.csv') \
        .to_csv("data/merged.csv", sep=',', encoding='utf-8', index=False)
