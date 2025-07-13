from pathlib import Path
import os
BASE_DIR = Path(__file__).parent
os.chdir(Path(__file__).parent)

IsExit = False

def join_type(words):
    result = []
    i = 0
    while i < len(words):
        if words[i] == "::" and result:
            result[-1] += "::" + words[i + 1]
            i += 2
        else:
            result.append(words[i])
            i += 1
    return " ".join(result)

def clean_default_value(tokens):
    res = ""
    for t in tokens:
        if t == '{':
            res += " { "
        elif t == '}':
            res += " } "
        elif t == ',':
            res += ", "
        else:
            res += t + " "
    return " ".join(res.split())

while(not IsExit):
    Hname = input("type your filename: ").strip()
    header_path = BASE_DIR / f"{Hname}.h"
    Hwords = []
    FileCursor = ""
    StartedClass = False

    ClassName = ""
    ClassFields = ""
    ClassMethods = ""

    try:
        with open(Hname + ".h", "r") as file:
            content = file.read()
    except FileNotFoundError:
        print("file not found.")
        continue

    separators = set("{}:;,()=[]")
    two_char = {":":":", "*":"*", "&":"&"}
    i = 0
    while(i < len(content)):
        c = content[i]

        if(c == ":" and i + 1 < len(content) and content[i+1] == ":"):
            FileCursor += "::"
            i += 2
            continue

        if(c.isspace()):
            if(FileCursor):
                if(StartedClass):
                    Hwords.append(FileCursor)
                FileCursor = ""
            i += 1
            continue

        elif(c in separators):
            if(FileCursor and StartedClass):
                Hwords.append(FileCursor)

            Hwords.append(c)
            FileCursor = ""
            i += 1
            continue

        if(c in two_char and FileCursor):
            FileCursor += c
        else:
            FileCursor += c
        i += 1

        if(FileCursor == "class"):
            Hwords.append(FileCursor)
            StartedClass = True
            FileCursor = ""

    if (FileCursor):
        Hwords.append(FileCursor)

    if "class" in Hwords:
        idx = Hwords.index("class")
        if idx + 1 < len(Hwords):
            ClassName = Hwords[idx + 1]

    IsPrivateSection, ISPublicSection = False, False
    i = 0
    FieldsStrokes = []
    MethodsStrokes = []
    buf = []

    while i < len(Hwords):
        word = Hwords[i]

        if(word == "{" and not buf):
            i+= 1
            continue

        if(word in ("private", "public") and i+1 < len(Hwords) and Hwords[i+1] == ":"):
            ISPublicSection, IsPrivateSection = (word == "public"), (word == "private")
            i+=2
            continue
        if(ISPublicSection or IsPrivateSection):
            if (word == "("):
                params = []
                param = ""
                i += 1
                depth = 1
                #bonus(sf::Vector2f startPos, sf::Vector2f size, const Texture* texturePtr, BonusType type, int lineIndex, float speed);
                while(i < len(Hwords) and depth):
                    if (Hwords[i] == "("): depth+=1
                    elif(Hwords[i] == ")"):
                        depth-=1
                        if (depth == 0):
                            i += 1
                            break
                    if(Hwords[i] != ","):
                        param += Hwords[i] + " "
                    if(Hwords[i] == ","):
                        params.append(param[:-1])
                        param = ""
                    i += 1

                if (param):
                    params.append(param[:-1])

                new_params = []
                for p in params:
                    parts = p.split()
                    name  = parts[-1]
                    typ   = join_type(parts[:-1])
                    new_params.append(f"{name} : {typ}")

                if(len(buf) >= 1):
                    ret_type = join_type(buf[:-1]) if len(buf) > 1 else ""
                    meth_name = buf[-1]
                access = "+ " if ISPublicSection else "- "

                MethodsStrokes.append(f"{access}{meth_name}({', '.join(new_params)}) : {ret_type}" if ret_type else f"{access}{meth_name}({', '.join(new_params)})")
                buf.clear()
                while(i < len(Hwords) and Hwords[i] != ";"):
                    i+=1
                i+= 1
                continue

            if(word == "=" and buf):
                access = "+ " if ISPublicSection else "- "

                if "[" in buf:
                    arr_idx = buf.index('[')
                    field_name = buf[arr_idx - 1]
                    type_part = join_type(buf[:arr_idx - 1])
                    arr_size = buf[arr_idx + 1] if (arr_idx + 1) < len(buf) else ""
                    field_type = f"{type_part}[{arr_size}]"
                else:
                    field_type = join_type(buf[:-1]) if len(buf) > 1 else ""
                    field_name = buf[-1]
                default_tokens = []
                i += 1

                if(i < len(Hwords) and Hwords[i] == '{'):
                    brace_depth = 1
                    default_tokens.append(Hwords[i])
                    i += 1
                    while i < len(Hwords) and brace_depth > 0:
                        token = Hwords[i]
                        default_tokens.append(token)
                        if token == '{':
                            brace_depth += 1
                        elif token == '}':
                            brace_depth -= 1
                        i += 1
                else:
                    while i < len(Hwords) and Hwords[i] != ";":
                        default_tokens.append(Hwords[i])
                        i += 1

                default_value = clean_default_value(default_tokens)

                FieldsStrokes.append(
                    f"{access}{field_name} : {field_type} = {default_value}"
                )

                buf.clear()
                i += 1
                continue

            if(word == "{" and buf):
                access = "+ " if ISPublicSection else "- "
                if "[" in buf:
                    arr_idx = buf.index('[')
                    field_name = buf[arr_idx - 1]
                    type_part = join_type(buf[:arr_idx - 1])
                    arr_size = buf[arr_idx + 1] if (arr_idx + 1) < len(buf) else ""
                    field_type = f"{type_part}[{arr_size}]"
                else:
                    field_type = join_type(buf[:-1]) if len(buf) > 1 else ""
                    field_name = buf[-1]
                default_tokens = ["{"]
                brace_depth = 1
                i += 1
                while i < len(Hwords) and brace_depth:
                    tok = Hwords[i]
                    default_tokens.append(tok)
                    if tok == "{":
                        brace_depth += 1
                    elif tok == "}":
                        brace_depth -= 1
                    i += 1

                default_value = clean_default_value(default_tokens)

                FieldsStrokes.append(
                    f"{access}{field_name} : {field_type} = {default_value}"
                )
                buf.clear()
                continue

            if (word == ";"):

                if not buf:
                    i += 1
                    continue

                if "[" in buf:
                    arr_idx = buf.index('[')
                    field_name = buf[arr_idx-1]
                    type_part = join_type(buf[:arr_idx - 1])
                    arr_size = buf[arr_idx + 1] if (arr_idx + 1) < len(buf) else ""
                    field_type = f"{type_part}[{arr_size}]"

                else:
                    field_type = join_type(buf[:-1]) if len(buf) > 1 else ""
                    field_name = buf[-1]

                if(field_name == "}"):
                    buf.clear()
                    i += 1
                    continue
                access = "+ " if ISPublicSection else "- "
                FieldsStrokes.append(f"{access}{field_name} : {field_type}")
                buf.clear()
                i += 1
                continue



            buf.append(word)
        i += 1

    print(ClassName + "\n")

    for word in FieldsStrokes:
        print(word)

    for word in MethodsStrokes:
        print(word)

    if(FieldsStrokes):
        for word in FieldsStrokes:
            ClassFields += word + "\n"

    if(MethodsStrokes):
        for word in MethodsStrokes:
            ClassMethods += word + "\n"

    outString = ""
    with open(Hname + ".txt", "w") as file:
        outString += ClassName + "\n" + "\n"
        for line in ClassFields:
            outString += line
        outString += "\n"
        for line in MethodsStrokes:
            outString += line + "\n"
        file.write(outString)
    IsNext = input("Next? y/n: ")
    if(IsNext == "n"):
        IsExit = True
