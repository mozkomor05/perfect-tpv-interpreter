#!/usr/bin/env python3

import os
from interpreter import Interpreter


def valid_path(string):
    if os.path.exists(string):
        return string
    else:
        raise Exception(f'{string} is not a valid path')


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=valid_path,
                        help='Path to a file or directory')

    args = parser.parse_args()

    files = []

    if os.path.isfile(args.path):
        files.append(args.path)
    elif os.path.isdir(args.path):
        for filename in os.listdir(args.path):
            if filename.lower().endswith('.tpv'):
                files.append(os.path.join(args.path, filename))

    for filename in files:
        with open(filename, 'r') as file:
            print(f'Processing {filename}...')
            try:
                interpreter = Interpreter(file.read())
                im = interpreter.run()

                if im is not None:
                    im.save(os.path.join(
                        args.directory, filename[:-4] + '.png'))  # save file to same folder
                    try:
                        im.show()
                    except Exception:
                        pass
            except Exception as e:  # exception is raised if code is invalid
                print(f'Code for {filename} is invalid: {e}')
                raise e
            print(f'Done processing {filename}!')


if __name__ == '__main__':
    main()
