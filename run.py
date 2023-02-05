#!/usr/bin/env python3

import sys
import traceback

def main():
    try:
        from same.main import Samegirl
        same = Samegirl()
        same.run()
    
    except SyntaxError:
        traceback.print_exc()
        print("\n>>> Syntax Raised Error ! <<<\n")

    except KeyboardInterrupt:
        # already had print KeyboardInterrupt
        pass

    # TODO: fix the func of closing loop and client session
    except:
        traceback.print_exc()
        print("\n>>> Unexpected Error <<<\n") 

if __name__ == '__main__':
    main()
