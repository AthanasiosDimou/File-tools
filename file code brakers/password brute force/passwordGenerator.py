#!/usr/bin/python
import sys

from typing import List

'''
drive = str(input("Enter the drive to search: "))

fh = open(drive, "rt")
password = fh.read()
fh.close()

ascii_min = 32
ascii_max = 126
password_max = len(password)
ASCII = []
'''

def convert(ASCII: List[int], password_max: int, ascii_min: int) -> str:
    #global ASCII, password_max, ascii_min
    result = ""
    for i in range(password_max):
        if ASCII[i] >= ascii_min:
            result += chr(ASCII[i])
        else:
            break
    return result


def increase(i: int, ASCII: List[int], ascii_min: int, ascii_max: int, password_max: int) -> bool:
    #global ASCII, ascii_min, ascii_max, password_max
    if ASCII[i] < ascii_min:
        if i > 0:
            return 0
    if ASCII[i] < ascii_max:
        ASCII[i] += 1
        for i in range(i + 1, password_max):
            if ASCII[i] >= ascii_min:
                ASCII[i] = ascii_min
        return 1
    return 0


def extend(ASCII: List[int], ascii_min: int, password_max: int) -> bool:
    for i in range(password_max):
        if ASCII[i] >= ascii_min:
            ASCII[i] = ascii_min
        else:
            ASCII[i] = ascii_min
            return 1
    return 0


def generate(ASCII: List[int], password_max: int, ascii_min: int, ascii_max: int):
    #global ASCII, password_max, ascii_min
    for i in range(password_max - 1, -1, -1):
        if increase(i, ASCII, ascii_min, ascii_max, password_max):
            return
    if extend(ASCII, ascii_min, password_max):
        return
    print("End of " + str(password_max) + " characters")
    sys.exit()


# original to run standalone
'''
print("password = " + password)

for n in range(password_max):
    ASCII.append(ascii_min - 1)

counter = 0
while True:
    generate()
    counter += 1
    guess = convert()
    if guess == password:
        print("---- FOUND ----")
        print("guess = " + guess)
        print("counter " + str(counter))
        sys.exit()
'''

# ONLY RUN THIS IF EXECUTED DIRECTLY
if __name__ == "__main__":
    drive = str(input("Enter the file to read: "))
    # Use 'utf-8' encoding to avoid the UnicodeDecodeError you saw
    with open(drive, "rt", encoding="utf-8") as fh:
        password = fh.read()
    