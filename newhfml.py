from pathlib import Path
import re
img_num = 0


def get_img_num(index_num, index_end):
    global img_num
    img_num += 1

    """ if index_end == 'a':
        img_num = (int(index_num)*2) - 1
    elif index_end == 'b':
        img_num = (int(index_num)*2) """
    return img_num


def update_pagination(hfml_text):
    new_hfml = ''
    match_extra = None
    text_lists = hfml_text.splitlines()
    for text in text_lists:
        if re.search(r"\[([𰵀-󴉱])?\d+[a-z]{1}\]", text):
            output = re.search(r"\[([𰵀-󴉱])?(\d+)([a-z]{1})\]", text)
            index_num = output.group(2)
            index_end = output.group(3)
            print(index_num+","+index_end)
            img_num = get_img_num(index_num, index_end)
            new_hfml += f'〔{img_num}〕' + '\n'
        else:
            text = re.sub("\[([𰵀-󴉱])?\d+[a-z]{1}\.\d+\]", "", text)
            if match_extra:
                if text:
                    new_hfml += match_extra+text + '\n'
                    match_extra = None
                else:
                    new_hfml += text + '\n'
            else:
                new_hfml += text + '\n'
    return new_hfml


if __name__ == '__main__':
    hfml_paths = list(Path(f'./output/lhasakangyur').iterdir())
    hfml_paths.sort()
    for hfml_path in hfml_paths:
        vol_num = hfml_path.stem
        hfml_text = Path(f'{hfml_path}').read_text(encoding='utf-8')
        new_hfml = update_pagination(hfml_text)
        Path(
            f'./new_hfml/lhasakangyur/{vol_num}.txt').write_text(new_hfml, encoding='utf-8')
        print(f'{vol_num} done')
        img_num = 0
