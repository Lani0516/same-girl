#!/usr/bin/env python3

import sys
import traceback

def main():
    
    try:
        from main import TestBot
        client = TestBot()
        client.run()
    
    # TODO: add all error exceptions
    except SyntaxError:
        print("\nSyntax Raised Error !\n")
        return

    except:
        print()
        traceback.print_exc()
        print("\nError Raised !\n")
        return

if __name__ == '__main__':
    main()