from collections import defaultdict
import string
import os
import linecache

class LocationOfSentence:
    def __init__(self, source_text, offset):
        self.source_text = source_text
        self.offset = offset

class AutoCompleteIndex:
    def __init__(self, main_root):
        self.main_root = main_root
        self.data_list = []
        self.substrings_dict = defaultdict(list)
        self.paths_list = []
        self.init_data_structure_from_files()

    def get_list_of_k_best(self, substr):
        return [self.data_list[i] for i in self.substrings_dict[substr]]

    def get_path(self, index):
        return self.paths_list[index]

    def get_sentence_from_file(self, location):
        return linecache.getline(self.get_path(location.source_text), location.offset)

    def set_k_best(self, substr, index):
        length = len(self.substrings_dict[substr])
        current_sentence = self.get_sentence_from_file(self.data_list[index])
        if length == 0:
            self.substrings_dict[substr].append(index)
        elif length < 5:
            if self.get_sentence_from_file(self.get_list_of_k_best(substr)[length - 1]) < current_sentence:
                self.substrings_dict[substr].insert(length - 1, index)
            else:
                self.substrings_dict[substr].append(index)
        else:
            if self.get_sentence_from_file(self.get_list_of_k_best(substr)[length - 1]) < current_sentence:
                self.substrings_dict[substr].pop(4)
                min_ = index
                min_index = length - 1
                min_sentence = current_sentence
                for i in range(4):
                    sentence = self.get_sentence_from_file(self.get_list_of_k_best(substr)[i])
                    if sentence < min_sentence:
                        min_ = self.substrings_dict[substr][i]
                        min_sentence = sentence
                        min_index = i
                self.substrings_dict[substr].append(min_)
                if min_ != index:
                    self.substrings_dict[substr][min_index] = index

    @staticmethod
    def fix_substrs(substrings):
        exclude = string.punctuation
        for i in range(len(substrings)):
            substrings[i] = (''.join(ch for ch in substrings[i] if ch not in exclude)).lower()
            while substrings[i].find("  ") != -1:
                substrings[i] = substrings[i].replace("  ", " ")
            if len(substrings[i]) > 0 and substrings[i][0] == " ":
                substrings[i].replace(" ", "", 1)
            if len(substrings[i]) > 1 and substrings[i][len(substrings[i]) - 1] == " ":
                substrings[i] = substrings[i][:len(substrings[i]) - 1]

        return set(substrings)

    def init_data_structure_from_files(self):
        index = 0
        for root, dirs, files in os.walk(self.main_root):
            for i, file in enumerate(files):
                path = os.path.join(root, file)
                print(path)
                self.paths_list.append(path)

                # insert single file to the data structure line by line
                with open(path, 'r', encoding="utf8") as the_file:
                    for line, query in enumerate(the_file):
                        if query != "":
                            self.data_list.append(LocationOfSentence(i, line + 1))
                            substrings = [query[i:j] for i in range(len(query)) for j in range(i + 1, len(query) + 1) if
                                              j - i <= 10]
                            substrings = self.fix_substrs(substrings)
                            for substr in substrings:
                                self.set_k_best(substr, index)
                            index += 1



completion_data_struct = AutoCompleteIndex("dir")

