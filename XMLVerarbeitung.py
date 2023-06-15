def compress_split_string(input_string):
    # Wandele den String in Kleinbuchstaben um
    input_string = input_string.lower()

    compressed_strings = []
    compressed_string = ""
    count = 1
    prev_char = ""

    for char in input_string:
        if char == prev_char:
            count += 1
        else:
            # Überprüfe die Länge des komprimierten Strings vor dem Hinzufügen des neuen Zeichens
            if len(compressed_string) + 2 + len(prev_char) > 50:
                # Füge den aktuellen Teil der komprimierten Zeichenkette zur Liste hinzu
                compressed_strings.append(compressed_string)
                compressed_string = "" 

            # Füge das vorherige Zeichen und seine Anzahl zur komprimierten Zeichenkette hinzu
            if prev_char:
                compressed_string += (str(count) if (count > 1 and not ((prev_char == 'w') or (prev_char == 'c'))) else (str(45 * count) if ((prev_char == 'w') or (prev_char == 'c')) else "")) + prev_char

            # Setze die Anzahl und das vorherige Zeichen für das neue Zeichen zurück
            count = 1
            prev_char = char

    # Füge das letzte Zeichen und seine Anzahl zur komprimierten Zeichenkette hinzu
    if prev_char:
        compressed_string += (str(count) if (count > 1 and not ((prev_char == 'w') or (prev_char == 'c'))) else (str(45 * count) if ((prev_char == 'w') or (prev_char == 'c')) else "")) + prev_char

    # Verarbeite den letzten Teil des komprimierten Strings
    if compressed_string:
        compressed_strings.append(compressed_string)

    return compressed_strings

