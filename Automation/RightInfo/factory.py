import pandas as pd
from automation.flex_gui.RightInfo import right
from automation.flex_gui.RightInfo import utils

class RightFactory:

    @staticmethod
    def createRight(
        record: pd.Series
    ) -> right.Right:
        
        richTitle = record['VSD.TieuDe']
        rightNameSet = utils.Parser.parseRichText2RightName(richText=richTitle)

        if len(rightNameSet) == 1: # đơn quyên -> trả ra object quyền
            return right.__dict__[rightNameSet.pop()](record)

        # trường hợp loại trừ hoặc đa quyền -> return None
        return
