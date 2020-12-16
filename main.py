import re
from pprint import pprint
import csv


def fix_fio(row: list):
    fio = f'{row[0].strip()} {row[1].strip()} {row[2].strip()}'.split()
    # add extra lines in case if one or more entries was empty (since we don't know exact qty of non-empty FIO entries)
    if len(fio) < 3:
        fio.extend(['', '', ''])
    row[0], row[1] = map(str, fio[:2])
    # the rest will be glued in third entry (so we will not lose the rest of the words after the third one)
    row[2] = ' '.join(fio[2:]).strip()
    # cut redundant items
    return row[:7]


def fix_tel(row: list):
    pattern = re.compile(r'([+][7]|8)?\s*-*\s*\(*\s*(\d{1,5})\s*\)*\s*-*\s*(\d{1,3})\s*-*\s*(\d{1,3})\s*-*\s*(\d{1,3})'
                         r'\s*\(?\s*[д.|доб.]*\s*(\d*)\s*\)?\s*')
    result = re.match(pattern, row[5])
    if result:
        tel = ''.join(result.groups()[1:5])
        tel = '{}({}){}-{}-{}{}'.format('+7', tel[:3], tel[3:6], tel[6:8], tel[8:],
                                        f' доб.{result.group(6)}' if result.group(6) else '')
        row[5] = tel
    return row


def smart_append(contacts_list: list, row: list) -> list:
    """
    Here we check if duplicate of same people exists and merge info
    Duplicate info if same firstname + lastname, other info might be empty or the same
    """
    is_merged = False
    for item in contacts_list:
        lastname_match = item[0] == row[0]
        firstname_match = item[1] == row[1]
        surname_match = item[2] == row[2] or not item[2] or not row[2]
        organization_match = item[3] == row[3] or not item[3] or not row[3]
        position_match = item[4] == row[4] or not item[4] or not row[4]
        phone_match = item[5] == row[5] or not item[5] or not row[5]
        email_match = item[6] == row[6] or not item[6] or not row[6]
        merge_needed = lastname_match and firstname_match and surname_match and organization_match and position_match \
                       and phone_match and email_match
        if merge_needed:
            item[2] = row[2] if row[2] else item[2]
            item[3] = row[3] if row[3] else item[3]
            item[4] = row[4] if row[4] else item[4]
            item[5] = row[5] if row[5] else item[5]
            item[6] = row[6] if row[6] else item[6]
            is_merged = True
    if not is_merged:
        contacts_list.append(row)
    return contacts_list


def normalize_csv(contacts_list: list):
    contacts_list_fixed = []
    for row in contacts_list:
        tmp = fix_fio(row)
        tmp = fix_tel(tmp)
        contacts_list_fixed = smart_append(contacts_list_fixed, tmp)
    return contacts_list_fixed


if __name__ == '__main__':
    with open("phonebook_raw.csv", encoding='utf8') as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)

    contacts_list_fixed = normalize_csv(contacts_list)

    pprint(contacts_list_fixed)
    with open("phonebook.csv", "w", encoding='utf8', newline='') as f:
        datawriter = csv.writer(f, delimiter=',')
        datawriter.writerows(contacts_list_fixed)
