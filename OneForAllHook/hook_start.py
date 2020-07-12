import frida, sys
import json
import IPython
import time
import os
import signal

api_log = []
package_name = ''
class_set = set()


def formatStackInfo(message):
    stackInfo = message['stack']
    infos = stackInfo.split('\n    ')
    message['stack'] = infos


def printError(message):
    formatStackInfo(message)
    print(json.dumps(message, indent=4))


def quit(signum, frame):
    print('stop ...')
    os._exit(0)


class CallerHook:
    api_log = []
    package_name = ''
    class_set = set()
    save_dir_path = ''
    process = None
    script = None

    def __init__(self, pacname, savedir):
        self.package_name = pacname
        self.save_dir_path = savedir
        pass

    def get_caller_class(self, call_stack, depth):
        stacks = call_stack.split('\n')
        depth = min(len(stacks), depth)
        for i in range(depth):
            caller_class = stacks[i].replace('\t', '')
            if caller_class.startswith('android.'):
                tmp = caller_class[:caller_class.find('(')]
                method = tmp.split('.')[-1]
                caller_class = tmp.replace(method, '')[:-1]
                self.class_set.add(caller_class)
            else:
                print('[+] ' + caller_class)

        return self.class_set

    def save_message(self, message):
        # path = os.path.join('.', 'log', self.package_name + '.json')
        path = os.path.join(self.save_dir_path, self.package_name + 'API.json')
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(message + '\n')
        else:
            with open(path, 'a+') as f:
                f.write(message + '\n')
        # if os.path.exists(path):
        #     with open(path) as f:
        #         log = json.load(f)
        # else:
        #     log = []
        # trace = json.loads(message)
        # log.append(trace)
        # with open(path, 'w') as f:
        #     json.dump(log, f, indent=4)

        pass

    def on_message(self, message, data):
        if message['type'] == 'send':
            report = json.loads(message['payload'])
            # if 'backtrace' in report.keys():
            #     self.class_set = self.get_caller_class(report['backtrace'], 5)
            #     print(self.class_set)
            report['timestamp'] = round(time.time() * 1000)
            self.save_message(json.dumps(report))
            # print("[*] {0}".format(message['payload']))
        else:
            printError(message)

    def start_hook(self, script_path):
        """
        直接hook进程
        :param script_path:
        :return:
        """
        try:
            signal.signal(signal.SIGINT, quit)
            signal.signal(signal.SIGTERM, quit)
            # 加载Frida
            with open(script_path, encoding='utf-8') as f:
                jscode = f.read()
            self.process = frida.get_usb_device().attach(self.package_name)
            self.process.enable_debugger()
            self.script = self.process.create_script(jscode, runtime="v8")
            self.script.on('message', self.on_message)
            print('[*] Running App')
            self.script.load()

            # sys.stdin.read()
        except Exception as e:
            print(e.args)
        pass

    def run_and_start_hook(self, script_path):
        """
        启动APP进程并hook
        :param script_path:
        :return:
        """
        try:
            signal.signal(signal.SIGINT, quit)
            signal.signal(signal.SIGTERM, quit)
            # 加载Frida
            with open(script_path, encoding='utf-8') as f:
                jscode = f.read()

            device = frida.get_usb_device()
            pid = device.spawn([self.package_name])
            self.process = device.attach(pid)
            self.script = self.process.create_script(jscode)
            self.script.on('message', self.on_message)
            print('[*] Running App')
            self.script.load()
            time.sleep(5)
            # resume()一定要放在后面，不然hook不到onCreate
            device.resume(pid)
            return pid

            # sys.stdin.read()
        except Exception as e:
            print(e.args)
        pass

    def stop_hook(self):
        print("[*] stop hook " + self.package_name)
        self.script.off('message', self.on_message)
        # self.process.off()
        pass

    pass


if __name__ == "__main__":
    package_name = sys.argv[1]
    ch = CallerHook(package_name, os.path.join('log'))
    # ch.start_hook(os.path.join('_agent.js'))
    ch.run_and_start_hook(os.path.join('_agent.js'))
    sys.stdin.read()
    ch.stop_hook()

    pass
