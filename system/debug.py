"""
debug - multiline prompt
"""
import signal

prompt = compile("""
try:
    _prompt
    _recursion = 1
except:
    _recursion = 0
if not _recursion:
    from traceback import print_exc as print_exc
    from traceback import extract_stack
    _stack = extract_stack()
    _frame = [frame]
    thisFrame = frame
    while 1:
        try:
            _frame.append(thisFrame.f_back)
            thisFrame = thisFrame.f_back
        except:
            break
    _frame.reverse()
    _frame.append(None)
    _frame.append(None)
    _currentPos = -3
    _prompt = {'print_exc':print_exc, 'inp':'','inp2':'','co':''}
    _lastPos = 0
    while 1:
        if _lastPos != _currentPos:
            _lastPos = _currentPos
            _a_es, _b_es, _c_es, _d_es = extract_stack()[_currentPos]
            if _c_es == '?':
                _c_es = '__main__'
            else:
                _c_es += '()' 
            print '\\ndebug in %s at %s:%s  -  continue with CTRL-D' % (_c_es, _a_es, _b_es)
        try:
            _prompt['inp']=raw_input('>>> ')
            if not _prompt['inp']:
                continue
            if _prompt['inp'][-1] == chr(4): 
                break
            if _prompt['inp'] == "up":
                _currentPos -= 1
                frame = _frame[_currentPos]
                continue
            elif _prompt['inp'] == "down":
                _currentPos += 1
                frame = _frame[_currentPos]
                continue
            elif _prompt['inp'] == "top":
                _currentPos = -len(_frame) + 1
                frame = _frame[_currentPos]
                continue
            elif _prompt['inp'] == "bot":
                _currentPos = -3
                frame = _frame[_currentPos]
                continue
            code = compile(_prompt['inp'],'<prompt>','single')
            exec(code, frame.f_globals, frame.f_locals)
        except EOFError:
            print
            break
        except SyntaxError:
            while 1:
                _prompt['inp']+=chr(10)
                try:
                    _prompt['inp2']=raw_input('... ')
                    if _prompt['inp2']:
                        if _prompt['inp2'][-1] == chr(4): 
                            print
                            break
                        _prompt['inp']=_prompt['inp']+_prompt['inp2']
                    _prompt['co']=compile(_prompt['inp'],'<prompt>','exec')
                    if not _prompt['inp2']:
                        if _prompt['co'] == "up":
                            _currentPos -= 1
                            frame = _frame[_currentPos]
                            continue
                        elif _prompt['co'] == "down":
                            _currentPos += 1
                            frame = _frame[_currentPos]
                            continue
                        elif _prompt['co'] == "top":
                            _currentPos = -len(_frame) + 1
                            frame = _frame[_currentPos]
                            continue
                        elif _prompt['co'] == "bot":
                            _currentPos = -3
                            frame = _frame[_currentPos]
                            continue
                        exec(_prompt['co'], frame.f_globals, frame.f_locals)
                        break
                    continue
                except EOFError:
                    print
                    break
                except:
                    if _prompt['inp2']: 
                        continue
                    _prompt['print_exc']()
                    break
        except:
            _prompt['print_exc']()
    print 'continuing...'
    # delete the prompts stuff at the end
    del _prompt
""", '<prompt>', 'exec')

def handler(signum, frame):
    exec prompt
signal.signal(signal.SIGTSTP, handler) # suspend

