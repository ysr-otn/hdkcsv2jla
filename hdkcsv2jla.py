#! /usr/bin/env python

# Copyright (c) 2024 Yoshihiro Ohtani

import argparse
from enum import IntEnum


class Index(IntEnum):
    FNAME = 0
    NAME = 1
    POSTN = 2
    ADR1 = 3
    ADR2 = 4
    ADR3 = 5
    ADR4 = 6
    TITLE = 7
    JNAME = 8
    JTITLE = 9
    CAT = 10
    HIST = 11
    ID = 12
    
class NengajoAddress:
    def __init__(self, line, year, category):
        data = line.split(',')
        
        self.fname = data[Index.FNAME]
        self.name = data[Index.NAME]
        self.postn = data[Index.POSTN]
        self.adr1 = data[Index.ADR1]
        self.adr2 = data[Index.ADR2]
        self.adr3 = conv_adr_japanese(data[Index.ADR3])
        self.adr4 = conv_adr_japanese(data[Index.ADR4]);
        self.title = data[Index.TITLE];
        self.jname = data[Index.JNAME];
        self.jtitle = data[Index.JTITLE];
        self.cat = set(data[Index.CAT].split(':'))       # ':' で分割し重複を set 型に変換
        self.hist = data[Index.HIST];
        # 指定した年が履歴に含まれているかを判定
        if (str(year) + '送') in self.hist:
            if category != None:
                # カテゴリが指定されている場合は自身のカテゴリと一致するものがあるかを
                # 集合席で判定
                if set(category.split(':')) & self.cat:
                    self.send = True
                else:
                    self.send = False
            else:
                self.send = True
        else:
            self.send = False
    

def conv_adr_japanese(address):
    adr = address.translate(str.maketrans({'0': '〇', '1': '一', '2': '二', '3': '三', '4': '四', '5': '五', 
                                           '6': '六', '7': '七', '8': '八', '9': '九', '-': 'ー'}))
    return adr.translate(str.maketrans({'A': 'Ａ', 'B': 'Ｂ', 'C': 'Ｃ', 'D': 'Ｄ', 'E': 'Ｅ', 'F': 'Ｆ', 
                                        'G': 'Ｇ', 'H': 'Ｈ', 'I': 'Ｉ', 'J': 'Ｊ', 'K': 'Ｋ', 'L': 'Ｌ', 
                                        'M': 'Ｍ', 'N': 'Ｎ', 'O': 'Ｏ', 'P': 'Ｐ', 'Q': 'Ｑ', 'R': 'Ｒ', 
                                        'S': 'Ｓ', 'T': 'Ｔ', 'U': 'Ｕ', 'V': 'Ｖ', 'W': 'Ｗ', 'X': 'Ｘ', 
                                        'Y': 'Ｙ', 'Z': 'Ｚ'}))

def conv_old_kanji2utfcode(kanji):
    return kanji.translate(str.maketrans({'﨑': '\\UTF{FA11}', '髙': '\\UTF{9AD9}'}))


class HagakiDsgnKitCSV2JLetterAddress:
    def __init__(self, input_file, output_file, year, category):
        self.input_file = input_file
        self.output_file = output_file
        self.year = year
        self.category = category
        self.adr_list = []
        
    def read_data(self):
        with open(self.input_file) as f:
            lines = f.readlines()
            
            for line in lines:
                # 年賀状住所で送信判定されたデータのみをリストに追加
                nenga_adr = NengajoAddress(line, self.year, self.category)
                if nenga_adr.send == True:
                    self.adr_list.append(nenga_adr)

    def get_element(self, element):
        return '{' + element + '}'
    
    def fname2space(self, fname):
        return '　' * len(fname)
    
    def adjust_name_space(self, name_mine, name_other):
        len_mine = len(name_mine)
        len_other = len(name_other)
        
        # 自分の名前が相手の名前より短かければスペースを入れて名前の長さを調整
        if len_mine < len_other:
            num_space_bef = len_other - len_mine
            # 基本的に名字と名前の間にスペースを入れて名前の末尾が揃うようにするが，
            # 自身: 1 文字，相手: 3 文字のように，自身の名前の長さが，挿入される
            # スペースよりも短かい場合は名前の後にスペースを 1 文字入れて見栄えを調整
            if num_space_bef > len_mine:
                num_space_aft = 1
                num_space_bef -= num_space_aft
            else:
                num_space_aft = 0
            return '　' * num_space_bef + name_mine + '　' * num_space_aft
        else:
            return name_mine
    
    def write_data(self):
        addaddress = ''
        for l in self.adr_list:
            addaddress += '\\addaddress\n'
            addaddress += '     ' + self.get_element(l.fname                   + ' ' + self.adjust_name_space(l.name, l.jname)) + self.get_element(l.title ) + '\n'
            addaddress += '     ' + self.get_element(self.fname2space(l.fname) + ' ' + self.adjust_name_space(l.jname, l.name)) + self.get_element(l.jtitle) + '\n'
            addaddress += '     ' + self.get_element(l.postn) + '\n'
            if(len(l.adr1) + len(l.adr2) + len(l.adr3) + len(l.adr4) <= 20):
                addaddress += '     ' + self.get_element(l.adr1 + ' ' + l.adr2 + ' ' + l.adr3 + ' ' + l.adr4) + '\n'
                addaddress += '     ' + self.get_element('') + '\n'
            elif len(l.adr1) + len(l.adr2) + len(l.adr3) <= 20:
                addaddress += '     ' + self.get_element(l.adr1 + ' ' + l.adr2 + ' ' + l.adr3) + '\n'
                addaddress += '     ' + self.get_element(l.adr4) + '\n'
            else:
                addaddress += '     ' + self.get_element(l.adr1 + ' ' + l.adr2) + '\n'
                addaddress += '     ' + self.get_element(l.adr3 + ' ' + l.adr4) + '\n'
            addaddress = conv_old_kanji2utfcode(addaddress)
        
        
        with open(self.output_file) as f:
            lines = f.readlines()

        state = 1
        output = ""
            
        # \addaddress 以降のコードを書き換え
        for line in lines:
            if state == 1 and line == '\\addaddress\n':
                state = 2
            elif state == 2 and line == '\\end{document}\n':
                state = 3
                    
            if state == 1:
                output += line
            elif state == 2:
                output += ''
            elif state == 3:
                output += addaddress
                output += '\n'
                output += '\\end{document}\n'
                    
        with open(self.output_file, mode = 'w') as f:
            f.write(output)
        

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', help = 'Input file of CVS file of Hagaki Design Kit.')
    parser.add_argument('-o', '--output-file', help = 'Output file of LaTeX file for class of jletteraddress.')
    parser.add_argument('-y', '--year', type = int, help = 'The Year that nengajo will be send.')
    parser.add_argument('-c', '--category', help = 'Specify the category of nengajo data with \':\' to separate the keyword if it is needed.')
    args = parser.parse_args()
    
    hdkcsv2jla = HagakiDsgnKitCSV2JLetterAddress(args.input_file, args.output_file, args.year, args.category)
    
    hdkcsv2jla.read_data()
    hdkcsv2jla.write_data()
