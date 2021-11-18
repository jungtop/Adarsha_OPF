import re
import shutil
import os
import requests
from bs4 import BeautifulSoup

base = 'https://adarsha.dharma-treasure.org/'
workBase = 'https://adarsha.dharma-treasure.org/kdbs/{name}'
apiBase = 'https://adarsha.dharma-treasure.org/api/kdbs/{name}/pbs?size=10&lastId={pbs}'


def findMissing(counters, formatedLines, fileName):
    page = formatedLines[0][1:-1]
    if page == '1a':
        counters[1] = 1
    elif page == '1b':
        counters[1] = 2
    number = int(page[:-1]) * 2
    if page[-1] == 'a':
        number -= 1
    if page[-1] == 'c':
        counters[1] -= 1
    if page[-1] == 'd':
        counters[1] -= 1
    counters[0] = number
    if counters[0] != counters[1]:
        with open(f'{outdir}report.txt', 'a+', encoding='utf-8') as file:
            file.writelines(f'missing: {fileName} {page} + 1\n')
        counters[1] -= 1
    counters[1] += 1
    return counters


def formatLines(lines):
    formatedLines = []
    volume = lines.pop(0)
    formatedLines.append(volume)
    page = lines.pop(0)
    side = lines.pop(0)
    formatedLines.append(f'[{page}{side}]')
    i = 1
    for line in lines:
        formatedLines.append(f'[{page}{side}.{i}]{line}')
        i += 1
    return formatedLines


def extractLines(page):
    # [volume, page, side, l1, ..., l7]
    lines = []
    volume = int(re.search('"pbId":"(\d+?)-', page).group(1))
    lines.append(volume)
    pageNum = int(re.search('"pbId":"\d+?-\d+?-(\d+?)[a-z]', page).group(1))
    lines.append(pageNum)
    side = re.search('"pbId":"\d+?-\d+?-\d+?([a-z])', page).group(1)
    lines.append(side)
    text = re.search('"text":"(.+?)"', page).group(1)
    text = re.sub('\s+', ' ', text)
    ls = list(filter(None, text.split('\\n')))
    lines += ls
    return lines


def item_generator(things):
    # ...because writelines() is such a tease
    for item in things:
        yield item
        yield '\n'


def writePage(page):
    lines = extractLines(page)
    formatedLines = formatLines(lines)

    fileName = "{:0>3d}".format(formatedLines.pop(0))

    findMissing(counters, formatedLines, fileName)

    with open(f'{outdir}{fileName}.txt', 'a+', encoding='utf-8') as file:
        file.writelines(item_generator(formatedLines))


def testUrl(work, pbs):
    # check if url has text
    url = apiBase.format(name=work[0], pbs=pbs)
    response = requests.get(url)
    if response.text == '{"total":0,"data":[]}':
        # print(response.text)
        status = False
    else:
        status = True
    return status


def normalizeUni(strNFC):
    strNFC = strNFC.replace("\u0F00", "\u0F68\u0F7C\u0F7E")  # ༀ
    strNFC = strNFC.replace("\u0F43", "\u0F42\u0FB7")  # གྷ
    strNFC = strNFC.replace("\u0F48", "\u0F47\u0FB7")  # ཈
    strNFC = strNFC.replace("\u0F4D", "\u0F4C\u0FB7")  # ཌྷ
    strNFC = strNFC.replace("\u0F52", "\u0F51\u0FB7")  # དྷ
    strNFC = strNFC.replace("\u0F57", "\u0F56\u0FB7")  # བྷ
    strNFC = strNFC.replace("\u0F5C", "\u0F5B\u0FB7")  # ཛྷ
    strNFC = strNFC.replace("\u0F69", "\u0F40\u0FB5")  # ཀྵ
    strNFC = strNFC.replace("\u0F73", "\u0F71\u0F72")  # ཱི
    strNFC = strNFC.replace("\u0F75", "\u0F71\u0F74")  # ཱུ
    strNFC = strNFC.replace("\u0F76", "\u0FB2\u0F80")  # ྲྀ
    strNFC = strNFC.replace("\u0F77", "\u0FB2\u0F71\u0F80")  # ཷ
    strNFC = strNFC.replace("\u0F78", "\u0FB3\u0F80")  # ླྀ
    strNFC = strNFC.replace("\u0F79", "\u0FB3\u0F71\u0F80")  # ཹ
    strNFC = strNFC.replace("\u0F81", "\u0F71\u0F80")  # ཱྀ
    strNFC = strNFC.replace("\u0F93", "\u0F92\u0FB7")  # ྒྷ
    strNFC = strNFC.replace("\u0F9D", "\u0F9C\u0FB7")  # ྜྷ
    strNFC = strNFC.replace("\u0FA2", "\u0FA1\u0FB7")  # ྡྷ
    strNFC = strNFC.replace("\u0FA7", "\u0FA6\u0FB7")  # ྦྷ
    strNFC = strNFC.replace("\u0FAC", "\u0FAB\u0FB7")  # ྫྷ
    strNFC = strNFC.replace("\u0FB9", "\u0F90\u0FB5")  # ྐྵ
    return strNFC


def getwork(work):
    i = work[1]
    while testUrl(work, i):
        url = apiBase.format(name=work[0], pbs=i)
        response = requests.get(url)
        text = response.text.replace("},{", "},\n{")
        text = normalizeUni(text)
        pages = text.splitlines()
        for page in pages:
            writePage(page)
        print(f'pbs: {i}')
        i += 10


if __name__ == '__main__':

    # [work, starting pbs]2308063
    #work = ['degetengyur', 2843237]
    #work = ['degekangyur', 2977725]
    work = ['lhasakangyur', 2747738]
    #work = ['jiangkangyur', 2561410]

    counters = [0, 0]

    outdir = f'output/{work[0]}/'
    if os.path.exists(outdir):
        shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir)

    getwork(work)

    print('Done!')
