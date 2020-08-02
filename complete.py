import init
from init import completion_data_struct
from string import ascii_lowercase, digits, punctuation
import linecache


class AutoCompleteData:
    def __init__(self, completed_sentence, source_text, offset, score):
        self.completed_sentence = completed_sentence
        self.source_text = source_text
        self.offset = offset
        self.score = score


def fix_input(str_input):
    exclude = punctuation
    str_input = (''.join(ch for ch in str_input if ch not in exclude)).lower()
    while str_input.find("  ") != -1:
        str_input = str_input.replace("  ", " ")
    if len(str_input) > 0 and str_input[0] == " ":
        str_input.replace(" ", "", 1)
    if len(str_input) > 1 and str_input[len(str_input) - 1] == " ":
        str_input = str_input[:len(str_input) - 1]

    return str_input


def get_sentence_from_file(location):
    print(location.source_text)
    return linecache.getline(completion_data_struct.get_path(location.source_text), location.offset)


def add_and_check_dup(fixed_list, new_list, scores):
    lst = []
    if len(new_list) > 0:
        for i in range(len(new_list)):
            flag = True
            for x in fixed_list:
                if x.source_text == completion_data_struct.get_path(new_list[i].source_text) and x.offset == new_list[
                    i].offset:
                    flag = False
            if flag == True:
                lst.append(
                    AutoCompleteData(get_sentence_from_file(new_list[i]),
                                     completion_data_struct.get_path(new_list[i].source_text), new_list[i].offset,
                                     scores))
    return lst


def add_or_delete_char(str_input, start, end=-1):
    if end == -1:
        end = len(str_input)
    fixed_list = []
    characters_list = list(ascii_lowercase) + list(digits) + list(punctuation)
    for i in range(start, end):
        fixed_list += completion_data_struct.get_list_of_k_best(str_input[:i] + str_input[i + 1:])
        for ch in characters_list:
            fixed_list += completion_data_struct.get_list_of_k_best(str_input[:i + 1] + ch + str_input[i + 1:])
    return fixed_list


def swap_char(str_input, start, end=-1):
    if end == -1:
        end = len(str_input)
    fixed_list = []
    if len(str_input) <= start:
        return fixed_list
    characters_list = list(ascii_lowercase) + list(digits) + list(punctuation)
    for i in range(start, end):
        if str_input[i] != " ":
            for char in characters_list:
                fixed_list += completion_data_struct.get_list_of_k_best(str_input[:i] + char + str_input[i + 1:])
    return fixed_list


def fix_mistake(str_input, fixed_list, k_best):
    scores = len(str_input) * 2
    # 1 score
    fixed_list += list(
        sorted(add_and_check_dup(fixed_list, swap_char(str_input, 4), scores - 1), key=lambda x: x.completed_sentence))[
                  :k_best]
    if len(fixed_list) < k_best:
        # 2 scores
        buf = add_or_delete_char(str_input, 4)
        buf += swap_char(str_input, 3, 4)
        fixed_list += list(sorted(add_and_check_dup(fixed_list, buf, scores - 2)[:k_best - len(fixed_list)],
                                  key=lambda x: x.completed_sentence))[:k_best - len(fixed_list)]
        if len(fixed_list) < k_best:
            # 3scores
            fixed_list += list(sorted(add_and_check_dup(fixed_list, swap_char(str_input, 2, 3), scores - 3),
                                      key=lambda x: x.completed_sentence))[:k_best - len(fixed_list)]
            if len(fixed_list) < k_best:
                # 4scores
                buf = swap_char(str_input, 1, 2)
                buf += add_or_delete_char(str_input, 3, 4)
                fixed_list += list(sorted(add_and_check_dup(fixed_list, buf, scores - 4)[:k_best - len(fixed_list)],
                                          key=lambda x: x.completed_sentence))[:k_best - len(fixed_list)]
                if len(fixed_list) < k_best:
                    # k_bestscores
                    fixed_list += list(
                        sorted(add_and_check_dup(fixed_list, swap_char(str_input, 0, 1), scores - k_best),
                               key=lambda x: x.completed_sentence))[:k_best - len(fixed_list)]
                    if len(fixed_list) < k_best:
                        # 6scores
                        fixed_list += list(
                            sorted(add_and_check_dup(fixed_list, add_or_delete_char(str_input, 2, 3), scores - 6),
                                   key=lambda x: x.completed_sentence))[:k_best - len(fixed_list)]
                        if len(fixed_list) < k_best:
                            # 8scores
                            fixed_list += list(
                                sorted(add_and_check_dup(fixed_list, add_or_delete_char(str_input, 1, 2), scores - 8),
                                       key=lambda x: x.completed_sentence))[:k_best - len(fixed_list)]
                            if len(fixed_list) < k_best:
                                # 10scores
                                fixed_list += list(sorted(
                                    add_and_check_dup(fixed_list, add_or_delete_char(str_input, 1, 2), scores - 10),
                                    key=lambda x: x.completed_sentence))[:k_best - len(fixed_list)]

    return fixed_list


def get_best_k_completions(input_to_search):
    input_to_search = fix_input(input_to_search)
    try:
        if len(completion_data_struct.substrings_dict[input_to_search]) < 5:
            raise Exception
        return list(sorted(
            add_and_check_dup([], completion_data_struct.get_list_of_k_best(input_to_search), len(input_to_search) * 2),
            key=lambda x: x.completed_sentence))
    except Exception:
        ls = list(sorted(
            add_and_check_dup([], completion_data_struct.get_list_of_k_best(input_to_search), len(input_to_search) * 2),
            key=lambda x: x.completed_sentence))
        return fix_mistake(input_to_search, ls, 5)
