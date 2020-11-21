from datetime import datetime

import mplfinance as mpf
from tabulate import tabulate

from app.config.basecontainer import BaseContainer


class ReportPublisher(BaseContainer):

    def generate_report(self, market, dt_since, dt_to):
        alerts_df = self.lookup_object("alert_data_store").fetch_data()
        market_data_df = self.lookup_object("market_data_store").fetch_data(market, dt_since, dt_to)
        order_data_df = self.lookup_object("order_data_store").fetch_data()

        self._print_table("CryptoRider :: Summary Report",
                          self._generate_summary(market, dt_since, dt_to, market_data_df, order_data_df))
        self._print_table("Trades", self._generate_orders_list(market, order_data_df))
        self._print_table("Alerts", self._generate_alerts_list(market, alerts_df))

    def _print_table(self, title, data):
        print("===== {} =====".format(title))
        print(tabulate(data, headers="firstrow", tablefmt="grid"))

    def _generate_summary(self, market, dt_from, dt_to, market_data_df, order_data_df):
        open_at_start, close_at_end, buy_and_hold_profit_loss, buy_hold_pct_change = self._buy_and_hold_change(
            market_data_df)
        total_profit_loss = (order_data_df["sell_price"] - order_data_df["buy_price"]).sum()
        return [
            ["Metric", "Value"],
            ["Market", market],
            ["Start at", dt_from],
            ["End at", dt_to],
            ["Total trades", len(order_data_df)],
            ["Total P/L", "{:.2f}".format(total_profit_loss)],
            # ["Total P/L %", "{:.2f}".format()],
            ["Open at start", open_at_start],
            ["Close at end", "{:.2f}".format(close_at_end)],
            ["Buy and Hold P/L", "{:.2f}".format(buy_and_hold_profit_loss)],
            ["Buy and Hold P/L %", "{:.2f} %".format(buy_hold_pct_change)],
        ]

    def _generate_orders_list(self, market, order_data_df):
        orders_list = [
            ["Market", "P/L Percent", "P/L", "Buy Date", "Sell Date", "Buy Price", "Sell Price", "Trade Duration",
             "Sell Reason"]
        ]
        for _, order in order_data_df.iterrows():
            buy_price = order.get("buy_price")
            sell_price = order.get("sell_price")
            profit_percent = (sell_price - buy_price) / buy_price * 100
            profit = sell_price - buy_price
            buy_dt = datetime.fromtimestamp(order.get("buy_timestamp") / 1000)
            sell_dt = datetime.fromtimestamp(order.get("sell_timestamp") / 1000)
            trade_duration = sell_dt - buy_dt

            orders_list.append([
                market,
                "{:.2f} %".format(profit_percent),
                profit,
                buy_dt,
                sell_dt,
                "{:.2f}".format(buy_price),
                "{:.2f}".format(sell_price),
                trade_duration,
                order.get("sell_reason")
            ])
        return orders_list

    def _generate_alerts_list(self, market, alerts_df):
        alerts_list = [
            ["Market", "Strategy", "Alert Date", "Alert Type", "Close Price", "Message"]
        ]
        for _, alert in alerts_df.iterrows():
            alerts_list.append([
                market,
                alert.get("strategy"),
                datetime.fromtimestamp(alert.get("timestamp") / 1000),
                alert.get("alert_type"),
                alert.get("close_price"),
                alert.get("message")
            ])
        return alerts_list

    def _plot_chart(self, market_data, expanded_market_data, dt_from, dt_to):
        close_50_sma = expanded_market_data["close"].rolling(50).mean()
        close_100_sma = expanded_market_data["close"].rolling(100).mean()
        additional_plts = [
            mpf.make_addplot(close_50_sma[dt_from:dt_to], linestyle="dashed"),
            mpf.make_addplot(close_100_sma[dt_from:dt_to], linestyle="dashed")
        ]
        mpf.plot(
            market_data,
            type="line",
            volume=True,
            # savefig=save,
            addplot=additional_plts,
            style="yahoo",
        )

    def _buy_and_hold_change(self, df):
        open_at_start = df["open"].iloc[0]
        close_at_end = df["close"].iloc[-1]
        profit_loss = close_at_end - open_at_start
        return open_at_start, close_at_end, profit_loss, profit_loss / open_at_start * 100
