import json
import time

from pprint import pprint
from datetime import datetime, timedelta
from func_utils import format_number


def is_open_positions(client, market):
    time.sleep(0.2)

    # Get positions
    all_positions = client.private.get_positions(
        market=market,
        status="OPEN"
        )

    # Determine if open
    if len(all_positions.data["positions"]) > 0:
        return True
    else:
        return False



def check_order_status(client, order_id):
    order = client.private.get_order_by_id(order_id)
    if order.data:
        if "order" in order.data.keys():
            return order.data["order"]["status"]
    return "FAILED"


def place_market_order(client, market, side, size, price, reduce_only):
    # Get Position Id
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]

    # Get expiration time
    server_time = client.public.get_time()
    expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "")) + timedelta(seconds=70)

    # Place an order
    placed_order = client.private.create_order(
        position_id=position_id, 
        market=market,
        side=side,
        order_type="MARKET",
        post_only=False,
        size=size,
        price=price,
        limit_fee='0.015',
        expiration_epoch_seconds=expiration.timestamp(),
        time_in_force="FOK", 
        reduce_only=reduce_only
    )
    return placed_order.data



def abort_all_positions(client):
    client.private.cancel_all_orders()
    time.sleep(0.5)
    markets = client.public.get_markets().data # find tick size
    time.sleep(0.5)

    positions = client.private.get_positions(status="OPEN")
    all_positions = positions.data["positions"]

    # handle open positions
    close_orders = []
    if len(all_positions) > 0:
        for position in all_positions:
            market = position["market"]
            side = "BUY"
            if position["side"] == "LONG":
                side = "SELL"

            # get Price
            price = float(position["entryPrice"])
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            tick_size = markets["markets"][market]["tickSize"]
            accept_price = format_number(accept_price, tick_size)

            # place order to close
            order = place_market_order(
                client,
                market,
                side,
                position["sumOpen"],    
                accept_price,
                True
            )
            close_orders.append(order)
            time.sleep(0.2)

        return close_orders