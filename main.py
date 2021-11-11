import datetime
import pathlib
import statistics
import time

import matplotlib.pyplot as plt
import pandas


def draw_predictions(merged_data, data):
    merged_data = pandas.read_csv(merged_data)
    currency = "USD"
    target_company = "Boeing Aerospace"
    companies = ["Airbus", "Lockheed Martin"]

    dates = []
    real_price_values = []
    ev_ebitda_values = []
    ev_s_values = []
    p_e_values = []
    p_bv_values = []

    for index, record in merged_data.iterrows():
        record_date = datetime.date.fromisoformat(record["Date"])
        record_date_year = record_date.year

        if record_date_year == 2021:
            record_date_year = 2020

        target_data = data[target_company]
        target_general_data = target_data["general_data"]
        target_close = record[f"Close_{target_data['symbol']}"]
        target_volume = record[f"Volume_{target_data['symbol']}"]
        target_equity = target_close * target_volume
        target_enterprise = target_equity + target_general_data[record_date_year]["Total liabilities (Debt)"]

        companies_equities = {
            c:
                record[f"Close_{data[c]['symbol']}"] * record[f"Volume_{data[c]['symbol']}"]
            for c in companies
        }
        companies_enterprise_values = {
            c:
                record[f"Close_{data[c]['symbol']}"] * record[f"Volume_{data[c]['symbol']}"] +
                data[c]["general_data"][record_date_year]["Total liabilities (Debt)"]
            for c in companies
        }

        ev_ebitda_values.append(
            statistics.mean(
                [
                    companies_enterprise_values[c] / data[c]["general_data"][record_date_year]["EBITDA"]
                    for c in companies
                ] + [target_enterprise / target_general_data[record_date_year]["EBITDA"]]
            ) * target_general_data[record_date_year]["EBITDA"] / target_volume
        )

        ev_s_values.append(
            statistics.mean(
                [
                    companies_enterprise_values[c] / data[c]["general_data"][record_date_year]["Total revenue"]
                    for c in companies
                ] + [target_enterprise / target_general_data[record_date_year]["Total revenue"]]
            ) * target_general_data[record_date_year]["Total revenue"] / target_volume
        )

        p_e_values.append(
            statistics.mean(
                [
                    companies_equities[c] / data[c]["general_data"][record_date_year]["Net income"]
                    for c in companies
                ] + [target_equity / target_general_data[record_date_year]["Net income"]]
            ) * target_general_data[record_date_year]["Net income"] / target_volume
        )

        p_bv_values.append(
            statistics.mean(
                [
                    companies_equities[c] / data[c]["general_data"][record_date_year]["Book value"]
                    for c in companies
                ] + [target_equity / target_general_data[record_date_year]["Book value"]]
            ) * target_general_data[record_date_year]["Book value"] / target_volume
        )

        dates.append(record_date)
        real_price_values.append(target_close)

    plt.plot(dates, real_price_values)
    plt.xlabel("Years")
    plt.ylabel(currency)
    plt.gcf().autofmt_xdate()
    plt.title(f"Real price in {currency}")
    plt.show()

    plt.plot(dates, ev_ebitda_values)
    plt.xlabel("Years")
    plt.ylabel("EV / EBITDA")
    plt.gcf().autofmt_xdate()
    plt.title(f"Prediction by mean(EV / EBITDA) in {currency}")
    plt.show()

    plt.plot(dates, ev_s_values)
    plt.xlabel("Years")
    plt.ylabel("EV / S")
    plt.gcf().autofmt_xdate()
    plt.title(f"Prediction by mean(EV / S) in {currency}")
    plt.show()

    plt.plot(dates, p_e_values)
    plt.xlabel("Years")
    plt.ylabel("P / E")
    plt.gcf().autofmt_xdate()
    plt.title(f"Prediction by mean(P(equity value) / Net Income) in {currency}")
    plt.show()

    plt.plot(dates, p_bv_values)
    plt.xlabel("Years")
    plt.ylabel("P / BV")
    plt.gcf().autofmt_xdate()
    plt.title(f"Prediction by mean(P(Equity value) / Book Value) in {currency}")
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
    skip_general_data_plotting = True
    skip_equity_values_calculating = True
    skip_calculating_predictions = False
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
        if skip_general_data_plotting:
            break

        draw_data(company, companies_data[company]["general_data"], line_chart_data)

    print(f"[INFO] --- Sheets drawing ended in {time.time() - start_time:.3f}s")
    start_time = time.time()

    for company in companies_data:
        if skip_equity_values_calculating:
            break

        companies_data[company]["equity"] = calculate_equity_value(
            pandas.read_csv(
                f"{base_path}/{companies_data[company]['symbol']}.csv"
            )
        )

    print(f"[INFO] --- Stock data loading ended in {time.time() - start_time:.3f}s")
    start_time = time.time()

    if not skip_calculating_predictions:
        draw_predictions("data/merged.csv", companies_data)

    print(f"[INFO] --- Multipliers calculation ended in {time.time() - start_time:.3f}s")
