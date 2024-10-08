# coding: utf-8
# ==========================================================================
#   Copyright (C) since 2024 All rights reserved.
#
#   filename : 蓍草卜卦.py
#   author   : chendian / okcd00@qq.com
#   date     : 2024/08/12 04:00:24
#   desc     : 算卦第一步“三变生爻，六爻为卦”
#              (sum%4 in {6老阴,7少阳,8少阴,9老阳}, 2<<6=64, 随机数生成)
# ==========================================================================
import random


class 蓍草卜卦(object):
    八卦 = {  # 三个阴阳顺序为从下往上
        "阳阳阳": "乾",  # 乾三连【天】
        "阴阴阴": "坤",  # 坤六断【地】
        "阳阴阳": "離",  # 离中虚【火】
        "阴阳阴": "坎",  # 坎中满【水】
        "阴阳阳": "巽",  # 巽下断【风】
        "阳阴阴": "震",  # 震仰盂【雷】
        "阴阴阳": "艮",  # 艮覆碗【山】
        "阳阳阴": "兌",  # 兑上缺【泽】
    }
    六十四卦 = {
        line.strip().split('_')[-1]: line.strip().split('_') 
        for line in open('references/易经标题目录.txt', 'r', encoding='utf8')
    }
    解卦 = {}  # TODO: 每种卦象对应的解释待整理

    def __init__(self, debug=False):
        self.debug = debug
        self.蓍草 = []  # 本轮卜卦过程中，还在桌上的所有蓍草的编号 
    
    def 备蓍草(self):
        # 古时，定义天地之数为 1-10 的奇偶数
        天数 = 1 + 3 + 5 + 7 + 9
        地数 = 2 + 4 + 6 + 8 + 10
        
        # 因此，卜卦前需要准备天地之数总计 55 根蓍草
        天地之数 = 天数 + 地数  # 55
        self.蓍草 = [编号 + 1 for 编号 in range(天地之数)]

        # 大衍之数五十有五，其用四十有九
        其用之数 = 天地之数 - 6  # 49

        # 随机扔掉六根后，剩余的蓍草放在桌上，即已准备就绪
        self.蓍草 = random.choices(self.蓍草, k=其用之数)

    def 变(self, 分堆位置=-1):
        """
        变: 三变生爻中的 “变” 的过程。
                一次变的过程包括将蓍草分为天地人三种，对 4 取余 (余0时取4) 后相加可得到本次变数
        分堆位置: 即 [0, 分堆位置) 为天，[分堆位置, total) 为地
        """
        # 现在桌面上的蓍草需要被分为两堆
        if not 0 < 分堆位置 < len(self.蓍草)-1:
            分堆位置 = random.randint(1, len(self.蓍草)-1-1)
        
        # 鸿蒙初开，天地分离，桌面上的蓍草分为两堆，一堆是天，一堆是地
        天, 地 = self.蓍草[:分堆位置], self.蓍草[分堆位置:]
        
        # 大道四九，遁走其一，即从地草中拿出一根，这是人草，地草即少了一根
        地, 人 = 地[:-1], 地[-1:]

        # 天地人三堆分别对四取余，得到需要拿出多少根
        变数_天 = 4 if len(天) % 4 == 0 else len(天) % 4
        变数_地 = 4 if len(地) % 4 == 0 else len(地) % 4
        变数_人 = len(人)
        天, 地 = 天[:-变数_天], 地[:-变数_地]

        # 桌上的蓍草被取出若干根后的当前状态更新
        self.蓍草 = 天 + 地

        return [变数_天, 变数_地, 变数_人]

    def 三变生爻(self):
        self.备蓍草() 
        一变_天地人 = self.变()  # 一变：天, 地, 人，和为 5 或 9
        二变_天地人 = self.变()  # 二变：天, 地, 人，和为 4 或 8
        三变_天地人 = self.变()  # 三变：天, 地, 人，和为 ? 或 8
        爻 = {
            6: "老阴", 7: "少阳",
            8: "少阴", 9: "老阳"
        }.get(len(self.蓍草) // 4)
        return 爻, [一变_天地人, 二变_天地人, 三变_天地人]

    def 六爻为卦(self):
        六爻 = [self.三变生爻()[0] for _ in range(6)]
        本卦 = self.认卦(六爻)
        变爻 = [self.变爻(爻) for 爻 in 六爻]
        变卦 = self.认卦(变爻)
        return 本卦, 变卦

    def 变爻(self, 爻):
        if 爻[0] == '老':
            return '变' + ("阴" if 爻[1] == "阳" else "阳")
        return 爻

    def 认卦(self, 六爻):
        下, 上 = 六爻[:3], 六爻[3:]
        下卦 = self.八卦.get(''.join([爻[1] for 爻 in 下]))
        上卦 = self.八卦.get(''.join([爻[1] for 爻 in 上]))
        return f"{上卦}上{下卦}下"

    def __call__(self):
        本卦, 变卦 = self.六爻为卦()
        print("本卦：", 本卦, self.六十四卦[本卦])
        print("变卦：", 变卦, self.六十四卦[变卦])
        return 本卦, 变卦
    

if __name__ == "__main__":
    卜卦 = 蓍草卜卦()
    本卦, 变卦 = 卜卦()
    """
    示例: 
    本卦： 震上乾下 ['34', '《易經》第三十四卦', '大壯', '雷天大壯', '震上乾下']
    变卦： 震上離下 ['55', '《易經》第五十五卦', '丰', '雷火丰', '震上離下']
    """

