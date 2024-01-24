from enum import Enum

class Side(Enum):
    Sell = "Sell"
    Buy = "Buy"
    
    def __str__(self) -> str:
        return self.value

class RR:
    
    def __init__(self, entry_price:float, qty:float, side:Side = Side.Buy.value, ratio:float = 2, sl:float = 0):
        
        self.entry_price = entry_price
        self.side = side
        self.qty = qty
        self.ratio = ratio 
        self.stoploss_price = sl
        
    
    def get_tp_price(self) -> float:
        entry_value = self.entry_price * self.qty
        stoploss_value = self.stoploss_price * self.qty
        
        if self.side == Side.Buy.value:
            loss = (entry_value - stoploss_value)
            target_profit = loss * self.ratio
            target_price = (target_profit + entry_value ) / self.qty
        else:
            loss = (stoploss_value - entry_value)
            target_profit = loss * self.ratio
            target_price = (entry_value - target_profit) / self.qty
        
        vDigit = str(self.stoploss_price)[::-1].find('.')
        
        return round(target_price, vDigit)
    
    
def main():
    rr = RR(entry_price=9.302, sl=9.250, side=Side.Buy.value, ratio=2.5, qty=100/9.302)
    print(f"TP Price Buy Side: {rr.get_tp_price()}")
    rr = RR(entry_price=9.002, sl=9.099, side=Side.Sell.value, ratio=2.5, qty=100/9.002)
    print(f"TP Price Sell Side: {rr.get_tp_price()}")
    
if __name__ == "__main__":
    main()