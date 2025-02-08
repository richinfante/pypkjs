from __future__ import absolute_import
__author__ = 'katharine'

import STPyV8 as v8

class Console(object):
    def __init__(self, runtime):
        self.runtime = runtime
        self.runtime.register_syscall("console.log", self.log)
        self.runtime.register_syscall("console.warn", self.warn)
        self.runtime.register_syscall("console.info", self.info)
        self.runtime.register_syscall("console.error", self.error)
        
        self.runtime.run_js("""
        window.console = {
            log: function () { _syscall.exec('console.log', Array.prototype.slice.call(arguments)); },
            warn: function () { _syscall.exec('console.warn', Array.prototype.slice.call(arguments)); },
            info: function () { _syscall.exec('console.info', Array.prototype.slice.call(arguments)); },
            error: function () { _syscall.exec('console.error', Array.prototype.slice.call(arguments)); }
        };
        """)

    def log(self, *params):
        print('LOG', *params)
        return
        # kOverview == kLineNumber | kColumnOffset | kScriptName | kFunctionName
        trace_str = str(v8.JSStackTrace.GetCurrentStackTrace(2, v8.JSStackTrace.Options.Overview))
        try:
            frames = v8.JSError.parse_stack(trace_str.strip())
            caller_frame = frames[0]
            filename = caller_frame[1]
            line_num = caller_frame[2]
            file_and_line = u"{}:{}".format(filename, line_num)
        except:
            file_and_line = u"???:?:?"
        log_str = u' '.join([x.toString().decode('utf-8') if hasattr(x, 'toString')
                                           else bytes(x).decode('utf-8') for x in params])
        self.runtime.log_output(u"{} {}".format(file_and_line, log_str))

    def warn(self, *params):
        self.log(*params)

    def info(self, *params):
        self.log(*params)

    def error(self, *params):
        self.log(*params)