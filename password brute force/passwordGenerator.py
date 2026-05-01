#!/usr/bin/python
import sys

drive = str(input("Enter the drive to search: "))

fh = open(drive, "rt")
password = fh.read()
fh.close()

ascii_min = 32
ascii_max = 126
password_max = len(password)
ASCII = []


def convert():
    global ASCII, password_max, ascii_min
    result = ""
    for i in range(password_max):
        if ASCII[i] >= ascii_min:
            result += chr(ASCII[i])
        else:
            break
    return result


def increase(i):
    global ASCII, ascii_min, ascii_max, password_max
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


def extend():
    for i in range(password_max):
        if ASCII[i] >= ascii_min:
            ASCII[i] = ascii_min
        else:
            ASCII[i] = ascii_min
            return 1
    return 0


def generate():
    global ASCII, password_max, ascii_min
    for i in range(password_max - 1, -1, -1):
        if increase(i):
            return
    if extend():
        return
    print("End of " + str(password_max) + " characters")
    sys.exit()


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
