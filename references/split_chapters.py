# coding: utf-8
# ==========================================================================
#   Copyright (C) since 2024 All rights reserved.
#
#   filename : split_chapters.py
#   author   : chendian / okcd00@qq.com
#   date     : 2024/08/12 03:05:39
#   desc     : 
#              
# ==========================================================================
import sys
sys.path.append('./')

import re
from utils.number_utils import chinese_number_to_digit


if __name__ == "__main__":
    chapters = ''.join(open('references/zhouyi.txt', 'r', encoding='utf8', errors='replace').readlines()).split('\n \n')
    for i, (title, contents) in enumerate(zip(chapters[::2], chapters[1::2])):
        title = title.strip().replace(' ', '')
        contents = contents.strip()
        
        if not title.startswith('《易經》'):
            with open(f'references/{title}', 'w', encoding='utf8') as f:
                # f.write(title + '\n \n')
                f.write(contents)
            continue
        
        rank = re.findall('第(.*)卦', title)[0]
        rank_number, title = f"{chinese_number_to_digit(rank):02d}", title[4+2+len(rank):]
        position, title = title[-4:], title[:-4]
        if len(title) == 6:
            name, parts = title[:2], title[2:]
        elif len(title) == 4:
            name, parts = title[:1], title[1:]
        else:
            raise ValueError(title)

        title = f"{rank_number}_《易經》第{rank}卦_{name}_{parts}_{position}"
        with open(f'references/{title}', 'w', encoding='utf8') as f:
            # f.write(title + '\n \n')
            f.write(contents)
