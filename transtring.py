import getopt
import os
import shutil
import sys
import time
import xml.etree.ElementTree as ET
import re
import googletrans
from pathlib import Path
from googletrans import Translator

def main(argv):
    start_time = time.perf_counter()
    name_of_this_file = os.path.basename(__file__)

    # language codes supported
    supported_codes_list = []
    for code in googletrans.LANGUAGES:
        supported_codes_list.append(code)
    supported_codes_list.sort()

    # project root directory
    pathRoot = Path(__file__).parent

    input_file = ''
    output_dir = ''

    # translate from language code (ISO-639-2), default is auto detect
    alpha_2_from = ''

    # translate to language code/codes, if empty or not specified then translate to all languages
    alpha_2_to_list = []

    # subdirectories prefix in translations
    subDirPrefix = "values"

    # translator used to translate strings from strings.xml
    translator = Translator()

    # delimiter used to splitting/joining lists/strings before/after translation
    delimiter = '\n'*5

    # console separators
    sep_under = '_' * 15
    sep_dot = '.' * 30
    sep_star = '*' * 20

    # exit at iter x, for testing
    translation_number = 0

    # errors list, saves errors related to translations
    error_list = []

    # error messages
    err_msg_too_many_reqs = """
                failed to translate:
                translation failed, most likely you got temporarily blocked from Google Translate due to
                sending to many HTTP requests when translating, i.e you might have translated to alot
                of languages in short time period.
                try to translate at a later time.""".strip()
    err_msg_delimiter_problem = f'incorrect translations:\n' \
                                f'{"".ljust(15," ")}missing translations, this could be caused by a conflict between the delimiter used to split/join strings and the strings in your strings.xml file.\n' \
                                f'{"".ljust(15," ")}the new translated strings.xml file translations could be partially or completely wrong.\n' \
                                f'{"".ljust(15," ")}try changing the delimiter if possible. or ignore this message if you are satisfied with the results.'

    # default translate to language list
    default_to_lang_list = ['zh-cn', 'es', 'de', 'fr', 'ar'
                            , 'ru', 'pt', 'ja', 'hi', 'it'
                            , 'en', 'ko', 'id', 'pa', 'jw'
                            , 'bn', 'iw']

    # default translate to languages text used in help message
    default_to_lang_str = ''
    c = 0 # to number lines
    for code in default_to_lang_list:
        c+=1
        default_to_lang_str += f'{str(c).rjust(30," ")}) {str(googletrans.LANGUAGES.get(code)).capitalize().ljust(20, " ")} - {code}\n'

    # usage
    u_example = f'python {name_of_this_file} -i <input_file> -o <output_directory> -f [from_language] -t [to_language]'
    u_ex_multi = r'python .\transtring.py -i .\test\strings.xml -o .\test\ -t tr:ru:bn'
    u_ex_one = r'python .\transtring.py -i .\test\strings.xml -o .\test\ -t it'
    u_ex_def = r'python .\transtring.py -i .\test\strings.xml -o .\test\ '

    # number of all supported codes
    num_of_codes = len(supported_codes_list)

    # number of all supported codes divided by 4 plus 1
    quarter_len = num_of_codes // 4 + 1

    # width used for str.ljust()
    ljust_width = 30

    # usage language code - language pairs
    u_codes = ''

    # fill u_codes with code - language pairs
    for i in range(0, quarter_len):
        for j in range(i, num_of_codes, quarter_len):
            if j < num_of_codes:
                u_codes += f'{supported_codes_list[j]} - {googletrans.LANGUAGES.get(supported_codes_list[j])}'.ljust(
                    ljust_width, " ")
        u_codes += '\n'

    # get args entered through console
    try:
        opts, args = getopt.getopt(argv, "i:o:f:t:h",
                                   ["input-file=", "output-directory=", "help", "from-language=", "to-language="])
    except getopt.GetoptError:
        print(u_example)
        sys.exit(2)

    # fill entered args into local variables
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            ljust_width = 25
            ljust_width_con = ljust_width + 2
            ljust_example = 5
            print(f'\nusage:\n'
                  f'{"".ljust(ljust_example, " ")}{u_example}\n\n'
                  f'examples:\n'
                  f'translate to one language (Italian):\n'
                  f'{"".ljust(ljust_example, " ")}{u_ex_one}\n\n'
                  f'translate to multiple languages (Turkish, Russian and Bengali):\n'
                  f'{"".ljust(ljust_example, " ")}{u_ex_multi}\n\n'
                  f'translate to default languages:\n'
                  f'{"".ljust(ljust_example, " ")}{u_ex_def}\n\n'
                  f'options:\n'
                  f'{"-h / --help".ljust(ljust_width, " ")}_ to get this help message\n'
                  f'{"-i / --input-file".ljust(ljust_width, " ")}_ relative or absolute path to the strings.xml file to translate to other languages\n'
                  f'{"-o / --output-directory".ljust(ljust_width, " ")}_ relative or absolute path to the directory to save the results to\n'
                  f'{"-f / --from-language".ljust(ljust_width, " ")}_ language code ISO-639-2 or BCP 47 to translate from, if not specified,\n '
                  f'{"".ljust(ljust_width_con, " ")}will default to auto detect\n'
                  f'{"-t / --to-language".ljust(ljust_width, " ")}_ language code/s ISO-639-2 or BCP 47 to translate to.\n'
                  f'{"".ljust(ljust_width_con, " ")}to translate to one language only => -t xx\n'
                  f'{"".ljust(ljust_width_con, " ")}to translate to multiple languages => -t xx:yy:zz , i.e separate codes with colon\n'
                  f'{"".ljust(ljust_width_con, " ")}if no code is specified, will translate to these {len(default_to_lang_list)} languages:\n'
                  f'{default_to_lang_str}\n'
                  f'\nsupported language codes:\n'
                  f'{u_codes}')
            sys.exit()
        if opt in ("-i", "--input-file"):
            input_file = os.path.abspath(arg)
            if not os.path.isfile(input_file):
                sys.exit(f'\"{input_file}\" is not a file.')

        if opt in ("-o", "--output-directory"):
            output_dir = os.path.abspath(arg)
            if not os.path.isdir(output_dir):
                sys.exit(f'\"{output_dir}\" is not a directory/')
        if opt in ("-f", "--from-language"):
            alpha_2_from = arg
            if supported_codes_list.count(alpha_2_from) == 0:
                sys.exit(
                    f'--from-language => \"{alpha_2_from}\" not supported, enter -h to see supported language codes.')
        if opt in ("-t", "--to-language"):
            alpha_2_to_list = arg.split(":")
            if len(alpha_2_to_list) >= 1:
                if alpha_2_to_list[0] in (
                '-i', '-o', '-h', '-f', '-t', "--input-file", "--output-directory", "--help", "--from-language",
                "--to-language"):
                    print(f'--to-language empty, will translate to all available languages.', flush=True)
                else:
                    for code in alpha_2_to_list:
                        if supported_codes_list.count(code) == 0:
                            sys.exit(
                                f'--to-language => \"{code}\" not supported, enter -h to see supported language codes.')
    # just in case..
    if len(input_file) == 0:
        sys.exit(f'* input file path not specified')
    if len(output_dir) == 0:
        sys.exit(f'* output directory path not specified')

    # created translations directory
    createdTranslationsDir = os.path.join(output_dir, "translations_values")

    # print started translation
    print(f'\n{sep_dot}'
          f'\nAndroid Strings Translator\n'
          f'translation started\n', flush=True)

    # if --to-language code not specified, then will translate to all languages
    if len(alpha_2_to_list) == 0:
        alpha_2_to_list = default_to_lang_list

    # if --from-language code not specified, then will set to auto detect
    if len(alpha_2_from) < 2:
        alpha_2_from = 'auto'

    # go over all ISO-639-2 (values-xx) codes supported by google translate, some are BCP 47 (values-xxx) as well
    for to_code in alpha_2_to_list:
        translation_number += 1

        # for translation to Chinise => values-zh, because values-zh-cn or values-zh-tw isn't supported in android
        to_code_folder_suffix = to_code.split('-')[0]

        # new values-xx directory
        newValuesDir = os.path.join(createdTranslationsDir, f'{subDirPrefix}-{to_code_folder_suffix}')

        # create directory and sub directory (value-xx) to save strings.xml inside for each language
        Path(newValuesDir).mkdir(parents=True, exist_ok=True)

        # copy original strings.xml file to new language directory
        shutil.copy(input_file, newValuesDir)

        # reading strings.xml that will be translated
        original_xml_tree = ET.parse(input_file)
        original_xml_root = original_xml_tree.getroot()
        original_file_strings_list = []
        for elm in original_xml_root.findall('string'):
            original_file_strings_list.append(elm.text)

        # translate all strings as one delimited string
        translations = translator.translate(delimiter.join(original_file_strings_list), to_code, alpha_2_from)

        # translated from, in case 'auto' is specified we get the detected language code, else we get the code we sent
        alpha_2_from = translations.src

        # uncomment below to prevent translating the same language, e.g to_code == 'en' and alpha_2_from = 'en'
        # if to_code == alpha_2_from:
        #     translation_number -= 1
        #     continue

        # handle returned translation
        returned_translations_string = translations.text

        # correct single quote translation in languages like French or Italian
        corrected_returned_string = re.sub(r"(?<!\\)'", r"\'", returned_translations_string)

        # corret newline in translation from LTR to RTL languages
        corrected_returned_string = re.sub(r"\\ n", r'\\n', corrected_returned_string)

        translated_strings_list:list[str] = corrected_returned_string.split(delimiter)

        # update translated strings.xml inside values-xx
        xmlTree = ET.parse(os.path.join(newValuesDir, 'strings.xml'))
        rootElm = xmlTree.getroot()
        translated_elm_list = rootElm.findall('string')
        strings_received_len = len(translated_strings_list)
        strings_sent_len = len(translated_elm_list)

        # left justify width here
        ljust_here = 7
        # print progress/error/result
        print(f'translation {translation_number}\n'
              f'{"from:".ljust(ljust_here)}{alpha_2_from} - {googletrans.LANGUAGES.get(translations.src)}\n'
              f'{"to:".ljust(ljust_here)}{to_code} - {googletrans.LANGUAGES.get(to_code)}\n'
              f'{"received / sent:".ljust(ljust_here)} {strings_received_len}/{strings_sent_len}', flush=True)
        if strings_sent_len != strings_received_len:
            # check for translations mismatch, i.e number of strings sent is different from number of strings received
            print(
                f'{"status:".ljust(ljust_here, " ")} failed\n'
                f'{"error:".ljust(ljust_here, " ")} {abs(strings_sent_len - strings_received_len)} strings.xml string translations mismatch'
                , flush=True)
            error_list.append(
                {
                    "at_iter": translation_number,
                    "from_to": f'{alpha_2_from} - {googletrans.LANGUAGES.get(alpha_2_from)}  -->  {to_code} - {googletrans.LANGUAGES.get(to_code)}',
                    "sent": strings_sent_len,
                    "received": strings_received_len,
                    "err_message": err_msg_delimiter_problem
                }
            )

        # check if no translations were received
        same_strings_counter = 0
        for i in range(0, len(translated_elm_list)):
            if translated_elm_list[i].text == translated_strings_list[i]:
                same_strings_counter += 1
        if same_strings_counter == len(translated_elm_list) and to_code != alpha_2_from:
            print(f'{"status:".ljust(ljust_here, " ")} failed\n'
                  f'{"error:".ljust(ljust_here)} no translations were received'
                  , flush=True)
            error_list.append(
                {
                    "at_iter": translation_number,
                    "from_to": f'{alpha_2_from} - {googletrans.LANGUAGES.get(alpha_2_from)}  -->  {to_code} - {googletrans.LANGUAGES.get(to_code)}',
                    "sent": strings_sent_len,
                    "received": strings_received_len,
                    "err_message": err_msg_too_many_reqs
                }
            )

        else:
            # insert translated strings to new strings.xml file
            for i in range(0, len(translated_elm_list)):
                if i < len(translated_strings_list):
                    translated_elm_list[i].text = translated_strings_list[i]

            # apply changes to new strings.xml file
            xmlTree.write(os.path.join(newValuesDir, 'strings.xml'), encoding='UTF-8', xml_declaration=True)

            print(f'{"status:".ljust(ljust_here, " ")} success\n'
                  f'{sep_under}', flush=True)

    # find how much time it took to translate
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # print finished info
    print(f'\ntranslation finished.\n'
          f'translated to {translation_number} language/s.\n'
          f'problems with {len(error_list)} translations.\n'
          f'time elapsed: {elapsed_time:0.2f} seconds\n'
          f'check the results at {createdTranslationsDir}'
          , flush=True)

    # left justifty width for use below
    lj_w_1 = 10
    if len(error_list) > 0:
        print(f'review problems below:\n'
              f'{sep_dot}\n'
              f'{sep_star}\n'
              f'{len(error_list)} problem/s found:', flush=True)
        c = 0  # errors counter
        for err in error_list:
            c += 1
            print(f'{"".ljust(lj_w_1, " ")}{c}) at translation {err["at_iter"]},'
                  f'{"".ljust(lj_w_1, " ")}{err["from_to"]},'
                  f'{"".ljust(lj_w_1, " ")}received: {err["received"]}, should be {err["sent"]}\n'
                  f'{"".ljust(lj_w_1, " ")}{err["err_message"]}\n', flush=True)
        print(sep_star, flush=True)
    else:
        print(f'{sep_dot}', flush=True)

if __name__ == "__main__":
    main(sys.argv[1:])