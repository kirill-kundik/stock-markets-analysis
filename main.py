import datetime
import pathlib
import time

import matplotlib.pyplot as plt
import pandas


def draw_multipliers(name, data):
    currency = "USD in millions"

    dates = []
    ev_ebitda_values = []
    ev_s_values = []
    p_e_values = []
    p_bv_values = []

    for record in data["equity"]:
        record_date = datetime.date.fromisoformat(record["Date"])

        if record_date.year == 2021:
            continue

        year_data = data["general_data"][record_date.year]
        enterprise_value = record["Equity"] + year_data["Total liabilities (Debt)"]

        ev_ebitda_values.append(enterprise_value / year_data["EBITDA"])
        ev_s_values.append(enterprise_value / year_data["Total revenue"])
        p_e_values.append(record["Equity"] / year_data["Net income"])
        p_bv_values.append(record["Equity"] / year_data["Book value"])
        dates.append(record_date)

    plt.plot(dates, ev_ebitda_values)
    plt.xlabel("Years")
    plt.ylabel("EV / EBITDA")
    plt.gcf().autofmt_xdate()
    plt.title(f"{name} EV / EBITDA ({currency})")
    plt.show()

    plt.plot(dates, ev_s_values)
    plt.xlabel("Years")
    plt.ylabel("EV / S")
    plt.gcf().autofmt_xdate()
    plt.title(f"{name} EV / S ({currency})")
    plt.show()

    plt.plot(dates, p_e_values)
    plt.xlabel("Years")
    plt.ylabel("P / E")
    plt.gcf().autofmt_xdate()
    plt.title(f"{name} P(equity value) / Net Income ({currency})")
    plt.show()

    plt.plot(dates, p_bv_values)
    plt.xlabel("Years")
    plt.ylabel("P / BV")
    plt.gcf().autofmt_xdate()
    plt.title(f"{name} P(Equity value) / Book Value ({currency})")
    plt.show()


def calculate_equity_value(data):
    data["Equity"] = data["Volume"] * data["Close"]
    return data[["Date", "Equity"]].to_dict('records')


def extract_sheet_data(sheet):
    data = {}
    available_data = sheet.index.values

    for year in sheet:
        year = int(year)
        data[year] = dict(zip(available_data, sheet[year]))

    return data


def draw_data(name, data, columns):
    currency = "USD in millions"

    for column in columns:
        years = []
        values = []

        for year in data:
            years.append(year)
            values.append(data[year][column])

        plt.plot(years, values)
        plt.xlabel("Years")
        plt.ylabel(column)
        plt.title(f"{name} {column} ({currency})")
        plt.show()


if __name__ == "__main__":
    base_path = pathlib.Path(__file__).parent / "data"
    path = base_path / "Boeing Aerospace Company report.xlsx"
    companies_symbols = {"Boeing Aerospace": "BA", "Airbus": "AIR.PA", "Lockheed Martin": "LMT"}
    df = pandas.read_excel(path, sheet_name=None, index_col=0)
    companies_data = {}
    line_chart_data = [
        "Total revenue", "Operating profit", "Deprecation and amortisation", "EBITDA",
        "Net income", "Total liabilities (Debt)", "Total assets", "Book value",
    ]

    start_time = time.time()

    sheet_name: str
    for sheet_name in df:
        companies_data[sheet_name] = {
            "general_data": extract_sheet_data(df[sheet_name]),
            "symbol": companies_symbols[sheet_name]
        }

    print(f"[INFO] --- Sheets loading ended in {time.time() - start_time:.3f}s")
    start_time = time.time()

    for company in companies_data:
        draw_data(company, companies_data[company]["general_data"], line_chart_data)

    print(f"[INFO] --- Sheets drawing ended in {time.time() - start_time:.3f}s")
    start_time = time.time()

    for company in companies_data:
        companies_data[company]["equity"] = calculate_equity_value(
            pandas.read_csv(
                f"{base_path}/{companies_data[company]['symbol']}.csv"
            )
        )

    print(f"[INFO] --- Stock data loading ended in {time.time() - start_time:.3f}s")
    start_time = time.time()

    for company in companies_data:
        draw_multipliers(company, companies_data[company])

    print(f"[INFO] --- Multipliers calculation ended in {time.time() - start_time:.3f}s")
