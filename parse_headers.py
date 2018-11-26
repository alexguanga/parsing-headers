import os
import json
from collections import defaultdict, OrderedDict
from reportlab.pdfgen import canvas
import string

class SearchInformation:

    def get_dirs(self):
        # Get all the possible path given the current directory
        paths = self.get_all_paths()
        return self.rm_dirs(paths)

    def get_all_paths(self):
        ''' Returns all the possible path given the current directory '''
        current_path = os.getcwd()
        paths = [paths for paths, _, _, in os.walk(current_path)]
        return paths

    def rm_dirs(self, paths_in_dir):
        '''Will remove hidden directories that will be included in the courseoutline document'''

        filtered_list = []
        list_to_filter = ['ipynb_checkpoints', 'git', 'Assignments', 'PDFs', 'images']

        # Skipping the first entry since we do not want to use the path itself
        paths_in_dir = iter(paths_in_dir)
        next(paths_in_dir)
        d = defaultdict(dict)

        for path in paths_in_dir:

            if all(f not in path for f in list_to_filter):
                dirs = self.get_last_entry(path) # Extracting the parent directory "../../.." of the file
                files_dirs = os.listdir(path) # Extracting all the files in the directory

                for f in files_dirs:
                    if f.endswith(('.R', '.ipynb')):
                        pwd = '/'.join([os.getcwd(), dirs, f])
                        extracted_headers = self.load_json(pwd)
                        d[dirs][f] = extracted_headers

        cleaned_d = self.clean_dict(d)
        return cleaned_d



    def clean_dict(self, unsorted_d):
        '''Returns a sorted dictioary (with the nester dictioanries as well)'''
        d = OrderedDict(sorted(unsorted_d.items()))
        d_sorted = defaultdict(dict)

        # Cleaned the sorting of the nested dictionary
        for k, v in d.items():
            d_nested = OrderedDict(sorted(v.items()))
            for nested_k, nested_v in d_nested.items():
                d_sorted[k][nested_k] = nested_v
        return d_sorted

    def get_last_entry(self, path):
        ''' Returns the parent directory given the path'''
        split_entries = path.split('/')
        recent_entry = split_entries[-1]
        return recent_entry

    def load_json(self, pwd):
        with open(pwd) as f:
            json_file = json.load(f)
            json_cells =  json_file['cells']
            headers = self.get_headers(json_cells)
            return headers

    def get_headers(self, cells):
        '''Returns a list of the top headers and the second headers'''
        headers_1 = []; headers_2 = []
        for cell in cells:
            if str(cell['source'][0]).startswith("##"):
                header = cell['source'][0]
                header = self.clean_header(header, "##")
                headers_2.append(header)

            elif str(cell['source'][0]).startswith("#"):
                header = cell['source'][0]
                header = self.clean_header(header, "#")
                headers_1.append(header)

        return[headers_1, headers_2]

    def clean_header(self, header, remove_chr):
        header = header.replace(remove_chr, "")
        header = header.strip()
        return header


class WriteTableContents:

    def write_file(self, cleaned_d):
        print(cleaned_d)
        f = open('CourseOutline.md', 'wt')
        f.write(f"# Machine Learning\n")

        for i, (k, v) in enumerate(cleaned_d.items()):
            chpt_num = i+1
            f.write(f'{chpt_num}. [{k}]\n')

            for nested_i, (nested_k, nested_v) in enumerate(v.items()):
                nested_chpt_num = nested_i+1
                nested_k = nested_k.split("_")[1].replace('.ipynb', '')
                f.write(f'\t{nested_chpt_num}. [{nested_k}]\n')

                for header in nested_v[1]:
                    f.write(f'\t\t- {header}\n')
        f.close()




if __name__ == "__main__":
    s = SearchInformation()
    content = s.get_dirs()
    w = WriteTableContents()
    w.write_file(content)
