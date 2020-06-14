"""Mosolov Alexander.
The function normalizes the text, removes words from the list of stop words, and selects the stem of the remaining words. Accepts text as a string as input, and a list of stems as output.
:param: text
:type param: string
:param: stop_words
:type param: list
:return: text
:rtype: list
"""
def text_normalize(text, stop_words):
    PERF_GER_1 = ['вшись', 'вши', 'в']
    PERF_GER_2 = ['ывшись', 'ившись', 'ывши', 'ивши', 'ыв', 'ив']
    ADJ = ['его', 'ого', 'ему', 'ому', 'ими', 'ыми', 'ее', 'ие', 'ые', 'ый', 'ое', 'ей', 'ий', 'ой', 'ем', 'им', 'ым',
           'ом', 'их', 'ых', 'ую', 'юю', 'ая', 'яя', 'ою', 'ею']
    PART_1 = ['ем', 'нн', 'вш', 'ющ', 'щ']
    PART_2 = ['ивш', 'ывш', 'ующ']
    REF = ['ся', 'сь']
    VERB_1 = ['ете', 'йте', 'ешь', 'нно', 'ла', 'на', 'ли', 'ем', 'ло', 'но', 'ет', 'ют', 'ны', 'ть', 'й', 'л', 'н']
    VERB_2 = ['ейте', 'уйте', 'ила', 'ыла', 'ена', 'ите', 'или', 'ыли', 'ило', 'ыло', 'ено', 'ены', 'ить', 'ыть', 'ишь',
              'ует', 'уют', 'ей', 'уй', 'ил', 'ыл', 'им', 'ым', 'ен', 'ят', 'ит', 'ыт', 'ую', 'ю']
    NOUN = ['иями', 'иям', 'ией', 'ием', 'ями', 'ами', 'иях', 'ев', 'ов', 'ие', 'ье', 'еи', 'ии', 'ей', 'ой', 'ию',
            'ью', 'ья', 'ия', 'ий', 'ям', 'ем', 'ам', 'ом', 'ах', 'ях', 'ы', 'ь', 'я', 'ю', 'и', 'е', 'й', 'о', 'а',
            'у']
    SUP = ['ейше', 'ейш']
    DER = ['ость', 'ост']
    glas = ['а', 'е', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я', 'ё']

    #Lowercase conversion
    text=text.lower()
    for t in text:
        if (not t.isalpha()) & (t!=" "):
            text=text.replace(t,"")
    text=text.split(' ')

    #Delete words containing Latin and Cyrillic letters
    for word in text:
        kk = 0
        kl = 0
        for i in word:
            if i in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                kk += 1
            if i in 'abcdefghijklmnopqrstuvwxyz':
                kl += 1
        if kk!=len(word) and kl!=len(word) or (kk==0 and kl==0):
            text.remove(word)

    #Counting the number of vowels of Russian letters
    def count_glas(word):
        k = 0
        for i in range(len(word)):
            if word[i] in glas:
                k += 1
        return (k)

    #Counting the number of vowels of English letters
    def count_gl_en(word):
        k = 0
        for i in range(len(word)):
            if word[i] in 'euioa':
                k += 1
        return (k)

    #Deleting stop words
    i=0
    while i in range(len(text)):
        if text[i] in stop_words:
            del text[i]
        else:
            i+=1

    #Delete words that do not contain vowels or consonants
    i=0
    while i in range(len(text)):
        if (text[i][0] in 'abcdefghijklmnopqrstuvwxyz' and count_gl_en(text[i])==0) or count_gl_en(text[i])==len(text[i])\
                or (text[i][0] in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' and count_glas(text[i])==0)\
                or count_glas(text[i])==len(text[i]):
            del text[i]
        else:
            i+=1

    #STEMMING
    for N in range(len(text)):
        word = text[N]
        if word[0] in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            f = -1
            RV = R2 = ""
            if count_glas(word) > 0:
                f = 0
                for i in range(len(word)):
                    if word[i] in glas and f == 0:
                        RV = word[i + 1:]
                        f = 1
                        f_2 = 1
                        pos_1 = i + 1
                for i in range(len(word) - 1):
                    if word[i] in glas and not (word[i + 1] in glas) and f_2 == 1:
                        R1 = word[i + 2:]
                        pos_2 = i + 2
                        f_2 = 2
                        for i in range(len(R1) - 1):
                            if R1[i] in glas and not (R1[i + 1] in glas) and f_2 == 2:
                                R2 = R1[i + 2:]
                                f_2 = 3
                                pos_3 = pos_2 + i + 2
            # STEP 1
            if f == 1:
                for i in PERF_GER_1:
                    if RV.rfind(i) != -1 and (RV[RV.rfind(i) - 1] == 'а' or RV[RV.rfind(i) - 1] == 'я') and len(
                            RV) - RV.rfind(i) == len(i) and f != 2:
                        RV = RV[:RV.rfind(i)]
                        word = word[:pos_1] + RV
                        f = 2
                for i in PERF_GER_2:
                    if RV.rfind(i) != -1 and len(RV) - RV.rfind(i) == len(i) and f != 2:
                        RV = RV[:RV.rfind(i)]
                        word = word[:pos_1] + RV
                        f = 2
            if f == 1:
                for i in REF:
                    if RV.rfind(i) != -1 and len(RV) - RV.rfind(i) == len(i):
                        RV = RV[:RV.rfind(i)]
                        word = word[:pos_1] + RV
                        f = 2
                L = [0, 0, 0]
                for i in ADJ:
                    if RV.rfind(i) != -1 and len(RV) - RV.rfind(i) == len(i):
                        L[0] = len(i)
                        for i in PART_1:
                            if RV.rfind(i) != -1 and (
                                    RV[RV.rfind(i) - 1] == 'а' or RV[RV.rfind(i) - 1] == 'я') and RV.rfind(i) - 1 > -1 and (
                                    (len(RV) - RV.rfind(i) - L[0]) == len(i)):
                                f = 5
                                L[0] += len(i)
                        for i in PART_2:
                            if RV.rfind(i) != -1 and ((len(RV) - RV.rfind(i) - L[0]) == len(i)):
                                f = 5
                                L[0] += len(i)
                if f == 1 or f == 2:
                    for i in VERB_1:
                        if RV.rfind(i) != -1 and RV.rfind(i) != 0 and (
                                RV[RV.rfind(i) - 1] == 'а' or RV[RV.rfind(i) - 1] == 'я') and len(RV) - RV.rfind(i) == len(
                                i):
                            f = 5
                            L[1] = len(i)
                    for i in VERB_2:
                        if RV.rfind(i) != -1 and len(RV) - RV.rfind(i) == len(i):
                            f = 5
                            L[1] = len(i)
                if f == 1 or f == 2:
                    for i in NOUN:
                        if RV.rfind(i) != -1 and len(RV) - RV.rfind(i) == len(i) and (f == 1 or f == 2):
                            f = 5
                            L[2] = len(i)
                RV = RV[:len(RV) - max(L)]
                word = word[:pos_1] + RV
                # STEP 2
                if RV and RV[len(RV) - 1] == 'и':
                    RV = RV[:len(RV) - 1]
                    word = word[:pos_1] + RV
                # STEP 3
                if R2 and f != -1:
                    for i in DER:
                        if word[pos_3:].rfind(i) != -1 and len(word[pos_3:]) - word[pos_3:].rfind(i) == len(i):
                            RV = RV[:len(RV) - len(word[pos_3:])] + word[pos_3:][:len(word[pos_3:]) - len(i)]
                            word = word[:pos_1] + RV
                # STEP 4
                if RV:
                    if RV.rfind("нн") != -1 and len(RV) - RV.rfind("нн") == 2:
                        RV = RV[:RV.rfind("н")]
                        word = word[:pos_1] + RV
                    elif RV[len(RV) - 1] == 'ь':
                        RV = RV[:len(RV) - 1]
                        word = word[:pos_1] + RV
                    else:
                        for i in SUP:
                            if RV.rfind(i) != -1 and len(RV) - RV.rfind(i) == len(i):
                                RV = RV[:RV.rfind(i)]
                                word = word[:pos_1] + RV
                                if RV.rfind("нн") != -1 and len(RV) - RV.rfind("нн") == 2:
                                    RV = RV[:RV.rfind("н")]
                                    word = word[:pos_1] + RV
            if f != -1:
                text[N] = word
    return text