import { colors as c } from "../lib/color";
import { ArrayMap, JavaClass, Throwable } from "../lib/type";
import { parse } from "path";
export namespace hooking {

    export function get_class_method_names(clazz_instance: any) {
        try {
            if (typeof(clazz_instance) == 'string') {
                clazz_instance = Java.use(clazz_instance);
            }
            let method_names: string[] = clazz_instance.class.getDeclaredMethods().filter(function(method : any) {
                if (method.getName().indexOf("-") == 0) {
                    return false;
                }
                return true;
            }).map((method : any) => {
                // let m: string = method.toGenericString();
                // while (m.includes("<")) { m = m.replace(/<.*?>/g, ""); }
                // if (m.indexOf(" throws ") !== -1) { m = m.substring(0, m.indexOf(" throws ")); }
                // m = m.slice(m.lastIndexOf(" "));
                // m = m.replace(` ${clazz_instance.class.getName()}.`, "");
                // return m.split("(")[0];
                return method.getName();
            }).filter((value:any, index:any, self:any) => {
                return self.indexOf(value) === index;
            });

            return method_names;
        } catch(e) {
            return [];
        }
    }

    function hook_method_implementation(def_class: string, method_implementation: any, trace_flag: boolean, arg_val_flag: boolean) {
        let class_name: string = def_class;
        let method_name: string = method_implementation.methodName;
        let args: string[] = method_implementation.argumentTypes.map((arg:any) => arg.className)
        let args_type: string = args.join(',');
        let return_type: string = method_implementation.returnType.className;
        console.log(
            `[+] Hooking ${c.green(class_name)}.${c.greenBright(method_name)}(${c.red(args_type)})`
        );
        const throwable: Throwable = Java.use("java.lang.Throwable");
        method_implementation.implementation = function() {
            console.log(
                `[+] Call ${c.green(class_name)}.${c.greenBright(method_name)}(${c.red(args_type)})`
            );
            let report : any= {};
            report['callee'] = class_name + '.' + method_name;
            report['argTypes'] = args_type
            report['retType'] = return_type
            if (trace_flag) {
                report['backtrace'] = throwable.$new().getStackTrace().map((trace_element:any) => trace_element.toString() + "\n\t").join("")
            }
            if (arg_val_flag) {
                report['argVals'] = arguments;
            }
            send(JSON.stringify(report, null));
            // actually run the intended method
            return method_implementation.apply(this, arguments);
        }
    }

    export function hook_class_methods(clazz: string, trace_flag: boolean, arg_val_flag: boolean) {
        try {
            let clazz_instance = Java.use(clazz);
            let simple_method_names: string[] = get_class_method_names(clazz_instance);
            simple_method_names.forEach(name => {
                // 这里的method类型和getDeclaredMethods()方法拿到的method不一样，注意区分两个的差异
                clazz_instance[name].overloads.forEach((method: any) => {
                    hook_method_implementation(clazz, method, trace_flag, arg_val_flag);
                })
            })
        }catch(e) {}
    }

    export function hook_target_method(
        clazz: string, method_name: string, 
        arg_types: string, return_types: string, 
        trace_flag: boolean, arg_val_flag: boolean) {
        try {
            let clazz_instance = Java.use(clazz);
            clazz_instance[method_name].overloads.forEach((method: any) => {
                let same_flag: boolean = true;
                let args_string: string = method.argumentTypes.map((arg:any) => arg.className).join(',');
                //空入参的target方法入参写 ‘void’
                if (args_string == '') {
                    args_string = 'void'
                }
                let return_string: string = method.returnType.className.toString();
                if (arg_types != '' && arg_types != args_string) {
                    same_flag = false;
                }
                if (return_types != '' && return_types != return_string) {
                    same_flag = false;
                }
                if (same_flag) {
                    hook_method_implementation(clazz, method, trace_flag, arg_val_flag);
                }
            });
        }catch(e){
            console.log('no target class');
        }
    }

}